#!/usr/bin/env python3

from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import time

app = Flask(__name__)

desks = {
    1 : {'name' : 'Desk 1', 'colour' : 'red'},
    2 : {'name' : 'Desk 2', 'colour' : 'yellow'},
    3 : {'name' : 'Desk 3', 'colour' : 'green'},
    4 : {'name' : 'Desk 4', 'colour' : 'orange'},
    5 : {'name' : 'Desk 5', 'colour' : 'pink'},
    6 : {'name' : 'Desk 6', 'colour' : 'purple'}
}

job_queue = []

error_msg = False

manual_control = False

sched_alg = "none"

# Next job to be written to the file
next_job = None

# Last job that was written to the file
written_job = None

# Job that is being processed by logic
currently_processing = None

# Attempts to prevent race conditions between write_job and check_file
CURRENTLY_WRITING = 0

@app.route("/")
def index():
    templateData = {
        'desks' : desks
    }
    return render_template('index.html', **templateData)

@app.route("/manual")
def manual_toggle():
    global manual_control
    global written_job
    global CURRENTLY_WRITING

    # prevent race condition
    while (CURRENTLY_WRITING):
        time.sleep(0.1)

    CURRENTLY_WRITING = 1

    manual_control = not manual_control
    message = " Manual override toggled."
    error_msg = False

    written_job = None

    file = open("dest.txt","w")
    file.seek(0)
    file.truncate()

    if (manual_control):
        # Special character for manual override
        file.write("100")
    else:
        file.write("200")
    file.close()


    templateData = {
        'desks' : desks,
        'message' : message,
        'error_msg' : error_msg,
        'manual_control' : manual_control
    }

    CURRENTLY_WRITING = 0

    return render_template('index.html', **templateData)


@app.route("/<int:desk>/<action>")
def action(desk, action):
    global CURRENTLY_WRITING
    global currently_processing
    global job_queue

    # prevent race condition
    while (CURRENTLY_WRITING):
        time.sleep(0.1)

    CURRENTLY_WRITING = 1
    # if desk provided in URL does not exist, return error page
    if desk not in desks:
        print("\nCall to invalid desk number: " + str(desk) + "\n")
        templateData = {
            'desks' : desks,
            'message' : ' Desk does not exist!',
            'error_msg' : True
        }
        CURRENTLY_WRITING = 0
        return render_template('index.html', **templateData)

    deskName = desks[desk]['name']

    if action == "call":
        if desk not in job_queue and desk != currently_processing:
            message = " OfficeBot has been called to " + deskName + "."
            error_msg = False

            # add desk to front of job_queue
            job_queue.insert(0, desk)
            print("\ncall " + str(desk) + "\njob_queue is: " + str(job_queue) + "\n")
            reorder_jobs()
            write_job()
            CURRENTLY_WRITING = 0

        # multiple calls to the same location are ignored
        else:
            message = " OfficeBot was called to " + deskName + " already!"
            error_msg = True
            print("\ncall void" + "\njob_queue is: " + str(job_queue) + "\n")
            CURRENTLY_WRITING = 0
    else:
        message = " Unknown action."
        error_msg = True
    templateData = {
        'desks' : desks,
        'message' : message,
        'error_msg' : error_msg
    }
    CURRENTLY_WRITING = 0
    return render_template('index.html', **templateData)

# Reorders job_queue based on the sched_alg and current job
def reorder_jobs():
    global next_job
    global currently_processing
    global job_queue

    # Assumption: the desk numbers reflect their absolute order
    # Eg:
    #         |- 4
    #  3 -----|
    #         |--- 2
    #         |
    #    1 ---|
    #

    # Simplest algorithm. Checks closest location to currently_processing
    # and moves it to the front of the queue.
    if ((len(job_queue) > 1) and (currently_processing is not None)):
        differences = [abs(currently_processing - loc) for loc in job_queue]
        idx_smallest = differences.index(min(differences))
        print("REORDER_JOBS. Closest to " + str(currently_processing) + " is " + str(job_queue[idx_smallest]) + ".")
        job_queue.append(job_queue.pop(idx_smallest))
    print("REORDER_JOBS COMPLETE. job_queue: " + str(job_queue))

def write_job():
    global next_job
    global job_queue
    global written_job
    global currently_processing

    print("Logic is processing " + str(currently_processing) + ".")

    # If there are jobs in the queue
    if (len(job_queue) > 0):

        next_job = job_queue[-1]
        print("next_job: " + str(next_job))

        # Check if file is empty (logic has taken a destination to process)
        file = open("dest.txt","r+")
        content = file.read()
        print("File content: " + content)

        # If file contains a destination, overwrite it
        if (len(content) > 0):
            write_to_file(file)
        # Else, the destination is being processed and should be removed
        # from the job_queue.
        else:
            # If jobs have been written previously, we should remove that job
            # that was polled by logic from our job_queue
            # if written_job is none, this means the file was empty
            # because we just initialised the app. skip written_job removal.
            if (written_job is not None):
                job_queue.remove(written_job)
                print("REMOVED " + str(written_job) + " from job queue.")
                reorder_jobs()
                print("job_queue: " + str(job_queue))
                currently_processing = written_job
                written_job = None
                next_job = job_queue[-1]

            write_to_file(file)

    print("\n")

def write_to_file(f):
    global next_job
    global written_job
    global job_queue

    f.seek(0)
    f.truncate()
    f.write(str(next_job))
    f.close()
    print("next_job: " + str(next_job))
    written_job = next_job
    print("OVERWROTE, new content: " + str(next_job) + ".")

# Checks text file periodically, and if a job has been removed then it
# removes it from the job_queue
def check_file():
    global next_job
    global written_job
    global job_queue
    global CURRENTLY_WRITING
    global currently_processing

    if (CURRENTLY_WRITING == 0):

        CURRENTLY_WRITING = 1
        file = open("dest.txt","r")
        content = file.read()
        print("File content: " + content)
        # Initial state will have written_job = None
        if ((len(content) == 0) and written_job is not None):
            job_queue.remove(written_job)
            currently_processing = written_job
            written_job = None
            reorder_jobs()
            write_job()
            print("Logic has processed a job. New job_queue: " + str(job_queue))
        file.close()
        CURRENTLY_WRITING = 0

def main():
    scheduler = BackgroundScheduler()
    job = scheduler.add_job(check_file, 'interval', seconds=2)
    scheduler.start()

# redirect unknown URLs to homepage
@app.errorhandler(404)
def page_not_found(e):
    return index()


if __name__ == "__main__":
    main()
    app.run(host='0.0.0.0', port=80, debug=True)

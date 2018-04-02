#!/usr/bin/env python3

from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
import time
import numpy as np
import logging

app = Flask(__name__)

desks = {
    1 : {'name' : 'Desk 1', 'colour' : 'red'},
    2 : {'name' : 'Desk 2', 'colour' : 'yellow'},
    3 : {'name' : 'Desk 3', 'colour' : 'green'},
    4 : {'name' : 'Desk 4', 'colour' : 'orange'},
    5 : {'name' : 'Desk 5', 'colour' : 'pink'},
    6 : {'name' : 'Desk 6', 'colour' : 'purple'}
}

# x and y coordinates for desks
desks_x_y = [[1, 1], [3, 2], [0, 3], [3, 3], [4, 5], [1, 6]]

# matrix of distances between desks
distances = []

# for priority scheduling
priorities = [0, 0, 0, 0, 0, 0]

# starvation cut-off (number of priorities that can pass ahead
# before a normal call is turned into a priority one)
starvation_cutoff = -4

job_queue = []

error_msg = False

manual_control = False

# scheduling algorithm. values: simple, parameterised
sched_alg = "parameterised"

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

@app.route("/manual_refresh")
def manual_refresh():
    global manual_control

    if (manual_control):
        message = "Manual control is still on: please trigger the controller to disable it."
        error_msg = True
    else:
        message = "Manual control has been set off."
        error_msg = False

    # return either the normal or desk-filled index page
    templateData = {
        'desks' : desks,
        'message' : message,
        'error_msg' : error_msg,
        'manual_control' : manual_control
    }

    return render_template('index.html', **templateData)

@app.route("/manual")
def manual_toggle():
    global manual_control, written_job, CURRENTLY_WRITING

    # prevent race condition
    while (CURRENTLY_WRITING):
        time.sleep(0.1)

    CURRENTLY_WRITING = 1

    manual_control = True
    message = " Manual override toggled."
    error_msg = False

    written_job = None

    file = open("dest.txt","w")
    file.seek(0)
    file.truncate()

    if (manual_control):
        # Special character for manual override
        file.write("100")

    file.close()


    templateData = {
        'desks' : desks,
        'message' : message,
        'error_msg' : error_msg,
        'manual_control' : manual_control
    }

    CURRENTLY_WRITING = 0

    return render_template('index.html', **templateData)


def add_priority(desk):
    global job_queue, priorities

    # add desk to front of job_queue, behind any other prioritised desks
    i = 0
    while (len(job_queue) != i and priorities[job_queue[i] - 1] != 1):
        # print("len(job_queue): " + str(len(job_queue)) + " priorities[job_queue[i]]: " + str(priorities[job_queue[i]]))
        # print("i: " + str(i) + ". incrementing i.")
        i += 1

    if (len(job_queue) == i):
        job_queue.append(desk)
    else:
        job_queue.insert(i, desk)

    # set that desk to be a priority desk
    priorities[desk - 1] = 1


@app.route("/<int:desk>/<action>")
def action(desk, action):
    global CURRENTLY_WRITING, currently_processing, job_queue, sched_alg, priorities

    # prevent race condition
    while (CURRENTLY_WRITING):
        time.sleep(0.1)

    CURRENTLY_WRITING = 1
    # if desk provided in URL does not exist, return error page
    if desk not in desks:
        print("**ACTION**\nCall to invalid desk number: " + str(desk) + "\n")
        templateData = {
            'desks' : desks,
            'message' : ' Desk does not exist!',
            'error_msg' : True
        }
        CURRENTLY_WRITING = 0
        return render_template('index.html', **templateData)

    deskName = desks[desk]['name']

    if action == "call" or action == "priority-call":
        if desk not in job_queue and desk != currently_processing:
            message = " OfficeBot has been called to " + deskName + "."
            error_msg = False

            if action == "call":
                # add desk to end of job_queue
                job_queue.insert(0, desk)
            # priority call
            else:
                add_priority(desk)

            print("**ACTION**\nCall to " + str(desk) + ".")
            if (action == "call"):
                print("Standard call.\n")
            else:
                print("Priority call.\n")
            print("job_queue is: " + str(job_queue) + "\n")
            print("priorities queue: " + str(priorities))
            reorder_jobs(sched_alg)
            write_job()
            CURRENTLY_WRITING = 0

        # multiple calls to the same location are ignored
        else:
            message = " OfficeBot was called to " + deskName + " already!"
            error_msg = True
            print("**ACTION**\nCall void" + "\njob_queue is: " + str(job_queue) + "\n")
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

def calc_distances():
    global desks_x_y, distances

    nr_desks = len(desks_x_y)
    distances = np.zeros((len(desks_x_y), len(desks_x_y)))

    # creates a matrix of distances D(x,y): abs(x_1 - x_2) + abs(y_1 - y_2)
    for i in range (0, nr_desks):
        for j in range (0, nr_desks):
            distances[i][j] = abs((desks_x_y[i][0] - desks_x_y[j][0])) + abs((desks_x_y[i][1] - desks_x_y[j][1]))
    print("Calculated distances:\n\n" + str(distances) + "\n")

# Updates priority list to prevent starvation
def update_priorities():
    global priorities, job_queue, starvation_cutoff
    for i in range(0, len(priorities)):
        # do not update priority of desks that are not in job_queue right now
        if ((i + 1) in job_queue):
            # skip if priority
            if priorities[i] != 1:
                # make the standard call a priority call
                if priorities[i] == starvation_cutoff:
                    print("Updating priority of " + str(i + 1) + ".\n")
                    job_queue.remove(i + 1)
                    # prioritise, move ahead
                    # TODO: any kind of problem with written_job/currently_processing?
                    # what if no priorities left, issue?
                    add_priority(i + 1)
                # update all other desks
                else:
                    priorities[i] = priorities[i] - 1
    print("UPDATE_PRIORITIES done. priorities queue: " + str(priorities) + " job_queue: " + str(job_queue) + "\n")



# Reorders job_queue based on the sched_alg and current job
def reorder_jobs(alg):
    global next_job, currently_processing, job_queue, distances, priorities

    # Assumption: the desk numbers reflect their absolute order
    # Eg:
    #         |- 4
    #  3 -----|
    #         |--- 2
    #         |
    #    1 ---|
    #

    if ((len(job_queue) > 1) and (currently_processing is not None)):

        # if the current front of queue is not a priority
        if (priorities[job_queue[-1] - 1] != 1):
            # print("job_queue[-1]: " + str(job_queue[-1]) + " priorities[job_queue[-1] - 1]: " + str(priorities[job_queue[-1] - 1]))
            # print("priorities queue: " + str(priorities))
            print("Not a priority call!\n")
            # Simplest algorithm. Checks closest location to currently_processing
            # and moves it to the front of the queue.
            if (alg == "simple"):
                differences = [abs(currently_processing - loc) for loc in job_queue]
            # Uses distances calculated using calc_distances (x and y coordinates of desks).
            elif (alg == "parameterised"):
                # - 1 needed to account for 0-indexing of distances
                differences = [distances[currently_processing - 1][loc - 1] for loc in job_queue]
            else:
                print("SCHEDULING ALGORITHM NOT FOUND. job_queue unchanged.")

            idx_smallest = differences.index(min(differences))
            print("**REORDER_JOBS**\nScheduling algorithm: " + str(alg) + ".")
            print("job_queue was: " + str(job_queue))
            print("Closest to " + str(currently_processing) + " is " + str(job_queue[idx_smallest]) + ".")
            job_queue.append(job_queue.pop(idx_smallest))
            print("job_queue: " + str(job_queue) + "\n")
        else:
            # To make standard calls into priority ones if needed
            update_priorities()
            print("FRONT OF QUEUE HAS PRIORITY. REORDER_JOBS doesn't execute.")
            print("job_queue: " + str(job_queue) + "\n")

    else:
        print("REORDER_JOBS not needed for execution.")

def write_job():
    global next_job, job_queue, written_job, currently_processing, sched_alg, priorities

    print("**WRITE_JOB**\ncurrently_processing: " + str(currently_processing) + ".")

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
                print("REMOVED " + str(written_job) + " from job_queue.")
                reorder_jobs(sched_alg)
                currently_processing = written_job
                # reset priority of that desk
                priorities[currently_processing - 1] = 0
                print("priorities queue: " + str(priorities))
                written_job = None
                next_job = job_queue[-1]
                print("job_queue: " + str(job_queue))

            write_to_file(file)

    print("\n")

def write_to_file(f):
    global next_job, written_job, job_queue

    f.seek(0)
    f.truncate()
    f.write(str(next_job))
    f.close()
    print("**WRITE_TO_FILE**\nnext_job: " + str(next_job) + ", so overwrote file with " + str(next_job) + ".")
    written_job = next_job

# Checks text file periodically, and if a job has been removed then it
# removes it from the job_queue
def check_file():
    global next_job, written_job, job_queue, CURRENTLY_WRITING, currently_processing, sched_alg, priorities, manual_control

    if (CURRENTLY_WRITING == 0):

        CURRENTLY_WRITING = 1
        file = open("dest.txt","r+")
        content = file.read()
        print("**CHECK_FILE**\nFile content: " + content + "\n")
        if (not manual_control):
            # Initial state will have written_job = None
            if ((len(content) == 0) and written_job is not None):
                print("Logic has processed a job. START OF CHECK_FILE UPDATING.")
                job_queue.remove(written_job)
                currently_processing = written_job
                # reset priority of that desk
                priorities[currently_processing - 1] = 0
                print("priorities queue: " + str(priorities))
                written_job = None
                reorder_jobs(sched_alg)
                write_job()
                print("END OF CHECK_FILE. New job_queue: " + str(job_queue) + "\n")
        else:
            print("Manual control on. Looking for code 200 only\n")
            # Look for 200
            if (int(content) == 200):
                print("CODE 200. Emptying all.\n")
                # reset everything; assume position 1
                job_queue = []
                currently_processing = None
                writteb_job = None
                next_job = None
                priorities = [0, 0, 0, 0, 0, 0]
                position = 1
                # empty file
                file.seek(0)
                file.truncate()
                manual_control = False

        file.close()
        CURRENTLY_WRITING = 0

def main():
    # clear dest.txt when app.py first launched
    file = open("dest.txt","r+")
    content = file.read()
    file.seek(0)
    file.truncate()
    file.close()

    scheduler = BackgroundScheduler()
    job = scheduler.add_job(check_file, 'interval', seconds=2)
    scheduler.start()

    if (sched_alg == "parameterised"):
        calc_distances()

    # disable Flask HTTP messages (better readability)
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

# redirect unknown URLs to homepage
@app.errorhandler(404)
def page_not_found(e):
    return index()


if __name__ == "__main__":
    main()
    app.run(host='0.0.0.0', port=80, debug=True)

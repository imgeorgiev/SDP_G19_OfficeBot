#!/usr/bin/env python3

from flask import Flask, render_template

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

sched_alg = "none"

next_job = None

written_job = None

@app.route("/")
def index():
    templateData = {
        'desks' : desks
    }
    return render_template('index.html', **templateData)


@app.route("/<int:desk>/<action>")
def action(desk, action):
    # if desk provided in URL does not exist, return error page
    if desk not in desks:
        print("\nDEBUG:\nCall to invalid desk number: " + str(desk) + "\n")
        templateData = {
            'desks' : desks,
            'message' : ' Desk does not exist!',
            'error_msg' : True
        }
        return render_template('index.html', **templateData)

    deskName = desks[desk]['name']

    if action == "call":
        if desk not in job_queue:
            message = " OfficeBot has been called to " + deskName + "."
            error_msg = False

            # add desk to front of job_queue
            job_queue.insert(0, desk)
            print("\nDEBUG:\ncall " + str(desk) + "\njob_queue is: " + str(job_queue) + "\n")
            reorder_jobs()

        # multiple calls to the same location are ignored
        else:
            message = " OfficeBot was called to " + deskName + " already!"
            error_msg = True
            print("\nDEBUG:\ncall VOID" + "\njob_queue is: " + str(job_queue) + "\n")
    else:
        message = " Unknown action."
        error_msg = True
    templateData = {
        'desks' : desks,
        'message' : message,
        'error_msg' : error_msg
    }

    return render_template('index.html', **templateData)

def reorder_jobs():
    global next_job
    # Reorders job_queue based on the sched_alg and current job
    # TO-DO implement basic scheduling alg

    # Idea: the desk numbers reflect their absolute order
    # Eg:
    #         |- 4
    #  3 -----|
    #         |--- 2
    #         |
    #    1 ---|
    #
    if (len(job_queue) > 0):
        next_job = job_queue[-1]
        print("next job is: " + str(next_job))
        write_job()

def write_job():
    global next_job # TODO: might not need to be global
    global job_queue
    global written_job
    # TODO: poll the document every second to add to it if empty.

    # If there are jobs in the queue
    if (len(job_queue) > 0):

        # Check if file is empty (logic has taken a destination to process)
        file = open("dest.txt","r")
        content = file.read()
        file.close()
        print("Content of file is: " + content)
        # TODO: Might cause issues if logic pulls information between read &
        # write here (inaccurate data)

        # If file contains a destination, overwrite it
        if (len(content) > 0):
            # TODO: extract into own function
            file = open("dest.txt","w")
            file.write(str(next_job))
            file.close()
            print("Next job is: " + str(next_job))
            written_job = next_job
            print("Overwrote, new destination: " + str(next_job) + ".")
            #TODO: keep track of latest one that was written in
        # Else, the destination is being processed and should be removed
        # from the job_queue.
        # TODO: the first time we get an empty is because of init
        else:
            # If jobs have been written previously, we should remove that job
            # that was polled by logic from our job_queue
            if (written_job is not None):
                job_queue.remove(written_job)
                print("Removed " + str(written_job) + " from job queue.")
                print("job_queue is: " + str(job_queue))
                written_job = None
                next_job = job_queue[-1]

            # Write
            file = open("dest.txt","w")
            file.write(str(next_job))
            file.close()
            print("Next job is: " + str(next_job))
            written_job = next_job
            print("Wrote, new destination: " + str(next_job) + ".")

    print("\n")

# redirect unknown URLs to homepage
@app.errorhandler(404)
def page_not_found(e):
    return index()


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

#!/usr/bin/env python3

from flask import Flask, render_template

app = Flask(__name__)

global desks, job_queue, sched_alg, next_job

desks = {
    1 : {'name' : 'Desk 1', 'colour' : 'red'},
    2 : {'name' : 'Desk 2', 'colour' : 'yellow'},
    3 : {'name' : 'Desk 3', 'colour' : 'green'},
    4 : {'name' : 'Desk 4', 'colour' : 'orange'},
    5 : {'name' : 'Desk 5', 'colour' : 'pink'},
    6 : {'name' : 'Desk 6', 'colour' : 'purple'}
}

#TODO: temporary edit
job_queue = [5, 1, 3, 4]

error_msg = False

sched_alg = "none"

next_job = None

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
    write_queue()

def write_queue():
    #TODO: is read/write going to cause sync issues when used with logic_draft

    # If there are jobs in the queue
    if (len(job_queue) > 0):

        # process file, check if any items were removed
        # remove them from the job_queue
        # put the new queue in (if still not empty)

        # Open file
        file = open("dest.txt","r")
        content = file.read()
        file.close()

        # Convert content to list of ints
        content = content.split()
        content = list(map(int, content))
        print(content)



    else:
        print("write_queue was called, but there are no jobs in job_queue.")

        # Check if job_queue

        # # Check if file is empty (logic has taken a destination to process)
        # file = open("dest.txt","r")
        # content = file.read()
        # file.close()
        # print("Content of file is: " + content)
        # # TODO: Might cause issues if logic pulls information between read &
        # # write here (inaccurate data)
        #
        # # If file contains a destination still:
        # if (len(content) > 0):
        #     next_job = job_queue[-1]
        #     file = open("dest.txt","w")
        #     file.write(str(next_job))
        #     file.close()
        #     print("Overwritten new destination: " + str(next_job) + ".")
        # # Else, the destination is being processed and should be removed
        # # from the job_queue.
        # else:
            # Check needed as on initialisation, dest.txt is empty and
            # next_job is None
            # if (next_job is None):
            #     job_queue.remove(next_job)
            #     print("Removed " + next_job + " from job queue.")
            #     print("job_queue is: " + str(next_job))
            # else:
            #     print("File is empty on initialisation, no action taken.")

# redirect unknown URLs to homepage
@app.errorhandler(404)
def page_not_found(e):
    return index()


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

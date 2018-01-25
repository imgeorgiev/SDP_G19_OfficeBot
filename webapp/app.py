from flask import Flask, render_template, request
app = Flask(__name__)

desks = {
   1 : {'name' : 'Desk 1'},
   2 : {'name' : 'Desk 2'},
   3 : {'name' : 'Desk 3'},
   4 : {'name' : 'Desk 4'},
   5 : {'name' : 'Desk 5'},
   6 : {'name' : 'Desk 6'}
   }

job_queue = []

error_msg = False

@app.route("/")
def index():
   templateData = {
      'desks' : desks
      }
   return render_template('index.html', **templateData)

@app.route("/<desk>/<action>")
def action(desk, action):
   desk = int(desk)
   deskName = desks[desk]['name']

   if action == "call":
      if desk not in job_queue:
          message = " OfficeBot has been called to " + deskName + "."
          error_msg = False
          job_queue.insert(0, desk)
          print("\nDEBUG:\ncall " + str(desk) + "\njob_queue is: " + str(job_queue) +"\n")
      # multiple calls to the same location are ignored
      else:
          message = " OfficeBot was called to " + deskName + " already!"
          error_msg = True
          print("\nDEBUG:\ncall VOID" + "\njob_queue is: " + str(job_queue) +"\n")

   templateData = {
      'desks' : desks,
      'message' : message,
      'error_msg' : error_msg
   }

   return render_template('index.html', **templateData)

if __name__ == "__main__":
   app.run(host='0.0.0.0', debug=True)

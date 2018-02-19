### Meeting notes 15.01 - first idea

Idea: Office bot: a robot that can be called/scheduled through a web-app, that can deliver mail/packages/documents/stationery/fruit/water/rubbish
* Controlled through web-app?
* Follows pre-determined pathway on ground?

### Meeting notes 17.01 - idea of implementation

* Routes would be hard, how to pick up things
* Web-app is scaleable aspect
* Market approach: saves time (send off for signature of manager), multitasking, time for proper breaks
* Office Bot (Team RetroSpark for now)
* Temp speaker for Friday: Callum
* MAKE SLIDE, pretty slide
* Precomputed lines being followed, with map. Some depth sensing.
* Web-app for ordering it around
* External computer for steering -> look into EV3
* http://thetechnicgear.com/2014/03/howto-create-line-following-robot-using-mindstorms/ (white floor, black line)
* Colour-coded destination
* Might use Wi-Fi signal strength?
* Start off with a robot that can follow different paths
* Two wheel robot with sphere
* Raspberry Pi - programming in python etc. middle-man for processing, 35 quid for pi, 20 quid for camera
* Localisation of robot?
* Basic line-following robot (ultrasonic, gyro, color) -- use previous SDP code
* PROJECT PLAN (http://www.inf.ed.ac.uk/teaching/courses/sdp/projectplan2018.html) 15%!
* go through use case?

### Meeting notes 18.01 - Connie meeting

* Web app button for arrived/can leave
* Ask client about ROS/wifi capabilities
* Connie sdp code will find
* Project plan: milestones. Connie is willing 2 read through! Mention core features/improvements (collisions, camera)
* Fill in doodle poll again for weekly meetings
* Will get scope idea after pitch+client
* Seems fairly ambitious but achievable: report will do well!
* Ask client about whether we can decide color line, floor color: ask client -> will define how hard camera/vision will be. contact on slack
* If collision but no avoidance implementation: stop & sound
* Pi: for easier programming & higher processing power
* Slide: robot, diagram, webapp -> make mockup
* Write out a draft of pitch

### Meeting notes 19.01 - pitch feedback

To include in project plan:
* staged development
* milestones
* constraint/assumptions for prototype
* interface system
* background info eg. stats (exist in some form already?)
* picture, physical mockup, state diagram
* v important to have how we will develop space on level 3 to demonstrate. talk to gary in week 2
* **Wednesday soft deadline for report to get feedback**

we can offload some of the processing onto a laptop, justify it in report

##### Siobhan's feedback:

* include in report that ppl won't take items out of tray = assumptions, or implement weight/sensor. what about mistake calling? -> assumption for future implementation.
* docking place
* ability to charge itself
* roomba -- existing technology, we are building technology on top of it. mention in report
* replacing with pi = camera capabilities. **only do hacky things with camera** (aka not actual obstacle detection as it's a project on its own, but if something jumps in front of it/sudden change), just to experiment with it
* internet has template of connecting web-apps to pis
* IoT problems are all online & solved <3
* can give report advice but busy thursday

##### Connie's feedback:

next steps:
* project plan. **reports are very important 50%!!**
* rasp. pi yes/no? ask gary.
* initial prototype: follow a coloured line

we can always start with focus on initial implementation, then specialise in vision maybe. allocations. sub-teams.
eg. Yijie: vision, Vaida: web-app, Callum: manager -> how do we structure team?

* planning meetings where people work in the space together, fix bugs etc

Milestones: set yourself, and evaluated. in project plan. idk if we can modify milestones? dates on website.
* follow coloured line, choose specific coloured line.
* simple collision detection (alarm if stuck)
* integration with web-app

* Can give report advice

### Meeting 22.01 - organisation

* buy Pi
* EV3/arduino as hardware controller? EV3

Tasks:
* Build a basic robot
* Control of robot, basic workspace sketch
* Web-app brainstorm
* Writing report

* on-the-way delivery: optional feature
* agile development: people focus on tasks that they have time/skill for, rather than micro-managing tasks.
* pair-programming, working around people
* battery situation
* **Python. SSH-ing into Pi.**
* Voice feedback (greet you at desk), lets you know there's a collision
* Arduino: tag detection capabilities. some stronger sensors are not lego-capable.

Milestones:
**7th Feb: first milestone**
* do a small sprint weekend before
* basic line-following
* mockup environment, diagram
* logic of robot draft

### Meeting notes 29.01

* Basic robot by end of week
* Camera for detecting edges of object for collision avoidance
* Remote-controlled robot (bluetooth in Pi for PS4 controller: Callum), as well as basic line following for first client demo
* IVR from two years ago had line following/detection

### Meeting notes 05.02

##### Demo:
* web-app on pi & console output
* show video of camera
* one (possibly) sensor for line-following
* ** Any changes to a group’s milestones should be written up and sent to the client by the end of
the day for official approval.**

arduino forwarding of sensors to pi
ev3 has a mini-usb port, so can power it.

### Demo feedback 07.02
* needing to connect through eduroam for app, as needs to be traceable (computing regulations)- solutions/workarounds?
* quantitative testing needed (graphs, some way of showing why we are choosing some values/how we test)
* 3d printing: make the right choices, cheap material.


### Notes for meeting 12.02
* Trello tasks & demo/milestones review

### Notes for meeting 19.02 - Sprint week
* Pi accessible everywhere & interface accessible
* Install OpenCV on Pi
* Line-following and multi-colour line following
* Test camera in demo space, pure functions for camera (efficiency for Pi), how to actually interact with robot. Laplace transforms?
* Line following: rounded corners? Multi-lines?

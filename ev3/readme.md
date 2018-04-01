## ps4_control.py
Launch python script from the EV3. Allows you to control the robot with a joystick via bluetooth.
First you must pair te controller with the EV3; Left stick used for steering; right stick used for moving forwards and backwards
4 buttons on the right side of the controller makes the robot talk (mostly there for evaluation purposes).

## TCP Communcation
All source files contained within the `tcp` folder.

To use to comms protocol launch `python3 parser.py`.

To check if working correctly launch `python3 tcp_test.py` from another machine connected to the EV3. Make sure that you put in the correct IP in the `parser.py` file

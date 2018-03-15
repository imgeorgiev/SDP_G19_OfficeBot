# TCP Comms between the RPi and EV3

A  new library called `tcpcom_py3` has been created so that it is compatable with python3.

`tcp_rpi.py` a higher-level class of using the interface. To use it simply import it in your code and initialise it. Best import it using its absolute path.

`s = Server(5005)  # port 5005 is being used currently`

Available functions are:

- `getSensors()` - requests sensor values of the EV3. If the EV3 is not connected at this time, calling this will crash the program
- `sendMotorCommand(l_motor, r_motor)`
- `sendLineFollow(currentColor, nextColor, side, numJunctionsToIgnote)`

Common issues:
- RPi sometime changes it's IP even though it is set to have a static one. This can be checked with `ifconfig` in its terminal. The IP as of wirting this is `169.254.23.50`
- Sometimes the EV3 becomes really slow and unresponsive due to an unknown reason. It responds to messages with a big delay. This can be checked by using the onboard buttons and checking its responsiveness. To fix this simply reboot the EV3.
- The joystick can't be connected the the RPi while its working as a TCP Server

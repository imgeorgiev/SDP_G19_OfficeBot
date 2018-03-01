# LineFollower.py class user guide

This class provides a _line follower_ object. 
 
### Instantiating a line follower

The _speed_ parameter is optional and will default to 200 degrees per second.

```
speed = 200
lf = LineFollower(speed)
```

### Using the line follower

The method _follow_line_ can be used to tell the EV3 to attempt line following, given the following parameters:
_colorToFollow_, _nextLineColor_, _sideTurnIsOn_ and _junctionsToIgnore_.

```
lf.follow_line("Black", "Blue", "Left", 0)
```

This example will instruct the robot to follow a black line, and turn and stop on the next blue line, provided it's on the left.

_colorToFollow_ and _nextLineColor_ take any color from the list (case sensitive):

```
"None", "Black", "Blue", "Green", "Yellow", "Red", "White" and "Brown"
```

_sideTurnIsOn_ takes either "Left" or "Right"


**Following multiple lines**
You can also pass a list with multiple lines to follow_lines:
```
listOfLines = [['Black', 'Blue', 'Left', '0'],
               ['Blue', 'Black', 'Right', '0'],
               ['Black', 'Blue', 'Right', '0']]
lf.follow_lines(listOfLines)
```

An example can be seen in [Example_LineFollower.py](./Example_LineFollower.py)

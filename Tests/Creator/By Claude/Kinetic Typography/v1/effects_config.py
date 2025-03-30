# SPECIAL_BEAT_SKIP_VALUES: Defines how many beat intervals to skip when a special character is encountered.
# Keys correspond to special characters:
#   '.'  -> Adds 2 skip beats (pause effect).
#   '&'  -> Adds 1 skip beat and triggers a pop-in animation.
#   '!'  -> Adds 1 skip beat and triggers a side-slide animation.
#   '^'  -> Adds 1 skip beat and triggers a rotation animation.
DEFAULT_BEAT_SKIP_VALUE = 1
SPECIAL_BEAT_SKIP_VALUES = {
    '.': 2,
    '&': 1,
    '!': 1,
    '^': 1
}

# SIDE_SLIDE_DURATION: Duration (in seconds) over which the side-slide animation occurs (triggered by '!').
SIDE_SLIDE_DURATION = 2.0

# POP_IN_DURATION: Duration (in seconds) for the pop-in animation (triggered by '&').
POP_IN_DURATION = 0.2

# POP_IN_INITIAL_SCALE: The initial scale factor for the pop-in effect; the clip scales from this value down to 1.0.
POP_IN_INITIAL_SCALE = 5.0

# ROTATION_DURATION: Duration (in seconds) for the rotation animation (triggered by '^').
ROTATION_DURATION = 0.5

# ROTATION_INITIAL_ANGLE: The initial rotation angle (in degrees) for the rotation effect; the text rotates from this angle to 0°.
ROTATION_INITIAL_ANGLE = 20
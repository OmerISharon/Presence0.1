"""
Kinetic Typography Video Generator

Special Characters in the input text:
  '.'  : Removed from the displayed text and causes a pause. Each '.' adds a skip of SPECIAL_BEAT_SKIP_VALUES['.'] beats.
  '*'  : Removed from the displayed text and toggles the foreground (text) and background colors.
         A subsequent '*' toggles the colors back.
  '&'  : Removed from the displayed text and triggers a pop-in effect (sizing and fade-in animation)
         on the word. Each '&' adds a skip of SPECIAL_BEAT_SKIP_VALUES['&'] beats.
  '!'  : Removed from the displayed text and triggers a side-slide effect, where the word enters from the side,
         overshoots the center, and then settles back to the center. Each '!' adds a skip of SPECIAL_BEAT_SKIP_VALUES['!'] beats.
  '^'  : Removed from the displayed text and triggers a rotation effect.
         The word rotates from an initial angle (e.g. 20°) to 0° over the effect duration.
         
Usage:
    python main.py "Your text here with special characters like . * & ! ^" [--uppercase]
"""

from moviepy.video.fx import FadeIn

from config import *
from effects_config import *

def apply_rotation_effect(clip, effect_duration=ROTATION_DURATION, initial_angle=ROTATION_INITIAL_ANGLE):
    """
    Applies a rotation effect to a clip:
      - The clip rotates from initial_angle (in degrees) to 0° over effect_duration seconds.
    """
    def angle_func(t):
        if t >= effect_duration:
            return 0
        return initial_angle * (1 - t / effect_duration)
    return clip.rotate(angle_func)

def apply_side_slide_effect(clip, effect_duration, overshoot=50):
    """
    Applies a side-slide effect to a clip:
      - The clip slides in from off-screen left,
      - Overshoots the center by 'overshoot' pixels,
      - Then returns to center,
      over effect_duration seconds.
    After effect_duration, the clip remains centered.
    
    Args:
        clip: The clip to animate.
        effect_duration: Duration (in seconds) during which the movement happens.
        overshoot: The number of pixels to overshoot the center.
    """
    center_x = VIDEO_WIDTH / 2
    center_y = VIDEO_HEIGHT / 2
    start_x = -clip.w  # Start completely off-screen to the left.

    def position_func(t):
        if t >= effect_duration:
            return (center_x - clip.w / 2, center_y - clip.h / 2)
        u = t / effect_duration
        if u <= 0.5:
            # First half: slide from start_x to (center_x + overshoot)
            u2 = u / 0.5
            x = start_x + (center_x + overshoot - start_x) * u2
        else:
            # Second half: slide back from (center_x + overshoot) to center_x
            u2 = (u - 0.5) / 0.5
            x = (center_x + overshoot) + (center_x - (center_x + overshoot)) * u2
        return (x - clip.w / 2, center_y - clip.h / 2)

    return clip.with_position(position_func)

def apply_pop_in_effect(clip, pop_duration=POP_IN_DURATION):
    """
    Applies a pop-in effect to a clip:
      - Scales from POP_IN_INITIAL_SCALE to 1.0 over pop_duration seconds.
      - Fades in over pop_duration seconds.
    """
    clip = clip.resized(lambda t: POP_IN_INITIAL_SCALE - (POP_IN_INITIAL_SCALE - 1) * (min(t, pop_duration) / pop_duration))
    clip = FadeIn(duration=pop_duration).apply(clip)
    return clip
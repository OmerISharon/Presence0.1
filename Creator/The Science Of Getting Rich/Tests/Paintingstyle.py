#!/usr/bin/env python3
from manim import *

class PaintingStyleTextAnimation(Scene):
    def construct(self):
        # Create a canvas background resembling a painted canvas (beige color)
        canvas = Rectangle(
            width=1080, height=1920,
            fill_color="#F5F5DC",  # Beige
            fill_opacity=1,
            stroke_width=0
        )
        self.add(canvas)
        
        # Define the text to animate
        text_str = "Painting-Style Animation"
        
        # Create a Text mobject.
        # Using a bold font and a defined stroke helps simulate a brush effect.
        text_mob = Text(
            text_str,
            font="Arial",
            weight=BOLD,
            color=BLACK
        ).scale(1.5)
        text_mob.move_to(ORIGIN)
        
        # Split the text into individual letters to animate them one by one.
        letters = VGroup(*text_mob)
        
        # Create an animation for each letter using Write,
        # which draws the outlines as if painted by a brush.
        # The lag_ratio parameter makes the letters appear one after another.
        self.play(AnimationGroup(
            *[Write(letter, run_time=0.5) for letter in letters],
            lag_ratio=0.1
        ))
        
        self.wait(2)

if __name__ == "__main__":
    # Render the scene when running this script directly.
    # Adjust the configuration as needed.
    from manim import config
    config.background_color = "#F5F5DC"  # Set canvas color to beige
    scene = PaintingStyleTextAnimation()
    scene.render()

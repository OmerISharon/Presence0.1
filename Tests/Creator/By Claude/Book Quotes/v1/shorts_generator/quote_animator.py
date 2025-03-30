"""
Quote Animator module using Manim to create handwriting-style and kinetic typography effects.
"""

import os
import textwrap
from pathlib import Path

from manim import *
from shorts_generator.text_effects import apply_old_book_styling

# Configure Manim to be quiet by default
config.verbosity = "WARNING"


class QuoteAnimator:
    """Class to create animated quotes using Manim."""
    
    def __init__(self, quote, width=1080, height=1920, fps=60, duration=15):
        self.quote = quote
        self.width = width
        self.height = height
        self.fps = fps
        self.duration = duration
        
        # Configure Manim settings
        config.pixel_width = width
        config.pixel_height = height
        config.frame_rate = fps
        
        # Derived settings based on duration
        # This helps adjust animation speeds based on quote length and video duration
        self.words_per_second = len(quote.split()) / (duration * 0.6)  # Use 60% of duration for text
        self.writing_speed = max(0.5, min(2.0, 1.0 / self.words_per_second * 5))
    
    def split_quote_into_segments(self, max_chars_per_line=40):
        """Split the quote into smaller segments for animation."""
        # Use textwrap to create aesthetically pleasing line breaks
        lines = textwrap.wrap(self.quote, width=max_chars_per_line)
        
        # Further segment very long lines if needed
        segments = []
        for line in lines:
            if len(line) > max_chars_per_line * 0.8:  # If line is close to max width
                words = line.split()
                midpoint = len(words) // 2
                segments.append(' '.join(words[:midpoint]))
                segments.append(' '.join(words[midpoint:]))
            else:
                segments.append(line)
                
        return segments
    
    def create_animation(self, output_path):
        """Create the quote animation and save to output_path."""
        # Define a custom Manim scene for our animation
        class OldBookQuoteScene(Scene):
            def __init__(self, quote_animator, **kwargs):
                super().__init__(**kwargs)
                self.quote_animator = quote_animator
            
            def construct(self):
                # Set background to old paper color
                self.camera.background_color = "#F5EBC8"
                
                # Create decorative border
                border = Rectangle(
                    height=config.frame_height * 0.9,
                    width=config.frame_width * 0.9,
                    stroke_width=3,
                    stroke_color=DARK_BROWN
                )
                border.set_fill(opacity=0)
                
                # Add corner decorations
                corners = self.create_corner_decorations()
                
                # Create quote text elements
                segments = self.quote_animator.split_quote_into_segments()
                text_objects = self.create_text_objects(segments)
                
                # Arrange text objects in a centered vertical group
                text_group = VGroup(*text_objects)
                text_group.arrange(DOWN, buff=0.6)
                text_group.scale(0.9)  # Scale to fit nicely
                text_group.move_to(ORIGIN)
                
                # Start the animation sequence
                
                # 1. Fade in border and corners first
                self.play(
                    Create(border, run_time=1.5),
                    *[FadeIn(corner, run_time=1) for corner in corners]
                )
                
                # 2. Animate each text segment with handwriting effect
                for i, text in enumerate(text_objects):
                    # Calculate appropriate run time based on text length
                    run_time = max(1.5, min(3.5, len(text.text) * 0.1))
                    
                    # Different animation for first segment vs. others
                    if i == 0:
                        self.play(Write(text, run_time=run_time))
                    else:
                        self.play(Write(text, run_time=run_time))
                
                # 3. Add a decorative divider line
                divider = Line(
                    start=text_group.get_bottom() + DOWN * 0.5 + LEFT * 2,
                    end=text_group.get_bottom() + DOWN * 0.5 + RIGHT * 2,
                    color=DARK_BROWN
                )
                
                self.play(Create(divider, run_time=1))
                
                # 4. Final pause to let viewers read
                self.wait(3)
            
            def create_corner_decorations(self):
                """Create decorative corner elements."""
                corners = []
                
                # Define a simple corner decoration
                def create_corner():
                    lines = VGroup()
                    # Horizontal line
                    lines.add(Line(
                        start=ORIGIN, 
                        end=RIGHT, 
                        stroke_width=3,
                        color=DARK_BROWN
                    ))
                    # Vertical line
                    lines.add(Line(
                        start=ORIGIN, 
                        end=UP, 
                        stroke_width=3,
                        color=DARK_BROWN
                    ))
                    # Diagonal flourish
                    lines.add(Arc(
                        radius=0.5,
                        angle=PI/2,
                        start_angle=0,
                        stroke_width=2,
                        color=DARK_BROWN
                    ))
                    return lines
                
                # Create and position corners
                corner = create_corner()
                
                # Top-left corner
                c1 = corner.copy()
                c1.to_corner(UL, buff=0.5)
                
                # Top-right corner
                c2 = corner.copy()
                c2.rotate(PI/2)
                c2.to_corner(UR, buff=0.5)
                
                # Bottom-left corner
                c3 = corner.copy()
                c3.rotate(-PI/2)
                c3.to_corner(DL, buff=0.5)
                
                # Bottom-right corner
                c4 = corner.copy()
                c4.rotate(PI)
                c4.to_corner(DR, buff=0.5)
                
                corners.extend([c1, c2, c3, c4])
                return corners
            
            def create_text_objects(self, segments):
                """Create styled text objects for each segment."""
                text_objects = []
                
                for segment in segments:
                    # Create text with handwriting font styling
                    text = Text(
                        segment,
                        font="Times New Roman",  # Can be replaced with actual handwriting font
                        color=DARK_BROWN,
                        weight=NORMAL
                    )
                    
                    # Apply old book styling effects
                    apply_old_book_styling(text)
                    
                    text_objects.append(text)
                
                return text_objects
        
        # Set constants for the scene
        DARK_BROWN = "#5C4033"
        
        # Instantiate and render the scene
        scene = OldBookQuoteScene(quote_animator=self)
        scene.render()
        
        # Find and move the output file to the specified path
        # Check multiple possible output locations based on your system's structure
        print("Searching for the output video file...")
        
        # Try several possible locations where Manim might save the file
        potential_locations = [
            Path("media") / "videos" / "OldBookQuoteScene" / f"{self.height}p{self.fps}",
            Path("media") / "videos" / f"{self.height}p{self.fps}",
            Path("media") / "videos"
        ]
        
        # Search for the MP4 file in all potential locations
        output_file = None
        for location in potential_locations:
            print(f"Checking {location}...")
            if location.exists():
                mp4_files = list(location.glob("*.mp4"))
                if mp4_files:
                    output_file = mp4_files[0]
                    print(f"Found output file: {output_file}")
                    break
                else:
                    print(f"No MP4 files found in {location}")
        
        # If we still haven't found it, do a broader search
        if not output_file:
            print("Performing broader search for MP4 files...")
            all_mp4s = list(Path("media").glob("**/*.mp4"))
            if all_mp4s:
                # Sort by creation time, newest first
                all_mp4s.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                output_file = all_mp4s[0]
                print(f"Found most recent MP4 file: {output_file}")
        
        # If we found a file, copy it to the destination
        if output_file:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            import shutil
            print(f"Copying {output_file} to {output_path}")
            shutil.copy2(output_file, output_path)
            return True
        else:
            raise FileNotFoundError(
                f"Could not find any output MP4 files in the media directory. "
                f"Please check if Manim is generating output correctly."
            )
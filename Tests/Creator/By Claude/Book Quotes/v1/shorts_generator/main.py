"""
Main module for the YouTube Shorts Generator.
Provides high-level functions and CLI interface for generating videos.
"""

import argparse
import os
import sys
from pathlib import Path

from shorts_generator.quote_animator import QuoteAnimator
from shorts_generator.paper_generator import PaperTextureGenerator
from shorts_generator.utils.video_enhancer import VideoEnhancer

# Configuration constants
OUTPUT_FILE = "old_book_quote.mp4"
SHORTS_WIDTH = 1080
SHORTS_HEIGHT = 1920
FPS = 60
DURATION = 15  # seconds

# Default quote
DEFAULT_QUOTE = """The men and women who practice the foregoing instructions will certainly get rich; and the riches they receive will be in exact proportion to the definiteness of their vision, the fixity of their purpose, the steadiness of their faith, and the depth of their gratitude"""


class OldBookQuoteGenerator:
    """Main class to generate YouTube Shorts videos with animated text."""
    
    def __init__(self, output_file=OUTPUT_FILE, width=SHORTS_WIDTH, 
                 height=SHORTS_HEIGHT, fps=FPS, duration=DURATION,
                 quote=DEFAULT_QUOTE):
        self.output_file = output_file
        self.width = width
        self.height = height
        self.fps = fps
        self.duration = duration
        self.quote = quote
        
        # Set up paths
        self.temp_dir = Path("temp")
        self.assets_dir = Path("assets")
        
        # Create necessary directories
        self.temp_dir.mkdir(exist_ok=True)
        self.assets_dir.mkdir(exist_ok=True)
        
        # Initialize components
        self.paper_generator = PaperTextureGenerator(self.assets_dir)
        self.animator = QuoteAnimator(
            quote=self.quote,
            width=self.width,
            height=self.height,
            fps=self.fps,
            duration=self.duration
        )
        self.enhancer = VideoEnhancer(
            width=self.width,
            height=self.height,
            fps=self.fps,
            assets_dir=self.assets_dir
        )
        
        # Prepare assets
        self.prepare_assets()
    
    def prepare_assets(self):
        """Prepare necessary assets like paper textures and fonts."""
        # Create old paper texture if it doesn't exist
        paper_texture_path = self.assets_dir / "old_paper.jpg"
        if not paper_texture_path.exists():
            self.paper_generator.generate_old_paper_texture(paper_texture_path)
        
        # Ensure other necessary assets exist
        # This would include checking for fonts, decorative elements, etc.
        self.check_and_download_fonts()
    
    def check_and_download_fonts(self):
        """Check if required fonts exist, download if needed."""
        handwriting_font_path = self.assets_dir / "handwriting.ttf"
        if not handwriting_font_path.exists():
            # In a real implementation, you would download a font from a reliable source
            print(f"Warning: Handwriting font not found at {handwriting_font_path}")
            print("Using default fonts instead. For best results, please add a handwriting font.")
    
    def generate(self):
        """Generate the complete YouTube Shorts video."""
        try:
            # Step 1: Create the base animation with Manim
            manim_output = self.temp_dir / "manim_animation.mp4"
            print("Generating base animation...")
            self.animator.create_animation(manim_output)
            
            # Step 2: Enhance with MoviePy
            print("Adding effects and enhancements...")
            self.enhancer.enhance_video(manim_output, self.output_file)
            
            print(f"Successfully generated YouTube Shorts video: {self.output_file}")
            print(f"Video specs: {self.width}x{self.height}, {self.fps} FPS, {self.duration}s duration")
            
            # Clean up temporary files if needed
            if manim_output.exists():
                try:
                    os.remove(manim_output)
                except PermissionError:
                    print(f"Note: Could not remove temporary file {manim_output} - it may be in use")
                    # Just continue without failing the whole process
                
            return True
            
        except Exception as e:
            print(f"Error generating video: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def generate_quote_video(quote=DEFAULT_QUOTE, output_file=OUTPUT_FILE, 
                        duration=DURATION, fps=FPS):
    """
    Generate a YouTube Shorts video with the given quote.
    
    Args:
        quote (str): The quote to animate
        output_file (str): Path to save the output video
        duration (int): Duration in seconds
        fps (int): Frames per second (default: 60 for Shorts)
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Ensure output is saved to the specific directory
    output_path = ensure_output_directory(output_file)
    
    generator = OldBookQuoteGenerator(
        output_file=str(output_path),
        duration=duration,
        fps=fps,
        quote=quote
    )
    return generator.generate()


def ensure_output_directory(output_file):
    """
    Ensure the output is saved to the specified directory.
    If the output_file is just a filename without a path, 
    it will be placed in the desired output directory.
    
    Args:
        output_file (str): The output filename or path
        
    Returns:
        Path: The full path where the file should be saved
    """
    # Define the specific output directory
    output_dir = Path("D:/2025/Projects/Presence/Presence0.1/Tests/Creator/By Claude/Book Quotes/v1/output")
    
    # Ensure output directory exists
    output_dir.mkdir(exist_ok=True)
    
    # Convert to Path object if it's a string
    output_path = Path(output_file)
    
    # If only a filename was provided without a path, place it in the output directory
    if len(output_path.parts) == 1:  # Just a filename
        return output_dir / output_path
    
    return output_path

def cli_main():
    """Command-line interface for the generator."""
    parser = argparse.ArgumentParser(
        description="Generate a YouTube Shorts video with an animated old book style quote"
    )
    
    parser.add_argument(
        "--quote", 
        type=str, 
        default=DEFAULT_QUOTE,
        help="Quote text to animate"
    )
    
    parser.add_argument(
        "--quote-file", 
        type=str, 
        help="Path to a text file containing the quote"
    )
    
    parser.add_argument(
        "--output", 
        type=str, 
        default=OUTPUT_FILE,
        help="Output video filename"
    )
    
    parser.add_argument(
        "--duration", 
        type=int, 
        default=DURATION,
        help="Video duration in seconds"
    )
    
    parser.add_argument(
        "--fps", 
        type=int, 
        default=FPS,
        help="Frames per second"
    )
    
    args = parser.parse_args()
    
    # If quote file is provided, read from it
    quote = args.quote
    if args.quote_file:
        try:
            with open(args.quote_file, 'r', encoding='utf-8') as f:
                quote = f.read().strip()
        except Exception as e:
            print(f"Error reading quote file: {str(e)}")
            return 1
    
    # Generate the video with direct path specification
    output_file = os.path.join(
        "D:/2025/Projects/Presence/Presence0.1/Tests/Creator/By Claude/Book Quotes/v1/output", 
        args.output
    )
    
    success = generate_quote_video(
        quote=quote,
        output_file=output_file,
        duration=args.duration,
        fps=args.fps
    )
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(cli_main())

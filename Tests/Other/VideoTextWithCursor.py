import time
import itertools
from moviepy import ImageClip, concatenate_videoclips
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def create_frame(text, cursor, size=(800, 200), bg_color=(0, 0, 0), text_color=(255, 255, 255), 
                font_size=30, font_path=None):
    """
    Create a frame with the given text and cursor.
    
    Args:
        text: Text to display
        cursor: Cursor character to append to text
        size: Size of the image (width, height)
        bg_color: Background color in RGB
        text_color: Text color in RGB
        font_size: Font size in pixels
        font_path: Path to TTF font file (optional)
    
    Returns:
        PIL Image object
    """
    # Create a blank image with background color
    img = Image.new('RGB', size, color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Use default font if no font path is provided
    if font_path:
        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()
    else:
        # Try to use a common system font, or fall back to default
        try:
            # Try a common monospace font that should be available on most systems
            font = ImageFont.truetype("Courier", font_size)
        except IOError:
            try:
                font = ImageFont.truetype("Courier New", font_size)
            except IOError:
                try:
                    font = ImageFont.truetype("DejaVuSansMono", font_size)
                except IOError:
                    font = ImageFont.load_default()
    
    # Calculate text position - we'll handle text and cursor separately
    # to ensure consistent positioning regardless of cursor character width
    
    # First get the text dimensions without cursor
    text_width, text_height = 0, 0
    if hasattr(draw, 'textsize'):
        text_width, text_height = draw.textsize(text, font=font)
    else:
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except AttributeError:
            # If all else fails, make a rough estimate
            text_width = len(text) * (font_size // 2)
            text_height = font_size
    
    # Calculate space width
    space_width = 0
    if hasattr(draw, 'textsize'):
        space_width, _ = draw.textsize(" ", font=font)
    else:
        try:
            bbox = draw.textbbox((0, 0), " ", font=font)
            space_width = bbox[2] - bbox[0]
        except AttributeError:
            # Estimate space width
            space_width = font_size // 3
    
    # Calculate cursor width - we'll use a fixed width space for cursor positioning
    cursor_width = font_size // 2  # Fixed width regardless of actual cursor character
    
    # Calculate total content width (text + space + cursor width)
    total_width = text_width + space_width + cursor_width
    
    # Center the text horizontally based on the total width
    x_position = (size[0] - total_width) // 2
    y_position = (size[1] - text_height) // 2
    
    # Draw the text
    draw.text((x_position, y_position), text, font=font, fill=text_color)
    
    # Draw the space and cursor
    draw.text((x_position + text_width, y_position), " " + cursor, font=font, fill=text_color)
    
    return np.array(img)

def animate_cursor_frames(duration=3, cursor_chars='|/-\\', interval=0.1, 
                         text="", **frame_kwargs):
    """
    Generate frames for a rotating cursor animation.
    
    Args:
        duration: Time in seconds for the animation
        cursor_chars: Characters to cycle through for the cursor
        interval: Time between cursor changes in seconds
        text: Text to display before the cursor
        frame_kwargs: Additional arguments for create_frame function
    
    Returns:
        List of (frame, duration) tuples
    """
    cursor_cycle = itertools.cycle(cursor_chars)
    frames = []
    
    num_frames = int(duration / interval)
    for _ in range(num_frames):
        cursor = next(cursor_cycle)
        frame = create_frame(text, cursor, **frame_kwargs)
        frames.append((frame, interval))
    
    return frames

def type_text_frames(text, typing_speed=0.1, cursor="|", **frame_kwargs):
    """
    Generate frames for typing animation.
    
    Args:
        text: Text to type out
        typing_speed: Time between typing each character
        cursor: Cursor character to show
        frame_kwargs: Additional arguments for create_frame function
    
    Returns:
        List of (frame, duration) tuples
    """
    frames = []
    current_text = ""
    
    for char in text:
        current_text += char
        frame = create_frame(current_text, cursor, **frame_kwargs)
        frames.append((frame, typing_speed))
    
    return frames

def create_typing_video(output_file="typing_animation.mp4", width=800, height=200, 
                       text="Welcome to the character-by-character typing simulator!",
                       typing_speed=0.1, fps=24):
    """
    Create a video of typing animation with a rotating cursor at start and end.
    
    Args:
        output_file: Path to save the output video
        width: Width of the video in pixels
        height: Height of the video in pixels
        text: Text to type out in the video
        typing_speed: Time between typing each character
        fps: Frames per second for the video
    """
    size = (width, height)
    frame_kwargs = {'size': size}
    
    # Collect all frames with their durations
    all_frames = []
    
    # Initial pause with rotating cursor (3 seconds)
    all_frames.extend(animate_cursor_frames(duration=3, text="", **frame_kwargs))
    
    # Type the text character by character
    all_frames.extend(type_text_frames(text, typing_speed, **frame_kwargs))
    
    # Final pause with rotating cursor (3 seconds)
    all_frames.extend(animate_cursor_frames(duration=3, text=text, **frame_kwargs))
    
    # Create clips from frames
    clips = []
    for frame, duration in all_frames:
        clip = ImageClip(frame).with_duration(duration)
        clips.append(clip)
    
    # Concatenate all clips
    final_clip = concatenate_videoclips(clips, method="compose")
    
    # Write the result to a file
    final_clip.write_videofile(output_file, fps=fps, codec="libx264", 
                               audio=False, ffmpeg_params=["-pix_fmt", "yuv420p"])
    
    print(f"Video saved as {output_file}")

def main():
    # Text to be typed
    text_to_type = "Welcome to the character-by-character typing simulator with a fixed cursor!"
    
    # Create the typing animation video
    create_typing_video(
        output_file="typing_animation.mp4",
        width=800, 
        height=200,
        text=text_to_type,
        typing_speed=0.1,  # Time between characters in seconds
        fps=30
    )
    
    print("Done!")

if __name__ == "__main__":
    main()
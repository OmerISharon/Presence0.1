from moviepy import *
from moviepy.audio.fx.AudioLoop import AudioLoop
from moviepy.audio.AudioClip import concatenate_audioclips, AudioArrayClip
import numpy as np
import os

# === CONFIG ===
IMAGE_FOLDER = fr"D:\2025\Projects\Presence\Presence0.1\Tests\Creator\TickTock_v1\resources\images"
MUSIC_PATH = fr"D:\2025\Projects\Presence\Presence0.1\Tests\Creator\TickTock_v1\resources\audio\background.mp3"
OUTPUT_FILE = fr"D:\2025\Projects\Presence\Presence0.1\Tests\Creator\TickTock_v1\output\results.mp4"

DURATION = 1.0                         # Duration each image shows (in seconds)
START_DELAY = 0.5                      # Time before the first image appears (in seconds)
RESOLUTION = (1080, 1920)              # 9:16 video resolution

# === INTRO CONFIG ===
INTRO_DURATION = 3.0
INTRO_TEXT = "PHOTOS SLIDE"
TEXT_COLOR = (255, 255, 255)           # white
BACKGROUND_COLOR = (0, 0, 0)           # black
FONT_PATH = fr"C:\Windows\Fonts\ALGER.ttf"

def load_images(folder):
    valid_extensions = ['.jpg', '.jpeg', '.png']
    files = sorted([
        os.path.join(folder, f) 
        for f in os.listdir(folder)
        if os.path.splitext(f)[1].lower() in valid_extensions
    ])
    return files

def make_video(image_paths, duration, resolution, output_file, music_path):
    clips = []

    # === INTRO CLIP WITH TEXT ===
    intro_bg = ColorClip(size=resolution, color=BACKGROUND_COLOR, duration=INTRO_DURATION)
    txt_clip = TextClip(
        text=INTRO_TEXT,
        font=FONT_PATH,
        font_size=70,
        color=TEXT_COLOR,
        bg_color=None,
        size=resolution,
        method="caption",
        text_align="center",
        duration=INTRO_DURATION
    ).with_position("center")
    intro_clip = CompositeVideoClip([intro_bg, txt_clip])
    clips.append(intro_clip)

    # === BLACK START DELAY ===
    if START_DELAY > 0:
        black_start = ColorClip(size=resolution, color=(0, 0, 0), duration=START_DELAY)
        clips.append(black_start)

    # === IMAGE SLIDES ===
    for path in image_paths:
        img_clip = ImageClip(path).with_duration(duration).resized(height=resolution[1]).with_position("center")
        background = ColorClip(size=resolution, color=(0, 0, 0), duration=duration)
        final_clip = CompositeVideoClip([background, img_clip.with_position("center")])
        clips.append(final_clip)

    final_video = concatenate_videoclips(clips, method="compose")

    # === BACKGROUND MUSIC AFTER INTRO ===
    if os.path.isfile(music_path):
        full_audio = AudioFileClip(music_path)

        # Split into first play and looping tail
        first_play = full_audio
        looped_part = full_audio.subclipped(0.4)
        remaining_duration = final_video.duration - INTRO_DURATION - first_play.duration

        if remaining_duration > 0:
            n_loops = int(remaining_duration / looped_part.duration) + 1
            looped_audio = concatenate_audioclips([looped_part] * n_loops).with_duration(remaining_duration)
            combined_audio = concatenate_audioclips([first_play, looped_audio]).with_duration(final_video.duration - INTRO_DURATION)
        else:
            combined_audio = first_play.with_duration(final_video.duration - INTRO_DURATION)

        # Pad beginning with stereo silence for INTRO_DURATION
        fps = combined_audio.fps
        n_samples = int(INTRO_DURATION * fps)
        silent_array = np.zeros((n_samples, 2))  # stereo silence
        silent_intro = AudioArrayClip(silent_array, fps=fps)

        final_audio = concatenate_audioclips([silent_intro, combined_audio])

        # Add audio after full clip is constructed
        final_video = final_video.with_audio(final_audio)

        # Write video before closing audio
        final_video.write_videofile(output_file, fps=30)
        full_audio.close()

    else:
        print(f"⚠️ Music file not found: {music_path}")
        final_video.write_videofile(output_file, fps=30)


# === MAIN ===
if __name__ == "__main__":
    images = load_images(IMAGE_FOLDER)
    if not images:
        print("No images found in the folder.")
    else:
        make_video(images, DURATION, RESOLUTION, OUTPUT_FILE, MUSIC_PATH)

import json
import os
import shutil
from moviepy import *
from datetime import datetime
from moviepy.audio.fx.AudioFadeOut import AudioFadeOut
from moviepy.audio.fx.AudioFadeIn import AudioFadeIn
from moviepy.video.fx.FadeIn import FadeIn
from moviepy.video.fx.FadeOut import FadeOut
from moviepy.video.fx.Loop import Loop

# Configuration Variables
CHANNEL_NAME = "Chill Frame"
CLIP_NAME = "Rick and Morty - I had to become the villain to escape"
CLIP_PACKAGE_DIR = fr"D:\2025\Projects\Presence\Presence0.1\Creator\Channels\{CHANNEL_NAME}\Resources\Clip Packages"
OUTPUT_DIR = fr"D:\2025\Projects\Presence\Presence0.1\Channels\{CHANNEL_NAME}\Clips"
OUTPUT_CLIP_FPS = 30
OUTPUT_CLIP_RESOLUTION = (1920, 1080)
FADE_DURATION = 3  # in seconds

TITLE_STRING = fr"Chill Frame: {CLIP_NAME} | Relaxing, Studying, Sleeping"
DESCRIPTION_STRING = fr"""Enjoy the relaxing vibes of "{CLIP_NAME}" — a soothing mix of visuals and sound for your peace of mind.
If you liked it, don't forget to **like** the video and **subscribe** for more calm and cinematic moments. 🎧✨"""

def write_metadata_json(title, description, output_clip_dir):
    """
    Writes a metadata.json file to output_clip_dir with:
    - title: 'Chill Frame: {clip_name}'
    - description: description
    - creation_timestamp: current ISO timestamp
    """
    metadata = {
        "title": f"{title}",
        "description": description,
        "creation_timestamp": datetime.now().isoformat()
    }

    output_path = os.path.join(output_clip_dir, "metadata.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

    return output_path


# Construct paths
clip_audio_dir = os.path.join(CLIP_PACKAGE_DIR, CLIP_NAME, "Audio")
clip_video_dir = os.path.join(CLIP_PACKAGE_DIR, CLIP_NAME, "Video")
output_clip_dir = os.path.join(OUTPUT_DIR, CLIP_NAME)
os.makedirs(output_clip_dir, exist_ok=True)
output_clip_path = os.path.join(output_clip_dir, f"{CLIP_NAME.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")

# Load and process audio files with fade-in/out
audio_files = sorted([
    os.path.join(clip_audio_dir, f)
    for f in os.listdir(clip_audio_dir)
    if f.lower().endswith(".mp3")
])

audio_clips = []
for audio_file in audio_files:
    audio = AudioFileClip(audio_file)
    faded_in = AudioFadeIn(duration=FADE_DURATION).apply(audio)
    faded_audio = AudioFadeOut(duration=FADE_DURATION).apply(faded_in)
    audio_clips.append(faded_audio)

# Concatenate all audio tracks
final_audio = concatenate_audioclips(audio_clips)

# Load video files and loop them to match the audio duration
video_files = sorted([os.path.join(clip_video_dir, f) for f in os.listdir(clip_video_dir) if f.lower().endswith((".mp4", ".mov", ".mkv"))])
if not video_files:
    print(f"No video files found in {clip_video_dir}")
    raise FileNotFoundError(f"No video files found")

video_clips = []
for video_file in video_files:
    video = VideoFileClip(video_file, target_resolution=OUTPUT_CLIP_RESOLUTION)
    if video.audio is not None:
        video = video.without_audio()
        
    video_clips.append(video)

if not video_clips:
    raise ValueError("No video clips were loaded successfully.")

# Concatenate the video clips
concatenated_clip = concatenate_videoclips(video_clips)

# Apply custom loop effect to match the audio duration
looped_clip: VideoClip = Loop(duration=final_audio.duration).apply(concatenated_clip)

# Apply custom FadeIn and FadeOut effects
faded_video = FadeIn(duration=FADE_DURATION).apply(looped_clip)
faded_video = FadeOut(duration=FADE_DURATION).apply(faded_video)

# Set the frame rate
full_video: VideoClip = faded_video.with_fps(OUTPUT_CLIP_FPS)

# Add the final audio
final_clip: VideoClip = full_video.with_audio(final_audio)

# Export the final video
final_clip.write_videofile(
    output_clip_path,
    codec="libx264",
    audio_codec="aac",
    fps=OUTPUT_CLIP_FPS,
    threads=8,
    preset="ultrafast"
)

write_metadata_json(TITLE_STRING, DESCRIPTION_STRING, output_clip_dir)
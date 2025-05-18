import os
import sys
import json
import random
import time
import argparse
from datetime import datetime

from moviepy import VideoClip, VideoFileClip

def get_center_crop_coords(video_w, video_h, target_w, target_h):
    x1 = int((video_w - target_w) / 2)
    y1 = int((video_h - target_h) / 2)
    return x1, y1, x1 + target_w, y1 + target_h

def get_aspect_crop(video_w, video_h, target_ratio):
    video_ratio = video_w / video_h
    if video_ratio > target_ratio:
        new_w = int(video_h * target_ratio)
        new_h = video_h
    else:
        new_w = video_w
        new_h = int(video_w / target_ratio)
    return get_center_crop_coords(video_w, video_h, new_w, new_h)

def parse_resolution(res_str):
    try:
        w, h = map(int, res_str.lower().split('x'))
        return w, h
    except:
        raise argparse.ArgumentTypeError("Resolution must be in format WIDTHxHEIGHT (e.g. 1080x1920)")

def cut_and_process_video(
    input_path,
    output_dir_name,
    output_name=None,
    title=None,
    description=None,
    duration=60,
    cut_point="random",
    resolution=(1080, 1920),
    fps=30
):
    output_name = output_name or str(int(time.time()))
    base_dir = os.path.dirname(os.path.abspath(input_path))
    full_output_dir = os.path.join(base_dir, output_dir_name, output_name)
    os.makedirs(full_output_dir, exist_ok=True)

    output_path = os.path.join(full_output_dir, output_name + ".mp4")
    json_path = os.path.join(full_output_dir, "metadata.json")

    clip = VideoFileClip(input_path)
    video_duration = clip.duration
    target_w, target_h = resolution

    # Choose start point
    if cut_point == "random":
        max_start = max(0, video_duration - duration)
        start_time = random.uniform(0, max_start)
    else:
        start_time = float(cut_point)
        if start_time + duration > video_duration:
            start_time = max(0, video_duration - duration)

    end_time = start_time + duration

    crop_x1, crop_y1, crop_x2, crop_y2 = get_aspect_crop(clip.w, clip.h, target_w / target_h)

    final_clip = (
        clip.subclipped(start_time, end_time)
            .cropped(x1=crop_x1, y1=crop_y1, x2=crop_x2, y2=crop_y2)
            .resized((target_w, target_h))
            .with_fps(fps)
    )

    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

    metadata = {
        "title": title,
        "description": description,
        "creation_timestamp": datetime.now().isoformat()
    }

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=4)

    clip.reader.close()
    if clip.audio:
        clip.audio.close()

    print(f"\n✅ Video saved to: {output_path}")
    print(f"📄 Metadata saved to: {json_path}")

def main():
    parser = argparse.ArgumentParser(description="Cut and crop a video clip")
    parser.add_argument("--input_video", help="Path to input MP4 video")
    parser.add_argument("--output_dir", help="Subdirectory name (inside input video's parent dir)")
    parser.add_argument("--output_name", default=datetime.now().strftime("%Y%m%d_%H%M%S"), help="Output file name (default: timestamp)")
    parser.add_argument("--title", default=None, help="Output file name (default: timestamp)")
    parser.add_argument("--description", default=None, help="Output file name (default: timestamp)")
    parser.add_argument("--duration", type=int, default=60, help="Duration of the clip in seconds (default: 60)")
    parser.add_argument("--cut_point", default="random", help="Start point in seconds or 'random'")
    parser.add_argument("--resolution", type=parse_resolution, default=(1080, 1920), help="Output resolution (e.g. 1080x1920)")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second (default: 30)")

    args = parser.parse_args()

    cut_and_process_video(
        input_path=args.input_video,
        output_dir_name=args.output_dir,
        output_name=args.output_name,
        title=args.title,
        description=args.description,
        duration=args.duration,
        cut_point=args.cut_point,
        resolution=args.resolution,
        fps=args.fps
    )

if __name__ == "__main__":
    main()

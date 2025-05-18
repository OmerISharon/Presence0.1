#!/usr/bin/env python3
"""
split_audio.py

Splits an input MP3 into fixed-duration segments, discarding any final remainder shorter than the specified duration.

Usage:
    python split_audio.py --input_file input.mp3 --output_dir segments/ --segment_duration 10
"""

import argparse
import os
from pydub import AudioSegment

def split_audio(input_file: str, output_dir: str, segment_duration: float):
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Load audio
    audio = AudioSegment.from_mp3(input_file)
    total_duration_ms = len(audio)
    segment_duration_ms = int(segment_duration * 1000)

    # Compute number of full segments
    num_segments = total_duration_ms // segment_duration_ms
    if num_segments == 0:
        print(f"Audio is shorter than segment duration ({segment_duration}s). No segments created.")
        return

    for i in range(num_segments):
        start_ms = i * segment_duration_ms
        end_ms = start_ms + segment_duration_ms
        segment = audio[start_ms:end_ms]
        output_path = os.path.join(output_dir, f"segment_{i+1:03d}_{int(start_ms/1000)}s_to_{int(end_ms/1000)}s.mp3")
        print(f"Writing segment {i+1}/{num_segments}: {output_path}")
        segment.export(output_path, format="mp3")

    print(f"Finished splitting into {num_segments} segments.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split an MP3 into fixed-duration segments, discarding any final partial segment."
    )
    parser.add_argument("--input_file", required=True, help="Path to the input MP3 file")
    parser.add_argument("--output_dir", required=True, help="Directory to write segment MP3 files")
    parser.add_argument("--segment_duration", type=float, required=True, help="Duration (in seconds) for each output segment")

    args = parser.parse_args()
    split_audio(args.input_file, args.output_dir, args.segment_duration)

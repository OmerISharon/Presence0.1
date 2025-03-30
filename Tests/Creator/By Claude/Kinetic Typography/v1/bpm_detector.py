#!/usr/bin/env python3
import argparse
import librosa
import json
import sys
import os

def detect_beats(audio_path):
    """
    Load the audio file, detect BPM and beat times using librosa, and return them
    as native Python types.
    """
    try:
        # Load audio file; sr=None preserves the native sampling rate
        y, sr = librosa.load(audio_path, sr=None)
        # Estimate the tempo and beat frames
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        # Convert beat frames to time (in seconds)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)
        # Ensure that BPM is a native Python float and beat_times is a list
        return float(tempo), beat_times.tolist()
    except Exception as e:
        print(f"Error processing audio file: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description="Detect BPM and beat times from an audio file using librosa."
    )
    parser.add_argument("audio_file", help="Path to the audio file")
    args = parser.parse_args()

    # Check if the specified file exists
    if not os.path.isfile(args.audio_file):
        print(f"Error: File '{args.audio_file}' does not exist.", file=sys.stderr)
        sys.exit(1)

    bpm, beat_times = detect_beats(args.audio_file)
    output = {"bpm": bpm, "beat_times": beat_times}
    
    # Print the result as a formatted JSON string
    print(json.dumps(output, indent=2))

if __name__ == '__main__':
    main()

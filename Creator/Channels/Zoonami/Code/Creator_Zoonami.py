import os
import random
import subprocess
import datetime
from metadata_items_list import ANIMAL_VIDEO_TITLES, ANIMAL_VIDEO_DESCRIPTIONS
import random

INPUT_VIDEO_DIR   = fr"D:\2025\Projects\Presence\Presence0.1\Creator\Channels\Zoonami\Resources\Videos"
CLIPS_ROOT_DIR    = fr"D:\2025\Projects\Presence\Presence0.1\Channels\Zoonami\Clips"
VIDEO_CUTTER_PATH = fr"D:\2025\Projects\Presence\Presence0.1\Resources\Internal_Modules\creators\video_cutter\video_cutter_v1\video_cutter_v1.py"


def pick_random_mp4(directory: str) -> str | None:
    if not os.path.isdir(directory):
        print(f"❌  Not a valid directory: {directory}")
        return None
    mp4s = [f for f in os.listdir(directory) if f.lower().endswith(".mp4")]
    if not mp4s:
        print("⚠️  No MP4 files found.")
        return None
    return os.path.join(directory, random.choice(mp4s))


if __name__ == "__main__":
    # 1️⃣  Select a random source video
    src_video = pick_random_mp4(INPUT_VIDEO_DIR)
    if not src_video:
        raise SystemExit(1)

    # 2️⃣  Generate a timestamp for metadata
    timestamp    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir   = os.path.join(CLIPS_ROOT_DIR)   # only used for folder
    output_name  = timestamp  # fixed output filename

    os.makedirs(output_dir, exist_ok=True)

    title = random.choice(ANIMAL_VIDEO_TITLES)
    description = random.choice(ANIMAL_VIDEO_DESCRIPTIONS)

    # 3️⃣  Run cutter
    cutter_args = [
        "python", VIDEO_CUTTER_PATH,
        "--input_video",   src_video,
        "--output_dir",    output_dir,
        "--output_name",   output_name,
        "--title",         title,
        "--description",   description,
        "--duration",      "58",
    ]

    print("🎬 Running video_cutter_v1.py …")
    subprocess.run(cutter_args, check=True)

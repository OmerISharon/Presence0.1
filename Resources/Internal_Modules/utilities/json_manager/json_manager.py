

from datetime import datetime
import json
import os


def create_json(text, description, output_dir):
    creation_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    metadata = {
        "title": text,
        "description": description,
        "creation_timestamp": creation_timestamp,
    }
    with open(output_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)


    # # --- 9. Save metadata as JSON ---
    # json_title = segments[0]['text'] if segments else ""
    # json_description = " ".join([s['text'] for s in segments])
    # json_output_dir = Path(output_path).parent
    # create_json(json_title, json_description, json_output_dir)
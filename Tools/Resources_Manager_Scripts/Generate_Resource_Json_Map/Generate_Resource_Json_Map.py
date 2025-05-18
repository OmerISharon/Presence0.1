import json
from pathlib import Path

def create_overall_json(root_dir, output_file):
    # Define allowed media extensions and separate sets for videos and images
    allowed_media_ext = {".jpg", ".jpeg", ".png", ".mp4", ".mov", ".avi"}
    video_exts = {".mp4", ".mov", ".avi"}
    image_exts = {".jpg", ".jpeg", ".png"}
    
    overall = {}
    # Recursively find all JSON files
    for json_file in Path(root_dir).rglob("*.json"):
        parent_folder = json_file.parent
        
        # Read the content of the JSON file to include its properties.
        try:
            with open(json_file, "r", encoding="utf-8") as jf:
                json_properties = json.load(jf)
        except Exception as e:
            json_properties = {}
        
        # Search for a media file in the parent folder (ignore the JSON file itself)
        media_files = [
            f for f in parent_folder.iterdir() 
            if f.is_file() and f.suffix.lower() in allowed_media_ext and f.name != json_file.name
        ]
        if not media_files:
            continue
        
        # Try to select the media file that matches the folder name (common in our structure)
        media_file = None
        for f in media_files:
            if f.stem == parent_folder.name:
                media_file = f
                break
        if media_file is None:
            media_file = media_files[0]  # if no match, pick the first one

        ext = media_file.suffix.lower()
        if ext in video_exts:
            media_kind = "video"
        elif ext in image_exts:
            media_kind = "image"
        else:
            media_kind = "unknown"

        # Build the overall mapping for this JSON file
        overall[parent_folder.name] = {
            "dir": str(parent_folder.resolve()),
            "json_path": str(json_file.resolve()),
            "media_path": str(media_file.resolve()),
            "media_kind": media_kind,
            "media_extension": ext,
            "json_properties": json_properties  # The content of the JSON file
        }
    
    # Write the overall mapping to a JSON file
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(overall, f, indent=4)

if __name__ == "__main__":
    # Change these paths as needed
    root_directory = r"D:\\2025\\Projects\\Presence\\Presence0.1\\Resources\\Media_Resources"
    output_json = r"D:\\2025\\Projects\\Presence\\Presence0.1\\Resources\\Media_Resources\\overall_metadata.json"
    create_overall_json(root_directory, output_json)

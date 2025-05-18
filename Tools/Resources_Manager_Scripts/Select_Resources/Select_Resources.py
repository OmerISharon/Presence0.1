import argparse
import json
from pathlib import Path
import math

# Overall metadata JSON file path
OVERALL_JSON_PATH = r"D:\\2025\\Projects\\Presence\\Presence0.1\\Resources\\Media_Resources\\overall_metadata.json"

def hex_to_rgb(hex_str):
    """Convert a hex color (e.g. '#aabbcc') to an (R,G,B) tuple."""
    hex_str = hex_str.lstrip("#")
    if len(hex_str) != 6:
        return (0, 0, 0)
    return tuple(int(hex_str[i:i+2], 16) for i in (0, 2, 4))

def color_distance(c1, c2):
    """Euclidean distance between two RGB colors."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

def parse_resolution(res_str):
    """Parse a resolution string formatted as 'widthxheight' and return (width, height)."""
    try:
        parts = res_str.lower().split("x")
        if len(parts) != 2:
            return None, None
        width = int(parts[0].strip())
        height = int(parts[1].strip())
        return width, height
    except Exception:
        return None, None

def load_overall_metadata():
    with open(OVERALL_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def filter_entries(entries, args):
    # Prepare filters (all lower-case for case-insensitive matching)
    # Media type filter: if not 'both', it must match exactly.
    media_type_filter = args.media_type.lower() if args.media_type else "both"
    
    # Subjects list is required.
    subjects_filter = {s.strip().lower() for s in args.subjects.split(",") if s.strip()}
    
    # Tags to include (if provided)
    include_tags = {t.strip().lower() for t in args.tags.split(",")} if args.tags else set()
    # Tags to ignore (if provided)
    ignore_tags = {t.strip().lower() for t in args.ignore_tags.split(",")} if args.ignore_tags else set()
    
    # Orientation filter: vertical (default) or horizontal.
    orientation_filter = args.orientation.lower() if args.orientation else "vertical"
    
    # Color mode filter: if provided ("dark" or "light"), else both.
    color_mode_filter = args.color_mode.lower() if args.color_mode else None
    
    # Main color filter: if provided, convert to RGB.
    main_color_filter = hex_to_rgb(args.main_color) if args.main_color else None
    main_color_threshold = 60  # Adjust threshold for "close enough"
    
    filtered = []
    
    for key, data in entries.items():
        # data structure:
        # { "dir": ..., "json_path": ..., "media_path": ..., "media_kind": ..., "media_extension": ...,
        #   "json_properties": { "subject": ..., "tags": ..., "resolution": ..., "color_mode": ..., "main color": ... , ... } }
        json_props = data.get("json_properties", {})
        
        # Check subject: we assume json_props contains "subject"
        subject = json_props.get("subject", "").lower()
        if subject not in subjects_filter:
            continue
        
        # Check media type if filter is not 'both'
        media_kind = data.get("media_kind", "").lower()
        if media_type_filter != "both" and media_kind != media_type_filter:
            continue
        
        # Check tags:
        # Assume json_props["tags"] is a string of comma-separated tags.
        tags_str = json_props.get("tags", "")
        tags_set = {tag.strip().lower() for tag in tags_str.split(",") if tag.strip()}
        
        # If include tags provided, at least one must be in tags_set.
        if include_tags and not (include_tags & tags_set):
            continue
        
        # If any tag from ignore list is present, skip.
        if ignore_tags and (ignore_tags & tags_set):
            continue
        
        # Check orientation via resolution.
        resolution = json_props.get("resolution", "")
        width, height = parse_resolution(resolution)
        if width is None or height is None:
            continue
        if orientation_filter == "vertical":
            if height <= width:
                continue
        elif orientation_filter == "horizontal":
            if width <= height:
                continue
        
        # Check color_mode if provided.
        if color_mode_filter:
            json_color_mode = json_props.get("color_mode", "").lower()
            if json_color_mode != color_mode_filter:
                continue
        
        # Check main_color if provided: using "close enough" criteria on RGB.
        if main_color_filter:
            json_main_color_hex = json_props.get("main color", "")
            if not json_main_color_hex:
                continue
            json_main_color = hex_to_rgb(json_main_color_hex)
            if color_distance(main_color_filter, json_main_color) > main_color_threshold:
                continue
        
        # Passed all filters.
        filtered.append(data)
        
        # If we already reached the required amount, break.
        if len(filtered) >= args.amount:
            break

    return filtered

def main():
    parser = argparse.ArgumentParser(
        description="Filter overall metadata JSON based on provided criteria and return media paths."
    )
    parser.add_argument("amount", type=int, help="Amount of returned items (required).")
    parser.add_argument("--media_type", type=str, default="both", 
                        help="Media type: 'image' or 'video' (optional, default both).")
    parser.add_argument("--subjects", type=str, required=True,
                        help="Comma-separated list of subjects (required).")
    parser.add_argument("--tags", type=str, default="",
                        help="Comma-separated list of tags (optional, default none).")
    parser.add_argument("--ignore_tags", type=str, default="",
                        help="Comma-separated list of tags to ignore (optional, default none).")
    parser.add_argument("--orientation", type=str, default="vertical",
                        help="Orientation: 'vertical' or 'horizontal' (optional, default vertical).")
    parser.add_argument("--color_mode", type=str, default="",
                        help="Color mode: 'dark' or 'light' (optional, default both).")
    parser.add_argument("--main_color", type=str, default="",
                        help="Main color as hex (e.g., '#aabbcc') (optional, default none).")
    
    args = parser.parse_args()
    
    # Load overall metadata JSON.
    overall = load_overall_metadata()
    
    # Filter entries based on criteria.
    filtered_entries = filter_entries(overall, args)
    
    # Extract media_path from each filtered entry.
    media_paths = [entry.get("media_path") for entry in filtered_entries if entry.get("media_path")]
    
    # Limit to the requested amount (if not already limited in filter_entries).
    media_paths = media_paths[:args.amount]
    
    # Build output string: each path in quotes, separated by comma and space.
    output_str = ", ".join(f'"{path}"' for path in media_paths)
    print(output_str)

if __name__ == "__main__":
    main()

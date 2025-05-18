import argparse
import random
from pathlib import Path

def main(output_files_num, theme):
    base_dir = Path(r"D:\\2025\\Projects\\Presence\\Presence0.1\\Resources\\Media_Resources\\Video\\1080x1920")
    theme_folder = base_dir / theme
    if not theme_folder.exists():
        print(f"Theme folder '{theme}' not found in {base_dir}.")
        return ""
    
    # List only folders within the theme folder.
    subdirs = [d for d in theme_folder.iterdir() if d.is_dir()]
    
    # If fewer folders exist than requested, use all; otherwise, select randomly.
    selected = subdirs if len(subdirs) <= output_files_num else random.sample(subdirs, output_files_num)
    
    result_paths = []
    for folder in selected:
        # Assume each folder contains at least one mp4 file and choose the first found.
        mp4_files = list(folder.glob("*.mp4"))
        if mp4_files:
            result_paths.append(str(mp4_files[0].resolve()))
    
    # Create a comma-separated string of the full paths.
    result = ", ".join(f'"{p}"' for p in result_paths)
    print(result)
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Select output mp4 files from theme folders")
    parser.add_argument('--output_files_num', type=int, required=True,
                        help="Number of folders (output files) to choose")
    parser.add_argument('--theme', type=str, required=True,
                        help="Theme folder name (e.g. 'Nature')")
    args = parser.parse_args()
    main(args.output_files_num, args.theme)
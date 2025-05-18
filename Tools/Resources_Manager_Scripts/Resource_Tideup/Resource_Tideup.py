import sys
import types

# Create a dummy roc_curve function if sklearn.metrics is imported later.
dummy_module = types.ModuleType("sklearn.metrics")
dummy_module.roc_curve = lambda *args, **kwargs: None
sys.modules["sklearn.metrics"] = dummy_module


import json
from pathlib import Path
import shutil
import cv2
import numpy as np
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch

# Static stop words list
STATIC_STOP_WORDS = [
    "a", "an", "the", "in", "on", "with", "is", "are", "of", "to", "and", "for", "from", "at", "by", "this", "that"
]

# Load BLIP image captioning model
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def get_dominant_color(image, k=4):
    image_resized = cv2.resize(image, (100, 100), interpolation=cv2.INTER_AREA)
    pixels = image_resized.reshape((-1, 3)).astype(np.float32)
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
    _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    counts = np.bincount(labels.flatten())
    dominant = centers[np.argmax(counts)]
    r, g, b = int(dominant[2]), int(dominant[1]), int(dominant[0])
    return (r, g, b), f"#{r:02x}{g:02x}{b:02x}"

def detect_color_mode(rgb_tuple):
    r, g, b = rgb_tuple
    brightness = (0.299 * r + 0.587 * g + 0.114 * b)
    return "light" if brightness > 127 else "dark"

def describe_image_from_array(image_array):
    pil_image = Image.fromarray(image_array)
    inputs = processor(pil_image, return_tensors="pt")
    out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)

def describe_image(path):
    image = Image.open(path).convert("RGB")
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)

def tokenize_and_filter(caption):
    tokens = caption.lower().replace(".", "").split()
    return [word for word in tokens if word not in STATIC_STOP_WORDS]

def process_media(directory):
    base_dir = Path(directory)
    subject_dir_name = base_dir.name

    image_exts = [".jpg", ".jpeg", ".png"]
    video_exts = [".mp4", ".mov", ".avi"]

    for media_file in base_dir.glob("*"):
        if media_file.suffix.lower() not in image_exts + video_exts:
            continue

        folder_name = media_file.stem
        target_folder = base_dir / folder_name
        target_folder.mkdir(exist_ok=True)

        target_path = target_folder / media_file.name
        shutil.move(str(media_file), str(target_path))
        print(f"Moved {media_file.name} to folder: {folder_name}")

        metadata = {
            "subject": subject_dir_name,
            "tags": "",
            "caption": "",
            "color_mode": "",
            "main color": "",
            "resolution": ""
        }

        if media_file.suffix.lower() in video_exts:
            cap = cv2.VideoCapture(str(target_path))
            width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, first_frame = cap.read()
            if ret:
                rgb, hex_color = get_dominant_color(first_frame)
                color_mode = detect_color_mode(rgb)
            else:
                hex_color = ""
                color_mode = ""

            frame_indices = [0]
            if total_frames > 1:
                frame_indices.append(total_frames // 2)
                frame_indices.append(total_frames - 1)
            else:
                frame_indices.extend([0, 0])

            all_tokens = []
            all_captions = []

            for idx in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
                ret, frame = cap.read()
                if ret:
                    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    caption = describe_image_from_array(rgb_frame)
                    all_captions.append(caption)
                    tokens = tokenize_and_filter(caption)
                    all_tokens.extend(tokens)

            cap.release()
            unique_tags = list(dict.fromkeys(all_tokens))
            merged_caption = " | ".join(dict.fromkeys(all_captions))

            metadata["resolution"] = f"{int(width)}x{int(height)}"
            metadata["main color"] = hex_color
            metadata["color_mode"] = color_mode
            metadata["tags"] = ", ".join(unique_tags)
            metadata["caption"] = merged_caption

        elif media_file.suffix.lower() in image_exts:
            image = cv2.imread(str(target_path))
            height, width, _ = image.shape
            rgb, hex_color = get_dominant_color(image)
            color_mode = detect_color_mode(rgb)
            caption = describe_image(str(target_path))
            filtered_tokens = tokenize_and_filter(caption)

            metadata["resolution"] = f"{width}x{height}"
            metadata["main color"] = hex_color
            metadata["color_mode"] = color_mode
            metadata["tags"] = ", ".join(filtered_tokens)
            metadata["caption"] = caption

        metadata_file = target_folder / "metadata.json"
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=4)
        print(f"Created metadata file in folder: {folder_name}")

if __name__ == "__main__":
    # Specify the directory with your media files (both images and videos)
    target_directory = fr"C:\downloads"
    process_media(target_directory)

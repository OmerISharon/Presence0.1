import os
import json

BASE_DIR = r"D:\\2025\\Projects\\Presence\\Presence0.1\\Channels"

all_credentials = {}

for entry in os.listdir(BASE_DIR):
    full_path = os.path.join(BASE_DIR, entry)
    if os.path.isdir(full_path) and not entry.endswith("(not in use)"):
        metadata_path = os.path.join(full_path, "MetaData", "credentials.json")
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    credentials = json.load(f)
                    all_credentials[entry] = credentials
            except Exception as e:
                print(f"Error reading {metadata_path}: {e}")

# Output all JSON contents as a string
result = json.dumps(all_credentials, indent=4, ensure_ascii=False)
print(result)

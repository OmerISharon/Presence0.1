"""
╔═══════════════════════════════════════════════════════════════════════════════╗
║     ChatGPT Media Prompt Module                                               ║
║     Send dynamic requests to ChatGPT and parse structured output.             ║
║                                                                               ║
║ Arguments:                                                                    ║
║ ──────────────────────────────────────────────────────────────────            ║
║ system_prompt     (str)   : ChatGPT's persona/context.                        ║
║ user_prompt       (str)   : The actual request from the user.                 ║
║ vibe_needed       (bool)  : Whether to extract "vibe" (default: True).        ║
║ subject_needed    (bool)  : Whether to extract "subject" (default: True).     ║
║ tags_needed       (bool)  : Whether to extract "tags" (default: True).        ║
║ model             (str)   : ChatGPT model to use (default: gpt-4-turbo).      ║
║ max_tokens        (int)   : Max tokens to generate (default: 100).            ║
║                                                                               ║
║ Returns:                                                                      ║
║ (text, vibe, subject, tags) - All as strings or None if disabled.             ║
╚═══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import requests
import json
import random
import os

# Load credentials
CREDENTIALS_DIR = "D:\\2025\\Projects\\Presence\\Presence0.1\\Resources\\Credentials"
sys.path.insert(0, CREDENTIALS_DIR)
from credential_keys import OPENAI_API_KEY

def get_api_key():
    return OPENAI_API_KEY

def request_chatgpt_response(
    system_prompt: str,
    user_prompt: str,
    vibe_needed: bool = True,
    subject_needed: bool = True,
    tags_needed: bool = True,
    model: str = "gpt-4.1",
    max_tokens: int = 100,
    prompts_history: str = None
):
    # Load recent descriptions if prompts_history dir is provided
    recent_descriptions = []
    if prompts_history and os.path.isdir(prompts_history):
        subdirs = sorted(
            [os.path.join(prompts_history, d) for d in os.listdir(prompts_history)
            if os.path.isdir(os.path.join(prompts_history, d))],
            key=os.path.getmtime,
            reverse=True
        )[:3]

        for subdir in subdirs:
            metadata_path = os.path.join(subdir, "metadata.json")
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        metadata = json.load(f)
                        if "description" in metadata:
                            recent_descriptions.append(metadata["description"])
                except Exception as e:
                    print(f"Error reading metadata.json in {subdir}: {e}")

    # Append recent descriptions to user prompt to avoid repetition
    if recent_descriptions:
        user_prompt += "\n\nAvoid repeating the ideas in the following recent clips:\n"
        for i, desc in enumerate(recent_descriptions, 1):
            user_prompt += f"{i}. {desc}\n"


    # Construct full prompt with expected format
    full_user_prompt = f"""
{user_prompt}

Respond using this exact format:

Text: <the clip-worthy text here>
{ "Vibe: <the overall vibe in 1–2 words>" if vibe_needed else "" }
{ "Subject: <search-friendly subject>" if subject_needed else "" }
{ "Tags: <comma-separated, search-optimized keywords that are directly and semantically related to the Subject. Make them listed in the same order they are mentioned, based on how the story unfolds. Only include visual or conceptual topics that someone might search for to find this type of story. Use high-level, relevant tags that help categorize the content within its subject domain.>" if tags_needed else "" }
"""
# { "Tags: <comma-separated, search-friendly and very common visual keywords that appear in the text - listed in the same order they are mentioned, based on how the story unfolds>" if tags_needed else "" }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": full_user_prompt}
        ],
        "temperature": random.uniform(0.7, 1.0),
        "max_tokens": max_tokens
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )
        response.raise_for_status()
        content = response.json()['choices'][0]['message']['content']
        return parse_response(content, vibe_needed, subject_needed, tags_needed)

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None, None, None, None

def parse_response(response_text, vibe_needed, subject_needed, tags_needed):
    text, vibe, subject, tags = "", "", "", ""
    current_label = None

    for line in response_text.splitlines():
        line = line.strip()

        if line.lower().startswith("text:"):
            current_label = 'text'
            text = line[5:].strip()
        elif vibe_needed and line.lower().startswith("vibe:"):
            current_label = 'vibe'
            vibe = line[5:].strip()
        elif subject_needed and line.lower().startswith("subject:"):
            current_label = 'subject'
            subject = line[8:].strip()
        elif tags_needed and line.lower().startswith("tags:"):
            current_label = 'tags'
            tags = line[5:].strip()
        else:
            if current_label == 'text':
                text += ' ' + line
            elif current_label == 'vibe':
                vibe += ' ' + line
            elif current_label == 'subject':
                subject += ' ' + line
            elif current_label == 'tags':
                tags += ' ' + line

    return text.strip(), vibe.strip(), subject.strip(), tags.strip()


# ─────────────────────────────────────────────
# Optional demo block (can be removed in prod)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    demo_subject = "Urban Dreams"
    system_prompt = (
        "You are a creative assistant specialized in generating short, engaging, and "
        "inspiring texts perfectly suited for media clips on social platforms like TikTok, "
        "Instagram Reels, or YouTube Shorts. Your texts should be original, visually evocative, "
        "and inspire strong emotional connections."
    )
    user_prompt = f"Write a creative short video quote about: {demo_subject}"

    text, vibe, subject, tags = request_chatgpt_response(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        vibe_needed=True,
        subject_needed=True,
        tags_needed=True,
        max_tokens=200
    )

    print("\n─── ChatGPT Response ───\n")
    print(f"Text:\n{text}\n")
    print(f"Vibe:\n{vibe}\n")
    print(f"Subject:\n{subject}\n")
    print(f"Tags:\n{tags}\n")

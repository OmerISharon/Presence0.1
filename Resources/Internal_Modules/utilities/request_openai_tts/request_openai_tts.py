"""
Title: Text-to-Speech (TTS) MP3 Generator using OpenAI (Python SDK - Async)

Description:
This script takes a block of text and generates an MP3 audio file using OpenAI's Text-to-Speech (TTS) API via the official `openai` Python SDK (async client).
It supports advanced voice options, model selection, speed adjustment, and voice styling via `instructions`.

Supported Models:
-----------------
1. **gpt-4o-mini-tts**  (Latest, Fastest, Most Expressive)
   - Best-in-class fidelity and realism
   - Supports `instructions` for nuanced voice control
   - Optimized for live playback and high expressiveness

2. **tts-1**            (Legacy Standard Quality)
   - High-quality but does not support `instructions`
   - Best for simple voiceover generation

3. **tts-1-hd**         (Legacy High Definition)
   - Enhanced voice clarity and emotion
   - Does not support `instructions`
   - Slower but more polished audio

Supported Voices:
-----------------
- **alloy**   – Crisp, confident, and clear (default legacy voice)
- **ash**     – Warm, smooth, balanced (optimized for `gpt-4o`)
- **ballad**  – Gentle and storytelling-like
- **coral**   – Light, charming, and animated
- **echo**    – Calm, soft, meditative
- **fable**   – Expressive, dynamic, great for characters
- **nova**    – Energetic, youthful, casual
- **onyx**    – Deep, rich, cinematic
- **sage**    – Calm and trustworthy, teacher-like
- **shimmer** – Airy, mystical, inspirational
- **verse**   – Poetic, thoughtful, musical

Note: Some voices are designed specifically for certain use cases like drama, narration, or podcasts. All voices are compatible with `gpt-4o-mini-tts`; some may be unavailable in legacy models.

Feature Support Matrix:
------------------------
| Feature           | tts-1 | tts-1-hd | gpt-4o-mini-tts |
|-------------------|-------|----------|-----------------|
| `instructions`    | ❌    | ❌       | ✅              |
| Voice variety     | ✅    | ✅       | ✅              |
| Streaming         | ✅    | ✅       | ✅              |
| Speed control     | ✅    | ✅       | ✅              |
| Max length        | 4096 chars | 4096 chars | 4096 chars |

Pricing (as of April 2025):
----------------------------
- **gpt-4o-mini-tts**: ~$0.015 per 1,000 characters
- **tts-1**:           ~$0.015 per 1,000 characters
- **tts-1-hd**:        ~$0.030 per 1,000 characters

Pricing may vary. Always confirm with: https://platform.openai.com/pricing

Request Parameters (POST /v1/audio/speech):
-------------------------------------------
- **input** (str): The text to synthesize (max 4096 characters).
- **model** (str): One of `tts-1`, `tts-1-hd`, or `gpt-4o-mini-tts`.
- **voice** (str): One of the supported voices listed above.
- **instructions** (str): [gpt-4o only] Optional style guide for tone, pacing, affect.
- **response_format** (str): One of `mp3`, `aac`, `opus`, `flac`, `pcm`, or `wav`. Default: `mp3`.
- **speed** (float): Multiplier for playback speed (range: 0.25 to 4.0, default is 1.0).

Usage Example:
--------------
$ python tts_generator.py \\
    --text "In the shadow of the mountain, silence grew heavy..." \\
    --output suspense.mp3 \\
    --model gpt-4o-mini-tts \\
    --voice ash \\
    --speed 1.0 \\
    --instructions "Read this in a slow, hushed tone with suspense and intrigue."

Author: Omer Sharon
Date: 2025-04-10
"""

import sys
import argparse
import openai
import random

# Load API key securely
CREDENTIALS_DIR = "D:\\2025\\Projects\\Presence\\Presence0.1\\Resources\\Credentials"
sys.path.insert(0, CREDENTIALS_DIR)
from credential_keys import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

available_models = ["tts-1", "tts-1-hd", "gpt-4o-mini-tts"]
available_voices = [
    "nova",     # Energetic and friendly
    "echo",     # Soft and gentle
    "fable",    # Animated and expressive
    "onyx",     # Deep and serious
    "shimmer",  # Airy and inspiring
    "alloy",    # Crisp and confident
    "ash",      # Warm and smooth (gpt-4o only)
    "ballad",   # Gentle, storytelling tone
    "coral",    # Light, charming, and animated
    "sage",     # Calm and wise
    "verse",    # Poetic, musical
]


def generate_speech(text, model="gpt-4o-mini-tts", voice=None, output_file="output.mp3", speed="1.0", instructions=None):
    try:
        selected_voice = voice or random.choice(available_voices)

        tts_input_text = text

        kwargs = {
            "model": model,
            "voice": selected_voice,
            "input": tts_input_text,
            "speed": float(speed),
            "response_format": "mp3"
        }

        # Only include instructions if provided and model supports it
        if model == "gpt-4o-mini-tts" and instructions:
            kwargs["instructions"] = instructions

        response = openai.audio.speech.create(**kwargs)

        audio_bytes = response.content
        del response

        with open(output_file, "wb") as f:
            f.write(audio_bytes)

        print(f"\n✅ Audio saved to '{output_file}' using model '{model}', voice '{selected_voice}' and speed {speed}")

    except Exception as e:
        print(f"\n❌ Error generating speech: {e}")


def main():
    parser = argparse.ArgumentParser(description="Generate speech using OpenAI TTS API.")
    parser.add_argument('--text', type=str, required=True, help="The input text to synthesize.")
    parser.add_argument('--model', type=str, default="gpt-4o-mini-tts", choices=available_models, help="Model to use for synthesis.")
    parser.add_argument('--output', type=str, default="output.mp3", help="Output file name (e.g. output.mp3)")
    parser.add_argument('--speed', type=str, default="1.0", help="Voice speed multiplier (e.g. 1.0 = normal, 0.8 = slower, 1.2 = faster)")
    parser.add_argument('--voice', type=str, default=None, choices=available_voices, help="Voice selection. If not specified, a random voice will be used.")
    parser.add_argument('--instructions', type=str, default=None, help="The instructions of the voice.")

    args = parser.parse_args()

    generate_speech(
        text=args.text,
        model=args.model,
        voice=args.voice,
        output_file=args.output,
        speed=args.speed,
        instructions=args.instructions
    )

if __name__ == "__main__":
    main()

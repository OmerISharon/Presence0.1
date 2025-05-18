"""
agent_content_creator.py
------------------------
• One agent  (Image_Generator_Agent)
• One tool   (create_image)
• Tool downloads 1 photo from Pexels, then calls Picasso *once*
• Prints debug info; on any error, prints and returns the error string (no retry)
"""

import argparse
import os
import sys
import asyncio
from typing import List

# ------------------------------------------------------------------
# Local module path
# ------------------------------------------------------------------
MODULES_DIR = fr"D:\2025\Projects\Presence\Presence0.1\Resources\Internal_Modules"
sys.path.insert(0, MODULES_DIR)
from assistants.assistants_manager.openai_assistant_runner import OpenAIAssistantRunner

# ------------------------------------------------------------------
# Internal helpers
# ------------------------------------------------------------------
from utilities.get_pexels_media.get_pexels_media import run_pexels_download, download_pexels_url_to_local
from utilities.vector_manager.vector_manager import find_best_image_for_text
from creators.picasso.picasso_v1.picasso_v1 import generate_image as picasso_generate_image

PEXELS_OUTPUT_DIR = fr"D:\2025\Projects\Presence\Presence0.1\Resources\Internal_Modules\utilities\get_pexels_media\test_output"

# ------------------------------------------------------------------
# helpers Functions
# ------------------------------------------------------------------

def _hex_to_rgba(s: str | None) -> str | None:
    if not s or not s.startswith("#"):
        return s                      # already rgba or empty
    hex_part = s.lstrip("#")
    if len(hex_part) == 6:            # RRGGBB
        r, g, b = int(hex_part[0:2], 16), int(hex_part[2:4], 16), int(hex_part[4:6], 16)
        a = 255
    elif len(hex_part) == 8:          # RRGGBBAA
        r, g, b = int(hex_part[0:2], 16), int(hex_part[2:4], 16), int(hex_part[4:6], 16)
        a = int(hex_part[6:8], 16)
    else:
        return s  # malformed; leave unchanged
    return f"{r},{g},{b},{a}"

def _get_image_from_pexels(subject: str, ideal_image_description):
    try:
        paths: List[str] = run_pexels_download(
            subject=subject,
            media_count=20,
            output_dir=PEXELS_OUTPUT_DIR,
            media_type="image",
            orientation="portrait",
            select_url=True
        )
        if not paths:
            err = f"No photo found for '{subject}'."
            print("[ERROR]", err)
            return f"[ERROR] {err}"

        # 👇 Use your embedding logic to find best match
        best_image = find_best_image_for_text(ideal_image_description, paths)
        print(f"✅ Best matching background image: {best_image}")
        best_image_local = download_pexels_url_to_local(best_image, default_output_dir)
        print(f"✅ Best matching background image downloaded successfully to : {best_image_local}")

        return best_image_local

    except Exception as e:
        err = f"Pexels download failed: {e}"
        print("[ERROR]", err)
        return f"[ERROR] {err}"

# ------------------------------------------------------------------
# The single tool
# ------------------------------------------------------------------
# @function_tool
def create_image(
    subject: str,
    text: str,
    ideal_image_description: str,
    image_orientation: str | None = None,
    fore_color: str | None = None,
    font_size: str | None = None,
    text_alpha: int | None = None,
    text_h_align: str | None = None,
    text_v_align: str | None = None,
    font_effect: str | None = None,
    font_stroke_effect_color: str | None = None,
    font_shadow_effect_color: str | None = None,
    font_marker_effect_color: str | None = None,
    font_fade_effect_color: str | None = None,
    font_fade_effect_strength: float | None = None,
    border_effect: str | None = None,
    border_effect_color: str | None = None,
    border_width: int | None = None,
    image_overlay_effect: str | None = None,
    image_overlay_effect_tint_color: str | None = None,
    blur_amount: int | None = None,
) -> str:
    """
    Download one HD photo for *subject* and render a poster with Picasso.

    Required:
      • subject       – background photo search term
      • text          – overlay text
      • output_path   – file to save (e.g. poster.jpg)

    All other args are optional style tweaks.
    """

    print("\n================= create_image() called =================")
    print(f"subject: {subject}")
    print(f"text: {text}")
    print(f"ideal_image_description: {ideal_image_description}")
    print(f"output_path: {globals().get('output_path')}")
    print("=========================================================\n")

    # -------- defaults moved into body --------
    bg_color = "255,255,255,255"
    font_path = fr"C:\Windows\Fonts\ariblk.ttf"

    image_orientation = image_orientation or "vertical"
    fore_color = fore_color or "0,0,0"
    font_size = font_size or "medium"
    text_alpha = 255 if text_alpha is None else text_alpha
    text_h_align = text_h_align or "center"
    text_v_align = text_v_align or "center"
    font_effect = font_effect or ""
    font_stroke_effect_color = font_stroke_effect_color or "255,255,255,128"
    font_shadow_effect_color = font_shadow_effect_color or "255,255,255,128"
    font_marker_effect_color = font_marker_effect_color or "255,255,255,128"
    font_fade_effect_color = font_fade_effect_color or "255,255,255,128"
    font_fade_effect_strength = font_fade_effect_strength or 0.2
    border_effect = border_effect or ""
    border_effect_color = border_effect_color or "255,255,255,128"
    border_width = border_width or 40
    image_overlay_effect = image_overlay_effect or ""
    image_overlay_effect_tint_color = (
        image_overlay_effect_tint_color or "255,255,255,50"
    )
    blur_amount = blur_amount or 5

    # ---------- normalize all color strings to RGBA ----------
    fore_color                      = _hex_to_rgba(fore_color)
    bg_color                        = _hex_to_rgba(bg_color)
    font_stroke_effect_color        = _hex_to_rgba(font_stroke_effect_color)
    font_shadow_effect_color        = _hex_to_rgba(font_shadow_effect_color)
    font_marker_effect_color        = _hex_to_rgba(font_marker_effect_color)
    font_fade_effect_color          = _hex_to_rgba(font_fade_effect_color)
    border_effect_color             = _hex_to_rgba(border_effect_color)
    image_overlay_effect_tint_color = _hex_to_rgba(image_overlay_effect_tint_color)

    # ------------ Debug: echo parameters ------------
    print("\n[DEBUG] create_image() called with:")
    for k, v in locals().items():
        if k != "self":
            print(f"  {k}: {v}")
    print("-----------------------------------------------")

    # ------------ Step 1: download photo ------------
    ideal_image = _get_image_from_pexels(subject, ideal_image_description)

    # ------------ Step 2: call Picasso -------------
    try:
        print("[DEBUG] Calling picasso_generate_image()...")
        picasso_generate_image(
            text=text,
            output_path=output_path,
            image_orientation=image_orientation,
            media_paths=[ideal_image],
            fore_color=fore_color,
            bg_color=bg_color,
            font_path=font_path,
            font_size=font_size,
            text_alpha=text_alpha,
            text_h_align=text_h_align,
            text_v_align=text_v_align,
            font_effect=font_effect,
            font_stroke_effect_color=font_stroke_effect_color,
            font_shadow_effect_color=font_shadow_effect_color,
            font_marker_effect_color=font_marker_effect_color,
            font_fade_effect_color=font_fade_effect_color,
            font_fade_effect_strength=font_fade_effect_strength,
            border_effect=border_effect,
            border_effect_color=border_effect_color,
            border_width=border_width,
            image_overlay_effect=image_overlay_effect,
            image_overlay_effect_tint_color=image_overlay_effect_tint_color,
            blur_amount=blur_amount,
        )
        print("✅ Picasso finished; poster saved at:", output_path)
    except Exception as e:
        err = f"Picasso generation failed: {e}"
        print("[ERROR]", err)
        return f"[ERROR] {err}"

    return output_path

# ------------------------------------------------------------------
# Agent
# ------------------------------------------------------------------

assistant_name = "Image_Generator_Agent"
runner = OpenAIAssistantRunner(
    assistant_name=assistant_name,
    tool_callbacks={"create_image": create_image}
)

# ------------------------------------------------------------------
# Demo runner
# ------------------------------------------------------------------
if __name__ == "__main__":

    async def main() -> None:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        global output_path, default_output_dir
        default_output_dir = os.path.join(current_dir, "test_output")

        # --- argparse ---
        parser = argparse.ArgumentParser(description="Run Image_Generator_Agent with custom prompt and output folder.")
        parser.add_argument("--prompt", type=str, required=True, help="User prompt describing the poster request.")
        parser.add_argument("--output_dir", type=str, default=default_output_dir, help="Folder path to save the output image.")
        args = parser.parse_args()

        # --- Run agent ---
        output_filename = "poster.jpg"   # or any default filename you prefer
        output_path = os.path.join(args.output_dir, output_filename)

        # optional: you can pass output_path via tools or just instruct the agent to use this folder
        user_prompt: str = args.prompt

        print(f"[INFO] Running agent with prompt:\n{user_prompt}")
        print(f"[INFO] Output will be saved to: {output_path}")

        # result = await Runner.run(image_agent, user_prompt)
        result = runner.run(prompt=user_prompt)

        print("\n=== Final output ===")
        print(result)

    asyncio.run(main())
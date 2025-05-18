import argparse
import random
from pathlib import Path
import sys
from typing import List, Tuple, Optional

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

Modules_Dir = "D:\\2025\\Projects\\Presence\\Presence0.1\\Resources\\Internal_Modules"
sys.path.insert(0, Modules_Dir)
from utilities.json_manager.json_manager import create_json

# --------------------------------------------------------------
# Helpers
# --------------------------------------------------------------

def _parse_rgba(s: str) -> Tuple[int, int, int, int]:
    parts = [int(p.strip()) for p in s.split(",")]
    if len(parts) == 3:
        parts.append(255)
    if len(parts) != 4:
        raise ValueError("RGBA string must have 3 or 4 values")
    return tuple(parts)  # type: ignore[misc]

FOUR_K = {
    "square": (2160, 2160),
    "horizontal": (3840, 2160),
    "vertical": (2160, 3840),
}

# Border effect implementation ------------------------------------------------

def _apply_border(img: Image.Image, effect: str, color: Tuple[int, int, int, int], width: int) -> Image.Image:
    if not effect:
        return img
    
    effect = effect.lower()

    if effect == "simple":
        new = Image.new("RGBA", (img.width + 2 * width, img.height + 2 * width), color)
        new.paste(img, (width, width))
        return new
    
    if effect == "rounded_corners":
        # Create rounded mask
        radius = width
        rounded = Image.new("L", img.size, 0)
        draw = ImageDraw.Draw(rounded)
        draw.rounded_rectangle((0, 0, img.width, img.height), radius, fill=255)
        masked = Image.new("RGBA", img.size)
        masked.paste(img, mask=rounded)
        return masked
    
    if effect == "glow":
        # how thick the border band is
        band = width                 # visible border width
        blur_radius = int(width * 0.8)  # softness of glow
        glow_color = color           # RGBA

        # 1️⃣ expand canvas so the border + glow fit
        cw, ch = img.width + 2 * band, img.height + 2 * band
        base = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        base.paste(img, (band, band))

        # 2️⃣ create a hollow rectangle (border ring)
        ring = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
        draw = ImageDraw.Draw(ring)
        draw.rectangle([0, 0, cw, ch], fill=glow_color)                         # outer
        draw.rectangle([band, band, band + img.width, band + img.height],       # inner cut‑out
                    fill=(0, 0, 0, 0))

        # 3️⃣ blur the ring to form the glow halo
        glow_layer = ring.filter(ImageFilter.GaussianBlur(blur_radius))

        # 4️⃣ composite glow UNDER the original picture
        base = Image.alpha_composite(glow_layer, base)   # halo sits around border
        return base

    return img

# Overlay filters -------------------------------------------------------------

def _apply_overlay(img: Image.Image, effects: List[str], color: Tuple[int, int, int, int], blur_amount: int) -> Image.Image:
    for fx in effects:
        fx = fx.strip().lower()
        if fx == "blur":
            img = img.filter(ImageFilter.GaussianBlur(radius=blur_amount))
        elif fx == "darken":
            img = ImageEnhance.Brightness(img).enhance(0.7)
        elif fx == "brighten":
            img = ImageEnhance.Brightness(img).enhance(1.3)
        elif fx == "color_tint":
            tint = Image.new("RGBA", img.size, color)
            img = Image.alpha_composite(img.convert("RGBA"), tint)
    return img

# Text placement --------------------------------------------------------------

def _wrap(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> List[str]:
    if not text or not text.strip():
        return []
    
    words = text.split()
    lines: List[str] = []
    cur: List[str] = []
    for w in words:
        test = " ".join(cur + [w])
        if draw.textlength(test, font=font) <= max_width:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def _auto_font_size(text: str, font_path: str, img_w: int, img_h: int, draw: ImageDraw.ImageDraw) -> int:
    if not text or not text.strip():
        return 10                         # return a dummy font size if text is empty
    
    # binary search for largest font that fits 80% width & 70% height
    lo, hi = 10, 400
    best = lo
    while lo <= hi:
        mid = (lo + hi) // 2
        font = ImageFont.truetype(font_path, mid)
        lines = _wrap(text, font, int(img_w * 0.8), draw)
        total_h = sum(draw.textbbox((0, 0), l, font=font)[3] for l in lines)
        max_w = max(draw.textlength(l, font=font) for l in lines)
        if total_h <= img_h * 0.7 and max_w <= img_w * 0.8:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return best


def _draw_text(
    img: Image.Image,
    text: str,
    font_path: str,
    font_size: str,
    text_alpha: int,
    fore_rgb: Tuple[int, int, int],
    font_effects: List[str],
    font_stroke_effect_color: Tuple[int, int, int, int],
    font_shadow_effect_color: Tuple[int, int, int, int],
    font_marker_effect_color: Tuple[int, int, int, int],
    font_fade_effect_color: Tuple[int, int, int, int],
    fade_strength: float,
    h_align: str,
    v_align: str,
):
    if not text or not text.strip():
        return img
    
    draw = ImageDraw.Draw(img)

    # base size calculation (80% width & 70% height)
    base_font_size = _auto_font_size(text, font_path, img.width, img.height, draw)
    size_map = {"tiny": 0.4, "small": 0.6, "medium": 0.8, "large": 1.0, "big": 1.1}
    scale = size_map.get(font_size, 1.0)
    font_size = max(10, int(base_font_size * scale))
    font = ImageFont.truetype(font_path, font_size)

    max_width = int(img.width * 0.8)
    lines = _wrap(text, font, max_width, draw)
    if not lines:
        return img


    line_heights = [draw.textbbox((0, 0), l, font=font)[3] for l in lines]
    total_h = sum(line_heights)

    # vertical alignment
    if v_align == "top":
        y = int(img.height * 0.1)
    elif v_align == "bottom":
        y = img.height - total_h - int(img.height * 0.1)
    else:
        y = (img.height - total_h) // 2

    num_lines = len(lines) or 1

    # ─ Marker Background Overlay (once per block) ─
    if "marker" in font_effects:
        overlay_margin = 20
        overlay_top = y - overlay_margin
        overlay_bottom = y + total_h + (overlay_margin * 3)
        overlay_left = int(img.width * 0.1) - overlay_margin
        overlay_right = img.width - int(img.width * 0.1) + overlay_margin
        overlay_box = (overlay_left, overlay_top, overlay_right, overlay_bottom)

        overlay_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
        overlay_draw = ImageDraw.Draw(overlay_layer)
        overlay_draw.rectangle(overlay_box, fill=font_marker_effect_color)
        img.alpha_composite(overlay_layer)

    for idx, line in enumerate(lines):
        line_h = line_heights[idx]
        w = draw.textlength(line, font=font)

        # horizontal alignment
        if h_align == "left":
            x = int(img.width * 0.1)
        elif h_align == "right":
            x = img.width - int(img.width * 0.1) - w
        else:
            x = (img.width - w) // 2

        # ─ Fade effect ─
        if "fade" in font_effects:
            factor = 1.0 - fade_strength * (idx / max(num_lines - 1, 1))
            line_rgb = tuple(
                int(c + (font_fade_effect_color[i] - c) * (1 - factor))
                for i, c in enumerate(fore_rgb[:3])  # 🟢 strip alpha safely
            )
            fill_color = (*line_rgb, text_alpha)
        else:
            fill_color = (*fore_rgb[:3], text_alpha)  # 🟢 always strip alpha here too

        # ─ Shadow ─
        if "shadow" in font_effects:
            shadow_offset = 20
            shadow_blur_radius = 30

            # Step 1: create shadow-only layer
            shadow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
            shadow_draw = ImageDraw.Draw(shadow_layer)
            shadow_draw.text((x + shadow_offset, y + shadow_offset), line, font=font,
                            fill=font_shadow_effect_color)

            # Step 2: blur the shadow
            blurred_shadow = shadow_layer.filter(ImageFilter.GaussianBlur(radius=shadow_blur_radius))

            # Step 3: composite the blurred shadow under the main text
            img.alpha_composite(blurred_shadow)

        # ─ Main Text ─
        text_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
        text_draw = ImageDraw.Draw(text_layer)

        # ─ Stroke effect ─
        if "stroke" in font_effects:
            text_draw.text((x, y), line, font=font,
                           fill=fill_color, stroke_width=2,
                           stroke_fill=font_stroke_effect_color[:3])
        else:
            text_draw.text((x, y), line, font=font, fill=fill_color)

        img.alpha_composite(text_layer)
        y += line_h



# -----------------------------------------------------------------------------
# Main API
# -----------------------------------------------------------------------------

def generate_image(
    text: str,
    output_path: str,
    image_orientation: str,
    media_paths: Optional[List[str]],
    fore_color: str,
    bg_color: str,
    font_path: str,
    font_size: str,
    text_alpha: int,
    font_effect: str,
    font_stroke_effect_color: str,
    font_shadow_effect_color: str,
    font_marker_effect_color: str,
    font_fade_effect_color: str,
    font_fade_effect_strength: float,
    border_effect: str,
    border_effect_color: str,
    image_overlay_effect: str,
    image_overlay_effect_tint_color: str,
    text_h_align: str,
    text_v_align: str,
    blur_amount: int,
    border_width: int,
):
    orientation = image_orientation.lower()
    if orientation not in FOUR_K:
        raise ValueError("Invalid orientation")
    w, h = FOUR_K[orientation]

    # base background
    if media_paths:
        src = Path(random.choice(media_paths))
        if not src.exists():
            raise FileNotFoundError(src)
        bg = Image.open(src).convert("RGBA")
        bg = bg.resize((w, h), Image.LANCZOS)  # force image to fill the entire output
        canvas = Image.new("RGBA", (w, h), _parse_rgba(bg_color))
        canvas.alpha_composite(bg)
    else:
        canvas = Image.new("RGBA", (w, h), _parse_rgba(bg_color))

    # overlay filters
    canvas = _apply_overlay(canvas, image_overlay_effect.split(",") if image_overlay_effect else [], _parse_rgba(image_overlay_effect_tint_color), blur_amount)

    # text drawing
    _draw_text(
        canvas,
        text,
        font_path,
        font_size,
        text_alpha,
        _parse_rgba(fore_color),
        [e.strip().lower() for e in font_effect.split(",") if e.strip()],
        _parse_rgba(font_stroke_effect_color),
        _parse_rgba(font_shadow_effect_color),
        _parse_rgba(font_marker_effect_color),
        _parse_rgba(font_fade_effect_color),
        font_fade_effect_strength,
        text_h_align,
        text_v_align,
    )

    # border
    canvas = _apply_border(canvas, border_effect.strip().lower(), _parse_rgba(border_effect_color), border_width)

    # save
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out, format="JPEG", quality=95)

    # metadata
    if not text or not text.strip():
        title = "Empty Image"
        description = "Empty Image"
    else:   
        title = text.split()[0][:60]
        description = text

    create_json(title, description, out.parent)

    print(f"Saved image at {out}")

# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("Picasso – 4K Image Generator")

    # mandatory
    p.add_argument("--text", required=True,
                   help="Input text content to render on the image.")
    p.add_argument("--output_path", required=True,
                   help="Full output path for the generated image file (e.g. output.jpg).")

    # image
    p.add_argument("--image_orientation", choices=["square", "vertical", "horizontal"], default="vertical",
                   help="Image layout format. 'square' = 2160x2160, 'vertical' = 2160x3840, 'horizontal' = 3840x2160.")
    p.add_argument("--media_path", nargs="*", default=None,
                   help="Path(s) to background image(s). One is randomly chosen and resized to fill the image.")

    # colors
    p.add_argument("--fore_color", type=str, default="0,0,0,255",
                   help="RGB color for the main text (e.g. '255,0,0,255' = red).")
    p.add_argument("--bg_color", type=str, default="255,255,255,255",
                   help="RGB fallback background color if no media is used.")

    # font
    p.add_argument("--font_path", default=r"C:\\Windows\\Fonts\\ariblk.ttf",
                   help="Path to a .ttf font file.")
    p.add_argument("--font_size", type=str, choices=["tiny", "small", "medium", "large", "big"], default="medium", 
                   help="Relative font size level. Options: tiny, small, medium, large, big.")
    p.add_argument("--text_alpha", type=int, default=255, 
                   help="Alpha (0–255) applied to all text lines (default: 255 = fully opaque).")
    p.add_argument("--text_h_align", choices=["left", "center", "right"], default="center",
                   help="Horizontal alignment of the text block.")
    p.add_argument("--text_v_align", choices=["top", "center", "bottom"], default="center",
                   help="Vertical alignment of the text block.")

    # effects
    p.add_argument("--font_effect", default="", 
                   help="Comma-separated font effects: 'stroke', 'shadow', 'marker', 'fade'")
    p.add_argument("--font_stroke_effect_color", type=str, default="255,255,255,128", 
                   help="RGBA color for font stroke effect.")
    p.add_argument("--font_shadow_effect_color", type=str, default="255,255,255,128", 
                   help="RGBA color for font shadow effect.")
    p.add_argument("--font_marker_effect_color", type=str, default="255,255,255,128", 
                   help="RGBA color for font marker effect.")
    p.add_argument("--font_fade_effect_color", type=str, default="255,255,255,128", 
                   help="RGBA color for font fade effect.")
    p.add_argument("--font_fade_effect_strength", type=float, default=0.2, 
                   help="0=no fade, 1=full fade for 'fade' font effect.")
    
    p.add_argument("--border_effect", default="", 
                   help="Border effect style: 'simple', 'rounded_corners', 'glow'.")
    p.add_argument("--border_effect_color", type=str, default="255,255,255,128",
                   help="RGBA color used for border effects.")
    p.add_argument("--border_width", type=int, default=40,
                   help="Border thickness in pixels (used by most border effects).")
    
    p.add_argument("--image_overlay_effect", default="",
                   help="Comma-separated overlay effects on the background: 'blur', 'darken', 'brighten', 'color_tint'.")
    p.add_argument("--image_overlay_effect_tint_color", type=str, default="255,255,255,50",
                   help="RGBA color used for the image overlay effect (e.g. tint color).")
    p.add_argument("--blur_amount", type=int, default=5,
                   help="Blur radius (used only if 'blur' is in image_overlay_effect).")

    return p

def main():
    args = _build_parser().parse_args()
    generate_image(
        text=args.text,
        output_path=args.output_path,
        image_orientation=args.image_orientation,
        media_paths=args.media_path,
        fore_color=args.fore_color,
        bg_color=args.bg_color,
        font_path=args.font_path,
        font_size=args.font_size,
        text_alpha=args.text_alpha,
        font_effect=args.font_effect,
        font_stroke_effect_color=args.font_stroke_effect_color,
        font_shadow_effect_color=args.font_shadow_effect_color,
        font_marker_effect_color=args.font_marker_effect_color,
        font_fade_effect_color=args.font_fade_effect_color,
        font_fade_effect_strength=args.font_fade_effect_strength,
        border_effect=args.border_effect,
        border_effect_color=args.border_effect_color,
        image_overlay_effect=args.image_overlay_effect,
        image_overlay_effect_tint_color=args.image_overlay_effect_tint_color,
        text_h_align=args.text_h_align,
        text_v_align=args.text_v_align,
        blur_amount=args.blur_amount,
        border_width=args.border_width,
    )

if __name__ == "__main__":
    main()
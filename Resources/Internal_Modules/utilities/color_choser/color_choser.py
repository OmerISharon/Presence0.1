#!/usr/bin/env python3
"""
color_map.py

Generates a hue-based map of 100 buckets. For any input hex color, it returns:
- A "primary" color (complementary hue)
- A "secondary" color (neutral gray depending on temperature)

Provides:
    get_complementary_colors(input_hex) → (primary_hex, secondary_hex)
    Stylish CLI output when run directly
"""

import colorsys

# Global color map
COLOR_MAP = {}

def rgb_to_hex(r, g, b):
    return "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))

def hex_to_rgb(hex_val):
    hex_val = hex_val.lstrip("#")
    return tuple(int(hex_val[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def generate_color_map():
    for i in range(100):
        start_deg = i * 3.6
        end_deg = (i + 1) * 3.6
        mid_deg = (start_deg + end_deg) / 2
        mid_h = mid_deg / 360.0

        comp_h = (mid_h + 0.5) % 1.0
        primary_rgb = colorsys.hls_to_rgb(comp_h, 0.5, 0.7)
        primary_hex = rgb_to_hex(*primary_rgb)

        secondary_hex = "#B0A99F" if mid_deg < 180 else "#A9A9A9"

        COLOR_MAP[i] = {
            "hue_range": (start_deg, end_deg),
            "mid_deg": mid_deg,
            "primary": primary_hex,
            "secondary": secondary_hex
        }

generate_color_map()

def get_complementary_colors(input_hex):
    """
    Returns (primary_hex: str, secondary_hex: str) for a given input hex color.
    """
    r, g, b = hex_to_rgb(input_hex)
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    hue_deg = h * 360
    bucket_index = min(int(hue_deg / 3.6), 99)
    mapping = COLOR_MAP[bucket_index]
    return mapping["primary"], mapping["secondary"]

def ansi_preview(hex_color, label=""):
    """Returns a string with ANSI colored preview block (works in terminals)."""
    r, g, b = hex_to_rgb(hex_color)
    return f"\033[48;2;{int(r*255)};{int(g*255)};{int(b*255)}m  {label.center(10)}  \033[0m"

# Preview mode
if __name__ == "__main__":
    import sys

    def print_color_preview(primary_hex, secondary_hex, bg_hex=None, bg_label=""):
        parts = []
        if isinstance(bg_hex, str) and bg_hex.startswith("#") and len(bg_hex) == 7:
            parts.append(ansi_preview(bg_hex, "Input"))
        parts.append(ansi_preview(primary_hex, "Primary"))
        parts.append(ansi_preview(secondary_hex, "Secondary"))
        print("  ".join(parts) + (f"  ← {bg_label}" if bg_label else ""))

    if len(sys.argv) == 2 and sys.argv[1] == "--preview":
        print("🎨 Stylish Preview of All 100 Hue Buckets:\n")
        for idx, data in COLOR_MAP.items():
            mid_deg = data["mid_deg"]
            primary = data["primary"]

            # Dynamically assign secondary color
            if mid_deg < 90 or mid_deg > 330:
                secondary = "#B0A99F"  # warm gray
            elif 90 <= mid_deg <= 270:
                secondary = "#A9A9A9"  # cool gray
            else:
                secondary = "#CCCCCC"  # soft neutral

            range_txt = f"Hue {data['hue_range'][0]:.1f}°–{data['hue_range'][1]:.1f}°"
            print_color_preview(primary, secondary, bg_hex=None, bg_label=range_txt)
        sys.exit(0)

    if len(sys.argv) != 2:
        print("Usage:")
        print("  python color_map.py <#hexcolor>     → Get primary/secondary pair")
        print("  python color_map.py --preview       → Stylish preview of all buckets")
        sys.exit(1)

    input_hex = sys.argv[1].strip()
    if not input_hex.startswith("#"):
        input_hex = "#" + input_hex

    try:
        # Compute hue and get color pair
        r, g, b = hex_to_rgb(input_hex)
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        hue_deg = h * 360

        # Dynamic secondary color
        if hue_deg < 90 or hue_deg > 330:
            secondary = "#B0A99F"  # warm gray
        elif 90 <= hue_deg <= 270:
            secondary = "#A9A9A9"  # cool gray
        else:
            secondary = "#CCCCCC"  # soft neutral

        # Complementary (primary) based on 180° hue rotation
        comp_h = (h + 0.5) % 1.0
        primary_rgb = colorsys.hls_to_rgb(comp_h, 0.5, 0.7)
        primary = rgb_to_hex(*primary_rgb)

        print(f"\n🎨 Input Color:     {input_hex.upper()} (Hue {hue_deg:.1f}°)")
        print(f"✅ Primary Color:   {primary}")
        print(f"✅ Secondary Color: {secondary}")
        print("\n🖼️  Terminal Preview:")
        print_color_preview(primary, secondary, bg_hex=input_hex)

    except Exception as e:
        print(f"❌ Error: {e}")

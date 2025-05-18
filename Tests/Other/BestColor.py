#!/usr/bin/env python3
"""
color_map.py (Enhanced)

A dynamic and creative module to map any HEX color to its complementary
(primary and secondary) design pair, based on hue.

When run directly, includes explanations, visual previews, and developer utilities.
"""

import colorsys

# Global mapping: hue buckets
COLOR_MAP = {}

# Optional: basic named color proximity
NAMED_COLORS = {
    "#FFFF00": "Yellow",
    "#008000": "Green",
    "#FF0000": "Red",
    "#0000FF": "Blue",
    "#FFA500": "Orange",
    "#800080": "Purple",
    "#00FFFF": "Cyan",
    "#FFC0CB": "Pink",
    "#A9A9A9": "Dim Gray",
    "#008080": "Teal",
    "#1E90FF": "Dodger Blue",
    "#4169E1": "Royal Blue"
}

def rgb_to_hex(r, g, b):
    """Converts RGB float (0..1) to hex string."""
    return "#{:02X}{:02X}{:02X}".format(int(r * 255), int(g * 255), int(b * 255))

def hex_to_rgb(hex_val):
    """Converts hex string to normalized RGB tuple."""
    hex_val = hex_val.lstrip("#")
    return tuple(int(hex_val[i:i+2], 16) / 255.0 for i in (0, 2, 4))

def generate_color_map():
    """Populates COLOR_MAP with 100 buckets across the hue circle."""
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
            "midpoint_deg": mid_deg,
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


def closest_named_color(hex_val):
    """Returns closest named color if within threshold (basic RGB distance)."""
    r1, g1, b1 = hex_to_rgb(hex_val)
    closest = None
    min_dist = float('inf')
    for hex_code, name in NAMED_COLORS.items():
        r2, g2, b2 = hex_to_rgb(hex_code)
        dist = ((r2 - r1)**2 + (g2 - g1)**2 + (b2 - b1)**2)
        if dist < min_dist:
            min_dist = dist
            closest = name
    return closest if min_dist < 0.02 else None

def print_color_swatches(primary, secondary, bg):
    """Prints styled swatches in the terminal (if supported)."""
    print(f"\033[48;2;{int(bg[0]*255)};{int(bg[1]*255)};{int(bg[2]*255)}m", end="")
    print("     BG     ", end="")
    print("\033[0m", end="  ")

    print(f"\033[38;2;{int(primary[0]*255)};{int(primary[1]*255)};{int(primary[2]*255)}m", end="")
    print("Primary", end="")
    print("\033[0m", end="  ")

    print(f"\033[38;2;{int(secondary[0]*255)};{int(secondary[1]*255)};{int(secondary[2]*255)}m", end="")
    print("Secondary")
    print("\033[0m", end="")

# --- Run mode ---
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python color_map.py <hex_color> | --preview")
        sys.exit(0)

    if sys.argv[1] == "--preview":
        print("🎨 Previewing all 100 hue buckets:")
        for i, data in COLOR_MAP.items():
            print(f"Bucket {i:02d} ({data['hue_range'][0]:.1f}°–{data['hue_range'][1]:.1f}°): "
                  f"Primary {data['primary']}  Secondary {data['secondary']}")
        sys.exit(0)

    # User provided a hex color
    input_hex = sys.argv[1].strip()
    if not input_hex.startswith("#"):
        input_hex = "#" + input_hex

    try:
        mapping, actual_hue = get_complementary_colors(input_hex)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    primary = mapping["primary"]
    secondary = mapping["secondary"]
    hue_range = mapping["hue_range"]
    midpoint = mapping["midpoint_deg"]

    print(f"\n🎨 Analyzing: {input_hex.upper()}")
    print(f"  → Detected Hue: {actual_hue:.1f}°")
    print(f"  → Hue Bucket: {hue_range[0]:.1f}° – {hue_range[1]:.1f}° (Midpoint {midpoint:.1f}°)")
    print(f"\n✅ Best-Fit Primary:   {primary}")
    print(f"✅ Best-Fit Secondary: {secondary}")

    name_match = closest_named_color(input_hex)
    if name_match:
        print(f"🔍 Closest named color: {name_match}")

    # Visual preview
    print("\n🖼️  Terminal Swatch Preview:")
    r_bg, g_bg, b_bg = hex_to_rgb(input_hex)
    r_pr, g_pr, b_pr = hex_to_rgb(primary)
    r_sc, g_sc, b_sc = hex_to_rgb(secondary)
    print_color_swatches((r_pr, g_pr, b_pr), (r_sc, g_sc, b_sc), (r_bg, g_bg, b_bg))


"""
Text Effects module for applying aesthetic styles to text in Manim.
"""

import random
from manim import *


def apply_old_book_styling(text_mobject):
    """Apply vintage book styling to a Text mobject."""
    
    # Slight slant for handwriting appearance
    text_mobject.slant = 0.1
    
    # Add slight randomness to letter spacing
    original_submobjects = text_mobject.submobjects.copy()
    for i, submob in enumerate(original_submobjects):
        if i > 0:
            # Add slight random horizontal displacement
            shift_x = random.uniform(-0.02, 0.02)
            shift_y = random.uniform(-0.01, 0.01)
            submob.shift([shift_x, shift_y, 0])
    
    return text_mobject


def create_pen_noise_effect(text_mobject):
    """
    Create a noise effect that resembles variations in pen pressure.
    This is applied during animation rather than to the static text.
    """
    # Create a noise texture that will be used to modulate stroke width
    # This is a placeholder for actual implementation using Manim's SVG capabilities
    noise_group = VGroup()
    
    # Here we'd create a more sophisticated effect for actual production use
    for submob in text_mobject.submobjects:
        # Add subtle dots and line variations around the text
        for _ in range(random.randint(1, 3)):
            dot = Dot(
                radius=random.uniform(0.01, 0.02),
                color=text_mobject.color,
                opacity=random.uniform(0.1, 0.3)
            )
            dot.move_to(submob.get_center() + 
                      [random.uniform(-0.1, 0.1), 
                       random.uniform(-0.1, 0.1), 0])
            noise_group.add(dot)
    
    return noise_group


def create_vintage_shadow(text_mobject, shadow_color="#8B4513", opacity=0.3, offset=(0.03, -0.03)):
    """Create a subtle shadow effect for text to give it depth on the page."""
    shadow = text_mobject.copy()
    shadow.set_color(shadow_color)
    shadow.set_opacity(opacity)
    shadow.shift([offset[0], offset[1], 0])
    
    return shadow


def create_decorative_underline(text_mobject, color="#8B4513", width_scale=1.2):
    """Create a decorative underline with slight wave effect."""
    # Get text width and position
    width = text_mobject.width * width_scale
    bottom_point = text_mobject.get_bottom()
    
    # Create underline with a wavy pattern
    num_points = 20
    points = []
    
    for i in range(num_points):
        x = (i / (num_points - 1) - 0.5) * width
        y = bottom_point[1] - 0.1 + 0.02 * np.sin(i * 0.5)
        points.append([x, y, 0])
    
    underline = VMobject(color=color)
    underline.set_points_as_corners(points)
    
    return underline


def create_ink_splotch_effect(color="#8B4513", opacity_range=(0.05, 0.15)):
    """Create random ink splotches for vintage aesthetic."""
    splotches = VGroup()
    
    # Create 3-5 random splotches
    for _ in range(random.randint(3, 5)):
        # Random position within frame
        x = random.uniform(-5, 5)
        y = random.uniform(-3, 3)
        
        # Random size and opacity
        radius = random.uniform(0.1, 0.3)
        opacity = random.uniform(opacity_range[0], opacity_range[1])
        
        # Create irregular shape using several overlapping circles
        splotch = VGroup()
        num_circles = random.randint(3, 6)
        
        for i in range(num_circles):
            offset_x = random.uniform(-radius/2, radius/2)
            offset_y = random.uniform(-radius/2, radius/2)
            circle_radius = random.uniform(radius * 0.5, radius * 1.2)
            
            circle = Circle(
                radius=circle_radius,
                color=color,
                fill_opacity=opacity,
                stroke_width=0
            )
            circle.move_to([x + offset_x, y + offset_y, 0])
            splotch.add(circle)
        
        splotches.add(splotch)
    
    return splotches


def apply_aging_effect(text_mobject, intensity=0.3):
    """
    Apply an aging effect to make text look worn and faded in places.
    This would be implemented using custom shader effects in a real production.
    For this example, we'll use opacity variations.
    """
    # Clone the text to preserve original
    aged_text = text_mobject.copy()
    
    # Apply random fading to parts of the text
    for submob in aged_text.submobjects:
        # Random opacity based on aging intensity
        fade_factor = 1 - random.uniform(0, intensity)
        submob.set_opacity(fade_factor)
    
    return aged_text


# Define some standard color constants for old book aesthetics
DARK_BROWN = "#8B4513"  # SaddleBrown
SEPIA = "#704214"       # Sepia
FADED_BLACK = "#333333" # Dark gray for aged text
AGED_PAPER = "#F5F5DC"  # Beige


# Collection of modifiers that can be applied together
def apply_complete_old_book_style(text_mobject):
    """Apply a complete set of old book styling effects to text."""
    styled_group = VGroup()
    
    # Add shadow first (behind original text)
    shadow = create_vintage_shadow(text_mobject)
    styled_group.add(shadow)
    
    # Apply styling to original text
    styled_text = apply_old_book_styling(text_mobject.copy())
    styled_group.add(styled_text)
    
    # Add decorative elements
    underline = create_decorative_underline(styled_text)
    styled_group.add(underline)
    
    # Optional ink noise effect
    if random.random() < 0.3:  # 30% chance to add noise
        noise = create_pen_noise_effect(styled_text)
        styled_group.add(noise)
    
    return styled_group

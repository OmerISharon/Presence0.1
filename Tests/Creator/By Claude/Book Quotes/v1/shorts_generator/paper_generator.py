"""
Paper Texture Generator module for creating vintage paper backgrounds.
"""

import random
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance


class PaperTextureGenerator:
    """Class to generate realistic old paper textures for video backgrounds."""
    
    def __init__(self, assets_dir):
        """
        Initialize the paper texture generator.
        
        Args:
            assets_dir (Path): Directory to store generated textures
        """
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(exist_ok=True)
    
    def generate_old_paper_texture(self, output_path, size=(2048, 2048), 
                                  age=0.7, stains=0.6, noise=0.5):
        """
        Generate an old paper texture with customizable parameters.
        
        Args:
            output_path (Path): Where to save the generated texture
            size (tuple): Width and height of the texture
            age (float): 0 to 1, how aged/yellowed the paper appears
            stains (float): 0 to 1, amount of staining/discoloration
            noise (float): 0 to 1, amount of noise/grain
        
        Returns:
            Path: Path to the generated texture
        """
        # Create a base beige/yellowish image
        # Color depends on the age parameter
        base_color = self._get_paper_color(age)
        base = Image.new('RGB', size, base_color)
        
        # Add paper grain/noise
        base = self._add_paper_grain(base, intensity=noise)
        
        # Add stains and aging effects
        if stains > 0:
            base = self._add_stains(base, intensity=stains)
        
        # Add subtle vignette effect
        base = self._add_vignette(base, intensity=0.2 + age * 0.2)
        
        # Add fold marks and creases if heavily aged
        if age > 0.6:
            base = self._add_fold_marks(base, intensity=age-0.3)
        
        # Apply final adjustments to enhance realism
        base = self._apply_final_enhancements(base)
        
        # Save the texture
        base.save(output_path)
        print(f"Generated old paper texture at {output_path}")
        
        return output_path
    
    def _get_paper_color(self, age):
        """
        Get an appropriate paper color based on age parameter.
        
        Args:
            age (float): 0 to 1, how aged/yellowed the paper appears
        
        Returns:
            tuple: RGB color tuple
        """
        # Newer paper is more white/cream, older is more yellow/brown
        r = int(245 - age * 25)
        g = int(235 - age * 40)
        b = int(200 - age * 50)
        return (r, g, b)
    
    def _add_paper_grain(self, image, intensity=0.5):
        """
        Add realistic paper grain and texture.
        
        Args:
            image (PIL.Image): Base image
            intensity (float): 0 to 1, strength of the grain effect
        
        Returns:
            PIL.Image: Image with grain added
        """
        # Convert to numpy array for pixel manipulation
        pixels = np.array(image)
        
        # Scale intensity for appropriate noise level
        noise_level = int(intensity * 15)
        
        # Generate Perlin-like noise (simplified with random noise)
        noise = np.random.normal(0, noise_level, pixels.shape).astype(np.int8)
        
        # Apply noise to the image
        noisy_pixels = np.clip(pixels + noise, 0, 255).astype(np.uint8)
        
        # Convert back to PIL Image
        return Image.fromarray(noisy_pixels)
    
    def _add_stains(self, image, intensity=0.6, num_stains=None):
        """
        Add realistic stains and discolorations to the paper.
        
        Args:
            image (PIL.Image): Base image
            intensity (float): 0 to 1, amount of staining
            num_stains (int): Number of stains to add, or None for automatic
        
        Returns:
            PIL.Image: Image with stains added
        """
        # Make a copy to avoid modifying the original
        stained = image.copy()
        draw = ImageDraw.Draw(stained)
        
        # Calculate automatic number of stains based on intensity if not specified
        if num_stains is None:
            num_stains = int(5 + intensity * 25)
        
        width, height = image.size
        
        # Add various stains
        for _ in range(num_stains):
            # Random position
            x = random.randint(0, width)
            y = random.randint(0, height)
            
            # Random size based on intensity
            max_radius = int(100 + intensity * 400)
            radius = random.randint(20, max_radius)
            
            # Random color for the stain (browns, yellows, and faded colors)
            r = random.randint(160, 220)
            g = random.randint(140, 190)
            b = random.randint(90, 150)
            color = (r, g, b)
            
            # Random opacity
            opacity = random.uniform(0.1, 0.4)
            
            # Draw the stain as a blurred ellipse
            # We'll simulate transparency by blending colors
            ellipse_shape = [(x-radius, y-radius), (x+radius, y+radius)]
            
            # Get original color for every pixel and blend with stain color
            for i in range(ellipse_shape[0][0], ellipse_shape[1][0]):
                if i < 0 or i >= width:
                    continue
                    
                for j in range(ellipse_shape[0][1], ellipse_shape[1][1]):
                    if j < 0 or j >= height:
                        continue
                        
                    # Check if point is in ellipse
                    if ((i - x) ** 2 + (j - y) ** 2) <= radius ** 2:
                        # Calculate distance from center for falloff
                        dist = ((i - x) ** 2 + (j - y) ** 2) ** 0.5
                        falloff = 1 - (dist / radius)
                        
                        # Get current pixel color
                        current_color = stained.getpixel((i, j))
                        
                        # Blend colors based on opacity and falloff
                        blend_factor = opacity * falloff
                        new_r = int(current_color[0] * (1 - blend_factor) + color[0] * blend_factor)
                        new_g = int(current_color[1] * (1 - blend_factor) + color[1] * blend_factor)
                        new_b = int(current_color[2] * (1 - blend_factor) + color[2] * blend_factor)
                        
                        draw.point((i, j), fill=(new_r, new_g, new_b))
        
        # Apply a slight blur to make stains look more natural
        stained = stained.filter(ImageFilter.GaussianBlur(radius=1))
        
        return stained
    
    def _add_vignette(self, image, intensity=0.3):
        """
        Add a subtle vignette effect to the edges.
        
        Args:
            image (PIL.Image): Base image
            intensity (float): 0 to 1, strength of the vignette
        
        Returns:
            PIL.Image: Image with vignette added
        """
        # Make a copy to avoid modifying the original
        result = image.copy()
        width, height = image.size
        
        # Create a new image for the vignette mask
        mask = Image.new('L', (width, height), 255)
        draw = ImageDraw.Draw(mask)
        
        # Calculate how far the vignette should extend
        vignette_width = int(width * (0.5 + intensity * 0.5))
        vignette_height = int(height * (0.5 + intensity * 0.5))
        
        # Draw a radial gradient for the vignette
        for i in range(width):
            for j in range(height):
                # Calculate distance from center (normalized)
                x_dist = abs(i - width/2) / (width/2)
                y_dist = abs(j - height/2) / (height/2)
                dist = (x_dist**2 + y_dist**2)**0.5
                
                # Apply radial falloff
                if dist > 0.6:  # Only apply to edges
                    # Map distance to mask value (darker toward edges)
                    # Scale based on intensity
                    value = int(255 * (1 - (dist - 0.6) / 0.4 * intensity))
                    value = max(0, min(255, value))
                    mask.putpixel((i, j), value)
        
        # Blur the mask for smoother transition
        mask = mask.filter(ImageFilter.GaussianBlur(radius=width/30))
        
        # Apply the mask to darken the edges
        result = Image.composite(
            Image.new('RGB', (width, height), (0, 0, 0)),
            result,
            mask
        )
        
        return result
    
    def _add_fold_marks(self, image, intensity=0.5):
        """
        Add subtle fold marks and creases to the paper.
        
        Args:
            image (PIL.Image): Base image
            intensity (float): 0 to 1, how prominent the folds appear
        
        Returns:
            PIL.Image: Image with fold marks added
        """
        # Make a copy to avoid modifying the original
        result = image.copy()
        draw = ImageDraw.Draw(result)
        width, height = image.size
        
        # Add horizontal and/or vertical fold lines
        num_folds = random.randint(1, 3)
        
        for _ in range(num_folds):
            # Decide between horizontal and vertical fold
            is_horizontal = random.random() > 0.5
            
            if is_horizontal:
                # Horizontal fold
                y = random.randint(height // 4, 3 * height // 4)
                fold_width = int(1 + intensity * 2)
                
                # Draw a thin dark line for the fold
                for i in range(width):
                    # Slight variation in the line position for realism
                    offset = random.randint(-1, 1)
                    y_pos = y + offset
                    
                    # Get current color
                    current = result.getpixel((i, y_pos))
                    
                    # Darken slightly for fold line
                    darkened = (
                        int(current[0] * 0.8),
                        int(current[1] * 0.8),
                        int(current[2] * 0.8)
                    )
                    
                    # Draw the fold line
                    for j in range(fold_width):
                        if 0 <= y_pos + j < height:
                            draw.point((i, y_pos + j), fill=darkened)
            else:
                # Vertical fold
                x = random.randint(width // 4, 3 * width // 4)
                fold_width = int(1 + intensity * 2)
                
                # Draw a thin dark line for the fold
                for j in range(height):
                    # Slight variation in the line position for realism
                    offset = random.randint(-1, 1)
                    x_pos = x + offset
                    
                    # Get current color
                    current = result.getpixel((x_pos, j))
                    
                    # Darken slightly for fold line
                    darkened = (
                        int(current[0] * 0.8),
                        int(current[1] * 0.8),
                        int(current[2] * 0.8)
                    )
                    
                    # Draw the fold line
                    for i in range(fold_width):
                        if 0 <= x_pos + i < width:
                            draw.point((x_pos + i, j), fill=darkened)
        
        # Add some random small creases
        num_creases = int(10 * intensity)
        for _ in range(num_creases):
            # Random starting point
            x1 = random.randint(0, width)
            y1 = random.randint(0, height)
            
            # Random length and angle
            length = random.randint(20, 100)
            angle = random.uniform(0, 2 * np.pi)
            
            # Calculate end point
            x2 = int(x1 + length * np.cos(angle))
            y2 = int(y1 + length * np.sin(angle))
            
            # Draw a thin slightly darker line
            for t in range(100):
                # Parametric equation of line
                x = int(x1 + (x2 - x1) * t / 100)
                y = int(y1 + (y2 - y1) * t / 100)
                
                # Skip if outside image
                if x < 0 or x >= width or y < 0 or y >= height:
                    continue
                
                # Get current color
                current = result.getpixel((x, y))
                
                # Slightly darken for crease
                darkened = (
                    int(current[0] * 0.9),
                    int(current[1] * 0.9),
                    int(current[2] * 0.9)
                )
                
                draw.point((x, y), fill=darkened)
        
        return result
    
    def _apply_final_enhancements(self, image):
        """
        Apply final enhancements for realism.
        
        Args:
            image (PIL.Image): Processed image
        
        Returns:
            PIL.Image: Enhanced image
        """
        # Adjust contrast slightly
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.1)
        
        # Add very subtle blur for smoothness
        image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
        
        return image
    
    def generate_texture_variants(self, base_name, count=3):
        """
        Generate multiple variants of paper textures.
        
        Args:
            base_name (str): Base name for the texture files
            count (int): Number of variants to generate
        
        Returns:
            list: Paths to the generated textures
        """
        paths = []
        
        for i in range(count):
            # Vary parameters slightly for each variant
            age = random.uniform(0.5, 0.9)
            stains = random.uniform(0.4, 0.8)
            noise = random.uniform(0.3, 0.7)
            
            output_path = self.assets_dir / f"{base_name}_{i+1}.jpg"
            
            self.generate_old_paper_texture(
                output_path,
                age=age,
                stains=stains,
                noise=noise
            )
            
            paths.append(output_path)
        
        return paths

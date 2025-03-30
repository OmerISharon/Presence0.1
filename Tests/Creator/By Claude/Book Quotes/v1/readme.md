# YouTube Shorts Generator - Old Book Quote Animation

A Python project that generates high-quality videos optimized for YouTube Shorts, featuring animated quotes with an old book aesthetic and handwriting-style kinetic typography.

## Features

- **60 FPS Video Output**: Smooth animations optimized for YouTube Shorts
- **Old Book Styling**: Vintage paper textures with decorative elements
- **Handwriting Animation**: Text appears as if being written by hand
- **Kinetic Typography Effects**: Dynamic text animations and transitions
- **Perfect Aspect Ratio**: 9:16 ratio (1080×1920) optimized for vertical video platforms
- **Customizable Quotes**: Easy to modify for different quotes and styles

## Demo

![Example Output](docs/example_output.gif)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/youtube-shorts-generator.git
   cd youtube-shorts-generator
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -e .
   # or
   pip install -r requirements.txt
   ```

### Prerequisites

- Python 3.8 or higher
- FFmpeg installed on your system (required for video processing)

## Usage

### Basic Usage

```python
from shorts_generator import generate_quote_video

# Generate a video with the default quote
generate_quote_video()

# Or with a custom quote
custom_quote = "Your custom quote goes here. Make it meaningful and inspirational!"
generate_quote_video(quote=custom_quote, output_file="my_custom_quote.mp4")
```

### Command Line Interface

```bash
# Generate with default settings
python -m shorts_generator.main

# Custom quote from a text file
python -m shorts_generator.main --quote-file quotes.txt --output custom_video.mp4
```

## Customization

You can customize various aspects of the generated video:

- Background textures (place your own textures in the `assets` folder)
- Font styles (modify the `handwriting_font_path` in the code)
- Colors and visual effects (adjust parameters in `text_effects.py`)
- Animation timing and effects (modify the Manim scene in `quote_animator.py`)

## Project Structure

```
youtube-shorts-generator/
├── assets/                 # Textures, fonts, and other static assets
├── shorts_generator/       # Main package code
│   ├── main.py             # Entry point and high-level functions
│   ├── quote_animator.py   # Manim animations for text
│   ├── text_effects.py     # Text styling and effects
│   ├── paper_generator.py  # Paper texture generation
│   └── utils/              # Utility functions
├── temp/                   # Temporary files during generation
└── examples/               # Example outputs and configuration
```

## Advanced Usage

For more advanced customization, you can extend the `OldBookQuoteGenerator` class:

```python
from shorts_generator import OldBookQuoteGenerator

class CustomGenerator(OldBookQuoteGenerator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom initialization
    
    def create_manim_animation(self, output_path):
        # Override with custom animation logic
        pass

# Use your custom generator
generator = CustomGenerator(output_file="custom_style.mp4")
generator.generate()
```

## Dependencies

This project relies on the following major libraries:

- **Manim**: For mathematical animations and text effects
- **MoviePy**: For video editing, composition, and effects
- **Pillow**: For image processing and texture generation
- **NumPy/SciPy**: For numerical operations and advanced effects

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Inspired by the kinetic typography style of educational YouTube channels
- Uses the Mathematical Animation Engine (Manim) created by 3Blue1Brown

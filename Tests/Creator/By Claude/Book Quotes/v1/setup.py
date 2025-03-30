from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="youtube-shorts-generator",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Generate YouTube Shorts videos with animated old book style quotes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/youtube-shorts-generator",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Multimedia :: Video",
        "Topic :: Artistic Software",
    ],
    python_requires=">=3.8",
    install_requires=[
        "manim>=0.17.2",
        "moviepy>=1.0.3",
        "numpy>=1.23.0",
        "scipy>=1.8.0",
        "Pillow>=9.0.0",
        "matplotlib>=3.5.0",
        "tqdm>=4.64.0",
        "pydub>=0.25.1",
    ],
    entry_points={
        "console_scripts": [
            "generate-shorts=shorts_generator.main:cli_main",
        ],
    },
)

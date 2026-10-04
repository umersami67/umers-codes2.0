# Umer Video AI

A local/open-source AI ad-video generator built around Wan video models.

## Features

- Text-to-video ad generation
- Optional reference-image generation for creator/product consistency
- 9:16, 16:9 and 1:1 output
- Fast, Quality and Ultra model presets
- Multi-clip generation and automatic stitching for longer ads
- Optional use of a REAL product screen recording so software UI and text stay accurate
- No per-video API bill when the models run locally

## Important reality check

There is no truly free infinite cloud video generator because video inference costs GPU compute. This project is unlimited only in the sense that the software itself does not charge per generation when you run it on your own machine. Hardware, electricity, storage and model downloads still cost resources.

Model presets:
- Fast: Wan 2.1 T2V 1.3B
- Quality: Wan 2.2 TI2V 5B
- Ultra: Wan 2.2 14B models

Fast is the practical starting point on a consumer GPU. Quality and Ultra need much more VRAM/RAM.

## Install

1. Install Python 3.11.
2. Install FFmpeg and make sure the ffmpeg command works in a terminal.
3. Create a virtual environment.
4. Run: pip install -r requirements.txt
5. Run: python app.py
6. Open http://127.0.0.1:7860

The first generation downloads the selected model from Hugging Face. Model downloads can be many gigabytes.

## Best workflow for software ads such as ALTRA

Do not ask a video model to recreate a complex app interface with exact text. Video models often distort UI and typography.

Generate the creator/environment shots here and use the Product Demo field for a real product screen recording. That keeps the app interface accurate.

## Hardware

- NVIDIA CUDA GPU strongly recommended.
- Fast preset: roughly 8 to 13 GB VRAM depending on offloading and system configuration.
- Quality/Ultra: much heavier; 24 GB or more VRAM or aggressive CPU offload may be required.
- CPU-only mode can run but is usually far too slow for practical video generation.

Normal free CPU web hosting is not suitable for these models. Run locally on an NVIDIA GPU or on a GPU machine you control.

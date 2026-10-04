from __future__ import annotations
import math
import shutil
import subprocess
import tempfile
from pathlib import Path

import torch
from diffusers import WanPipeline, WanImageToVideoPipeline
from diffusers.utils import export_to_video, load_image

MODEL_FAST = "Wan-AI/Wan2.1-T2V-1.3B-Diffusers"
MODEL_QUALITY = "Wan-AI/Wan2.2-TI2V-5B-Diffusers"
MODEL_ULTRA_T2V = "Wan-AI/Wan2.2-T2V-A14B-Diffusers"
MODEL_ULTRA_I2V = "Wan-AI/Wan2.2-I2V-A14B-Diffusers"

_PIPE_CACHE = {}

def _device():
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"

def _dtype():
    device = _device()
    if device == "cuda":
        return torch.bfloat16
    if device == "mps":
        return torch.float16
    return torch.float32

def _size(aspect: str, quality: str):
    if quality == "fast":
        sizes = {"9:16": (432, 768), "16:9": (768, 432), "1:1": (576, 576)}
    else:
        sizes = {"9:16": (480, 832), "16:9": (832, 480), "1:1": (640, 640)}
    return sizes[aspect]

def _load_pipe(quality: str, image_mode: bool):
    key = (quality, image_mode)
    if key in _PIPE_CACHE:
        return _PIPE_CACHE[key]

    if quality == "fast":
        model_id = MODEL_FAST
        pipeline_class = WanPipeline
    elif quality == "quality":
        model_id = MODEL_QUALITY
        pipeline_class = WanImageToVideoPipeline if image_mode else WanPipeline
    else:
        model_id = MODEL_ULTRA_I2V if image_mode else MODEL_ULTRA_T2V
        pipeline_class = WanImageToVideoPipeline if image_mode else WanPipeline

    pipe = pipeline_class.from_pretrained(model_id, torch_dtype=_dtype())

    if _device() == "cuda":
        try:
            pipe.enable_model_cpu_offload()
        except Exception:
            pipe.to("cuda")
    else:
        pipe.to(_device())

    try:
        pipe.vae.enable_tiling()
    except Exception:
        pass

    _PIPE_CACHE[key] = pipe
    return pipe

def _scene_prompt(base: str, index: int, total: int):
    return f"""
{base}

ADVERTISEMENT VIDEO RULES:
Scene {index + 1} of {total}. Maintain the exact same creator, wardrobe, location and product identity.
Photorealistic UGC, natural smartphone footage, realistic skin and hands.
Smooth purposeful motion, no random camera spins.
Preserve brand colors and product appearance from the reference image when supplied.
Do not invent readable interface text. Keep software screens visually simple because the real product recording can be inserted in editing.
No watermarks, unrelated logos, duplicate people, extra fingers, warped objects or beauty-filter skin.
Keep some clean negative space for captions.
"""

def _generate_clip(prompt: str, seconds: int, aspect: str, quality: str, reference_image: str | None, seed: int, output: Path):
    fps = 16
    num_frames = max(17, 4 * max(4, round(seconds * fps / 4)) + 1)
    width, height = _size(aspect, quality)
    generator = torch.Generator(device="cpu").manual_seed(seed)

    image_mode = bool(reference_image) and quality != "fast"
    pipe = _load_pipe(quality, image_mode)

    args = {
        "prompt": prompt,
        "width": width,
        "height": height,
        "num_frames": num_frames,
        "num_inference_steps": 20 if quality == "fast" else 28,
        "guidance_scale": 5.0,
        "generator": generator,
    }

    if image_mode:
        args["image"] = load_image(reference_image)

    frames = pipe(**args).frames[0]
    export_to_video(frames, str(output), fps=fps)

def _concat(clips: list[Path], output: Path):
    if len(clips) == 1:
        shutil.copy2(clips[0], output)
        return

    list_file = output.with_suffix(".txt")
    list_file.write_text("\n".join("file '" + p.as_posix() + "'" for p in clips), encoding="utf-8")
    command = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_file),
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output)
    ]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def _append_product_demo(generated: Path, demo: str, output: Path):
    command = [
        "ffmpeg", "-y",
        "-i", str(generated), "-i", str(demo),
        "-filter_complex",
        "[0:v]scale=720:-2,setsar=1[v0];[1:v]scale=720:-2,setsar=1[v1];[v0][v1]concat=n=2:v=1:a=0[v]",
        "-map", "[v]", "-c:v", "libx264", "-crf", "18",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(output)
    ]
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def generate_ad(prompt: str, duration: int, aspect: str, quality: str, reference_image=None, product_demo=None, seed=42):
    if not prompt.strip():
        raise ValueError("Enter an ad prompt.")
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is required. Install FFmpeg and make sure the ffmpeg command is on PATH.")

    clip_length = 4 if quality == "fast" else 5
    scene_count = max(1, math.ceil(duration / clip_length))
    workdir = Path(tempfile.mkdtemp(prefix="umer_video_ai_"))
    clips = []
    remaining = duration

    try:
        for index in range(scene_count):
            seconds = min(clip_length, remaining)
            remaining -= seconds
            scene_path = workdir / f"scene_{index + 1:02d}.mp4"
            _generate_clip(
                _scene_prompt(prompt, index, scene_count),
                seconds,
                aspect,
                quality,
                reference_image,
                seed + index,
                scene_path,
            )
            clips.append(scene_path)

        joined = workdir / "generated.mp4"
        _concat(clips, joined)

        final = Path(tempfile.gettempdir()) / "umer_video_ai_output.mp4"
        demo_path = None
        if product_demo:
            if isinstance(product_demo, str):
                demo_path = product_demo
            else:
                demo_path = getattr(product_demo, "name", None)

        if demo_path:
            _append_product_demo(joined, demo_path, final)
        else:
            shutil.copy2(joined, final)

        status = (
            f"Done. Preset: {quality}. Device: {_device()}. "
            "Local generation has no per-video API charge, but it still uses your hardware, electricity and storage. "
            "For exact software UI and readable text, use a real screen recording instead of generated UI."
        )
        return str(final), status

    except torch.cuda.OutOfMemoryError:
        raise RuntimeError("GPU memory ran out. Try Fast mode, a shorter video, or stronger hardware.")

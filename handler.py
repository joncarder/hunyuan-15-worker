import runpod
import torch
import os
import base64
import requests
from io import BytesIO
from PIL import Image
import subprocess
import tempfile
import uuid

# Initialize model globally for warm starts
model = None

def init_model():
    global model
    if model is not None:
        return model
    
    from diffusers import HunyuanVideoPipeline
    from diffusers.utils import export_to_video
    
    model_path = "/runpod-volume/models/hunyuan"
    
    pipe = HunyuanVideoPipeline.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
    )
    pipe.to("cuda")
    pipe.enable_model_cpu_offload()
    
    model = pipe
    return model

def handler(job):
    job_input = job["input"]
    
    # Get parameters
    image_url = job_input.get("image_url")
    image_base64 = job_input.get("image_base64")
    prompt = job_input.get("prompt", "A photo comes to life with gentle movement")
    num_frames = job_input.get("num_frames", 49)
    fps = job_input.get("fps", 24)
    width = job_input.get("width", 848)
    height = job_input.get("height", 480)
    num_inference_steps = job_input.get("steps", 8)
    
    # Load image
    if image_url:
        response = requests.get(image_url)
        image = Image.open(BytesIO(response.content)).convert("RGB")
    elif image_base64:
        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data)).convert("RGB")
    else:
        return {"error": "No image provided. Use image_url or image_base64"}
    
    image = image.resize((width, height))
    
    # Initialize model
    pipe = init_model()
    
    # Generate video
    video_frames = pipe(
        prompt=prompt,
        image=image,
        num_frames=num_frames,
        num_inference_steps=num_inference_steps,
        guidance_scale=1.0,
        width=width,
        height=height,
    ).frames[0]
    
    # Save to temp file
    temp_path = f"/tmp/{uuid.uuid4()}.mp4"
    export_to_video(video_frames, temp_path, fps=fps)
    
    # Read and encode as base64
    with open(temp_path, "rb") as f:
        video_base64 = base64.b64encode(f.read()).decode("utf-8")
    
    os.remove(temp_path)
    
    return {
        "video_base64": video_base64,
        "width": width,
        "height": height,
        "num_frames": num_frames,
        "fps": fps
    }

runpod.serverless.start({"handler": handler})

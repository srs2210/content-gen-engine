# services.py
import base64
import os
from datetime import datetime
from typing import Dict, List
import time

# The top-level 'vertexai' import is no longer needed
# import vertexai
from google.cloud import aiplatform
from google.cloud import firestore, storage
from loguru import logger
from models import AspectRatio, Job, JobStatus, Resolution, SocialMediaPlatform
from utils import POST_TEXT_CAPTION_TEMPLATE, generate_platform_specific_instructions
from vertexai.preview.generative_models import GenerativeModel

from google import genai
from google.genai import types


# --- GCP Configuration ---
PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = os.environ.get("LOCATION")
GCS_OUTPUT_BUCKET = os.environ.get("GCS_OUTPUT_BUCKET")
FIRESTORE_ID = os.environ.get("FIRESTORE_ID")
VIDEO_MODEL_NAME = os.environ.get("VIDEO_MODEL_NAME", "veo-3.0-generate-preview")
CAPTION_MODEL_NAME = os.environ.get("CAPTION_MODEL_NAME", "gemini-1.5-flash-001")

genaiClient = genai.Client(
    vertexai=True,
    project=PROJECT_ID,
    location="us-central1",
)

# CHANGE 1: The global vertexai.init() line has been removed.
# vertexai.init(project=PROJECT_ID, location=LOCATION)

storage_client = storage.Client(project=PROJECT_ID)
db = firestore.Client(project=PROJECT_ID, database=FIRESTORE_ID)
jobs_collection = db.collection("videoGenerationJobs")

# --- Services ---
def generate_captions(prompt: str, platforms: List[SocialMediaPlatform]) -> Dict[str, str]:
    logger.info(f"Generating captions for platforms: {[p.value for p in platforms]}")
    captions = {}
    
    # CHANGE 2: The GenerativeModel client is now initialized with its full, explicit path.
    # full_model_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{CAPTION_MODEL_NAME}"
    # model = GenerativeModel(full_model_name)

    for platform in platforms:
        try:
            platform_prompt = POST_TEXT_CAPTION_TEMPLATE.format(user_input=prompt, social_media_platform=platform.value.upper())
            full_prompt = f"{platform_prompt}\n**Instructions**:\n{generate_platform_specific_instructions(platform)}"
            # response = model.generate_content(full_prompt)
            response = genaiClient.models.generate_content(model="gemini-2.5-flash", contents=full_prompt)
            captions[platform.value] = response.text.strip()
        except Exception as e:
            logger.error(f"Failed caption for {platform.value}: {e}")
            captions[platform.value] = f"Error generating caption. Original prompt: {prompt}"
    return captions

def generate_video_from_prompt(prompt: str, duration: int, aspect_ratio: AspectRatio, resolution: Resolution, audio: bool) -> bytes:
    """
    Invokes the video model using the predict_long_running endpoint.
    """
    logger.info(f"Initiating long-running video generation for prompt: '{prompt}'")
    
    # This part is already correct, as it uses the full model path.
    model = aiplatform.Model(f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/{VIDEO_MODEL_NAME}")
    
    instances = [{"prompt": prompt}]
    parameters = {
        "durationSeconds": duration,
        "aspectRatio": aspect_ratio.value,
        "resolution": resolution.value,
        "generateAudio": audio,
        "addWatermark": True
    }

    logger.info("Submitting prediction job...")
    operation = model.predict_long_running(instances=instances, parameters=parameters)
    
    logger.info(f"Waiting for operation {operation.operation.name} to complete...")
    result = operation.result()
    
    logger.success("Prediction job completed.")
    video_b64 = result.predictions[0]['bytesBase64Encoded']
    return base64.b64decode(video_b64)

def generate_veo_video(
    prompt: str,
    duration: int,
    aspect_ratio: AspectRatio,
    resolution: Resolution,
    audio: bool,
) -> bytes:

    logger.info(f"Initiating long-running video generation for prompt: '{prompt}'")

    operation = genaiClient.models.generate_videos(
        model="veo-3.0-generate-preview",
        prompt=prompt,
    )

    logger.info(f"Waiting for operation {operation.name} to complete...")

    # Poll the operation status until the video is ready.
    while not operation.done:
        time.sleep(10)
        operation = genaiClient.operations.get(operation)

    logger.info(f"Operation {operation.name} completed.")

    # Download the generated video.
    generated_video = operation.response.generated_videos[0]
    return generated_video.video.video_bytes

def process_video_generation_job(job_data: dict):
    """The main background task orchestrator."""
    job = Job(**job_data)
    job_ref = jobs_collection.document(job.jobId)
    
    try:
        logger.info(f"Processing job {job.jobId} for user {job.userId}")
        job_ref.update({"status": JobStatus.PROCESSING})

        video_bytes = generate_veo_video(
            prompt=job.prompt,
            duration=job.durationSeconds,
            aspect_ratio=job.aspectRatio,
            resolution=job.resolution,
            audio=job.generateAudio
        )

        bucket = storage_client.bucket(GCS_OUTPUT_BUCKET)
        blob_name = f"videos/{job.userId}/{job.jobId}.mp4"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(video_bytes, content_type="video/mp4")
        video_url = blob.public_url

        captions = generate_captions(job.prompt, job.platforms)
        
        job_ref.update({
            "status": JobStatus.COMPLETED,
            "endTime": datetime.utcnow(),
            "videoUrl": video_url,
            "captions": {p.value: c for p, c in zip(job.platforms, captions.values())}
        })
        logger.success(f"Job {job.jobId} completed.")

    except Exception as e:
        logger.error(f"Job {job.jobId} failed: {e}")
        job_ref.update({
            "status": JobStatus.FAILED,
            "endTime": datetime.utcnow(),
            "error": str(e)
        })

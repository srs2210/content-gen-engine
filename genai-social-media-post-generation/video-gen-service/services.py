# services.py
import os
from datetime import datetime
from typing import Dict, List

import vertexai
from google.cloud import firestore, storage
from loguru import logger
from models import Job, JobStatus, SocialMediaPlatform
from utils import POST_TEXT_CAPTION_TEMPLATE, generate_platform_specific_instructions
from vertexai.preview.generative_models import GenerativeModel

# --- GCP Configuration ---
PROJECT_ID = os.environ.get("PROJECT_ID")
LOCATION = os.environ.get("LOCATION")
GCS_OUTPUT_BUCKET = os.environ.get("GCS_OUTPUT_BUCKET")
FIRESTORE_ID = os.environ.get("FIRESTORE_ID")
VIDEO_MODEL_NAME = os.environ.get("VIDEO_MODEL_NAME", "veo-3.0-generate-001")
CAPTION_MODEL_NAME = os.environ.get("CAPTION_MODEL_NAME", "gemini-1.5-flash-001")

vertexai.init(project=PROJECT_ID, location=LOCATION)
storage_client = storage.Client(project=PROJECT_ID)
db = firestore.Client(project=PROJECT_ID, database=FIRESTORE_ID)
jobs_collection = db.collection("videoGenerationJobs")

# --- Services ---
def generate_captions(prompt: str, platforms: List[SocialMediaPlatform]) -> Dict[str, str]:
    logger.info(f"Generating captions for platforms: {[p.value for p in platforms]}")
    captions = {}
    model = GenerativeModel(CAPTION_MODEL_NAME)
    for platform in platforms:
        try:
            platform_prompt = POST_TEXT_CAPTION_TEMPLATE.format(user_input=prompt, social_media_platform=platform.value.upper())
            full_prompt = f"{platform_prompt}\n**Instructions**:\n{generate_platform_specific_instructions(platform)}"
            response = model.generate_content(full_prompt)
            captions[platform.value] = response.text.strip()
        except Exception as e:
            logger.error(f"Failed caption for {platform.value}: {e}")
            captions[platform.value] = f"Error generating caption. Original prompt: {prompt}"
    return captions

# CHANGE 1: The 'duration_seconds' parameter is removed from this function's signature.
def generate_video_from_prompt(prompt: str) -> bytes:
    """
    Invokes a Vertex AI text-to-video model and returns the video bytes.
    """
    logger.info(f"Initiating video generation with model '{VIDEO_MODEL_NAME}'")
    model = GenerativeModel(VIDEO_MODEL_NAME)
    
    full_prompt = f"{prompt}, cinematic, 8k, professional footage, dynamic motion, 9:16 aspect ratio"
    
    response = model.generate_content([full_prompt])
    
    video_bytes = response.candidates[0].content.data
    logger.success("Successfully generated video from model.")
    return video_bytes

def process_video_generation_job(job_data: dict):
    """The main background task orchestrator."""
    job = Job(**job_data)
    job_ref = jobs_collection.document(job.jobId)
    
    try:
        logger.info(f"Processing job {job.jobId} for user {job.userId}")
        job_ref.update({"status": JobStatus.PROCESSING})

        # CHANGE 2: The call to the function below no longer passes 'job.duration_seconds'.
        video_bytes = generate_video_from_prompt(job.prompt) 

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
            "captions": {p.value: c for p, c in zip(job.platforms, captions.values())} # Ensure keys are strings
        })
        logger.success(f"Job {job.jobId} completed.")

    except Exception as e:
        logger.error(f"Job {job.jobId} failed: {e}")
        job_ref.update({
            "status": JobStatus.FAILED,
            "endTime": datetime.utcnow(),
            "error": str(e)
        })

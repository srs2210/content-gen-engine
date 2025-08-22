# main.py
import os

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from models import Job, JobCreationResponse, VideoGenerationRequest
from services import jobs_collection, process_video_generation_job

load_dotenv()
app = FastAPI(title="Video Generation Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CLIENT_ORIGIN_URL")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generate-video", 
          status_code=status.HTTP_202_ACCEPTED, 
          response_model=JobCreationResponse)
async def create_video_job(request: VideoGenerationRequest, background_tasks: BackgroundTasks):
    """Initiates a video generation job in the background."""
    new_job = Job(**request.model_dump())
    jobs_collection.document(new_job.jobId).set(new_job.model_dump())
    background_tasks.add_task(process_video_generation_job, new_job.model_dump())
    logger.info(f"Job {new_job.jobId} accepted for user {request.userId}.")
    return JobCreationResponse(jobId=new_job.jobId, status=new_job.status)

@app.get("/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """Poll this endpoint to get the status and result of a job."""
    job_doc = jobs_collection.document(job_id).get()
    if not job_doc.exists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    return Job(**job_doc.to_dict())

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Video Generation Service is running."}

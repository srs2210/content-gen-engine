# models.py
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

# This Enum can be part of a shared library later
class SocialMediaPlatform(str, Enum):
    instagram = 'instagram'
    facebook = 'facebook'
    linkedin = 'linkedin'
    x = 'x'
    tiktok = 'tiktok'
    youtube_shorts = 'youtube_shorts'

class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class VideoGenerationRequest(BaseModel):
    """Defines the input for starting a video generation job."""
    prompt: str = Field(..., min_length=10, description="Detailed text prompt for the video.")
    userId: str = Field(..., description="The ID of the user.")
    platforms: List[SocialMediaPlatform] = Field(
        default=[SocialMediaPlatform.instagram],
        description="Platforms to generate captions for."
    )
    # The duration_seconds field has been fully removed.

class Job(BaseModel):
    """Represents a video generation job stored in Firestore."""
    jobId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: JobStatus = JobStatus.PENDING
    userId: str
    prompt: str
    platforms: List[SocialMediaPlatform]
    # The duration_seconds field has been fully removed.
    requestTime: datetime = Field(default_factory=datetime.utcnow)
    endTime: Optional[datetime] = None
    videoUrl: Optional[str] = None
    captions: Optional[Dict[SocialMediaPlatform, str]] = None
    error: Optional[str] = None

class JobCreationResponse(BaseModel):
    """The immediate response after submitting a video generation request."""
    jobId: str
    status: JobStatus

# models.py
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field

# --- Enums for API parameters ---
class AspectRatio(str, Enum):
    PORTRAIT = "9:16"
    LANDSCAPE = "16:9"
    SQUARE = "1:1"

class Resolution(str, Enum):
    SD = "480p"
    HD = "720p"
    FHD = "1080p"

# --- Core Models (unchanged) ---
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

# --- Updated Request and Job Models ---
class VideoGenerationRequest(BaseModel):
    """Defines the input for starting a video generation job."""
    prompt: str = Field(..., min_length=10, description="Detailed text prompt for the video.")
    userId: str = Field(..., description="The ID of the user.")
    platforms: List[SocialMediaPlatform] = Field(
        default=[SocialMediaPlatform.instagram],
        description="Platforms to generate captions for."
    )
    # New parameters to match the working API call
    durationSeconds: int = Field(default=8, ge=2, le=59, description="Video duration in seconds.")
    aspectRatio: AspectRatio = Field(default=AspectRatio.PORTRAIT, description="Aspect ratio of the video.")
    resolution: Resolution = Field(default=Resolution.HD, description="Resolution of the video.")
    generateAudio: bool = Field(default=True, description="Whether to generate audio for the video.")

class Job(BaseModel):
    """Represents a video generation job stored in Firestore."""
    jobId: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: JobStatus = JobStatus.PENDING
    userId: str
    prompt: str
    platforms: List[SocialMediaPlatform]
    # New parameters are now stored in the job
    durationSeconds: int
    aspectRatio: AspectRatio
    resolution: Resolution
    generateAudio: bool
    requestTime: datetime = Field(default_factory=datetime.utcnow)
    endTime: Optional[datetime] = None
    videoUrl: Optional[str] = None
    captions: Optional[Dict[SocialMediaPlatform, str]] = None
    error: Optional[str] = None

class JobCreationResponse(BaseModel):
    """The immediate response after submitting a video generation request."""
    jobId: str
    status: JobStatus

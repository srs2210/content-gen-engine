"""
 Copyright 2024 Google LLC

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      https://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 """

from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime
from enum import Enum


# Enum for Request Status
class RequestStatus(str, Enum):
    pending = 'pending'
    completed = 'completed'
    evaluating = 'evaluating'
    error = 'error'

class AspectRatio(str, Enum):
    square = 'square'
    full_image = 'full_image'
    vertical = 'vertical'
    plain_square = 'plain_square'

class SocialMediaPlatform(str, Enum):
    instagram = 'instagram'
    facebook = 'facebook'
    linkedin = 'linkedin'
    x = 'x'

# Model for RequestConfig
class RequestConfig(BaseModel):
    requestTitle: str
    postDescription: str
    aspectRatio: AspectRatio
    artStyle: str
    subject: str
    backgroundColor: Optional[str] = Field(default=None)
    signOff: str
    isRecruitmentRelated: bool
    isCharityRelated: bool
    postCount: int
    socialMediaPlatform: Optional[SocialMediaPlatform] = Field(default=None)

# Model for Users
class User(BaseModel):
    userId: str
    name: str
    email: str
    pin: str
    createdAt: datetime
    signOff: str


# Model for Request
class Request(BaseModel):
    userId: str
    requestId: str
    requestConfig: RequestConfig
    requestDate: datetime
    status: RequestStatus
    originalRequestId: Optional[str] = Field(default=None)  # Optional field for edit


# Model for Posts
class PostStatus(str, Enum):
    replaced = 'replaced'
    original = 'original'


class EvaluationStatus(str, Enum):
    pending = 'pending'
    passed = 'passed'
    failed = 'failed'
    error = 'error'
    completed = 'completed'

class PostVote(int, Enum):
    upvote = 1
    novote = 0
    downvote = -1

class EvaluationReport(BaseModel):
    content_accuracy_and_balance_check: Optional[dict] = Field(default=None)
    factual_completeness_check: Optional[dict] = Field(default=None)
    representative_specific_prohibited_content_check: Optional[dict] = Field(default=None)
    prohibited_content_check: Optional[dict] = Field(default=None)
    job_title_check: Optional[dict] = Field(default=None)
    disclaimer_and_signoff_check: Optional[dict] = Field(default=None)
    charity_reference_check: Optional[dict] = Field(default=None)
    recruitment_compliance_check: Optional[dict] = Field(default=None)
    image_quality_check: Optional[dict] = Field(default=None)

class Post(BaseModel):
    userId: str
    generatedImageUrl: str
    finalImageUrl: str
    postCreationTime: datetime
    postId: str
    requestId: str
    postStatus: PostStatus = Field(default=PostStatus.original)
    postVote: PostVote = Field(default=PostVote.novote)
    evaluationStatus: EvaluationStatus = Field(default=EvaluationStatus.pending)
    evaluationOutcome: Optional[Literal["pass", "fail"]] = Field(default=None)
    evaluationReport: Optional[EvaluationReport] = Field(default=None)
    postCaption: Optional[str] = Field(default=None)

# Model for positionConfig
class PositionConfig(BaseModel):
    height: int
    width: int
    x: int
    y: int


# Model for Templates
class BackgroundSize(BaseModel):
    height: int
    width: int


class Template(BaseModel):
    templateName: str
    actorPosition: PositionConfig
    logoPosition: PositionConfig
    textDetailsPosition: PositionConfig
    textHeader1Position: PositionConfig
    textActionPosition: PositionConfig
    textTaglinePosition: PositionConfig
    backgroundSize: BackgroundSize

class LoginRequest(BaseModel):
    email: str
    pin: str

class GeneratePostRequest(BaseModel):
    userId: str
    requestConfig: RequestConfig

class RunGenerationPipelineRequest(BaseModel):
    requestId: str
    userId: str
    requestConfig: RequestConfig

class RunGenerationPipelineResponse(BaseModel):
    success: bool

class GeneratePostResponse(BaseModel):
    requestId: str

class GeneratedResultsRequest(BaseModel):
    userId: str
    requestId: str

class GeneratedResultsResponse(BaseModel):
    requestStatus: str
    posts: List[Post]

class AllRequestsResponse(BaseModel):
    requests: List[Request]

class LoginResponse(BaseModel):
    userId: str
    signOff: str
    name: str

class AllRequestsPayload(BaseModel):
    userId: str

class UpdateUserSignOffRequest(BaseModel):
    userId: str
    signOff: str
    isSignOffRemembered: bool

class UpdateUserSignOffResponse(BaseModel):
    success: bool

class UpdatePostVoteRequest(BaseModel):
    userId: str
    postId: str
    vote: PostVote

class UpdatePostVoteResponse(BaseModel):
    success: bool

class DownloadImageRequest(BaseModel):
    userId: str
    postId: str

class UpdateRequestStatusRequest(BaseModel):
    userId: str
    requestId: str
    status: RequestStatus

class UpdateRequestStatusResponse(BaseModel):
    success: bool

class EvaluatePostResponse(BaseModel):
    requestId: str
    message: str
    gcsImagePath: str
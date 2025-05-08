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

from fastapi import FastAPI, HTTPException, BackgroundTasks, File, Form, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from middlewares.tracker import TrackerMiddleware
from middlewares.user_validation import UserValidationMiddleware
from utils.types import AllRequestsPayload, AllRequestsResponse, DownloadImageRequest, EvaluationStatus, GeneratePostRequest, GeneratePostResponse, GeneratedResultsRequest, GeneratedResultsResponse, LoginResponse, RequestStatus, RunGenerationPipelineRequest, UpdatePostVoteRequest, UpdatePostVoteResponse, UpdateRequestStatusRequest, UpdateRequestStatusResponse, UpdateUserSignOffRequest, UpdateUserSignOffResponse, EvaluatePostResponse  # Import the RequestConfig and Post models
from service.firestore import firestore_service
from utils.types import LoginRequest, RequestConfig, AspectRatio  # Import the LoginRequest model
from utils.commons import add_signed_url_to_posts
from background_scripts.content_generation_pipeline import generate_posts_background, add_post_to_db, Post, PostStatus, PostVote
from service.cloud_storage import cs_service
from fastapi.responses import Response
from service.pubsub import pubsub_service
from utils.constants import GCS_INPUT_BUCKET_ROOT, GCS_USER_EVAL_UPLOADS_PREFIX, GCS_OUTPUT_DIR_POSTS, MAX_IMAGE_UPLOAD_SIZE_MB
from google.cloud import storage
import os
from datetime import datetime
from loguru import logger

app = FastAPI()
"""Middleware order is from bottom to top"""
# user_validation_middleware = UserValidationMiddleware()
app.add_middleware(TrackerMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(UserValidationMiddleware)

@app.post("/v1/evaluate-post", response_model=EvaluatePostResponse)
async def evaluate_post(
    userId: str = Form(...), caption: str = Form(...), file: UploadFile = File(...)
):  
    logger.info(f"Processing evaluate-post for userId: {userId}, caption: {caption}, file: {file.filename}")
    
    if not userId:
        raise HTTPException(status_code=401, detail="Unauthorized: userId is required")
    user = await firestore_service.get_user(userId)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized: userId is invalid")

    try:
        # Create the request object
        request_config = RequestConfig(
            requestTitle=f"Evaluation for {userId} - {file.filename}",
            postDescription=caption,
            aspectRatio=AspectRatio.full_image,
            artStyle="Photorealistic",
            subject="",
            signOff="John Vu",
            isRecruitmentRelated=False,
            isCharityRelated=False,
            postCount=0,
        )
        request_id = await firestore_service.create_request(userId, request_config)
        logger.info(f"Request ID created: {request_id}")

        # Upload image to GCS
        project_id = os.environ.get("PROJECT_ID")
        root_bucket = GCS_INPUT_BUCKET_ROOT
        destination_blob_name = (
            f"{GCS_OUTPUT_DIR_POSTS}/{GCS_USER_EVAL_UPLOADS_PREFIX}-{request_id}-{file.filename}"
        )

        storage_client = storage.Client(project=project_id)
        bucket = storage_client.bucket(root_bucket)
        blob = bucket.blob(destination_blob_name)
        blob.upload_from_file(file.file)
        gcs_url = f"gs://{GCS_INPUT_BUCKET_ROOT}/{destination_blob_name}"

        # Create post object
        post = Post(
            userId=userId,
            generatedImageUrl="",
            postCreationTime=datetime.now(),
            requestId=request_id,
            postStatus=PostStatus.original,
            postVote=PostVote.novote,
            evaluationStatus=EvaluationStatus.pending,
            finalImageUrl=gcs_url,
            postCaption=caption,
        )
        add_post_to_db(post)
        
        logger.info(f"Post object created for requestId: {request_id}")

        # Return the reponse
        return EvaluatePostResponse(
            requestId=request_id,
            message="Evaluation Post File uploaded successfully",
            gcsImagePath=gcs_url,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {e}",
        )

@app.post("/v1/generate-post", response_model=GeneratePostResponse)
async def generate_post(generate_post_payload: GeneratePostRequest, background_tasks: BackgroundTasks):
    request_id = await firestore_service.create_request(generate_post_payload.userId, generate_post_payload.requestConfig) 
    print(f"Starting background generation pipeline for request_id: {request_id}")
    background_tasks.add_task(
        generate_posts_background,
        request_id,
        generate_post_payload.userId,
        generate_post_payload.requestConfig.model_dump()
    )
    return GeneratePostResponse(requestId=request_id)

@app.post("/v2/generate-post", response_model=GeneratePostResponse)
async def generate_post(generate_post_payload: GeneratePostRequest):
    request_id = await firestore_service.create_request(generate_post_payload.userId, generate_post_payload.requestConfig) 
    print(f"Starting background generation pipeline for request_id: {request_id}")
    await pubsub_service.publish_message(
        topic_name="content-generation-v1",
        message_data={"requestId": request_id, "userId": generate_post_payload.userId, "requestConfig": generate_post_payload.requestConfig.model_dump()}
    )
    return GeneratePostResponse(requestId=request_id)



@app.post("/v2/generated-results", response_model=GeneratedResultsResponse)
async def generated_results(generated_results_request: GeneratedResultsRequest):
    request = await firestore_service.get_request(generated_results_request.requestId)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    if request.userId != generated_results_request.userId:
        raise HTTPException(status_code=403, detail="User does not have access to this request")
    posts, error_count = await firestore_service.get_posts_by_request_id(generated_results_request.requestId)
    posts = add_signed_url_to_posts(posts)
    if request.status == RequestStatus.completed:
        return GeneratedResultsResponse(requestStatus=request.status, posts=posts)
    print(f"request: {generated_results_request.requestId}, len(posts): {len(posts)}, request_post_count: {request.requestConfig.postCount}, error_count: {error_count}")

    #update request status to completed if all posts are evaluated
    request_post_count = request.requestConfig.postCount
    if len(posts) >= request_post_count - error_count and all(post.evaluationStatus != EvaluationStatus.pending for post in posts):
        request.status = RequestStatus.completed
        await firestore_service.update_request(generated_results_request.requestId, request)
        return GeneratedResultsResponse(requestStatus=request.status, posts=posts)
    
    request_status = request.status
    return GeneratedResultsResponse(requestStatus=request_status, posts=posts)

@app.post("/v1/requests-by-user-id", response_model=AllRequestsResponse)
async def requests_by_user_id(all_requests_payload: AllRequestsPayload):
    requests = await firestore_service.get_requests_by_user_id(all_requests_payload.userId)
    return AllRequestsResponse(requests=requests)

@app.get("/v1/health")
async def v1_health():
    return {"health": "ok"}

@app.post("/v1/login", response_model=LoginResponse)
async def login(login_request: LoginRequest):
    user = await firestore_service.get_user_by_email_and_pin(login_request.email, login_request.pin)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or pin")
    return LoginResponse(userId=user.userId, signOff=user.signOff, name=user.name)

@app.post("/v1/update-user-sign-off", response_model=UpdateUserSignOffResponse)
async def update_user_sign_off(update_user_sign_off_request: UpdateUserSignOffRequest):
    result = await firestore_service.update_user_sign_off(update_user_sign_off_request.userId, update_user_sign_off_request.signOff, update_user_sign_off_request.isSignOffRemembered)
    return UpdateUserSignOffResponse(success=result)

@app.post("/v1/update-post-vote", response_model=UpdatePostVoteResponse)
async def update_post_vote(update_post_vote_request: UpdatePostVoteRequest):
    result = await firestore_service.update_post_vote(update_post_vote_request.postId, update_post_vote_request.vote)
    return UpdatePostVoteResponse(success=result)

@app.post("/v1/download-image")
async def download_image(download_image_request: DownloadImageRequest):
    # Verify user has access to the post
    post = await firestore_service.get_post(download_image_request.postId)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.userId != download_image_request.userId:
        raise HTTPException(status_code=403, detail="User does not have access to this post")
    
    # Extract bucket and file path from the gs:// URL
    gs_url = post.finalImageUrl
    if not gs_url.startswith("gs://"):
        raise ValueError("Invalid gs:// URL")
    
    path_parts = gs_url[5:].split("/", 1)  # Remove 'gs://' and split
    bucket_name = path_parts[0]
    blob_name = path_parts[1] if len(path_parts) > 1 else ""
    
    # Download the image using existing method
    image_data = cs_service.download_blob_as_bytes(bucket_name, blob_name)
    
    return Response(
        content=image_data,
        media_type="image/png",
        headers={
            "Content-Disposition": f'attachment; filename="post-{download_image_request.postId}.png"'
        }
    )

@app.post("/v1/update-request-status", response_model=UpdateRequestStatusResponse)
async def update_request_status(update_request_status_request: UpdateRequestStatusRequest):
    request = await firestore_service.get_request(update_request_status_request.requestId)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    if request.userId != update_request_status_request.userId:
        raise HTTPException(status_code=403, detail="User does not have access to this request")
    result = await firestore_service.update_request_status(update_request_status_request.requestId, update_request_status_request.status)
    return UpdateRequestStatusResponse(success=result)
import uvicorn
if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
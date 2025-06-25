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

# TODO(dagadeepansh): updated imports
from requests import Response
from fastapi import HTTPException, UploadFile, status
from utils.constants import MAX_IMAGE_UPLOAD_SIZE_MB
from service.firestore import firestore_service
from loguru import logger
import os


def validate_response_succeeds(response: Response):
    if response.status_code not in [200, 201]:
        raise HTTPException(
            status_code=response.status_code, detail=str(response.content)
        )

# TODO(dagadeepansh): new validator
async def validate_eval_post_request(userId: str, caption: str, file: UploadFile):
    # Validate user ID
    user = await firestore_service.get_user(userId)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized: userId is invalid")

    # Validate file upload size
    _ = await file.seek(0, os.SEEK_END)
    file_size = await file.tell()
    await file.seek(0)

    MAX_UPLOAD_SIZE_BYTES = MAX_IMAGE_UPLOAD_SIZE_MB * 1024 * 1024

    if file_size > MAX_UPLOAD_SIZE_BYTES:
        logger.warning(f"Upload attempt failed for user '{userId}': File size {file_size} exceeds limit {MAX_IMAGE_UPLOAD_SIZE_MB}MB.")
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds the limit of {MAX_IMAGE_UPLOAD_SIZE_MB}MB."
        )

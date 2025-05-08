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

# TODO: updated imports
from service.cloud_storage import cs_service
from utils.types import Post
from typing import List
import concurrent.futures
from fastapi import UploadFile
from utils.constants import GCS_INPUT_BUCKET_ROOT, PROJECT_ID
from google.cloud import storage

def add_signed_url_to_posts(posts: List[Post]):
    print("adding signed url to posts")
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(cs_service.generate_signed_url_with_impersonation, post.finalImageUrl) for post in posts]
        for future in concurrent.futures.as_completed(futures):
            post = posts[futures.index(future)]
            post.finalImageUrl = future.result()
    # synchrous implementation
    # for post in posts:
    #     post.finalImageUrl = cs_service.generate_signed_url_with_impersonation(post.finalImageUrl)
    return posts

# TODO: new helper method
def upload_file_to_gcs(file: UploadFile, destination_blob_name: str) -> str:
    """Helper function to upload a file to Google Cloud Storage."""
    project_id = PROJECT_ID
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(GCS_INPUT_BUCKET_ROOT)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(file.file)
    return f"gs://{GCS_INPUT_BUCKET_ROOT}/{destination_blob_name}"

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

import base64
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
import json
import shutil
from google.cloud import firestore
from pydantic import BaseModel, Field
from vertexai.generative_models import GenerativeModel, Part
from loguru import logger
from datetime import datetime
import os
from enum import Enum
from google.cloud import storage
import time
from prompts_config import CONTENT_ACCURACY_AND_BALANCE_PROMPT, FACTUAL_COMPLETENESS_CHECK_PROMPT, REPRESENTATIVE_SPECIFIC_PROHIBITED_CONTENT_CHECK, PROHIBITED_CONTENT_CHECK, JOB_TITLE_CHECK_PROMPT, DISCLAIMER_AND_SIGNOFF_CHECK, CHARITY_REFERENCE_CHECK, RECRUITMENT_COMPLIANCE_CHECK, IMAGE_QUALITY_CHECK_PROMPT

# --- GCP Project Configuration ---
PROJECT_ID = os.environ.get("PROJECT_ID")
PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER")
FIRESTORE_INSTANCE_ID = "(default)"
db = firestore.Client(project=PROJECT_ID, database=FIRESTORE_INSTANCE_ID)

# --- GCS Bucket Configuration ---
# GCS_INPUT_BUCKET_ROOT = "marketing_content_generation_inputs"
GCS_INPUT_BUCKET_ROOT = "1003801603843_marketing_content_generation_inputs"
GCS_INPUT_BUCKET = f"{PROJECT_NUMBER}_{GCS_INPUT_BUCKET_ROOT}"
GCS_OUTPUT_DIR_POSTS = f"Artefacts/Final_Posts"
LOCAL_TEMP_DIR = "/tmp"  # Use /tmp for Cloud Functions

# Collection references
collection_posts = db.collection("posts")


class PostVote(int, Enum):
    upvote = 1
    novote = 0
    downvote = -1


class PostStatus(str, Enum):
    replaced = "replaced"
    original = "original"


class EvaluationStatus(str, Enum):
    pending = "pending"
    passed = "passed"
    failed = "failed"
    error = "error"
    completed = "completed"


class Post(BaseModel):
    userId: str
    generatedImageUrl: str
    postCreationTime: datetime
    requestId: str
    postStatus: PostStatus = Field(default=PostStatus.original)
    postVote: PostVote = Field(default=PostVote.novote)
    evaluationStatus: EvaluationStatus = Field(default=EvaluationStatus.pending)
    postCaption: str
    finalImageUrl: str
    postId: str

def download_blob(bucket_name, source_blob_name, destination_file_name, project_id):
    """Downloads a blob from the bucket."""
    # bucket_name = "your-bucket-name"
    # source_blob_name = "storage-object-name"
    # destination_file_name = "local/path/to/file"

    storage_client = storage.Client(project=project_id)

    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print(
        f"Downloaded storage object {source_blob_name} from bucket {bucket_name} to local file {destination_file_name}"
    )


def download_to_local_folder_from_gcs_bucket(
    bucket_name, file_name, local_folder, project_id
):
    try:
        local_file_path = os.path.join(local_folder, file_name)
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        download_blob(bucket_name, file_name, local_file_path, project_id)
    except Exception as e:
        print(f"An error occurred while downloading file from GCS: {e}")


def evaluate_post_by_image_path(image_path, post_caption):
    """
    Evaluates a post image using the Gemini API via Vertex AI.

    Args:
        image: path to image

    Returns:
        A dictionary containing the compliance report and evaluation outcome.
    """
    try:
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

        image = Part.from_data(
            mime_type="image/png", data=base64.b64decode(encoded_image)
        )

        model = GenerativeModel(
            "gemini-2.5-pro",
        )
        generation_config = {
            "max_output_tokens": 8192,
            "temperature": 1,
            "top_p": 0.95,
            "response_mime_type": "application/json",
        }
        prompts_dict = {
            "content_accuracy_and_balance_check": CONTENT_ACCURACY_AND_BALANCE_PROMPT,
            "factual_completeness_check": FACTUAL_COMPLETENESS_CHECK_PROMPT,
            "representative_specific_prohibited_content_check": REPRESENTATIVE_SPECIFIC_PROHIBITED_CONTENT_CHECK,
            "prohibited_content_check": PROHIBITED_CONTENT_CHECK,
            "job_title_check": JOB_TITLE_CHECK_PROMPT,
            "disclaimer_and_signoff_check": DISCLAIMER_AND_SIGNOFF_CHECK,
            "charity_reference_check": CHARITY_REFERENCE_CHECK,
            "recruitment_compliance_check": RECRUITMENT_COMPLIANCE_CHECK,
            "image_quality_check": IMAGE_QUALITY_CHECK_PROMPT,
        }
        compliance_report = {}
        overall_compliance_outcome = "pass"

        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(
                    model.generate_content,
                    [image, post_caption, prompt_text],
                    generation_config=generation_config,
                )
                for prompt_text in prompts_dict.values()
            ]
            responses = [future.result() for future in futures]

            for prompt_name, response in zip(prompts_dict.keys(), responses):
                json_for_print = json.loads(response.text)
                compliance_report[prompt_name] = json_for_print
                if (
                    prompt_name == "image_quality_check"
                    or prompt_name == "factual_completeness_check"
                ):
                    continue
                if overall_compliance_outcome == "pass":
                    for _, response in json_for_print.items():
                        if (
                            "outcome" in response
                            and response["outcome"] == "non-compliant"
                        ):
                            overall_compliance_outcome = "fail"
                            break
                        elif (
                            "outcome" in json_for_print
                            and json_for_print["outcome"] == "non-compliant"
                        ):
                            overall_compliance_outcome = "fail"
                            break
                json_print_string = json.dumps(json_for_print, indent=2)
                print(json_print_string)

        return {
            "compliance_report": compliance_report,
            "overall_compliance_outcome": overall_compliance_outcome,
        }

    except Exception as e:
        print(f"Error during evaluation: {e}")
        return {
            "compliance_report": "Error during evaluation",
            "overall_compliance_outcome": "N/A",
        }


# --- Cloud Function Entry Point ---


def retry_on_failure(max_retries=3, delay=4):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        logger.error(
                            f"Failed after {max_retries} attempts. Final error: {e}"
                        )
                        raise e
                    logger.warning(
                        f"Attempt {retries} failed. Retrying in {delay} seconds... Error: {e}"
                    )
                    time.sleep(delay * (2 ** (retries - 1)))  # Exponential backoff
                    # Clean up any partial results before retrying
                    if os.path.exists(LOCAL_TEMP_DIR):
                        for item in os.listdir(LOCAL_TEMP_DIR):
                            item_path = os.path.join(LOCAL_TEMP_DIR, item)
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path)

        return wrapper

    return decorator


@retry_on_failure(max_retries=3, delay=5)
def process_new_document(data, context) -> None:
    start_time = datetime.now()

    path_parts = context.resource.split("/documents/")[1].split("/")
    collection_path = path_parts[0]
    document_path = "/".join(path_parts[1:])

    affected_doc = db.collection(collection_path).document(document_path)

    start_time = datetime.now()
    logger.info(f"Evaluating post {affected_doc.id}")

    try:
        # Step 1: Extract details from the post document
        new_post = affected_doc.get().to_dict()
        new_post["postId"] = affected_doc.id
        new_post = Post(**new_post)

        final_image_url = new_post.finalImageUrl
        download_to_local_folder_from_gcs_bucket(
            GCS_INPUT_BUCKET_ROOT,
            f"Artefacts/Final_Posts/{final_image_url.split('/')[-1]}",
            LOCAL_TEMP_DIR,
            PROJECT_ID,
        )

        MAX_RETRIES = 3
        retries = 0
        while retries < MAX_RETRIES:
            # Step 2: Evaluate post by making calls to Gemini API
            evaluation_result = evaluate_post_by_image_path(
                os.path.join(
                    LOCAL_TEMP_DIR,
                    f"Artefacts/Final_Posts/{final_image_url.split('/')[-1]}",
                ),
                new_post.postCaption,
            )
            if (
                evaluation_result["overall_compliance_outcome"] != "N/A"
                and evaluation_result["compliance_report"] != "Error during evaluation"
            ):
                break
            retries += 1

        # Step 3: Update post with evaluation result
        collection_posts.document(new_post.postId).update(
            {
                "evaluationReport": evaluation_result["compliance_report"],
                "evaluationOutcome": evaluation_result["overall_compliance_outcome"],
                "evaluationStatus": (
                    "completed"
                    if evaluation_result["overall_compliance_outcome"] != "N/A"
                    else "error"
                ),
            }
        )

        # ... Clean up local storage for cloud function
        if os.path.exists(LOCAL_TEMP_DIR):
            for item in os.listdir(LOCAL_TEMP_DIR):
                item_path = os.path.join(LOCAL_TEMP_DIR, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            logger.info(f"cleaned up local storage for cloud function")

        logger.info(
            f"Post {new_post.postId} evaluated with status: {evaluation_result['overall_compliance_outcome']}"
        )
        logger.info(f"Evaluation time: {datetime.now() - start_time}")

    except Exception as e:
        logger.error(f"An error occurred while evaluating post {affected_doc.id}: {e}")
        raise e

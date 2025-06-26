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

from concurrent.futures import ThreadPoolExecutor
from enum import Enum
from functools import wraps
import os
import shutil
import json
import base64
import io
import datetime
import time
from typing import List, Literal, Optional
from google.cloud import firestore
from google.cloud import storage
from pydantic import BaseModel, Field
from rembg import remove, new_session
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from string import ascii_letters
from vertexai.generative_models import (
    GenerativeModel,
)
from vertexai.preview.vision_models import ImageGenerationModel
from loguru import logger
from datetime import datetime
from cloudevents.http import CloudEvent
import functions_framework
from google.events.cloud import firestore as firestoredata


# --- GCP Project Configuration ---
PROJECT_ID = os.environ.get("PROJECT_ID")
PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER")
FIRESTORE_INSTANCE_ID = "(default)"
db = firestore.Client(project=PROJECT_ID, database=FIRESTORE_INSTANCE_ID)

# --- GCS Bucket Configuration ---
GCS_INPUT_BUCKET_ROOT = "1003801603843_marketing_content_generation_inputs"
GCS_INPUT_BUCKET = f"{PROJECT_NUMBER}_{GCS_INPUT_BUCKET_ROOT}"

GCS_INPUT_DIR_ACTOR = f"Artefacts/Actors"
GCS_INPUT_DIR_TEMPLATES = f"Artefacts/Background"

GCS_OUTPUT_DIR_ACTOR = f"Artefacts/Actors_Processed"
GCS_OUTPUT_DIR_BG = f"Artefacts/Background_Processed"
GCS_OUTPUT_DIR_POSTS = f"Artefacts/Final_Posts"
GCS_OUTPUT_DIR_GENERATED_IMAGES = f"Artefacts/Generated_Images"

# --- Local Directory Configuration (for Cloud Functions, these will be temp directories) ---

LOCAL_TEMP_DIR = "/tmp"  # Use /tmp for Cloud Functions
# LOCAL_TEMP_DIR = "/Users/dsalomone/Documents/Projects/social-media-post-generation/fastapi-backend/tmp"
LOCAL_INPUT_DIR_FONTS = f"{LOCAL_TEMP_DIR}/Artefacts/Fonts"  # Subdirectory under /tmp
LOCAL_INPUT_DIR_GRAPHICS = (
    f"{LOCAL_TEMP_DIR}/Artefacts/Graphics"  # Subdirectory under /tmp
)

# Class Definitions


class RequestStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    evaluating = "evaluating"
    error = "error"


class AspectRatio(str, Enum):
    square = "square"
    full_image = "full_image"
    vertical = "vertical"


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


class Request(BaseModel):
    userId: str
    requestId: str
    requestConfig: RequestConfig
    requestDate: datetime
    status: RequestStatus
    originalRequestId: Optional[str] = Field(default=None)


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


class EvaluationReport(BaseModel):
    content_accuracy_and_balance_check: Optional[dict] = Field(default=None)
    factual_completeness_check: Optional[dict] = Field(default=None)
    representative_specific_prohibited_content_check: Optional[dict] = Field(
        default=None
    )
    prohibited_content_check: Optional[dict] = Field(default=None)
    job_title_check: Optional[dict] = Field(default=None)
    disclaimer_and_signoff_check: Optional[dict] = Field(default=None)
    charity_reference_check: Optional[dict] = Field(default=None)
    recruitment_compliance_check: Optional[dict] = Field(default=None)


class Post(BaseModel):
    userId: str
    generatedImageUrl: str
    postCreationTime: datetime
    requestId: str
    postCaption: str
    postStatus: PostStatus = Field(default=PostStatus.original)
    postVote: PostVote = Field(default=PostVote.novote)
    evaluationStatus: EvaluationStatus = Field(default=EvaluationStatus.pending)
    finalImageUrl: str
    evaluationOutcome: Optional[Literal["pass", "fail"]] = Field(default=None)
    evaluationReport: Optional[EvaluationReport] = Field(default=None)


class PositionConfig(BaseModel):
    height: int
    width: int
    x: int
    y: int


# Model for Templates
class BackgroundSize(BaseModel):
    height: int
    width: int


class Layout(BaseModel):
    layoutName: str
    actorPosition: Optional[PositionConfig] = Field(default=None)
    textDetailsPosition: Optional[PositionConfig] = Field(default=None)
    textHeader1Position: Optional[PositionConfig] = Field(default=None)
    textActionPosition: Optional[PositionConfig] = Field(default=None)
    textTaglinePosition: Optional[PositionConfig] = Field(default=None)
    backgroundSize: BackgroundSize


class Template(BaseModel):
    templateName: str
    layouts: List[Layout]


# --- Firestore Functions ---
collection_post_template = db.collection("post_template")
collection_posts = db.collection("posts")
collection_requests = db.collection("requests")


def get_post_template_by_name(template_name: str) -> Template:
    try:
        template = collection_post_template.document(template_name).get()
        template_dict = template.to_dict()
        return Template(**template_dict) if template_dict else None
    except Exception as e:
        logger.error(f"An error occurred while retrieving post template: {e}")
        return None


def add_post_to_db(post: Post) -> None:
    try:
        collection_posts.add(post.model_dump())
    except Exception as e:
        logger.error(f"An error occurred while adding post to db: {e}")

def update_request_in_db(request_id: str, requestConfig: RequestConfig, countOfImagesGenerated: int) -> None:
    logger.info(f"Updating post count in request {request_id} in db to {countOfImagesGenerated}")
    requestConfig["postCount"] = countOfImagesGenerated
    try:
        collection_requests.document(request_id).set({"requestConfig": requestConfig}, 
            merge=True)
    except Exception as e:
        logger.error(f"An error occurred while updating request in db: {e}")

# Prompt Definitions

IMAGE_GENERATION_INPUT_PARAMS_GENERATION_PROMPT = """
**User Input:** {user_input}

You are a skilled social media director and you are tasked to determine the best visual asset that accompanies a social media post.
Based on the user input provided above, determine the appropriate description for the subject, age of the subject, clothing that the subject should wear and theme (what subject is doing).
If the subject is an inanimate object, then the age and clothing should be "not applicable".

The concept for the image should be simple and impactful, and should not involve too much detail.

Your inputs will be used by a content creation team to produce a high quality image to accompany the social media post.

Example output:
{{
    subject: "a vibrant Indonesian woman",
    age: "age 40-50 years old",
    clothing: "wearing a traditional Balinese dress",
    theme: "enjoying movie on her phone screen wearing red headphones"
}}

{{
    subject: "an ice cream cone",
    age: "not applicable",
    clothing: "not applicable",
    theme: "ice cream with wafer cone and chocolate drizzle, on a sunny day"
}}

Generate the copy in the following JSON format:

{{
  subject: string,
  age: string,
  clothing: string,
  theme: string
}}

Provide your output in English.
"""

PREPROCESSING_PROMPT_FOR_IMAGEN_PROMPT = """
Post Description: {post_description}
the main actor or item shown in the post is {subject}
"""

NEGATIVE_PROMPT_FOR_IMAGEN = "((((ugly)))), (((duplicate))), ((morbid)), ((mutilated)), swimsuit, gambling, smoking, cigarettes, vapes, text, drugs, alchohol, out of frame, extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((text))), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck)))"

POST_TEXT_PROMPT_TEMPLATE = """

**User Input:** {user_input}

**Copy Text Generation Instructions:**

You are tasked to write the copy for a flyer for distribution on social media. The flyer should be catchy, engaging with right motivation.

The text content should embody Prudential's brand voice and adhere to the following principles:

**1. Human Benefit/Relatable Truth:**

* Lead with a clear human benefit or relatable truth relevant to the target audience.  For example, instead of "Park cleanup this Saturday," try framing it around the benefit, such as creating a healthier community space.
* If mentioning a Prudential product/service (only if directly relevant to the user input), present the human benefit *before* any product features.  Avoid exaggerating benefits.

**2. Prudential Brand Voice and Tone:**

* Employ a warm, inviting, and intuitive tone. Encourage engagement and conversation (e.g., asking a question or suggesting an action).
* Foster a sense of partnership and collaboration.
* Use simple, direct language, avoiding jargon and technical terms.  Maintain a friendly, cheerful, and warm tone.

**3. "Do" Usage (Crucial for Prudential's Brand):**

* Integrate the word "do" (or its variations – doing, does) authentically and seamlessly.  Follow established brand guidelines regarding capitalization (e.g., "DO" in standalone statements, "do" in sentence case otherwise).

**4. Compliance and Brand Safety:**

* **Essential:** The text content MUST be compliant with all regulations. Absolutely NO offensive, obscene, defamatory, threatening, discriminatory, controversial, racial, or political content. No misleading or biased language. No comparisons with competitors. No financial/insurance advice. No personal customer data.
*  Represent Prudential appropriately, aligning with brand guidelines. Do not present the poster as a separate legal entity.
* **Charity Partnership Clause:** If the user input mentions a charity partnership, the text content MUST include the disclaimer: "This activity has not been reviewed or approved by Prudential."  Focus solely on raising awareness and support for the cause; avoid conditional statements about fundraising or sales. 
* Avoid exaggerated claims or overpromising results. 

**5. Call to Action:**

* Include a clear and concise call to action if appropriate (e.g., "Learn more", "Join us", "DM us to find out more", "Take action now!").

**Example incorporating the above guidelines:**

"Creating a healthier community space is something we're passionate about. Join us this Saturday as Prudential volunteers help clean up the local park!"

**Important**: Provide the text content in plain text format without any font colors. Avoid HTML or any code in the output.

**Output Evaluation Criteria:**

The generated text content will be evaluated based on its adherence to the above instructions, its conciseness, clarity, engagement potential, and overall alignment with Prudential's brand voice and compliance guidelines.

Important: Note that the headline should be less than 10 words and the event_details should be at least 30 words and less than 60 words. Add newline characters to the event details where appropriate to improve readability of content for humans. Avoid hashtags.
The call to action should be concise and impactful, within 7 words. The call to action should not include email addresses or telephone numbers.

Generate the copy in the following JSON format:

{{
  headline: string,
  event_details: string,
  call_to_action: string
}}
"""

POST_TEXT_CAPTION_TEMPLATE = """

**User Input:** {user_input}

**Caption Text Generation Instructions:**

You are tasked to write the social media caption for a post for distribution on social media. The caption should be catchy, engaging with right motivation.

The text content should embody Prudential's brand voice and adhere to the following principles:

**1. Human Benefit/Relatable Truth:**

* Lead with a clear human benefit or relatable truth relevant to the target audience.  For example, instead of "Park cleanup this Saturday," try framing it around the benefit, such as creating a healthier community space.
* If mentioning a Prudential product/service (only if directly relevant to the user input), present the human benefit *before* any product features.  Avoid exaggerating benefits.

**2. Prudential Brand Voice and Tone:**

* Employ a warm, inviting, and intuitive tone. Encourage engagement and conversation (e.g., asking a question or suggesting an action).
* Foster a sense of partnership and collaboration.
* Use simple, direct language, avoiding jargon and technical terms.  Maintain a friendly, cheerful, and warm tone.

**3. "Do" Usage (Crucial for Prudential's Brand):**

* Integrate the word "do" (or its variations – doing, does) authentically and seamlessly.  Follow established brand guidelines regarding capitalization (e.g., "DO" in standalone statements, "do" in sentence case otherwise).

**4. Compliance and Brand Safety:**

* **Essential:** The text content MUST be compliant with all regulations. Absolutely NO offensive, obscene, defamatory, threatening, discriminatory, controversial, racial, or political content. No misleading or biased language. No comparisons with competitors. No financial/insurance advice. No personal customer data.
*  Represent Prudential appropriately, aligning with brand guidelines. Do not present the poster as a separate legal entity.
* **Charity Partnership Clause:** If the user input mentions a charity partnership, the text content MUST include the disclaimer: "This activity has not been reviewed or approved by Prudential."  Focus solely on raising awareness and support for the cause; avoid conditional statements about fundraising or sales. 
* Avoid exaggerated claims or overpromising results.

**5. Call to Action:**

* Include a clear and concise call to action if appropriate (e.g., "Learn more", "Join us", "DM us to find out more", "Take action now!").

**Example incorporating the above guidelines:**

"Creating a healthier community space is something we're passionate about. Join us this Saturday as Prudential volunteers help clean up the local park! #CommunityLove #DoGood #Prudential"

**Important**: Provide the text content in plain text format without any font colors. Avoid HTML or any code in the output.

**Output Evaluation Criteria:**

The generated text content will be evaluated based on its adherence to the above instructions, its conciseness, clarity, engagement potential, and overall alignment with Prudential's brand voice and compliance guidelines.

Important: Note that the caption should be between 50-100 words. Add newline characters to the caption where appropriate to improve readability of content for humans.
Avoid excessive use of hashtags and emojis, use them sparingly. Do not use any hashtags that mention Prudential such as #Prudential, #PFA, #PACS.

Return the caption as plain text:
"""

# --- GCS Helper Functions ---


def create_bucket_if_not_exists(bucket_name, project_id):
    """Creates a new bucket."""
    storage_client = storage.Client(project=project_id)
    try:
        bucket = storage_client.bucket(bucket_name)
        bucket.location = "US"  # Set bucket location
        storage_client.create_bucket(bucket)
        print(f"Bucket {bucket_name} created.")
    except Exception as e:
        print(f"Bucket {bucket_name} already exists. \n Error: {e}")


def delete_bucket_contents(bucket_name, project_id):
    """Deletes all the blobs/files inside a bucket"""
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.get_bucket(bucket_name)

    blobs = bucket.list_blobs()

    for blob in blobs:
        try:
            blob.delete()
        except Exception as e:
            print(f"Error deleting blob {blob.name}: {e}")

    print(f"Deleted all objects in bucket {bucket_name}")


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


def upload_blob(bucket_name, source_file_name, destination_blob_name, project_id):
    """Uploads a file to the bucket."""
    # bucket_name = "your-bucket-name"
    # source_file_name = "local/path/to/file"
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client(project=project_id)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")


def copy_file_to_gcs(source_file, bucket_name, gcs_folder, filename, project_id):
    try:
        upload_blob(bucket_name, source_file, f"{gcs_folder}/{filename}", project_id)
    except Exception as e:
        print(f"An error occurred while copying file to GCS: {e}")


def download_to_local_folder_from_gcs_bucket(
    bucket_name, file_name, local_folder, project_id
):
    try:
        local_file_path = os.path.join(local_folder, file_name)
        os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
        download_blob(bucket_name, file_name, local_file_path, project_id)
    except Exception as e:
        print(f"An error occurred while downloading file from GCS: {e}")


def download_folder_from_gcs(bucket_name, gcs_folder, local_folder, project_id):
    """Downloads all files in a specified folder from a GCS bucket to a local directory."""
    storage_client = storage.Client(project=project_id)
    blobs = storage_client.list_blobs(bucket_name, prefix=gcs_folder)

    for blob in blobs:
        # Construct the local file path
        local_file_path = os.path.join(
            local_folder, blob.name[len(gcs_folder) :].lstrip("/")
        )
        os.makedirs(
            os.path.dirname(local_file_path), exist_ok=True
        )  # Create directories if they don't exist

        try:
            blob.download_to_filename(local_file_path)
            print(f"Downloaded {blob.name} to {local_file_path}")
        except Exception as e:
            print(f"An error occurred while downloading {blob.name}: {e}")


def list_files_in_gcs_bucket(bucket_name, project_id, prefix=None):
    """Lists all the blobs in the bucket."""
    storage_client = storage.Client(project=project_id)
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
    file_list = []
    for blob in blobs:
        if not blob.name.endswith("/"):  # Exclude directories
            file_list.append(blob.name)
    return file_list


def list_blobs_with_prefix(bucket_name, prefix, project_id):
    storage_client = storage.Client(project=project_id)
    blobs = storage_client.list_blobs(bucket_name, prefix=prefix)
    return [blob for blob in blobs]


# --- Image and Text Processing Functions ---


def remove_background(
    input_path, output_path, mask_path, margin=10, alpha_threshold=10
):
    with open(input_path, "rb") as input_file:
        input_data = input_file.read()
    session = new_session("u2net")
    output_data = remove(
        input_data,
        session=session,
        alpha_matting=True,
        alpha_matting_foreground_threshold=230,
        alpha_matting_background_threshold=10,
        alpha_matting_erode_size=10,
    )
    output_image = Image.open(io.BytesIO(output_data)).convert("RGBA")
    output_array = np.array(output_image)
    alpha = output_array[:, :, 3]
    alpha_threshold_mask = alpha > alpha_threshold

    rows = np.any(alpha_threshold_mask, axis=1)
    cols = np.any(alpha_threshold_mask, axis=0)

    if np.any(rows) and np.any(cols):
        ymin, ymax = np.where(rows)[0][[0, -1]]
        xmin, xmax = np.where(cols)[0][[0, -1]]

        height, width = alpha.shape
        ymin = max(0, ymin - margin)
        ymax = min(height, ymax + margin)
        xmin = max(0, xmin - margin)
        xmax = min(width, xmax + margin)

        cropped_image = output_image.crop((xmin, ymin, xmax, ymax))
        cropped_image.save(output_path)

        mask_image = Image.fromarray(alpha)
        cropped_mask = mask_image.crop((xmin, ymin, xmax, ymax))
        cropped_mask.save(mask_path)

        print(f"Background removed image saved to {output_path}")
        print(f"Mask saved to {mask_path}")
    else:
        print("No content found after applying threshold. Saving original image.")
        output_image.save(output_path)
        Image.fromarray(alpha).save(mask_path)


def get_font_metrics(font):
    ascent, descent = font.getmetrics()
    avg_char_width = sum(font.getbbox(char)[2] for char in ascii_letters) / len(
        ascii_letters
    )
    return ascent, descent, avg_char_width


def wrap_text_custom(text, font, max_width):
    lines = []
    line_widths = []
    current_line = []
    current_width = 0

    for line in text.split("\n"):
        words = line.split()
        if not words:
            lines.append("")  # Handle empty lines
            line_widths.append(0)
            continue
        for word in words:
            word_width = font.getbbox(word)[2]
            space_width = (
                font.getbbox(" ")[2] or 0
            )  # Handle cases where space has zero width

            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width + space_width
            else:
                lines.append(" ".join(current_line))
                line_widths.append(current_width)
                current_line = [word]
                current_width = word_width + space_width

        if current_line:  # Add the last line of each paragraph
            lines.append(" ".join(current_line))
            line_widths.append(current_width)
        current_line = []  # Reset for the next paragraph
        current_width = 0

    return lines, line_widths


def get_font_size(textarea, text, font_name, pixel_gap=2, max_font_size=300):
    text_width, text_height = int(textarea[0]), int(textarea[1])

    for point_size in range(5, max_font_size):  # Iterate to find ideal font size
        try:  # Try creating font with specified size
            font = ImageFont.truetype(font_name, point_size)
        except IOError as e:  # Handle font loading errors gracefully
            print(f"Font loading error: {e}. Trying next size.")
            continue

        ascent, descent, avg_char_width = get_font_metrics(font)
        wrapped_lines, line_widths = wrap_text_custom(text, font, text_width)
        total_height = (ascent + descent + pixel_gap) * len(wrapped_lines) - pixel_gap

        # if total_height >= text_height:
        #     while (max(line_widths) >= text_width or total_height >= text_height) and point_size > 1:
        #         point_size -= 1
        #         font = ImageFont.truetype(font_name, point_size)
        #         wrapped_lines, line_widths = wrap_text_custom(text, font, text_width)
        #         total_height = (ascent + descent + pixel_gap) * len(wrapped_lines) - pixel_gap
        #     break

        if total_height >= text_height:
            point_size -= 2
            font = ImageFont.truetype(font_name, point_size)
            wrapped_lines, line_widths = wrap_text_custom(text, font, text_width)
            break

    logger.info(f"Font size is {point_size} for text {text}")

    return wrapped_lines, point_size


def place_singleline_text_overlay_on_background(
    overlay_image_path,
    text,
    initial_font_size,
    overlay_config,
    font_name,
    text_color,
    alignment,
    margin=5,
):
    x, y = overlay_config["x"], overlay_config["y"]
    width, height = overlay_config["width"], overlay_config["height"]

    with Image.open(overlay_image_path) as img:
        draw = ImageDraw.Draw(img)

        # Function to get text width
        def get_text_width(font):
            return draw.textbbox((0, 0), text, font=font)[2]

        # Start with the initial font size and decrease if necessary
        font_size = initial_font_size
        font = ImageFont.truetype(font_name, font_size)
        text_width = get_text_width(font)
        print(f"Processing text {text} with initial font size {initial_font_size}")

        # Decrease font size until text fits within max_width (including margin)
        while text_width > (width - 2 * margin) and font_size > 1:
            font_size -= 1
            font = ImageFont.truetype(font_name, font_size)
            text_width = get_text_width(font)
        print(f"Final text {text} with font size {font_size}")

        # Calculate text position and use Pillow's built-in alignment
        if alignment == "center":
            anchor = "mm"  # middle-middle
            text_x = x + width // 2
        elif alignment == "right":
            anchor = "rm"  # right-middle
            text_x = x + width - margin
        else:  # left alignment
            anchor = "lm"  # left-middle
            text_x = x + margin

        # Calculate vertical position (center of the height)
        text_y = y + height // 2

        # Draw the text using Pillow's alignment feature
        draw.text((text_x, text_y), text, font=font, fill=text_color, anchor=anchor)

        # Save the result
        img.save(overlay_image_path)
        return img


def place_multiline_text_overlay_on_background(
    overlay_image_path,
    text,
    overlay_config,
    font_path,
    text_color,
    alignment,
    margin=5,
    max_font_size=300,
):
    x, y = overlay_config["x"], overlay_config["y"]
    width, height = overlay_config["width"], overlay_config["height"]

    with Image.open(overlay_image_path) as img:
        draw = ImageDraw.Draw(img)

        wrapped_lines, font_size = get_font_size(
            (width, height), text, font_path, margin, max_font_size
        )

        if len(wrapped_lines) < 2:
            img = place_singleline_text_overlay_on_background(
                overlay_image_path,
                text,
                150,
                overlay_config,
                font_path,
                text_color,
                alignment,
                margin,
            )
            return img

        font = ImageFont.truetype(font_path, font_size)

        ascent, descent, _ = get_font_metrics(font)
        line_height = ascent + descent + margin

        starting_y = y
        ending_y = y + len(wrapped_lines) * line_height
        total_text_height = ending_y - starting_y
        y_offset_to_center_text_vertically = (height - total_text_height) // 2
        starting_y = y + y_offset_to_center_text_vertically

        current_y = starting_y
        for line in wrapped_lines:
            if alignment == "center":
                line_bbox = draw.textbbox((0, 0), line, font=font)
                line_width = line_bbox[2] - line_bbox[0]
                line_x = x + (width - line_width) // 2
            elif alignment == "right":
                line_bbox = draw.textbbox((0, 0), line, font=font)
                line_width = line_bbox[2] - line_bbox[0]
                line_x = x + width - line_width
            else:  # left alignment
                line_x = x

            draw.text((line_x, current_y), line, font=font, fill=text_color)
            current_y += line_height

        # Save the result
        img.save(overlay_image_path)
        return img


def place_image_overlay_on_background(
    overlay_image_path, background_image_path, overlay_config, output_path
):

    # Placement config
    target_x = overlay_config["x"]
    target_y = overlay_config["y"]
    target_width = overlay_config["width"]
    target_height = overlay_config["height"]

    # Open images
    background_image = Image.open(background_image_path).convert(
        "RGBA"
    )  # Convert to RGBA

    overlay_image = Image.open(overlay_image_path).convert("RGBA")  # Convert to RGBA

    # Calculate aspect ratio
    overlay_image_aspect_ratio = overlay_image.width / overlay_image.height

    print(
        f"Original size of overlay image {overlay_image_path}, Aspect Ratio - {overlay_image_aspect_ratio}, Size - {background_image.size}"
    )

    # Resize to meet target height, maintaining aspect ratio, using LANCZOS
    new_width = int(target_height * overlay_image_aspect_ratio)
    resized_overlay_image = overlay_image.resize(
        (new_width, target_height), Image.LANCZOS
    )
    print(f"Resized overlay image to Size - {resized_overlay_image.size}")

    # Check if resized width exceeds target width, and resize again if needed
    if new_width > target_width:
        new_height = int(target_width / overlay_image_aspect_ratio)
        resized_overlay_image = overlay_image.resize(
            (target_width, new_height), Image.LANCZOS
        )
        print(
            f"Width exceeds boundary, adjusting overlay image with width / height - {target_width} / {new_height} to Size - {resized_overlay_image.size}"
        )

    # Calculate centered coordinates
    final_x = target_x + (target_width - resized_overlay_image.width) // 2
    final_y = target_y + (target_height - resized_overlay_image.height) // 2

    # Paste actor image onto background
    background_image.paste(
        resized_overlay_image, (final_x, final_y), resized_overlay_image
    )  # Use mask for transparency

    # Save the result (optional)
    background_image.save(output_path)  # Save as PNG to preserve transparency

    return background_image


def create_background_for_text(image_path, overlay_config, output_path):
    image = Image.open(image_path).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))

    draw = ImageDraw.Draw(overlay)
    target_x = overlay_config["x"]
    target_y = overlay_config["y"]
    target_width = overlay_config["width"]
    target_height = overlay_config["height"]
    padding = 20
    img_width, img_height = image.size

    start_x = max(target_x - padding, 0)
    start_y = max(target_y - padding, 0)
    end_x = min(img_width, target_x + target_width + padding)
    end_y = min(img_height, target_y + target_height + padding)

    print(
        f"original values for config: {target_x}, {target_y}, {target_width}, {target_height}"
    )
    print(f"final values for config: {start_x}, {start_y}, {end_x}, {end_y}")

    rectangle_color = (255, 255, 255, 200)
    draw.rectangle([(start_x, start_y), (end_x, end_y)], fill=rectangle_color)

    combined_image = Image.alpha_composite(image, overlay)
    combined_image.save(output_path)
    return image


def create_marketing_banner_baseline(
    background_path,
    background_config,
    image_inputs: dict,
    text_inputs: dict,
    output_path,
    is_background_needed=False,
    is_qr_code_needed=False,
    primary_font_path=None,
    secondary_font_path=None,
):
    if "actor_position" in background_config:
        # Process Actor overlay
        place_image_overlay_on_background(
            image_inputs["actor_path"],
            background_path,
            background_config.get("actor_position"),
            output_path,
        )

    if "logo_position" in background_config:
        # Process Logo overlay
        place_image_overlay_on_background(
            image_inputs["logo_path"],
            output_path,
            background_config.get("logo_position"),
            output_path,
        )

    if "qr_code_position" in background_config and is_qr_code_needed:
        place_image_overlay_on_background(
            f"{LOCAL_TEMP_DIR}/Artefacts/qr_code.PNG",
            output_path,
            background_config["qr_code_position"],
            output_path,
        )

    if "text_header1_position" in background_config:
        # if is_background_needed:
        # create_background_for_text(output_path, background_config['text_header1_position'], output_path)
        # Process Text Header overlay
        text_header = text_inputs["text_header1"]
        text_color = (0, 0, 0)
        text_alignment = "left"
        text_margin = 5
        # font_name="AlbertSans-Bold.ttf"
        place_multiline_text_overlay_on_background(
            output_path,
            text_header,
            background_config["text_header1_position"],
            font_path=primary_font_path,
            text_color=text_color,
            alignment=text_alignment,
            margin=text_margin,
        )

    if "text_tagline_position" in background_config:
        # if is_background_needed:
        #     create_background_for_text(output_path, background_config['text_tagline_position'], output_path)
        # Process Text Tagline overlay
        text_header = text_inputs.get("text_tagline", "Error")
        text_color = (0, 0, 0)
        text_alignment = "center"
        text_margin = 2
        place_multiline_text_overlay_on_background(
            output_path,
            text_header,
            background_config["text_tagline_position"],
            font_path=secondary_font_path,
            text_color=text_color,
            alignment=text_alignment,
            margin=text_margin,
            max_font_size=20,
        )

    if "text_details_position" in background_config:
        if is_background_needed:
            create_background_for_text(
                output_path, background_config["text_details_position"], output_path
            )
        # Process Text Detail overlay
        text_header = text_inputs["text_details"]
        text_color = (0, 0, 0)
        text_alignment = "left"
        text_margin = 5
        place_multiline_text_overlay_on_background(
            output_path,
            text_header,
            background_config["text_details_position"],
            font_path=secondary_font_path,
            text_color=text_color,
            alignment=text_alignment,
            margin=text_margin,
        )

    if "text_action_position" in background_config:
        if is_background_needed:
            badge_overlay_config = {  # allows out of bounds stickers
                "x": background_config["text_action_position"]["x"] - 70,
                "y": background_config["text_action_position"]["x"] + 70,
                "height": background_config["text_action_position"]["height"] + 140,
                "width": background_config["text_action_position"]["width"] + 140,
            }
            place_image_overlay_on_background(
                f"{LOCAL_INPUT_DIR_GRAPHICS}/badge_1.png",  # TODO: add this to request config
                output_path,
                badge_overlay_config,
                output_path,
            )
            # create_background_for_text(output_path, background_config['text_action_position'], output_path)
        # Process Text Tagline overlay
        text_header = text_inputs["text_action"]
        text_color = (255, 255, 255)
        text_alignment = "center"
        text_margin = 10
        place_multiline_text_overlay_on_background(
            output_path,
            text_header,
            background_config["text_action_position"],
            font_path=primary_font_path,
            text_color=text_color,
            alignment=text_alignment,
            margin=text_margin,
        )

    return output_path


def get_filepath_in_folder_nested(root_folder):
    file_paths = []
    for dirpath, _, filenames in os.walk(root_folder):
        for filename in filenames:
            file_paths.append(os.path.join(dirpath, filename))
    return file_paths


def find_files_with_prefix(directory, prefix):
    """Finds files in a directory that start with a specific prefix."""
    matching_files = []
    for filename in os.listdir(directory):
        if filename.startswith(prefix):
            matching_files.append(os.path.join(directory, filename))
    return matching_files


def generate_image_generation_input_params(input_text):
    model = GenerativeModel(
        "gemini-2.5-pro",
    )
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 1,
        "top_p": 0.95,
        "response_mime_type": "application/json",
    }
    response = model.generate_content(
        [IMAGE_GENERATION_INPUT_PARAMS_GENERATION_PROMPT.format(user_input=input_text)],
        generation_config=generation_config,
    )

    output = response.text
    json_output = json.loads(output)
    subject = json_output.get("subject", "Error")
    age = json_output.get("age", "Error")
    clothing = json_output.get("clothing", "Error")
    theme = json_output.get("theme", "Error")

    logger.info(
        f"Image Generation Input Params - Subject: {subject}, Age: {age}, Clothing: {clothing}, Theme: {theme}"
    )

    return subject, age, clothing, theme


def invoke_gemini_for_text(prompt, model_input="gemini-2.5-pro"):
    model = GenerativeModel(model_input)
    response = model.generate_content(prompt)
    return response.text


def generate_imagen_outputs(
    prompt, number_of_images, aspect_ratio, model="imagen-3.0-generate-002"
):
    logger.info(
        f"Generating {number_of_images} images with aspect ratio {aspect_ratio} and model {model}"
    )
    generation_model = ImageGenerationModel.from_pretrained(model)
    image_list = generation_model.generate_images(
        prompt=prompt,
        number_of_images=number_of_images,
        aspect_ratio=aspect_ratio,
        negative_prompt=NEGATIVE_PROMPT_FOR_IMAGEN,
    )
    return image_list.images


def generate_image_assets(
    subject, age, clothing, theme, background, photography, request_id, image_count=4
):
    # Prepare the prompt for image generation
    prompt_user_input = f"""
        "Subject: {subject}"
        "Age: {age}"
        "Clothing: {clothing}"
        "Theme: {theme}"
        "Environment Settings: {background}"
        "Photography Setting: {photography}"

        If the subject involves multiple people, ensure that they DO NOT LOOK alike.
    """

    # prompt_rewrite = f"""
    #     Act as a prompt engineering expert to generate a high quality prompt for Imagen3 image generation strictly following the user input below.

    #     Extract all key information and entities required for you to rewrite the prompt retaining exact original intent without hyperbole to feed it to an image generation model.
    #     The input will be based for a marketing campaign description for creating posters, banners, etc.
    #     Strictly do not provide any input text in the output top prompts or high confidence prompt.
    #     You are only to generate image and not text on image.
    #     The output should be concise, explaining all entities of what is required in the image and how it has to be generated. If the user requests for a white background, ensure that there is no location specified and the background has no details.
    #     To meet the branding guidelines, ensure that Prudential Red (#E2001A) is incorporated into the image tastefully adhering to a ratio of 40% for simpler illustration and less for complex images.
    #     **Important**: As the image generated will be masked to remove background, ensure all subjects are fully within the frame, avoiding any awkward cropping of their bodies at the edges. It is acceptable to frame the image from the waist up, or even closer, to prioritize full inclusion of the subjects.
    #     Ensure that the generated image does not have too many details, as it will be masked. If there are people in the image, ensure that there are less than 4 people.
    #     Check if your response is a high quality prompt meeting the guidelines above, before responding.

    #     USER INPUT -
    #     {prompt_user_input}

    #     OUTPUT -
    # """

    prompt_rewrite = f"""
        Act as a prompt engineering expert to generate a high quality prompt for Imagen3 image generation strictly following the user input below.

        Extract all key information and entities required for you to rewrite the prompt retaining exact original intent without hyperbole to feed it to an image generation model.
        The input will be based for a marketing campaign description for creating posters, banners, etc.
        Strictly do not provide any input text in the output top prompts or high confidence prompt.
        The Imagen model should only generate image and there should be no text on the image.
        Translate any color codes provided by the user to an appropriate color description for the model to understand.

        The output should be concise, explaining all entities of what is required in the image and how it has to be generated. Follow the background requirements provided by the user closely. If specific details of a background are specified by the user, ensure that the background is minimalistic for a clean and simple image.
        To meet the branding guidelines, ensure that highly saturated red with minimal blue or yellow undertones (hex color code #E2001A) is incorporated into the image tastefully adhering to a ratio of 40% for simpler illustration and less for complex images.
        
        **Important**: As the image generated will be masked to remove background, make sure to leave sufficient negative space around the subjects and position them in the center of the image. It is acceptable to frame the image from the waist up, or even closer, to prioritize full inclusion of the subjects.
        Ensure that the generated image does not have too many details, as it will be masked. If there are people in the image, ensure that there are less than 4 people.

        **Important** Take note of the below guidelines when generating the Imagen prompt:
        • The image should not contain any personally identifiable customer information. If the user provided such information, omit those in the imagen prompt
        • The image should *not* contain any logos of any known companies or brands
        • The image should *not* contain anything offensive, obscene, defamatory, threatening, discriminatory (based on race, religion, gender, sexual orientation, etc.), controversial, racial, or political
        • Actors or items featured on the post should be appropriate for a professional context and should avoid any sexual or other offensive associations. Swimsuits or other revealing attire is not permitted.
        • The image should not contain any negative portrayals or inappropriate activities like alcohol consumption, smoking, vaping or gambling

        Check if your response is a high quality prompt meeting the guidelines above, before responding.

        USER INPUT -
        {prompt_user_input}

        OUTPUT -
    """

    imagen_prompt = invoke_gemini_for_text(prompt_rewrite)

    logger.info(f"prompt user input: {prompt_user_input}")
    logger.info(f"Imagen Prompt: {imagen_prompt}")

    image_lists = []
    # Generate images asynchronously
    with ThreadPoolExecutor() as executor:
        # Submit tasks to the executor
        futures = [
            executor.submit(
                generate_imagen_outputs,
                imagen_prompt,
                1,
                "1:1",
                "imagen-3.0-generate-002",
            )
            for _ in range(image_count)  # Generate 4 images
        ]

        # Collect results as they complete
        for future in futures:
            image_lists.append(future.result())
    logger.info(f"Images successfully generated")

    # Upload images to GCS bucket
    uploaded_image_urls = []
    local_image_paths = []
    for index, image_list in enumerate(image_lists):
        for generated_image in image_list:
            generated_image_data = base64.b64decode(generated_image._as_base64_string())
            pil_image = Image.open(io.BytesIO(generated_image_data))

            # Create a unique filename for the image
            image_filename = f"{LOCAL_TEMP_DIR}/{request_id}_{index}.png"
            local_image_paths.append(image_filename)
            # Upload the image to GCS
            gcs_url = f"gs://{GCS_INPUT_BUCKET_ROOT}/{GCS_OUTPUT_DIR_GENERATED_IMAGES}/{request_id}_{index}.png"
            gcs_path = f"{GCS_OUTPUT_DIR_GENERATED_IMAGES}/{request_id}_{index}.png"
            pil_image.save(image_filename, "PNG")  # Save temporarily to upload
            upload_blob(GCS_INPUT_BUCKET_ROOT, image_filename, gcs_path, PROJECT_ID)
            uploaded_image_urls.append(gcs_url)  # Store the GCS path

    logger.info(f"Images successfully uploaded to GCS")

    return uploaded_image_urls, local_image_paths


def generate_post_text(post_text_prompt_input):
    model = GenerativeModel(
        "gemini-2.5-pro",
    )
    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 1.2,
        "top_p": 0.95,
        "response_mime_type": "application/json",
    }

    headline = "Error occurred during generation"
    event_details = "Error occurred during generation"
    call_to_action = "Error occurred during generation"

    retry_count = 0
    while retry_count < 3 and (
        headline == "Error occurred during generation"
        or event_details == "Error occurred during generation"
        or call_to_action == "Error occurred during generation"
    ):
        logger.info(
            f"Generating headline, event details, and call to action, iteration {retry_count+1}"
        )
        response = model.generate_content(
            [POST_TEXT_PROMPT_TEMPLATE.format(user_input=post_text_prompt_input)],
            generation_config=generation_config,
        )

        output = response.text
        json_output = json.loads(output)
        headline = json_output.get("headline", "Error occurred during generation")
        event_details = json_output.get(
            "event_details", "Error occurred during generation"
        )
        call_to_action = json_output.get(
            "call_to_action", "Error occurred during generation"
        )

        retry_count += 1

    return headline, event_details, call_to_action


def generate_post_caption(post_text_prompt_input):
    model = GenerativeModel(
        "gemini-2.5-pro",
    )

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 1.2,
        "top_p": 0.95,
    }

    caption = ""
    retry_count = 0
    while retry_count < 3 and caption == "":
        logger.info(f"Generating caption, iteration {retry_count+1}")
        try:
            response = model.generate_content(
                [POST_TEXT_CAPTION_TEMPLATE.format(user_input=post_text_prompt_input)],
                generation_config=generation_config,
            )
            caption = response.text
            retry_count += 1
        except Exception as e:
            logger.error(f"Error generating caption: {e}")
            retry_count += 1
    return caption


def camel_to_snake(camel_case_str: str) -> str:
    """Convert camelCase string to snake_case."""
    return "".join(
        ["_" + i.lower() if i.isupper() else i for i in camel_case_str]
    ).lstrip("_")


def convert_template_to_snake_case(template: Template) -> dict:
    """Convert Template object properties to snake_case."""
    return {camel_to_snake(key): value for key, value in template.dict().items()}


def overlay_text_and_image(
    image_path,
    headline,
    event_details,
    call_to_action,
    sign_off,
    output_path,
    is_background_needed,
    template,
    primary_font_path,
    secondary_font_path,
):
    # Code to overlay text and image based on square_event_template
    post_template = template
    bg_path = (
        f"{LOCAL_TEMP_DIR}/{GCS_INPUT_DIR_TEMPLATES}/{post_template.layoutName}.png"
    )
    # Use overlay functionality to apply text and template
    create_marketing_banner_baseline(
        background_path=bg_path,
        background_config=convert_template_to_snake_case(post_template),
        image_inputs={"actor_path": image_path},
        text_inputs={
            "text_header1": headline,
            "text_details": event_details,
            "text_action": call_to_action,
            "text_tagline": sign_off,
        },
        output_path=output_path,
        is_background_needed=is_background_needed,
        is_qr_code_needed=False,  # TODO: add qr code overlay logic
        primary_font_path=primary_font_path,
        secondary_font_path=secondary_font_path,
    )
    return output_path


def aspect_ratio_to_template(aspect_ratio):
    if aspect_ratio == AspectRatio.full_image:
        return "SQUARE_FULL_IMAGE_TEMPLATE_1"
    elif aspect_ratio == AspectRatio.vertical:
        return "VERTICAL_TEMPLATE_1"
    else:
        return "SQUARE_FORMAL_TEMPLATE_1"


def create_final_sign_off_text(sign_off, is_recruitment_related, is_charity_related):
    disclaimer_link = "https://www.xyz-org.com/fc-info"
    charity_disclaimer = "This activity has not been reviewed or approved by the Organization."

    final_sign_off_text = sign_off

    if not is_recruitment_related:
        final_sign_off_text += f"\n{disclaimer_link}"  # Disclaimer link is only added if not recruitment related

    if is_charity_related:
        final_sign_off_text += f"\n{charity_disclaimer}"  # Charity disclaimer is only added if charity related

    return final_sign_off_text.strip()


def download_template_images(layouts):
    """Downloads template images in parallel using ThreadPoolExecutor."""

    def download_layout(layout):
        local_path = os.path.join(
            LOCAL_TEMP_DIR, f"{GCS_INPUT_DIR_TEMPLATES}/{layout.layoutName}.png"
        )
        # Check if file already exists
        if not os.path.exists(local_path):
            # Ensure directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            download_to_local_folder_from_gcs_bucket(
                GCS_INPUT_BUCKET_ROOT,
                f"{GCS_INPUT_DIR_TEMPLATES}/{layout.layoutName}.png",
                LOCAL_TEMP_DIR,
                PROJECT_ID,
            )
        else:
            logger.info(f"Template {layout.layoutName}.png already exists locally, skipping download")

    with ThreadPoolExecutor() as executor:
        executor.map(download_layout, layouts)

    local_layout_paths = [
        os.path.join(
            LOCAL_TEMP_DIR, f"{GCS_INPUT_DIR_TEMPLATES}/{layout.layoutName}.png"
        )
        for layout in layouts
    ]
    return local_layout_paths

def download_fonts_and_graphics():
    try:
        logger.info("Checking and downloading fonts and graphics")
        
        # Check if fonts directory exists and has contents
        fonts_exist = os.path.exists(LOCAL_INPUT_DIR_FONTS) and len(os.listdir(LOCAL_INPUT_DIR_FONTS)) > 0
        if not fonts_exist:
            logger.info("Downloading fonts")
            os.makedirs(LOCAL_INPUT_DIR_FONTS, exist_ok=True)
            download_folder_from_gcs(
                GCS_INPUT_BUCKET_ROOT, "Artefacts/Fonts", LOCAL_INPUT_DIR_FONTS, PROJECT_ID
            )
        else:
            logger.info("Fonts already exist locally, skipping download")

        # Check if graphics directory exists and has contents
        graphics_exist = os.path.exists(LOCAL_INPUT_DIR_GRAPHICS) and len(os.listdir(LOCAL_INPUT_DIR_GRAPHICS)) > 0
        if not graphics_exist:
            logger.info("Downloading graphics")
            os.makedirs(LOCAL_INPUT_DIR_GRAPHICS, exist_ok=True)
            download_folder_from_gcs(
                GCS_INPUT_BUCKET_ROOT,
                "Artefacts/Graphics",
                LOCAL_INPUT_DIR_GRAPHICS,
                PROJECT_ID,
            )
        else:
            logger.info("Graphics already exist locally, skipping download")

        logger.info("Fonts and graphics check complete")
    except Exception as e:
        logger.error(f"Error checking/downloading fonts and graphics: {e}")


def process_image(
    img_file_name,
    input_text,
    request_id,
    idx,
    aspect_ratio,
    layouts,
    primary_font_path,
    secondary_font_path,
    disclaimer_and_sign_off,
    generated_image_urls,
    user_id,
):
    no_bg_image_path = os.path.join(
        LOCAL_TEMP_DIR, f"NoBg_{img_file_name.split('/')[-1]}"
    )
    mask_path = os.path.join(LOCAL_TEMP_DIR, f"Mask_{img_file_name.split('/')[-1]}")
    is_background_needed = aspect_ratio == AspectRatio.full_image
    if not is_background_needed:
        remove_background(img_file_name, no_bg_image_path, mask_path)
        logger.info(f"removed background from {img_file_name}")

    headline, event_details, call_to_action = generate_post_text(input_text)
    caption = generate_post_caption(input_text)

    final_image_path = f"{LOCAL_TEMP_DIR}/final_{request_id}_{idx}.png"

    if not is_background_needed:
        overlay_text_and_image(
            no_bg_image_path,
            headline,
            event_details,
            call_to_action,
            disclaimer_and_sign_off,
            final_image_path,
            is_background_needed,
            layouts[idx],
            primary_font_path,
            secondary_font_path,
        )
    else:
        overlay_text_and_image(
            img_file_name,
            headline,
            event_details,
            call_to_action,
            disclaimer_and_sign_off,
            final_image_path,
            is_background_needed,
            layouts[idx],
            primary_font_path,
            secondary_font_path,
        )

    logger.info(f"overlayed text and image on {img_file_name}")
    copy_file_to_gcs(
        final_image_path,
        GCS_INPUT_BUCKET_ROOT,
        GCS_OUTPUT_DIR_POSTS,
        f"final_{request_id}_{idx}.png",
        PROJECT_ID,
    )

    post = Post(
        userId=user_id,
        generatedImageUrl=generated_image_urls[idx],
        postCreationTime=datetime.now(),
        requestId=request_id,
        postStatus=PostStatus.original,
        postVote=PostVote.novote,
        evaluationStatus=EvaluationStatus.pending,
        finalImageUrl=f"gs://{GCS_INPUT_BUCKET_ROOT}/{GCS_OUTPUT_DIR_POSTS}/final_{request_id}_{idx}.png",
        postCaption=caption,
    )
    add_post_to_db(post)
    logger.info(f"added post for {img_file_name} to db")

def format_background_color_description(background_color, art_style, aspect_ratio):
    if aspect_ratio == AspectRatio.full_image:
        return f"studio backdrop with a plain {"hex code " + background_color if background_color else 'pastel'} color background (if user specified any background details in the description, use that instead of the plain background)"
    elif art_style == "Vector Art":
        return "plain white background"
    else:
        return f"plain studio background with a green screen"


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
@functions_framework.cloud_event
# def generate_posts_background(request_id, user_id, request_config) -> None:
def generate_posts_background(cloud_event: CloudEvent) -> None:
    firestore_payload = firestoredata.DocumentEventData()
    firestore_payload._pb.ParseFromString(cloud_event.data)

    path_parts = firestore_payload.value.name.split("/")
    separator_idx = path_parts.index("documents")
    collection_path = path_parts[separator_idx + 1]
    document_path = "/".join(path_parts[(separator_idx + 2) :])

    print(f"Collection path: {collection_path}")
    print(f"Document path: {document_path}")

    affected_doc = db.collection(collection_path).document(document_path).get()

    request_id = affected_doc.id
    request: Request = affected_doc.to_dict()
    request_config = request["requestConfig"]
    user_id = request["userId"]

    logger.info(f"Generating posts for request {request_id}")
    start_time = datetime.now()
    logger.info(f"request config: {request_config}")
    post_description = request_config["postDescription"]
    subject = request_config["subject"]
    art_style = request_config["artStyle"]
    sign_off = request_config["signOff"]
    post_count = request_config["postCount"]
    aspect_ratio = request_config["aspectRatio"]
    background_color = request_config["backgroundColor"]
    is_recruitment_related = request_config["isRecruitmentRelated"]
    is_charity_related = request_config["isCharityRelated"]
    logger.info(f"post count: {post_count}")
    logger.info(f"Creating final sign off text")
    disclaimer_and_sign_off = create_final_sign_off_text(
        sign_off, is_recruitment_related, is_charity_related
    )

    input_text = PREPROCESSING_PROMPT_FOR_IMAGEN_PROMPT.format(
        post_description=post_description, subject=subject
    )
    subject, age, clothing, theme = generate_image_generation_input_params(input_text)
    generated_image_urls, local_image_paths = generate_image_assets(
        subject=subject,
        age=age,
        clothing=clothing,
        theme=theme,
        background=format_background_color_description(
            background_color, art_style, aspect_ratio
        ),
        photography=art_style,
        request_id=request_id,
        image_count=post_count,
    )

    if len(local_image_paths) == 0:
        logger.error(f"No images generated. Skipping post generation...")
        raise Exception("No images generated. Skipping post generation...")

    template = get_post_template_by_name(aspect_ratio_to_template(aspect_ratio))
    layouts = template.layouts
    download_template_images(layouts)

    download_fonts_and_graphics()

    # TODO: make this dynamic
    primary_font_path = os.path.join(
        LOCAL_INPUT_DIR_FONTS, "Gochi_Hand/GochiHand-Regular.ttf"
        # LOCAL_INPUT_DIR_FONTS, "Lora/Lora-Medium.ttf"
    )
    secondary_font_path = os.path.join(
        LOCAL_INPUT_DIR_FONTS, "AlbertSans/AlbertSans-SemiBold.ttf"
    )

    output_dir = LOCAL_TEMP_DIR + "/output"
    os.makedirs(output_dir, exist_ok=True)  # create a temp output directory
    try:
        if not template or not layouts:
            logger.error("No template or layout found. skipping post generation ...")
            return

        for idx, img_file_name in enumerate(local_image_paths):
            logger.info(f"currently processing img {idx+1} of {len(local_image_paths)}")
            process_image(
                img_file_name,
                input_text,
                request_id,
                idx,
                aspect_ratio,
                layouts,
                primary_font_path,
                secondary_font_path,
                disclaimer_and_sign_off,
                generated_image_urls,
                user_id,
            )

        #Update post count if the number of images generated is less than the requested count
        if len(local_image_paths) != post_count:
            update_request_in_db(request_id, request_config, len(local_image_paths))

        # Clean up local storage for cloud function while preserving templates, fonts and graphics
        if os.path.exists(LOCAL_TEMP_DIR):
            preserved_dirs = [
                f"{LOCAL_TEMP_DIR}/Artefacts",
                # f"{LOCAL_TEMP_DIR}/Artefacts/Graphics",
                # f"{LOCAL_TEMP_DIR}/{GCS_INPUT_DIR_TEMPLATES}"
            ]
            
            for item in os.listdir(LOCAL_TEMP_DIR):
                item_path = os.path.join(LOCAL_TEMP_DIR, item)
                logger.info(f"item_path: {item_path}")
                # Skip the directories we want to preserve
                if any(item_path.startswith(dir_path) for dir_path in preserved_dirs):
                    continue
                # Remove everything else
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
            logger.info(f"cleaned up local storage for cloud function while preserving templates, fonts and graphics")

        end_time = datetime.now()
        logger.info(f"Cloud function execution time: {end_time - start_time} seconds")
    except Exception as e:
        logger.error(f"An error occurred in cloud function: {e}")
        raise e

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

from enum import Enum
import os

# Project Settings
PROJECT_ID = os.environ.get("PROJECT_ID")
PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER")
FIRESTORE_ID = os.environ.get("FIRESTORE_ID")
SERVICE_ACCOUNT_FOR_SIGNING_URLS = "1003801603843-compute@developer.gserviceaccount.com"

GCS_INPUT_BUCKET_ROOT="1003801603843_marketing_content_generation_inputs"
GCS_INPUT_BUCKET=f"{PROJECT_NUMBER}_{GCS_INPUT_BUCKET_ROOT}"

GCS_INPUT_DIR_ACTOR="Artefacts/Actors"
GCS_INPUT_DIR_TEMPLATES="Artefacts/Background"

GCS_OUTPUT_DIR_ACTOR="Artefacts/Actors_Processed"
GCS_OUTPUT_DIR_BG="Artefacts/Background_Processed"
GCS_OUTPUT_DIR_POSTS="Artefacts/Final_Posts"
GCS_OUTPUT_DIR_GENERATED_IMAGES="Artefacts/Generated_Images"

# --- Local Directory Configuration (for Cloud Functions, these will be temp directories) ---

LOCAL_TEMP_DIR="/tmp"  # Use /tmp for Cloud Functions
# LOCAL_TEMP_DIR="/Users/dsalomone/Documents/Projects/social-media-post-generation/fastapi-backend/tmp"  # Use /tmp for Cloud Functions
LOCAL_INPUT_DIR_FONTS=f"{LOCAL_TEMP_DIR}/Artefacts/Fonts"  # Subdirectory under /tmp
LOCAL_INPUT_DIR_GRAPHICS=f"{LOCAL_TEMP_DIR}/Artefacts/Graphics"  # Subdirectory under /tmp

IMAGE_GENERATION_INPUT_PARAMS_GENERATION_PROMPT="""
**User Input:** {user_input}

You are a skilled social media director and you are tasked to determine the best visual asset that accompanies a social media post.
Based on the user input provided above, determine the appropriate description for the subject, age of the subject, clothing that the subject should wear and theme (what subject is doing).
If the subject is an inanimate object, then the age and clothing should be 'not applicable'.

The concept for the image should be simple and impactful, and should not involve too much details as the subject will need to be masked out from the background manually and we want to reduce the amount of work required to do this.
If there are people in the image, and their ethnicity is not specified by the user, then the ethnicity of the people featured in the image should be asian.

Your inputs will be used by a content creation team to produce a high quality image to accompany the social media post.

Example output:
{{
    subject: 'a vibrant Indonesian woman',
    age: 'age 40-50 years old',
    clothing: 'wearing a traditional Balinese dress',
    theme: 'enjoying movie on her phone screen wearing red headphones'
}}

{{
    subject: 'an ice cream cone',
    age: 'not applicable',
    clothing: 'not applicable',
    theme: 'ice cream with wafer cone and chocolate drizzle, on a sunny day'
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

PREPROCESSING_PROMPT_FOR_IMAGEN_PROMPT="""
Post Description: {post_description}
the main actor or item shown in the post is {subject}
"""

NEGATIVE_PROMPT_FOR_IMAGEN="""((((ugly)))), (((duplicate))), ((morbid)), ((mutilated)), swimsuit, gambling, smoking, cigarettes, vapes, text, drugs, alchohol, out of frame, extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((text))), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), table, bench"""

POST_TEXT_PROMPT_TEMPLATE="""

**User Input:** {user_input}

**Copy Text Generation Instructions:**

You are tasked to write the copy for a flyer for distribution on social media. The flyer should be catchy, engaging with right motivation.

The text content should embody Prudential's brand voice and adhere to the following principles:

**1. Human Benefit/Relatable Truth:**

* Lead with a clear human benefit or relatable truth relevant to the target audience.  For example, instead of 'Park cleanup this Saturday,' try framing it around the benefit, such as creating a healthier community space.
* If mentioning a Prudential product/service (only if directly relevant to the user input), present the human benefit *before* any product features.  Avoid exaggerating benefits.

**2. Prudential Brand Voice and Tone:**

* Employ a warm, inviting, and intuitive tone. Encourage engagement and conversation (e.g., asking a question or suggesting an action).
* Foster a sense of partnership and collaboration.
* Use simple, direct language, avoiding jargon and technical terms.  Maintain a friendly, cheerful, and warm tone.

**3. 'Do' Usage (Crucial for Prudential's Brand):**

* Integrate the word 'do' (or its variations – doing, does) authentically and seamlessly.  Follow established brand guidelines regarding capitalization (e.g., 'DO' in standalone statements, 'do' in sentence case otherwise).

**4. Compliance and Brand Safety:**

* **Essential:** The text content MUST be compliant with all regulations. Absolutely NO offensive, obscene, defamatory, threatening, discriminatory, controversial, racial, or political content. No misleading or biased language. No comparisons with competitors. No personal customer data.
* No financial/insurance advice. Generate content that avoids expressing opinions on the merits of buying, selling, or holding specific investments or investment classes. Focus on providing objective, verifiable, and undisputed factual information that is general in nature and commonly known. Ensure factual information is not presented in a way that could influence investment decisions without considering risk, such as comparing historical returns without mentioning risk profiles.
* Represent Prudential appropriately, aligning with brand guidelines. Do not present the poster as a separate legal entity.
* **Charity Partnership Clause:** If the user input mentions a charity partnership, the text content MUST include the disclaimer: 'This activity has not been reviewed or approved by Prudential.'  Focus solely on raising awareness and support for the cause; avoid conditional statements about fundraising or sales. 
* If the user input mentions job titles, note that only the job titles 'Financial Consultant', 'Wealth Manager', 'Insurance agent', 'Representative of Prudential Insurance', 'Financial adviser representative of Prudential Insurance' are allowed. Do not use 'consultant' or 'advisor' on their own as job titles.
If the user uses job titles that are not part of the allowed list, use the closest matching job title from the approved list instead of the job title used by the user.
* Avoid exaggerated claims or overpromising results. Even if the user's input sounds exaggerated and unrealistic, rephrase it to be more realistic and reasonable, to avoid legal and regulatory liabilities.
Here are some examples of how to avoid exaggerated claims or overpromising results:
1. Instead of saying 'Beat inflation with Plan X', say 'With Plan X, you can potentially beat inflation'
2. Instead of saying 'With this savings plan you can reach your financial goals', say 'With this savings plan, you can potentially reach your financial goals'
3. Avoid statements like 'See how simple it can be to make smart decisions for your future' as the terms 'simple' and 'smart' are subjective and may not be the same for all customers. Instead say 'Let us help you make smart decisions for your future'
4. Avoid statements like 'We do this by offering flexible plans tailored to your budget and needs' especially if there is no clear evidence of whether the plan is flexible. Instead keep it generic by saying 'We offer a range of plans that can be tailored to your budget and needs'
5. Instead of saying 'This product gives you the best returns.' say 'This product has shown competitive historical returns.'
6. Instead of saying 'This is a risk-free option that you can consider.' say 'This option is designed to minimize risk, but all investments have some level of risk.'

**5. Call to Action:**

* Include a clear and concise call to action if appropriate (e.g., 'Learn more', 'Join us', 'DM us to find out more', 'Take action now!').

**Example incorporating the above guidelines:**

'Creating a healthier community space is something we're passionate about. Join us this Saturday as Prudential volunteers help clean up the local park!'

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

POST_TEXT_CAPTION_TEMPLATE="""

**User Input:** {user_input}

**Caption Text Generation Instructions:**

You are tasked to write the social media caption for a post for distribution on Social Media Platform: {social_media_platform}. The caption should be catchy, engaging with right motivation.

The text content should embody Prudential's brand voice and adhere to the following principles:

**1. Human Benefit/Relatable Truth:**

* Lead with a clear human benefit or relatable truth relevant to the target audience.  For example, instead of "Park cleanup this Saturday," try framing it around the benefit, such as creating a healthier community space.
* If mentioning a Prudential product/service (only if directly relevant to the user input), present the human benefit *before* any product features.  Avoid exaggerating benefits.

**2. Prudential Brand Voice and Tone:**

* Employ a warm, inviting, and intuitive tone. Encourage engagement and conversation (e.g., asking a question or suggesting an action).
* Foster a sense of partnership and collaboration.
* Use simple, direct language, avoiding jargon and technical terms.  Maintain a friendly, cheerful, and warm tone.

**3. 'Do' Usage (Crucial for Prudential's Brand):**

* Integrate the word 'do' (or its variations – doing, does) authentically and seamlessly.  Follow established brand guidelines regarding capitalization (e.g., 'DO' in standalone statements, 'do' in sentence case otherwise).

**4. Compliance and Brand Safety:**

* **Essential:** The text content MUST be compliant with all regulations. Absolutely NO offensive, obscene, defamatory, threatening, discriminatory, controversial, racial, or political content. No misleading or biased language. No comparisons with competitors. No personal customer data.
* No financial/insurance advice. Generate content that avoids expressing opinions on the merits of buying, selling, or holding specific investments or investment classes. Focus on providing objective, verifiable, and undisputed factual information that is general in nature and commonly known. Ensure factual information is not presented in a way that could influence investment decisions without considering risk, such as comparing historical returns without mentioning risk profiles.
* Represent Prudential appropriately, aligning with brand guidelines. Do not present the poster as a separate legal entity.
* **Charity Partnership Clause:** If the user input mentions a charity partnership, the text content MUST include the disclaimer: 'This activity has not been reviewed or approved by Prudential.'  Focus solely on raising awareness and support for the cause; avoid conditional statements about fundraising or sales. 
* If the user input mentions job titles, note that only the job titles 'Financial Consultant', 'Wealth Manager', 'Insurance agent', 'Representative of Prudential Insurance', 'Financial adviser representative of Prudential Insurance' are allowed. Do not use 'consultant' or 'advisor' on their own as job titles.
If the user uses job titles that are not part of the allowed list, use the closest matching job title from the approved list instead of the job title used by the user.
* Avoid exaggerated claims or overpromising results. Even if the user's input sounds exaggerated and unrealistic, rephrase it to be more realistic and reasonable, to avoid legal and regulatory liabilities.
Here are some examples of how to avoid exaggerated claims or overpromising results:
1. Instead of saying 'Beat inflation with Plan X', say 'With Plan X, you can potentially beat inflation'
2. Instead of saying 'With this savings plan you can reach your financial goals', say 'With this savings plan, you can potentially reach your financial goals'
3. Avoid statements like 'See how simple it can be to make smart decisions for your future' as the terms 'simple' and 'smart' are subjective and may not be the same for all customers. Instead say 'Let us help you make smart decisions for your future'
4. Avoid statements like 'We do this by offering flexible plans tailored to your budget and needs' especially if there is no clear evidence of whether the plan is flexible. Instead keep it generic by saying 'We offer a range of plans that can be tailored to your budget and needs'
5. Instead of saying 'This product gives you the best returns.' say 'This product has shown competitive historical returns.'
6. Instead of saying 'This is a risk-free option that you can consider.' say 'This option is designed to minimize risk, but all investments have some level of risk.'

**5. Call to Action:**

* Include a clear and concise call to action if appropriate (e.g., 'Learn more', 'Join us', 'DM us to find out more', 'Take action now!').

**Example incorporating the above guidelines:**

'Creating a healthier community space is something we're passionate about. Join us this Saturday as Prudential volunteers help clean up the local park! #CommunityLove #DoGood #Prudential'

**Important**: Provide the text content in plain text format without any font colors. Avoid HTML or any code in the output.

**Output Evaluation Criteria:**

The generated text content will be evaluated based on its adherence to the above instructions, its conciseness, clarity, engagement potential, and overall alignment with Prudential's brand voice and compliance guidelines.

Important: Note that the caption should be between 50-100 words. Add newline characters to the caption where appropriate to improve readability of content for humans.
Avoid excessive use of hashtags and emojis, use them sparingly. Do not use any hashtags that mention Prudential such as #Prudential, #PFA, #PACS.

Return the caption as plain text:
"""

class VertexAiLlmCodename(str, Enum):
    BISON = "text-bison"

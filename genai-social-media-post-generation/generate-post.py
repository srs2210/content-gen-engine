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

import os
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel
from PIL import Image
import io

def generate_images(prompt, num_images=3):
    """
    Generate images using Imagen3 API via Vertex AI.
    
    Args:
    prompt (str): The text prompt to generate images from.
    num_images (int): Number of images to generate (default is 3).
    
    Returns:
    list: A list of PIL Image objects.
    """
    # Initialize Vertex AI
    vertexai.init(project=os.getenv("GOOGLE_CLOUD_PROJECT"), location="us-central1")

    # Create the image generation model
    generation_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")

    # Generate images
    generated_images = generation_model.generate_images(
        prompt=prompt,
        number_of_images=num_images,
        aspect_ratio="1:1",
        safety_filter_level="block_some",
        person_generation="allow_all",
    )

    # Convert generated images to PIL Image objects
    pil_images = []
    for img in generated_images:
        image_bytes = img._image_bytes
        pil_image = Image.open(io.BytesIO(image_bytes))
        pil_images.append(pil_image)

    return pil_images

# Example usage
if __name__ == "__main__":
    prompt = "A serene landscape with mountains and a lake at sunset"
    images = generate_images(prompt)
    for i, img in enumerate(images):
        img.save(f"generated_image_{i+1}.png")
        print(f"Image {i+1} saved as generated_image_{i+1}.png")

# utils.py
from models import SocialMediaPlatform

# Adapted from your original code for generating platform-specific captions
POST_TEXT_CAPTION_TEMPLATE = """
Act as a professional social media manager. Your task is to generate a compelling and engaging post caption.
The user's core idea is: "{user_input}".
The target platform is: {social_media_platform}.

Generate only the caption text. Do not add any extra explanations or introductory phrases.
"""

def generate_platform_specific_instructions(platform: SocialMediaPlatform) -> str:
    """Generates platform-specific instructions for caption generation."""
    if platform == SocialMediaPlatform.instagram:
        return (
            "Optimize for visual engagement. Keep the caption concise and impactful. "
            "Use relevant emojis sparingly and include a clear call to action."
        )
    elif platform == SocialMediaPlatform.linkedin:
        return (
            "Maintain a professional tone. Use industry keywords. "
            "Craft a compelling headline and encourage professional engagement (comments, shares)."
        )
    elif platform == SocialMediaPlatform.tiktok:
        return (
            "Keep it short, trendy, and punchy. Use popular hashtags relevant to the video's content. "
            "The tone should be very casual and engaging."
        )
    elif platform == SocialMediaPlatform.youtube_shorts:
        return (
            "The title is critical. Make it catchy and descriptive. The description can be longer, "
            "providing more context and using relevant keywords for searchability."
        )
    elif platform == SocialMediaPlatform.x:
        return (
            "Keep the caption strictly within 280 characters. "
            "Use relevant hashtags strategically and include a clear call to action."
        )
    else: # Default for Facebook, etc.
        return "Use a general tone. Facebook posts can be slightly longer, so feel free to provide more context."

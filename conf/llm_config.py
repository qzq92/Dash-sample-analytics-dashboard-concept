"""
LLM model configuration for vision-based traffic analysis.

Primary model is tried first. If rate-limited (HTTP 429),
the fallback model is used for that batch.
"""

VISION_MODEL_PRIMARY = "gemini-2.5-flash-preview-04-17"
VISION_MODEL_FALLBACK = "gemini-2.0-flash"

VISION_MODEL_PARAMS = {
    "temperature": 0.1,
    "max_output_tokens": 1024,
}

TRAFFIC_ANALYSIS_PROMPT = (
    "Analyze these traffic camera images from Singapore roads. "
    "For each camera ID, classify the visible traffic condition into exactly one category:\n\n"
    '- "heavy": Roads are congested, vehicles are closely packed or barely moving\n'
    '- "moderate": Noticeable traffic but vehicles are still moving\n'
    '- "light": Few vehicles, roads are mostly clear with some traffic\n'
    '- "clear": Very few or no vehicles visible\n\n'
    "If the image is too dark, blurry, or obstructed to determine, omit that camera from the response.\n\n"
    "Respond ONLY with a valid JSON object mapping camera_id to status. Example:\n"
    '{"1001": "heavy", "2703": "light", "4712": "clear"}\n\n'
    "Camera IDs and their images:"
)

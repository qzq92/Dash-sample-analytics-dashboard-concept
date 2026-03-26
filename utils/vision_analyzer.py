"""
Vision-based traffic condition analyzer using Google Gemini via LangChain.

Analyzes CCTV traffic camera images to classify traffic conditions as
heavy, moderate, light, or clear. Uses md5-based caching to avoid
redundant API calls for unchanged images.

Model selection is configured in conf/llm_config.py. The primary model
(Gemini 2.5 Flash) is tried first; on rate-limit (429), the fallback
model (Gemini 2.0 Flash) is used for that batch.

Designed for Google AI Studio free tier (15 RPM, 1500 RPD, 1M TPD).
Analysis is triggered only when the traffic conditions tab is active.
"""
import os
import json
import base64
import logging
import time
import threading
import requests
from typing import Dict, Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

from conf.llm_config import (
    VISION_MODEL_PRIMARY,
    VISION_MODEL_FALLBACK,
    VISION_MODEL_PARAMS,
    TRAFFIC_ANALYSIS_PROMPT,
)

logger = logging.getLogger(__name__)

_analysis_cache: Dict[str, dict] = {}
_last_analysis_time: float = 0
_analysis_lock = threading.Lock()
_analysis_running = False
_analysis_executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="vision-analysis")

ANALYSIS_INTERVAL_SECONDS = 300  # 5 minutes
BATCH_SIZE = 20

VALID_STATUSES = {"heavy", "moderate", "light", "clear"}


def _build_model(model_name: str):
    """Build a LangChain ChatGoogleGenerativeAI model instance."""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError:
        logger.warning("langchain-google-genai not installed, vision analysis disabled")
        return None

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.warning("GOOGLE_API_KEY not set, vision analysis disabled")
        return None

    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        **VISION_MODEL_PARAMS,
    )


def _download_image(url: str, timeout: int = 5) -> Optional[bytes]:
    """Download image bytes from URL."""
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.content
    except requests.exceptions.RequestException as e:
        logger.debug("Failed to download image %s: %s", url, e)
        return None


def _build_message_content(batch: List[Tuple[str, bytes]]) -> list:
    """Build LangChain HumanMessage content parts for a batch of images."""
    content_parts: list = [{"type": "text", "text": TRAFFIC_ANALYSIS_PROMPT}]

    for camera_id, image_bytes in batch:
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        content_parts.append({"type": "text", "text": f"\nCamera {camera_id}:"})
        content_parts.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
        })

    return content_parts


def _invoke_model(model, content_parts: list) -> Dict[str, str]:
    """
    Invoke the model and parse the JSON response.

    Returns:
        Dict mapping camera_id to valid traffic status.
        Only statuses in VALID_STATUSES are included; others are omitted.
    """
    from langchain_core.messages import HumanMessage

    response = model.invoke([HumanMessage(content=content_parts)])
    response_text = response.content.strip()

    if response_text.startswith("```"):
        lines = response_text.split("\n")
        response_text = "\n".join(lines[1:-1])

    raw_results = json.loads(response_text)

    return {
        str(cid): status
        for cid, status in raw_results.items()
        if status in VALID_STATUSES
    }


def _is_rate_limit_error(exc: Exception) -> bool:
    """Check if an exception indicates a 429 rate-limit error."""
    exc_str = str(exc)
    return "429" in exc_str or "ResourceExhausted" in exc_str or "rate" in exc_str.lower()


def _is_auth_error(exc: Exception) -> bool:
    """Check if an exception indicates an authentication/API key error."""
    exc_str = str(exc)
    return "401" in exc_str or "403" in exc_str or "InvalidArgument" in exc_str


def _analyze_batch(batch: List[Tuple[str, bytes]]) -> Dict[str, str]:
    """
    Send a batch of images for traffic classification.
    Tries the primary model first; falls back on rate-limit.

    Returns:
        Dict mapping camera_id to traffic status.
        Empty dict on failure (invalid key, endpoint down, etc.).
    """
    content_parts = _build_message_content(batch)

    # Try primary model
    primary = _build_model(VISION_MODEL_PRIMARY)
    if not primary:
        return {}

    try:
        results = _invoke_model(primary, content_parts)
        logger.info("Batch analyzed with %s (%d results)", VISION_MODEL_PRIMARY, len(results))
        return results
    except json.JSONDecodeError as e:
        logger.error("Failed to parse response from %s as JSON: %s", VISION_MODEL_PRIMARY, e)
        return {}
    except Exception as e:
        if _is_auth_error(e):
            logger.error("API authentication failed -- check GOOGLE_API_KEY: %s", e)
            return {}

        if not _is_rate_limit_error(e):
            logger.error("Analysis failed with %s: %s", VISION_MODEL_PRIMARY, e)
            return {}

        logger.warning(
            "Rate-limited on %s, falling back to %s",
            VISION_MODEL_PRIMARY,
            VISION_MODEL_FALLBACK,
        )

    # Fallback model
    fallback = _build_model(VISION_MODEL_FALLBACK)
    if not fallback:
        return {}

    try:
        results = _invoke_model(fallback, content_parts)
        logger.info("Batch analyzed with %s (fallback, %d results)", VISION_MODEL_FALLBACK, len(results))
        return results
    except json.JSONDecodeError as e:
        logger.error("Failed to parse response from %s as JSON: %s", VISION_MODEL_FALLBACK, e)
        return {}
    except Exception as e:
        if _is_auth_error(e):
            logger.error("API authentication failed on fallback -- check GOOGLE_API_KEY: %s", e)
        else:
            logger.error("Analysis failed with fallback %s: %s", VISION_MODEL_FALLBACK, e)
        return {}


def _run_analysis(camera_data: Dict[str, dict]) -> None:
    """
    Perform the full analysis cycle (runs in background thread).

    Downloads images for cameras whose md5/URL has changed,
    batches them, sends to Gemini, and updates the cache.
    Only valid statuses (heavy/moderate/light/clear) are cached.
    """
    global _last_analysis_time

    cameras_to_analyze = []
    for camera_id, info in camera_data.items():
        image_url = info.get("image_url", "")
        md5 = info.get("md5", "")
        cache_key = md5 if md5 else image_url

        cached = _analysis_cache.get(str(camera_id))
        if cached and cached.get("cache_key") == cache_key:
            continue

        if image_url:
            cameras_to_analyze.append((str(camera_id), image_url))

    if not cameras_to_analyze:
        _last_analysis_time = time.time()
        logger.info("All camera images unchanged, skipping analysis")
        return

    logger.info(
        "Analyzing %d cameras (out of %d total)",
        len(cameras_to_analyze),
        len(camera_data),
    )

    downloaded: List[Tuple[str, bytes]] = []
    with ThreadPoolExecutor(max_workers=10) as dl_pool:
        future_map = {
            dl_pool.submit(_download_image, url): (cid, url)
            for cid, url in cameras_to_analyze
        }
        for future in as_completed(future_map):
            cid, url = future_map[future]
            try:
                image_bytes = future.result()
                if image_bytes:
                    downloaded.append((cid, image_bytes))
            except Exception as e:
                logger.debug("Download error for camera %s: %s", cid, e)

    if not downloaded:
        _last_analysis_time = time.time()
        return

    batches = [downloaded[i : i + BATCH_SIZE] for i in range(0, len(downloaded), BATCH_SIZE)]

    for batch in batches:
        results = _analyze_batch(batch)
        if not results:
            continue

        now = time.time()
        for cid, status in results.items():
            md5 = camera_data.get(cid, {}).get("md5", "")
            url = camera_data.get(cid, {}).get("image_url", "")
            _analysis_cache[cid] = {
                "status": status,
                "cache_key": md5 if md5 else url,
                "timestamp": now,
            }
        logger.info(
            "Batch analyzed: %s",
            {cid: results.get(cid, "?") for cid, _ in batch},
        )

    _last_analysis_time = time.time()
    logger.info("Vision analysis cycle complete, %d cameras in cache", len(_analysis_cache))


def _run_analysis_safe(camera_data: Dict[str, dict]) -> None:
    """Wrapper that ensures _analysis_running is reset on completion."""
    global _analysis_running
    try:
        _run_analysis(camera_data)
    except Exception as e:
        logger.error("Vision analysis error: %s", e)
    finally:
        with _analysis_lock:
            _analysis_running = False


def trigger_analysis(camera_data: Dict[str, dict]) -> None:
    """
    Non-blocking: submit analysis to background thread if not already running
    and the rate-limit interval has elapsed.
    """
    global _analysis_running

    with _analysis_lock:
        if _analysis_running:
            return
        if time.time() - _last_analysis_time < ANALYSIS_INTERVAL_SECONDS:
            return
        _analysis_running = True

    _analysis_executor.submit(_run_analysis_safe, camera_data)


def get_cached_analysis() -> Dict[str, str]:
    """Return current cached analysis results without triggering new analysis."""
    return {cid: info.get("status") for cid, info in _analysis_cache.items() if info.get("status") in VALID_STATUSES}


def get_camera_status(camera_id: str) -> Optional[str]:
    """Get cached traffic status for a specific camera. Returns None if not available."""
    cached = _analysis_cache.get(str(camera_id))
    if cached and cached.get("status") in VALID_STATUSES:
        return cached["status"]
    return None


def get_status_color(status: str) -> str:
    """Map traffic status to display color."""
    return {
        "heavy": "#FF4444",
        "moderate": "#FFA500",
        "light": "#4CAF50",
        "clear": "#2196F3",
    }.get(status, "#999999")


def get_status_marker_url(status: str) -> str:
    """Map traffic status to leaflet colored marker icon URL."""
    color = {
        "heavy": "red",
        "moderate": "orange",
        "light": "green",
        "clear": "blue",
    }.get(status, "green")
    return (
        f"https://raw.githubusercontent.com/pointhi/leaflet-color-markers"
        f"/master/img/marker-icon-2x-{color}.png"
    )


def get_analysis_summary() -> Dict[str, int]:
    """Get a count summary of traffic statuses across all cached cameras."""
    summary: Dict[str, int] = {}
    for info in _analysis_cache.values():
        status = info.get("status")
        if status in VALID_STATUSES:
            summary[status] = summary.get(status, 0) + 1
    return summary


def is_analysis_available() -> bool:
    """Check if any valid analysis results are cached."""
    return any(info.get("status") in VALID_STATUSES for info in _analysis_cache.values())

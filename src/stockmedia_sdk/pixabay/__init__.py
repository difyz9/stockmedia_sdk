"""
Pixabay API client for stockmedia_sdk 鈥?a clean, typed wrapper for the Pixabay API.

Usage::

    from stockmedia_sdk.pixabay import PixabayClient

    # or via the top-level package:
    # from stockmedia_sdk import PixabayClient

    client = PixabayClient(api_key="YOUR_API_KEY")

    # Search images
    result = client.search_images("yellow flowers", image_type="photo")
    for img in result.hits:
        print(img.webformat_url)

    # Search videos
    result = client.search_videos("ocean")
    for video in result.hits:
        print(video.videos.medium.url)

    # Auto-paginate through all results
    for page in client.search_images_all("sunset", max_pages=3):
        for img in page:
            print(img.large_image_url)
"""

from .client import PixabayClient
from .enums import Category, Color, ImageType, Language, Order, Orientation, VideoType
from .exceptions import (
    PixabayAuthenticationError,
    PixabayError,
    PixabayNotFoundError,
    PixabayRateLimitError,
    PixabayServerError,
)
from .models import (
    Image,
    PixabayResponse,
    RateLimitInfo,
    Video,
    VideoQuality,
    VideoSizeSet,
)

__all__ = [
    # Client
    "PixabayClient",
    # Models
    "Image",
    "Video",
    "VideoQuality",
    "VideoSizeSet",
    "PixabayResponse",
    "RateLimitInfo",
    # Enums
    "ImageType",
    "VideoType",
    "Orientation",
    "Order",
    "Category",
    "Color",
    "Language",
    # Exceptions
    "PixabayError",
    "PixabayAuthenticationError",
    "PixabayRateLimitError",
    "PixabayNotFoundError",
    "PixabayServerError",
]

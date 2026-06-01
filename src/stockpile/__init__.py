"""
Stockpile — Python SDKs for free stock media APIs.

Usage::

    from stockpile import PexelsClient, PixabayClient

    # Pexels
    pexels = PexelsClient(api_key="...")
    for photo in pexels.search_photos("nature").results:
        print(photo.src.large)

    # Pixabay
    pixabay = PixabayClient(api_key="...")
    for img in pixabay.search_images("ocean").hits:
        print(img.webformat_url)
"""

# ── Pexels ───────────────────────────────────────────────────────────────

from .pexels.client import PexelsClient
from .pexels.enums import CollectionType, Color, Locale, Orientation, Size, SortOrder
from .pexels.exceptions import (
    PexelsAuthenticationError,
    PexelsError,
    PexelsNotFoundError,
    PexelsRateLimitError,
    PexelsServerError,
)
from .pexels.models import (
    Collection,
    PagedResponse,
    Photo,
    PhotoSource,
    RateLimitInfo,
    Video,
    VideoFile,
    VideoPicture,
    VideoUser,
)

# ── Pixabay ──────────────────────────────────────────────────────────────

from .pixabay.client import PixabayClient
from .pixabay.enums import Category, ImageType, Language, Order, VideoType
from .pixabay.exceptions import (
    PixabayAuthenticationError,
    PixabayError,
    PixabayNotFoundError,
    PixabayRateLimitError,
    PixabayServerError,
)
from .pixabay.models import Image, PixabayResponse, VideoQuality, VideoSizeSet

__all__ = [
    # Pexels
    "PexelsClient",
    "Photo",
    "PhotoSource",
    "Video",
    "VideoFile",
    "VideoPicture",
    "VideoUser",
    "Collection",
    "PagedResponse",
    "RateLimitInfo",
    "Orientation",
    "Size",
    "Color",
    "Locale",
    "CollectionType",
    "SortOrder",
    "PexelsError",
    "PexelsAuthenticationError",
    "PexelsRateLimitError",
    "PexelsNotFoundError",
    "PexelsServerError",
    # Pixabay
    "PixabayClient",
    "Image",
    "VideoQuality",
    "VideoSizeSet",
    "PixabayResponse",
    "ImageType",
    "VideoType",
    "Order",
    "Category",
    "Language",
    "PixabayError",
    "PixabayAuthenticationError",
    "PixabayRateLimitError",
    "PixabayNotFoundError",
    "PixabayServerError",
]

from importlib.metadata import version as _version

try:
    __version__ = _version("stockpile")
except Exception:
    __version__ = "0.0.0.dev"

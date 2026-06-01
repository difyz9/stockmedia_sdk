"""
Pexels SDK for Python — A clean, typed wrapper for the Pexels API v1.

Usage::

    from pexels_sdk import PexelsClient

    client = PexelsClient(api_key="YOUR_API_KEY")

    # Search photos
    result = client.search_photos("nature", per_page=10)
    for photo in result.results:
        print(photo.photographer, photo.src.large)

    # Get a photo by ID
    photo = client.get_photo(2014422)

    # Search videos
    videos = client.search_videos("ocean")

    # Paginate through all results
    for page in client.search_photos_all("sunset", max_pages=3):
        for photo in page:
            print(photo.url)
"""

from .client import PexelsClient
from .enums import CollectionType, Color, Locale, Orientation, Size, SortOrder
from .exceptions import (
    PexelsAuthenticationError,
    PexelsError,
    PexelsNotFoundError,
    PexelsRateLimitError,
    PexelsServerError,
)
from .models import (
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

__all__ = [
    # Client
    "PexelsClient",
    # Models
    "Photo",
    "PhotoSource",
    "Video",
    "VideoFile",
    "VideoPicture",
    "VideoUser",
    "Collection",
    "PagedResponse",
    "RateLimitInfo",
    # Enums
    "Orientation",
    "Size",
    "Color",
    "Locale",
    "CollectionType",
    "SortOrder",
    # Exceptions
    "PexelsError",
    "PexelsAuthenticationError",
    "PexelsRateLimitError",
    "PexelsNotFoundError",
    "PexelsServerError",
]

__version__ = "1.0.0"

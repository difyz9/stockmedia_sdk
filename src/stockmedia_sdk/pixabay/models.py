"""
Data models for Pixabay API responses.

All models are dataclasses with a ``from_dict()`` classmethod
that handles JSON-to-model conversion recursively.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


# ── Image model ─────────────────────────────────────────────────────────


@dataclass(frozen=True)
class Image:
    """A Pixabay image.

    Attributes:
        id: Unique identifier for this image.
        page_url: Source page on Pixabay.
        type: Image type ("photo", "illustration", "vector").
        tags: Comma-separated list of tags.
        preview_url: Low resolution preview (max 150px).
        preview_width: Preview image width.
        preview_height: Preview image height.
        webformat_url: Medium sized image (max 640px). URL valid for 24 hours.
        webformat_width: Webformat image width.
        webformat_height: Webformat image height.
        large_image_url: Scaled image (max 1280px).
        full_hd_url: Full HD image (max 1920px). Requires full API access.
        image_url: Original image URL. Requires full API access.
        image_width: Original image width.
        image_height: Original image height.
        image_size: Original image file size in bytes.
        views: Total number of views.
        downloads: Total number of downloads.
        likes: Total number of likes.
        comments: Total number of comments.
        user_id: Contributor user ID.
        user: Contributor username.
        user_image_url: Profile picture URL (250x250 px).
        vector_url: URL to vector resource. Requires full API access.
    """

    id: int
    page_url: str = ""
    type: str = ""
    tags: str = ""
    preview_url: str = ""
    preview_width: int = 0
    preview_height: int = 0
    webformat_url: str = ""
    webformat_width: int = 0
    webformat_height: int = 0
    large_image_url: str = ""
    full_hd_url: str = ""
    image_url: str = ""
    image_width: int = 0
    image_height: int = 0
    image_size: int = 0
    views: int = 0
    downloads: int = 0
    likes: int = 0
    comments: int = 0
    user_id: int = 0
    user: str = ""
    user_image_url: str = ""
    vector_url: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> Image:
        return cls(
            id=data["id"],
            page_url=data.get("pageURL", ""),
            type=data.get("type", ""),
            tags=data.get("tags", ""),
            preview_url=data.get("previewURL", ""),
            preview_width=data.get("previewWidth", 0),
            preview_height=data.get("previewHeight", 0),
            webformat_url=data.get("webformatURL", ""),
            webformat_width=data.get("webformatWidth", 0),
            webformat_height=data.get("webformatHeight", 0),
            large_image_url=data.get("largeImageURL", ""),
            full_hd_url=data.get("fullHDURL", ""),
            image_url=data.get("imageURL", ""),
            image_width=data.get("imageWidth", 0),
            image_height=data.get("imageHeight", 0),
            image_size=data.get("imageSize", 0),
            views=data.get("views", 0),
            downloads=data.get("downloads", 0),
            likes=data.get("likes", 0),
            comments=data.get("comments", 0),
            user_id=data.get("user_id", 0),
            user=data.get("user", ""),
            user_image_url=data.get("userImageURL", ""),
            vector_url=data.get("vectorURL", ""),
        )

    @property
    def webformat_180(self) -> str:
        """Get 180px tall version of the webformat image."""
        return self.webformat_url.replace("_640", "_180")

    @property
    def webformat_340(self) -> str:
        """Get 340px tall version of the webformat image."""
        return self.webformat_url.replace("_640", "_340")

    @property
    def webformat_960(self) -> str:
        """Get 960 x 720 px version of the webformat image."""
        return self.webformat_url.replace("_640", "_960")


# ── Video models ────────────────────────────────────────────────────────


@dataclass(frozen=True)
class VideoQuality:
    """A specific resolution/quality version of a Pixabay video.

    Attributes:
        url: Video URL. Append ?download=1 to force download.
        width: Video width in pixels.
        height: Video height in pixels.
        size: Approximate file size in bytes.
        thumbnail: Poster/thumbnail image URL for this rendition.
    """

    url: str = ""
    width: int = 0
    height: int = 0
    size: int = 0
    thumbnail: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> VideoQuality:
        return cls(
            url=data.get("url", ""),
            width=data.get("width", 0),
            height=data.get("height", 0),
            size=data.get("size", 0),
            thumbnail=data.get("thumbnail", ""),
        )


@dataclass(frozen=True)
class VideoSizeSet:
    """All available video sizes for a Pixabay video.

    Attributes:
        large: Usually 3840x2160 (may be empty if unavailable).
        medium: Usually 1920x1080 (always available).
        small: Usually 1280x720 (always available).
        tiny: Usually 960x540 (always available).
    """

    large: VideoQuality = field(default_factory=VideoQuality)
    medium: VideoQuality = field(default_factory=VideoQuality)
    small: VideoQuality = field(default_factory=VideoQuality)
    tiny: VideoQuality = field(default_factory=VideoQuality)

    @classmethod
    def from_dict(cls, data: dict) -> VideoSizeSet:
        return cls(
            large=VideoQuality.from_dict(data.get("large", {})),
            medium=VideoQuality.from_dict(data.get("medium", {})),
            small=VideoQuality.from_dict(data.get("small", {})),
            tiny=VideoQuality.from_dict(data.get("tiny", {})),
        )


@dataclass(frozen=True)
class Video:
    """A Pixabay video.

    Attributes:
        id: Unique identifier for this video.
        page_url: Source page on Pixabay.
        type: Video type ("film", "animation").
        tags: Comma-separated list of tags.
        duration: Video duration in seconds.
        videos: Set of differently sized video streams (large, medium, small, tiny).
        views: Total number of views.
        downloads: Total number of downloads.
        likes: Total number of likes.
        comments: Total number of comments.
        user_id: Contributor user ID.
        user: Contributor username.
        user_image_url: Profile picture URL (250x250 px).
    """

    id: int
    page_url: str = ""
    type: str = ""
    tags: str = ""
    duration: int = 0
    videos: VideoSizeSet = field(default_factory=VideoSizeSet)
    views: int = 0
    downloads: int = 0
    likes: int = 0
    comments: int = 0
    user_id: int = 0
    user: str = ""
    user_image_url: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> Video:
        return cls(
            id=data["id"],
            page_url=data.get("pageURL", ""),
            type=data.get("type", ""),
            tags=data.get("tags", ""),
            duration=data.get("duration", 0),
            videos=VideoSizeSet.from_dict(data.get("videos", {})),
            views=data.get("views", 0),
            downloads=data.get("downloads", 0),
            likes=data.get("likes", 0),
            comments=data.get("comments", 0),
            user_id=data.get("user_id", 0),
            user=data.get("user", ""),
            user_image_url=data.get("userImageURL", ""),
        )


# ── Paginated response ──────────────────────────────────────────────────


@dataclass(frozen=True)
class PixabayResponse(Generic[T]):
    """Wraps a Pixabay API response.

    Attributes:
        hits: List of typed model instances (Image or Video).
        total: The total number of hits available.
        total_hits: Number of items accessible through the API (max 500 per query).
        page: Current page number (estimated from per_page and offset).
        per_page: Number of results per page.
    """

    hits: list[T]
    total: int = 0
    total_hits: int = 0
    page: int = 1
    per_page: int = 20

    def __bool__(self) -> bool:
        return len(self.hits) > 0

    @property
    def has_next(self) -> bool:
        """True if there is likely a next page of results."""
        return self.page * self.per_page < self.total_hits

    @property
    def total_pages(self) -> int:
        """Estimated total number of pages."""
        if self.per_page <= 0:
            return 0
        return (self.total_hits + self.per_page - 1) // self.per_page


# ── Rate limit info ─────────────────────────────────────────────────────


@dataclass(frozen=True)
class RateLimitInfo:
    """Rate limit status from response headers.

    Attributes:
        limit: Maximum requests per 60 second window.
        remaining: Remaining requests in the current window.
        reset: Seconds until the current rate limit window resets.
    """

    limit: int | None = None
    remaining: int | None = None
    reset: int | None = None

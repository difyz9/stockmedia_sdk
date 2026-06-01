"""
Data models for Pexels API responses.

All models are dataclasses with a ``from_dict()`` classmethod
that handles JSON-to-model conversion recursively.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")


# ── Photo-related models ──────────────────────────────────────────────


@dataclass(frozen=True)
class PhotoSource:
    """URLs for different sizes/resolutions of a photo."""

    original: str = ""
    large2x: str = ""
    large: str = ""
    medium: str = ""
    small: str = ""
    portrait: str = ""
    landscape: str = ""
    tiny: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> PhotoSource:
        return cls(
            original=data.get("original", ""),
            large2x=data.get("large2x", ""),
            large=data.get("large", ""),
            medium=data.get("medium", ""),
            small=data.get("small", ""),
            portrait=data.get("portrait", ""),
            landscape=data.get("landscape", ""),
            tiny=data.get("tiny", ""),
        )


@dataclass(frozen=True)
class Photo:
    """A Pexels photo."""

    id: int
    width: int
    height: int
    url: str
    photographer: str
    photographer_url: str
    photographer_id: int
    avg_color: str
    liked: bool = False
    alt: str = ""
    src: PhotoSource = field(default_factory=PhotoSource)

    @classmethod
    def from_dict(cls, data: dict) -> Photo:
        return cls(
            id=data["id"],
            width=data["width"],
            height=data["height"],
            url=data["url"],
            photographer=data["photographer"],
            photographer_url=data["photographer_url"],
            photographer_id=data["photographer_id"],
            avg_color=data.get("avg_color", ""),
            liked=data.get("liked", False),
            alt=data.get("alt", ""),
            src=PhotoSource.from_dict(data.get("src", {})),
        )


# ── Video-related models ──────────────────────────────────────────────


@dataclass(frozen=True)
class VideoUser:
    """Videographer info."""

    id: int
    name: str
    url: str

    @classmethod
    def from_dict(cls, data: dict) -> VideoUser:
        return cls(
            id=data["id"],
            name=data["name"],
            url=data["url"],
        )


@dataclass(frozen=True)
class VideoFile:
    """A specific resolution/quality version of a video."""

    id: int
    quality: str
    file_type: str
    width: int | None = None
    height: int | None = None
    fps: float | None = None
    link: str = ""

    @classmethod
    def from_dict(cls, data: dict) -> VideoFile:
        return cls(
            id=data["id"],
            quality=data.get("quality", ""),
            file_type=data.get("file_type", ""),
            width=data.get("width"),
            height=data.get("height"),
            fps=data.get("fps"),
            link=data.get("link", ""),
        )


@dataclass(frozen=True)
class VideoPicture:
    """A preview/thumbnail image for a video."""

    id: int
    picture: str
    nr: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> VideoPicture:
        return cls(
            id=data["id"],
            picture=data.get("picture", ""),
            nr=data.get("nr", 0),
        )


@dataclass(frozen=True)
class Video:
    """A Pexels video."""

    id: int
    width: int
    height: int
    duration: int
    url: str
    image: str
    user: VideoUser = field(default_factory=lambda: VideoUser(0, "", ""))
    video_files: list[VideoFile] = field(default_factory=list)
    video_pictures: list[VideoPicture] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> Video:
        return cls(
            id=data["id"],
            width=data["width"],
            height=data["height"],
            duration=data["duration"],
            url=data["url"],
            image=data["image"],
            user=VideoUser.from_dict(data.get("user", {})),
            video_files=[VideoFile.from_dict(vf) for vf in data.get("video_files", [])],
            video_pictures=[VideoPicture.from_dict(vp) for vp in data.get("video_pictures", [])],
        )


# ── Collection models ─────────────────────────────────────────────────


@dataclass(frozen=True)
class Collection:
    """A Pexels curated collection."""

    id: str
    title: str
    description: str = ""
    private: bool = False
    media_count: int = 0
    photos_count: int = 0
    videos_count: int = 0

    @classmethod
    def from_dict(cls, data: dict) -> Collection:
        return cls(
            id=str(data.get("id", "")),
            title=data.get("title", ""),
            description=data.get("description", ""),
            private=data.get("private", False),
            media_count=data.get("media_count", 0),
            photos_count=data.get("photos_count", 0),
            videos_count=data.get("videos_count", 0),
        )


# ── Paginated response ────────────────────────────────────────────────


@dataclass(frozen=True)
class PagedResponse(Generic[T]):
    """Wraps a paginated API response.

    Attributes:
        results: List of typed model instances (Photo, Video, or Collection).
        page: Current page number.
        per_page: Number of results per page.
        total_results: Total number of results across all pages.
        next_page: URL for the next page, or None if on the last page.
        prev_page: URL for the previous page, or None if on the first page.
        url: Canonical Pexels URL for this search.
    """

    results: list[T]
    page: int
    per_page: int
    total_results: int
    next_page: str | None = None
    prev_page: str | None = None
    url: str = ""

    def __bool__(self) -> bool:
        return len(self.results) > 0

    @property
    def has_next(self) -> bool:
        """True if there is a next page of results."""
        return self.next_page is not None

    @property
    def has_prev(self) -> bool:
        """True if there is a previous page of results."""
        return self.prev_page is not None

    @property
    def total_pages(self) -> int:
        """Estimated total number of pages."""
        if self.per_page <= 0:
            return 0
        return (self.total_results + self.per_page - 1) // self.per_page


# ── Rate limit info ───────────────────────────────────────────────────


@dataclass(frozen=True)
class RateLimitInfo:
    """Rate limit status from response headers.

    Attributes:
        limit: Total requests allowed per period.
        remaining: Remaining requests in the current period.
        reset: Unix timestamp when the limit resets.
    """

    limit: int | None = None
    remaining: int | None = None
    reset: int | None = None

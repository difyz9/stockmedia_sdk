"""
Pixabay API client.

Usage::

    from stockpile.pixabay import PixabayClient
    # or: from stockpile import PixabayClient

    client = PixabayClient(api_key="YOUR_API_KEY")

    # Search images
    result = client.search_images("yellow flowers", image_type="photo", per_page=20)
    for img in result.hits:
        print(img.webformat_url)

    # Search videos
    result = client.search_videos("ocean", per_page=10)
    for video in result.hits:
        print(video.videos.medium.url)

    # Auto-paginate through all results
    for page in client.search_images_all("sunset", max_pages=3):
        for img in page:
            print(img.page_url)
"""

from __future__ import annotations

import time
from typing import Any, Generator

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .enums import Category, Color, ImageType, Language, Order, Orientation, VideoType
from .exceptions import (
    PixabayAuthenticationError,
    PixabayError,
    PixabayNotFoundError,
    PixabayRateLimitError,
    PixabayServerError,
)
from .models import Image, PixabayResponse, RateLimitInfo, Video

# ── Constants ───────────────────────────────────────────────────────────

BASE_URL_IMAGES = "https://pixabay.com/api/"
BASE_URL_VIDEOS = "https://pixabay.com/api/videos/"
DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 20
MAX_PER_PAGE = 200
MAX_TOTAL_RESULTS = 500  # Pixabay caps responses at 500 hits per query
DEFAULT_TIMEOUT = 30  # seconds


# ── Helpers ─────────────────────────────────────────────────────────────


def _clean_params(params: dict[str, Any]) -> dict[str, Any]:
    """Remove None values from a params dict so they aren't sent to the API."""
    return {k: v for k, v in params.items() if v is not None}


def _to_pixabay_param(value: Any) -> str | None:
    """Convert an enum or raw value to a Pixabay API parameter string."""
    if value is None:
        return None
    if hasattr(value, "value"):
        return value.value
    return str(value)


# ── Client ──────────────────────────────────────────────────────────────


class PixabayClient:
    """Client for the Pixabay API.

    Args:
        api_key: Your Pixabay API key. Get one at https://pixabay.com/api/docs/.
        timeout: Request timeout in seconds (default: 30).
        max_retries: Number of retries on 5xx / connection errors (default: 2).
        auto_rate_limit_wait: If True, automatically sleep when rate-limited
            and retry the request (default: False).

    Rate limits (as documented):
        - 100 requests per 60 seconds
    """

    def __init__(
        self,
        api_key: str,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = 2,
        auto_rate_limit_wait: bool = False,
    ):
        if not api_key:
            raise ValueError("api_key is required")

        self.api_key = api_key
        self.timeout = timeout
        self.auto_rate_limit_wait = auto_rate_limit_wait
        self._last_rate_limit_info: RateLimitInfo | None = None

        # Build session with retry logic
        self._session = requests.Session()
        self._session.headers.update(
            {
                "Accept": "application/json",
                "User-Agent": "pixabay-sdk-py/1.0.0",
            }
        )

        if max_retries > 0:
            retry_strategy = Retry(
                total=max_retries,
                backoff_factor=0.5,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET"],
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            self._session.mount("https://", adapter)
            self._session.mount("http://", adapter)

    # ── Rate limit info ─────────────────────────────────────────────────

    @property
    def rate_limit_info(self) -> RateLimitInfo | None:
        """Rate limit status from the most recent API call."""
        return self._last_rate_limit_info

    # ── Internal request helpers ────────────────────────────────────────

    def _parse_rate_limit(self, response: requests.Response) -> RateLimitInfo:
        """Extract rate limit info from response headers."""
        limit = response.headers.get("X-RateLimit-Limit")
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset = response.headers.get("X-RateLimit-Reset")
        info = RateLimitInfo(
            limit=int(limit) if limit is not None else None,
            remaining=int(remaining) if remaining is not None else None,
            reset=int(reset) if reset is not None else None,
        )
        self._last_rate_limit_info = info
        return info

    def _request(self, url: str, params: dict[str, Any] | None = None) -> dict:
        """Make a GET request and return the parsed JSON body.

        The API key is always added as a query parameter.

        Raises:
            PixabayAuthenticationError: 401, 403
            PixabayNotFoundError: 404
            PixabayRateLimitError: 429
            PixabayServerError: 5xx
            PixabayError: other non-2xx
        """
        params = _clean_params(params or {})
        params["key"] = self.api_key

        response = self._session.get(url, params=params, timeout=self.timeout)
        rate_info = self._parse_rate_limit(response)

        if response.status_code == 200:
            return response.json()

        # ── Error handling ──
        error_msg = response.text.strip()

        if response.status_code in (401, 403):
            raise PixabayAuthenticationError(
                error_msg, status_code=response.status_code
            )
        elif response.status_code == 404:
            raise PixabayNotFoundError(
                error_msg, status_code=response.status_code
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise PixabayRateLimitError(
                error_msg,
                status_code=429,
                retry_after=int(retry_after) if retry_after is not None else None,
                limit=rate_info.limit,
                remaining=rate_info.remaining,
                reset=rate_info.reset,
            )
        elif response.status_code >= 500:
            raise PixabayServerError(
                error_msg, status_code=response.status_code
            )
        else:
            raise PixabayError(
                error_msg, status_code=response.status_code
            )

    def _build_response(
        self,
        data: dict,
        model_from_dict,
        page: int = 1,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> PixabayResponse:
        """Build a PixabayResponse from raw API JSON."""
        hits = [model_from_dict(item) for item in data.get("hits", [])]
        return PixabayResponse(
            hits=hits,
            total=data.get("total", 0),
            total_hits=data.get("totalHits", 0),
            page=page,
            per_page=per_page,
        )

    def _paginate(
        self,
        url: str,
        params: dict[str, Any],
        model_from_dict,
        max_pages: int | None = None,
    ) -> Generator[list, None, None]:
        """Generator that yields pages of results automatically.

        Pixabay does not return next_page URLs, so we estimate based on
        per_page and totalHits.

        Args:
            url: API endpoint URL.
            params: Query parameters dict (page will be managed automatically).
            model_from_dict: Model classmethod for parsing items.
            max_pages: Maximum pages to fetch (None = all available, capped at 500 results).
        """
        page = params.get("page", DEFAULT_PAGE)
        per_page = params.get("per_page", DEFAULT_PER_PAGE)
        pages_fetched = 0
        total_yielded = 0

        while True:
            params["page"] = page
            data = self._request(url, params.copy())
            hits = [model_from_dict(item) for item in data.get("hits", [])]
            yield hits

            total_yielded += len(hits)
            pages_fetched += 1

            # Stop conditions
            if max_pages is not None and pages_fetched >= max_pages:
                break
            if len(hits) < per_page:
                break
            if total_yielded >= data.get("totalHits", 0):
                break
            if total_yielded >= MAX_TOTAL_RESULTS:
                break

            page += 1

    # ── Images API ──────────────────────────────────────────────────────

    def search_images(
        self,
        query: str | None = None,
        lang: Language | str | None = None,
        image_type: ImageType | str | None = None,
        orientation: Orientation | str | None = None,
        category: Category | str | None = None,
        min_width: int | None = None,
        min_height: int | None = None,
        colors: Color | str | list[Color | str] | None = None,
        editors_choice: bool = False,
        safesearch: bool = False,
        order: Order | str | None = None,
        page: int = DEFAULT_PAGE,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> PixabayResponse[Image]:
        """Search for images on Pixabay.

        Args:
            query: Search query (e.g., "yellow flowers"). If omitted, all
                images are returned. Max 100 characters.
            lang: Language code for search.
            image_type: Filter by image type (all, photo, illustration, vector).
            orientation: Filter by orientation (all, horizontal, vertical).
            category: Filter by category.
            min_width: Minimum image width in pixels.
            min_height: Minimum image height in pixels.
            colors: Filter by color(s). Can be a single Color, a string, or a
                list of Color/string values (comma-joined).
            editors_choice: If True, only return Editor's Choice images.
            safesearch: If True, only return images suitable for all ages.
            order: Sort order (popular, latest).
            page: Page number (starts at 1).
            per_page: Results per page (3–200, default 20).

        Returns:
            PixabayResponse of Image objects.
        """
        if query is not None and len(query.strip()) > 100:
            raise ValueError("query may not exceed 100 characters")

        # Build colors param
        colors_param: str | None = None
        if colors is not None:
            if isinstance(colors, list):
                colors_param = ",".join(_to_pixabay_param(c) for c in colors if c is not None)
            else:
                colors_param = _to_pixabay_param(colors)

        params: dict[str, Any] = {
            "q": query.strip() if query else None,
            "lang": _to_pixabay_param(lang),
            "image_type": _to_pixabay_param(image_type),
            "orientation": _to_pixabay_param(orientation),
            "category": _to_pixabay_param(category),
            "min_width": min_width,
            "min_height": min_height,
            "colors": colors_param,
            "editors_choice": "true" if editors_choice else None,
            "safesearch": "true" if safesearch else None,
            "order": _to_pixabay_param(order),
            "page": page,
            "per_page": min(per_page, MAX_PER_PAGE),
        }
        data = self._request(BASE_URL_IMAGES, params)
        return self._build_response(data, Image.from_dict, page, min(per_page, MAX_PER_PAGE))

    def search_images_all(
        self,
        query: str | None = None,
        lang: Language | str | None = None,
        image_type: ImageType | str | None = None,
        orientation: Orientation | str | None = None,
        category: Category | str | None = None,
        min_width: int | None = None,
        min_height: int | None = None,
        colors: Color | str | list[Color | str] | None = None,
        editors_choice: bool = False,
        safesearch: bool = False,
        order: Order | str | None = None,
        per_page: int = DEFAULT_PER_PAGE,
        max_pages: int | None = None,
    ) -> Generator[list[Image], None, None]:
        """Search images and auto-paginate through all results.

        Yields lists of Image objects, one page at a time.

        Args:
            max_pages: Maximum pages to fetch (None = all available).

        Yields:
            List of Image objects for each page.
        """
        if query is not None and len(query.strip()) > 100:
            raise ValueError("query may not exceed 100 characters")

        colors_param: str | None = None
        if colors is not None:
            if isinstance(colors, list):
                colors_param = ",".join(_to_pixabay_param(c) for c in colors if c is not None)
            else:
                colors_param = _to_pixabay_param(colors)

        params: dict[str, Any] = {
            "q": query.strip() if query else None,
            "lang": _to_pixabay_param(lang),
            "image_type": _to_pixabay_param(image_type),
            "orientation": _to_pixabay_param(orientation),
            "category": _to_pixabay_param(category),
            "min_width": min_width,
            "min_height": min_height,
            "colors": colors_param,
            "editors_choice": "true" if editors_choice else None,
            "safesearch": "true" if safesearch else None,
            "order": _to_pixabay_param(order),
            "per_page": min(per_page, MAX_PER_PAGE),
        }
        yield from self._paginate(BASE_URL_IMAGES, params, Image.from_dict, max_pages)

    def get_image(self, image_id: int) -> Image:
        """Get a single image by its Pixabay ID.

        Args:
            image_id: The Pixabay image ID.

        Returns:
            An Image object.
        """
        if image_id <= 0:
            raise ValueError("image_id must be a positive integer")
        data = self._request(BASE_URL_IMAGES, {"id": str(image_id)})
        hits_data = data.get("hits", [])
        if not hits_data:
            raise PixabayNotFoundError(f"Image {image_id} not found")
        return Image.from_dict(hits_data[0])

    # ── Videos API ──────────────────────────────────────────────────────

    def search_videos(
        self,
        query: str | None = None,
        lang: Language | str | None = None,
        video_type: VideoType | str | None = None,
        category: Category | str | None = None,
        min_width: int | None = None,
        min_height: int | None = None,
        editors_choice: bool = False,
        safesearch: bool = False,
        order: Order | str | None = None,
        page: int = DEFAULT_PAGE,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> PixabayResponse[Video]:
        """Search for videos on Pixabay.

        Args:
            query: Search query. If omitted, all videos are returned.
                Max 100 characters.
            lang: Language code for search.
            video_type: Filter by video type (all, film, animation).
            category: Filter by category.
            min_width: Minimum video width in pixels.
            min_height: Minimum video height in pixels.
            editors_choice: If True, only return Editor's Choice videos.
            safesearch: If True, only return videos suitable for all ages.
            order: Sort order (popular, latest).
            page: Page number (starts at 1).
            per_page: Results per page (3–200, default 20).

        Returns:
            PixabayResponse of Video objects.
        """
        if query is not None and len(query.strip()) > 100:
            raise ValueError("query may not exceed 100 characters")

        params: dict[str, Any] = {
            "q": query.strip() if query else None,
            "lang": _to_pixabay_param(lang),
            "video_type": _to_pixabay_param(video_type),
            "category": _to_pixabay_param(category),
            "min_width": min_width,
            "min_height": min_height,
            "editors_choice": "true" if editors_choice else None,
            "safesearch": "true" if safesearch else None,
            "order": _to_pixabay_param(order),
            "page": page,
            "per_page": min(per_page, MAX_PER_PAGE),
        }
        data = self._request(BASE_URL_VIDEOS, params)
        return self._build_response(data, Video.from_dict, page, min(per_page, MAX_PER_PAGE))

    def search_videos_all(
        self,
        query: str | None = None,
        lang: Language | str | None = None,
        video_type: VideoType | str | None = None,
        category: Category | str | None = None,
        min_width: int | None = None,
        min_height: int | None = None,
        editors_choice: bool = False,
        safesearch: bool = False,
        order: Order | str | None = None,
        per_page: int = DEFAULT_PER_PAGE,
        max_pages: int | None = None,
    ) -> Generator[list[Video], None, None]:
        """Search videos and auto-paginate through all results.

        Yields lists of Video objects, one page at a time.
        """
        if query is not None and len(query.strip()) > 100:
            raise ValueError("query may not exceed 100 characters")

        params: dict[str, Any] = {
            "q": query.strip() if query else None,
            "lang": _to_pixabay_param(lang),
            "video_type": _to_pixabay_param(video_type),
            "category": _to_pixabay_param(category),
            "min_width": min_width,
            "min_height": min_height,
            "editors_choice": "true" if editors_choice else None,
            "safesearch": "true" if safesearch else None,
            "order": _to_pixabay_param(order),
            "per_page": min(per_page, MAX_PER_PAGE),
        }
        yield from self._paginate(BASE_URL_VIDEOS, params, Video.from_dict, max_pages)

    def get_video(self, video_id: int) -> Video:
        """Get a single video by its Pixabay ID.

        Args:
            video_id: The Pixabay video ID.

        Returns:
            A Video object.
        """
        if video_id <= 0:
            raise ValueError("video_id must be a positive integer")
        data = self._request(BASE_URL_VIDEOS, {"id": str(video_id)})
        hits_data = data.get("hits", [])
        if not hits_data:
            raise PixabayNotFoundError(f"Video {video_id} not found")
        return Video.from_dict(hits_data[0])

    # ── Cleanup ─────────────────────────────────────────────────────────

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> PixabayClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

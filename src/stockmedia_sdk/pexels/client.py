"""
Pexels API client.

Usage::

    from stockmedia_sdk.pexels import PexelsClient
    # or: from stockmedia_sdk import PexelsClient

    client = PexelsClient(api_key="YOUR_API_KEY")

    # Search photos
    result = client.search_photos("nature", orientation="landscape", per_page=10)
    for photo in result.results:
        print(photo.src.large)

    # Get a single photo
    photo = client.get_photo(2014422)

    # Search videos
    videos = client.search_videos("ocean", per_page=5)
"""

from __future__ import annotations

import time
from typing import Any, Generator

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .enums import CollectionType, Color, Locale, Orientation, Size, SortOrder
from .exceptions import (
    PexelsAuthenticationError,
    PexelsError,
    PexelsNotFoundError,
    PexelsRateLimitError,
    PexelsServerError,
)
from .models import Collection, PagedResponse, Photo, RateLimitInfo, Video

# 鈹€鈹€ Constants 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

BASE_URL = "https://api.pexels.com/v1"
DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 15
MAX_PER_PAGE = 80
DEFAULT_TIMEOUT = 30  # seconds


# 鈹€鈹€ Helpers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€


def _clean_params(params: dict[str, Any]) -> dict[str, Any]:
    """Remove None values from a params dict so they aren't sent to the API."""
    return {k: v for k, v in params.items() if v is not None}


# 鈹€鈹€ Client 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€


class PexelsClient:
    """Client for the Pexels API v1.

    Args:
        api_key: Your Pexels API key. Get one at https://www.pexels.com/api/.
        timeout: Request timeout in seconds (default: 30).
        max_retries: Number of retries on 5xx / connection errors (default: 2).
        auto_rate_limit_wait: If True, automatically sleep when rate-limited
            and retry the request (default: False).

    Rate limits (as documented):
        - 200 requests per hour
        - 20,000 requests per month
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
                "Authorization": api_key,
                "Accept": "application/json",
                "User-Agent": "pexels-sdk-py/1.0.0",
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

    # 鈹€鈹€ Rate limit info 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

    @property
    def rate_limit_info(self) -> RateLimitInfo | None:
        """Rate limit status from the most recent API call."""
        return self._last_rate_limit_info

    # 鈹€鈹€ Internal request helpers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

    def _parse_rate_limit(self, response: requests.Response) -> RateLimitInfo:
        """Extract rate limit info from response headers."""
        limit = response.headers.get("X-Ratelimit-Limit")
        remaining = response.headers.get("X-Ratelimit-Remaining")
        reset = response.headers.get("X-Ratelimit-Reset")
        info = RateLimitInfo(
            limit=int(limit) if limit is not None else None,
            remaining=int(remaining) if remaining is not None else None,
            reset=int(reset) if reset is not None else None,
        )
        self._last_rate_limit_info = info
        return info

    def _request(self, path: str, params: dict[str, Any] | None = None) -> dict:
        """Make a GET request and return the parsed JSON body.

        Raises:
            PexelsAuthenticationError: 401
            PexelsNotFoundError: 404
            PexelsRateLimitError: 429
            PexelsServerError: 5xx
            PexelsError: other non-2xx
        """
        url = f"{BASE_URL}{path}"
        params = _clean_params(params or {})

        response = self._session.get(url, params=params, timeout=self.timeout)
        rate_info = self._parse_rate_limit(response)

        if response.status_code == 200:
            return response.json()

        # 鈹€鈹€ Error handling 鈹€鈹€
        try:
            body = response.json()
        except ValueError:
            body = {}

        error_msg = body.get("error", body.get("message", response.text))

        if response.status_code == 401:
            raise PexelsAuthenticationError(
                str(error_msg), status_code=401, response_body=body
            )
        elif response.status_code == 404:
            raise PexelsNotFoundError(
                str(error_msg), status_code=404, response_body=body
            )
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise PexelsRateLimitError(
                str(error_msg),
                status_code=429,
                response_body=body,
                retry_after=int(retry_after) if retry_after is not None else None,
                limit=rate_info.limit,
                remaining=rate_info.remaining,
                reset=rate_info.reset,
            )
        elif response.status_code >= 500:
            raise PexelsServerError(
                str(error_msg), status_code=response.status_code, response_body=body
            )
        else:
            raise PexelsError(
                str(error_msg), status_code=response.status_code, response_body=body
            )

    def _paginated_request(
        self,
        path: str,
        params: dict[str, Any],
        model_from_dict,
    ) -> PagedResponse:
        """Make a request that returns a paginated response."""
        data = self._request(path, params)
        results = [model_from_dict(item) for item in data.get(self._results_key(path), [])]

        return PagedResponse(
            results=results,
            page=data.get("page", params.get("page", DEFAULT_PAGE)),
            per_page=data.get("per_page", params.get("per_page", DEFAULT_PER_PAGE)),
            total_results=data.get("total_results", 0),
            next_page=data.get("next_page"),
            prev_page=data.get("prev_page"),
            url=data.get("url", ""),
        )

    def _paginate(
        self,
        path: str,
        params: dict[str, Any],
        model_from_dict,
        max_pages: int | None = None,
    ) -> Generator[list, None, None]:
        """Generator that yields pages of results automatically.

        Args:
            path: API endpoint path.
            params: Query parameters dict (page will be managed automatically).
            model_from_dict: Model classmethod for parsing items.
            max_pages: Maximum pages to fetch (None = unlimited).
        """
        page = params.get("page", DEFAULT_PAGE)
        pages_fetched = 0

        while True:
            params["page"] = page
            response = self._paginated_request(path, params.copy(), model_from_dict)
            yield response.results

            pages_fetched += 1
            if max_pages is not None and pages_fetched >= max_pages:
                break
            if not response.has_next:
                break
            page += 1

    @staticmethod
    def _results_key(path: str) -> str:
        """Determine the key for results in the JSON response based on endpoint."""
        if "/videos" in path:
            return "videos"
        elif "/collections" in path and "/featured" not in path:
            return "media"
        elif "/collections" in path:
            return "collections"
        return "photos"

    # 鈹€鈹€ Photos API 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

    def search_photos(
        self,
        query: str,
        orientation: Orientation | str | None = None,
        size: Size | str | None = None,
        color: Color | str | None = None,
        locale: Locale | str | None = None,
        page: int = DEFAULT_PAGE,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> PagedResponse[Photo]:
        """Search for photos by keyword query.

        Args:
            query: Search query (e.g., "nature", "people", "ocean").
            orientation: Desired photo orientation.
            size: Minimum photo size.
            color: Filter by dominant color (named color or hex like '#ff0000').
            locale: Search locale for localized results.
            page: Page number (starts at 1).
            per_page: Results per page (1鈥?0, default 15).

        Returns:
            PagedResponse of Photo objects.
        """
        if not query or not query.strip():
            raise ValueError("query is required for search_photos")

        params: dict[str, Any] = {
            "query": query.strip(),
            "orientation": orientation.value if isinstance(orientation, Orientation) else orientation,
            "size": size.value if isinstance(size, Size) else size,
            "color": color.value if isinstance(color, Color) else color,
            "locale": locale.value if isinstance(locale, Locale) else locale,
            "page": page,
            "per_page": min(per_page, MAX_PER_PAGE),
        }
        return self._paginated_request("/search", params, Photo.from_dict)

    def search_photos_all(
        self,
        query: str,
        orientation: Orientation | str | None = None,
        size: Size | str | None = None,
        color: Color | str | None = None,
        locale: Locale | str | None = None,
        per_page: int = DEFAULT_PER_PAGE,
        max_pages: int | None = None,
    ) -> Generator[list[Photo], None, None]:
        """Search photos and auto-paginate through all results.

        Yields lists of Photo objects, one page at a time.

        Args:
            query: Search query.
            orientation: Desired photo orientation.
            size: Minimum photo size.
            color: Filter by dominant color.
            locale: Search locale.
            per_page: Results per page (1鈥?0).
            max_pages: Maximum pages to fetch (None = all).

        Yields:
            List of Photo objects for each page.
        """
        if not query or not query.strip():
            raise ValueError("query is required")

        params: dict[str, Any] = {
            "query": query.strip(),
            "orientation": orientation.value if isinstance(orientation, Orientation) else orientation,
            "size": size.value if isinstance(size, Size) else size,
            "color": color.value if isinstance(color, Color) else color,
            "locale": locale.value if isinstance(locale, Locale) else locale,
            "per_page": min(per_page, MAX_PER_PAGE),
        }
        yield from self._paginate("/search", params, Photo.from_dict, max_pages)

    def curated_photos(
        self,
        page: int = DEFAULT_PAGE,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> PagedResponse[Photo]:
        """Get curated/trending photos from the Pexels homepage.

        Args:
            page: Page number (starts at 1).
            per_page: Results per page (1鈥?0).

        Returns:
            PagedResponse of Photo objects.
        """
        params = {"page": page, "per_page": min(per_page, MAX_PER_PAGE)}
        return self._paginated_request("/curated", params, Photo.from_dict)

    def curated_photos_all(
        self,
        per_page: int = DEFAULT_PER_PAGE,
        max_pages: int | None = None,
    ) -> Generator[list[Photo], None, None]:
        """Get curated photos and auto-paginate through all results.

        Yields lists of Photo objects, one page at a time.
        """
        params: dict[str, Any] = {"per_page": min(per_page, MAX_PER_PAGE)}
        yield from self._paginate("/curated", params, Photo.from_dict, max_pages)

    def get_photo(self, photo_id: int) -> Photo:
        """Get a single photo by its Pexels ID.

        Args:
            photo_id: The Pexels photo ID.

        Returns:
            A Photo object.
        """
        if photo_id <= 0:
            raise ValueError("photo_id must be a positive integer")
        data = self._request(f"/photos/{photo_id}")
        return Photo.from_dict(data)

    # 鈹€鈹€ Videos API 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

    def search_videos(
        self,
        query: str,
        orientation: Orientation | str | None = None,
        size: Size | str | None = None,
        locale: Locale | str | None = None,
        page: int = DEFAULT_PAGE,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> PagedResponse[Video]:
        """Search for videos by keyword query.

        Args:
            query: Search query (e.g., "ocean", "city").
            orientation: Desired video orientation.
            size: Minimum video size.
            locale: Search locale.
            page: Page number.
            per_page: Results per page (1鈥?0).

        Returns:
            PagedResponse of Video objects.
        """
        if not query or not query.strip():
            raise ValueError("query is required for search_videos")

        params: dict[str, Any] = {
            "query": query.strip(),
            "orientation": orientation.value if isinstance(orientation, Orientation) else orientation,
            "size": size.value if isinstance(size, Size) else size,
            "locale": locale.value if isinstance(locale, Locale) else locale,
            "page": page,
            "per_page": min(per_page, MAX_PER_PAGE),
        }
        return self._paginated_request("/videos/search", params, Video.from_dict)

    def search_videos_all(
        self,
        query: str,
        orientation: Orientation | str | None = None,
        size: Size | str | None = None,
        locale: Locale | str | None = None,
        per_page: int = DEFAULT_PER_PAGE,
        max_pages: int | None = None,
    ) -> Generator[list[Video], None, None]:
        """Search videos and auto-paginate through all results.

        Yields lists of Video objects, one page at a time.
        """
        if not query or not query.strip():
            raise ValueError("query is required")

        params: dict[str, Any] = {
            "query": query.strip(),
            "orientation": orientation.value if isinstance(orientation, Orientation) else orientation,
            "size": size.value if isinstance(size, Size) else size,
            "locale": locale.value if isinstance(locale, Locale) else locale,
            "per_page": min(per_page, MAX_PER_PAGE),
        }
        yield from self._paginate("/videos/search", params, Video.from_dict, max_pages)

    def popular_videos(
        self,
        min_width: int | None = None,
        min_height: int | None = None,
        min_duration: int | None = None,
        max_duration: int | None = None,
        page: int = DEFAULT_PAGE,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> PagedResponse[Video]:
        """Get popular/trending videos.

        Args:
            min_width: Minimum video width in pixels.
            min_height: Minimum video height in pixels.
            min_duration: Minimum video duration in seconds.
            max_duration: Maximum video duration in seconds.
            page: Page number.
            per_page: Results per page (1鈥?0).

        Returns:
            PagedResponse of Video objects.
        """
        params: dict[str, Any] = {
            "min_width": min_width,
            "min_height": min_height,
            "min_duration": min_duration,
            "max_duration": max_duration,
            "page": page,
            "per_page": min(per_page, MAX_PER_PAGE),
        }
        return self._paginated_request("/videos/popular", params, Video.from_dict)

    def popular_videos_all(
        self,
        min_width: int | None = None,
        min_height: int | None = None,
        min_duration: int | None = None,
        max_duration: int | None = None,
        per_page: int = DEFAULT_PER_PAGE,
        max_pages: int | None = None,
    ) -> Generator[list[Video], None, None]:
        """Get popular videos and auto-paginate through all results."""
        params: dict[str, Any] = {
            "min_width": min_width,
            "min_height": min_height,
            "min_duration": min_duration,
            "max_duration": max_duration,
            "per_page": min(per_page, MAX_PER_PAGE),
        }
        yield from self._paginate("/videos/popular", params, Video.from_dict, max_pages)

    def get_video(self, video_id: int) -> Video:
        """Get a single video by its Pexels ID.

        Args:
            video_id: The Pexels video ID.

        Returns:
            A Video object.
        """
        if video_id <= 0:
            raise ValueError("video_id must be a positive integer")
        data = self._request(f"/videos/videos/{video_id}")
        return Video.from_dict(data)

    # 鈹€鈹€ Collections API 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

    def featured_collections(
        self,
        page: int = DEFAULT_PAGE,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> PagedResponse[Collection]:
        """Get featured collections from Pexels.

        Args:
            page: Page number.
            per_page: Results per page (1鈥?0).

        Returns:
            PagedResponse of Collection objects.
        """
        params = {"page": page, "per_page": min(per_page, MAX_PER_PAGE)}
        return self._paginated_request("/collections/featured", params, Collection.from_dict)

    def featured_collections_all(
        self,
        per_page: int = DEFAULT_PER_PAGE,
        max_pages: int | None = None,
    ) -> Generator[list[Collection], None, None]:
        """Get featured collections and auto-paginate through all results."""
        params: dict[str, Any] = {"per_page": min(per_page, MAX_PER_PAGE)}
        yield from self._paginate("/collections/featured", params, Collection.from_dict, max_pages)

    def get_collection_media(
        self,
        collection_id: str,
        type: CollectionType | str | None = None,
        sort: SortOrder | str | None = None,
        page: int = DEFAULT_PAGE,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> PagedResponse[Photo] | PagedResponse[Video]:
        """Get media (photos or videos) from a specific collection.

        Args:
            collection_id: The collection ID.
            type: Media type filter ("photos" or "videos").
            sort: Sort order ("asc" or "desc").
            page: Page number.
            per_page: Results per page (1鈥?0).

        Returns:
            PagedResponse of Photo or Video objects depending on the type.
        """
        if not collection_id or not collection_id.strip():
            raise ValueError("collection_id is required")

        type_str = type.value if isinstance(type, CollectionType) else type
        params: dict[str, Any] = {
            "type": type_str,
            "sort": sort.value if isinstance(sort, SortOrder) else sort,
            "page": page,
            "per_page": min(per_page, MAX_PER_PAGE),
        }

        # Collection media returns either photos or videos based on type
        if type_str == "videos":
            return self._paginated_request(
                f"/collections/{collection_id}", params, Video.from_dict
            )
        else:
            return self._paginated_request(
                f"/collections/{collection_id}", params, Photo.from_dict
            )

    def get_collection_media_all(
        self,
        collection_id: str,
        type: CollectionType | str | None = None,
        sort: SortOrder | str | None = None,
        per_page: int = DEFAULT_PER_PAGE,
        max_pages: int | None = None,
    ) -> Generator[list[Photo] | list[Video], None, None]:
        """Get collection media and auto-paginate through all results.

        Yields lists of Photo or Video objects, one page at a time.
        """
        if not collection_id or not collection_id.strip():
            raise ValueError("collection_id is required")

        type_str = type.value if isinstance(type, CollectionType) else type
        params: dict[str, Any] = {
            "type": type_str,
            "sort": sort.value if isinstance(sort, SortOrder) else sort,
            "per_page": min(per_page, MAX_PER_PAGE),
        }
        model_from_dict = Video.from_dict if type_str == "videos" else Photo.from_dict
        yield from self._paginate(
            f"/collections/{collection_id}", params, model_from_dict, max_pages
        )

    # 鈹€鈹€ Cleanup 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

    def close(self) -> None:
        """Close the underlying HTTP session."""
        self._session.close()

    def __enter__(self) -> PexelsClient:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

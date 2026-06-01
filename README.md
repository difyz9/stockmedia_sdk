# Pexels SDK for Python

A clean, fully typed Python SDK for the [Pexels API v1](https://www.pexels.com/api/documentation/).

## Features

- ✅ All Pexels API endpoints: Photos, Videos, Collections
- ✅ Full type annotations with dataclass models
- ✅ Enum-based parameter validation (`Orientation`, `Size`, `Color`, `Locale`)
- ✅ Auto-pagination helpers (`*_all()` methods)
- ✅ Rate limit tracking from response headers
- ✅ Rich error hierarchy with typed exceptions
- ✅ Retry logic for transient failures
- ✅ Context manager support
- ✅ Zero heavy dependencies (only `requests`)

## Installation

```bash
pip install -e .
```

Or install from PyPI (coming soon):

```bash
pip install pexels-sdk
```

## Quick Start

```python
from pexels_sdk import PexelsClient

client = PexelsClient(api_key="YOUR_API_KEY")

# Search photos
result = client.search_photos("nature", per_page=10)
for photo in result.results:
    print(photo.photographer, photo.src.large)

# Get a single photo
photo = client.get_photo(2014422)

# Search videos
videos = client.search_videos("ocean")

# Paginate through all results
for page in client.search_photos_all("sunset", max_pages=3):
    for photo in page:
        print(photo.url)
```

## API Reference

### Client Initialization

```python
client = PexelsClient(
    api_key="YOUR_API_KEY",
    timeout=30,                # Request timeout in seconds
    max_retries=2,             # Auto-retry on 5xx/429 errors
    auto_rate_limit_wait=False # Auto-sleep and retry when rate-limited
)
```

### Photos

| Method | Description |
|--------|-------------|
| `search_photos(query, ...)` | Search photos by keyword |
| `search_photos_all(query, ...)` | Auto-paginating search (generator) |
| `curated_photos(page, per_page)` | Get curated/trending photos |
| `curated_photos_all(...)` | Auto-paginating curated photos |
| `get_photo(photo_id)` | Get a photo by ID |

### Videos

| Method | Description |
|--------|-------------|
| `search_videos(query, ...)` | Search videos by keyword |
| `search_videos_all(query, ...)` | Auto-paginating search |
| `popular_videos(...)` | Get popular/trending videos |
| `popular_videos_all(...)` | Auto-paginating popular videos |
| `get_video(video_id)` | Get a video by ID |

### Collections

| Method | Description |
|--------|-------------|
| `featured_collections(page, per_page)` | Get featured collections |
| `featured_collections_all(...)` | Auto-paginating collections |
| `get_collection_media(collection_id, ...)` | Get media from a collection |
| `get_collection_media_all(collection_id, ...)` | Auto-paginating collection media |

### Search Filters

```python
from pexels_sdk import Orientation, Size, Color, Locale

client.search_photos(
    "ocean",
    orientation=Orientation.LANDSCAPE,
    size=Size.LARGE,
    color=Color.BLUE,
    locale=Locale.ZH_CN,
)
```

### Rate Limit Info

```python
info = client.rate_limit_info
print(f"Remaining: {info.remaining}/{info.limit}")
```

### Error Handling

```python
from pexels_sdk import (
    PexelsError,
    PexelsAuthenticationError,
    PexelsRateLimitError,
    PexelsNotFoundError,
)

try:
    photo = client.get_photo(999999999)
except PexelsNotFoundError:
    print("Photo not found")
except PexelsAuthenticationError:
    print("Invalid API key")
except PexelsRateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except PexelsError as e:
    print(f"API error: {e}")
```

## Data Models

### Photo

```python
@dataclass(frozen=True)
class Photo:
    id: int
    width: int
    height: int
    url: str
    photographer: str
    photographer_url: str
    photographer_id: int
    avg_color: str
    liked: bool
    alt: str
    src: PhotoSource          # .original, .large, .medium, .small, .tiny, etc.
```

### Video

```python
@dataclass(frozen=True)
class Video:
    id: int
    width: int
    height: int
    duration: int             # seconds
    url: str
    image: str                # thumbnail URL
    user: VideoUser           # .id, .name, .url
    video_files: list[VideoFile]    # .quality, .file_type, .link, .width, .height, .fps
    video_pictures: list[VideoPicture]  # .id, .picture, .nr
```

## Rate Limits

- **200 requests per hour**
- **20,000 requests per month**

Rate limit status is available via `client.rate_limit_info` after each API call.

## License

MIT

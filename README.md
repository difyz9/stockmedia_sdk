# stockmedia-sdk

Python SDKs for free stock media APIs — [Pexels](https://www.pexels.com/api/documentation/) + [Pixabay](https://pixabay.com/api/docs/), cleanly wrapped.

```python
from stockmedia_sdk import PexelsClient, PixabayClient

pexels = PexelsClient(api_key="...")
pixabay = PixabayClient(api_key="...")
```

## Features

- **Pexels**: Photos, Videos, Collections
- **Pixabay**: Images, Videos with all quality variants
- Full type annotations with frozen dataclass models
- Enum-based parameter validation
- Auto-pagination helpers (`*_all()` methods)
- Rate limit tracking from response headers
- Typed exception hierarchy
- Retry logic for transient failures
- Context manager support
- Zero heavy dependencies (only `requests`)

## Installation

```bash
pip install stockmedia-sdk
```

---

## Pexels

```python
from stockmedia_sdk import PexelsClient
# or: from stockmedia_sdk.pexels import PexelsClient

client = PexelsClient(api_key="YOUR_API_KEY")

# Search photos
result = client.search_photos("nature", per_page=10)
for photo in result.results:
    print(photo.photographer, photo.src.large)

# Get a single photo
photo = client.get_photo(2014422)

# Auto-paginate through all results
for page in client.search_photos_all("sunset", max_pages=3):
    for photo in page:
        print(photo.url)
```

### Client Options

```python
client = PexelsClient(
    api_key="YOUR_API_KEY",
    timeout=30,                # Request timeout (seconds)
    max_retries=2,             # Auto-retry on 5xx/429
    auto_rate_limit_wait=False # Sleep+retry when rate-limited
)
```

### Search Filters

```python
from stockmedia_sdk import Orientation, Size, Color, Locale

client.search_photos(
    "ocean",
    orientation=Orientation.LANDSCAPE,
    size=Size.LARGE,
    color=Color.BLUE,
    locale=Locale.ZH_CN,
)
```

### Error Handling

```python
from stockmedia_sdk import (
    PexelsError, PexelsAuthenticationError,
    PexelsRateLimitError, PexelsNotFoundError,
)

try:
    photo = client.get_photo(999999999)
except PexelsNotFoundError:
    print("Photo not found")
except PexelsRateLimitError as e:
    print(f"Rate limited, retry after {e.retry_after}s")
```

### API Reference

| Photos | Videos | Collections |
|--------|--------|-------------|
| `search_photos(q, ...)` | `search_videos(q, ...)` | `featured_collections(...)` |
| `search_photos_all(q, ...)` | `search_videos_all(q, ...)` | `featured_collections_all(...)` |
| `curated_photos(...)` | `popular_videos(...)` | `get_collection_media(id, ...)` |
| `curated_photos_all(...)` | `popular_videos_all(...)` | `get_collection_media_all(id, ...)` |
| `get_photo(id)` | `get_video(id)` | |

**Rate limit**: 200 req/hour, 20k req/month. Track via `client.rate_limit_info`.

---

## Pixabay

```python
from stockmedia_sdk import PixabayClient
# or: from stockmedia_sdk.pixabay import PixabayClient

client = PixabayClient(api_key="YOUR_API_KEY")

# Search images
result = client.search_images("yellow flowers", image_type="photo", per_page=20)
for img in result.hits:
    print(img.webformat_url)

# Search videos
result = client.search_videos("ocean", per_page=10)
for video in result.hits:
    print(video.videos.medium.url)

# Auto-paginate
for page in client.search_images_all("sunset", max_pages=3):
    for img in page:
        print(img.large_image_url)
```

### Search Filters

```python
from stockmedia_sdk import ImageType, Orientation, Category, Color, Language, Order

client.search_images(
    "ocean",
    image_type=ImageType.PHOTO,
    orientation=Orientation.HORIZONTAL,
    category=Category.NATURE,
    colors=[Color.BLUE, Color.GREEN],
    order=Order.LATEST,
    lang=Language.ZH,
    min_width=1920, min_height=1080,
    editors_choice=True, safesearch=True,
)
```

### Error Handling

```python
from stockmedia_sdk import (
    PixabayError, PixabayAuthenticationError,
    PixabayRateLimitError, PixabayNotFoundError,
)
```

### API Reference

| Images | Videos |
|--------|--------|
| `search_images(q, ...)` | `search_videos(q, ...)` |
| `search_images_all(q, ...)` | `search_videos_all(q, ...)` |
| `get_image(id)` | `get_video(id)` |

**Rate limit**: 100 req/60s. Max 500 results per query. Track via `client.rate_limit_info`.

### Image URL Sizes

Replace `_640` in `webformat_url` or use convenience properties:

```python
img.webformat_url    # max 640px
img.webformat_180    # 180px tall
img.webformat_340    # 340px tall
img.webformat_960    # 960 x 720 px
img.large_image_url  # max 1280px
```

---

## Data Models

| Pexels | Pixabay |
|--------|---------|
| `Photo` | `Image` |
| `PhotoSource` | `Video` |
| `Video` / `VideoFile` / `VideoPicture` | `VideoQuality` / `VideoSizeSet` |
| `Collection` | `PixabayResponse[T]` |
| `PagedResponse[T]` | `RateLimitInfo` |
| `RateLimitInfo` | |

All models are frozen dataclasses with `from_dict()` classmethods.

## License

MIT

"""
Stockpile SDK — Basic Usage Examples
=====================================

Set your API keys as environment variables or replace them below.

    $env:PEXELS_API_KEY="your_key_here"     # PowerShell
    $env:PIXABAY_API_KEY="your_key_here"
    export PEXELS_API_KEY="your_key_here"    # Bash
    export PIXABAY_API_KEY="your_key_here"
    python examples/basic_usage.py
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stockpile import (
    PexelsClient,
    PixabayClient,
    Orientation,
    Size,
    Color,
    Locale,
    CollectionType,
    SortOrder,
    ImageType,
    Order,
    Category,
    Language,
)


def pexels_demo():
    print("\n" + "=" * 60)
    print("🟢 Pexels SDK Demo")
    print("=" * 60)

    api_key = os.getenv("PEXELS_API_KEY", "")
    if not api_key:
        print("⚠️  Set PEXELS_API_KEY to run Pexels examples.")
        return

    client = PexelsClient(api_key)

    # 1. Search Photos
    print("\n1. Search Photos: 'nature' (first 3)")
    result = client.search_photos("nature", per_page=3)
    for i, photo in enumerate(result.results, 1):
        print(f"  [{i}] {photo.photographer}: {photo.src.large}")

    # 2. Get a Photo
    print("\n2. Get Photo by ID: 2014422")
    photo = client.get_photo(2014422)
    print(f"  {photo.photographer}: {photo.url}")

    # 3. Filtered Search
    print("\n3. Filtered: 'ocean', landscape, large, blue")
    result = client.search_photos(
        "ocean",
        orientation=Orientation.LANDSCAPE,
        size=Size.LARGE,
        color=Color.BLUE,
        per_page=3,
    )
    for photo in result.results:
        print(f"  {photo.photographer}: {photo.width}x{photo.height}")

    # 4. Rate Limit
    print("\n4. Rate Limit Status")
    info = client.rate_limit_info
    if info:
        print(f"  Remaining: {info.remaining}/{info.limit}")

    # 5. Paginate
    print("\n5. Auto-paginate: 'sunset' (max 2 pages)")
    count = 0
    for page in client.search_photos_all("sunset", per_page=5, max_pages=2):
        for photo in page:
            count += 1
    print(f"  Total: {count} photos across pages")

    # 6. Context manager
    print("\n6. Context manager")
    with PexelsClient(api_key) as ctx:
        photo = ctx.get_photo(2014422)
        print(f"  Got photo: {photo.photographer}")


def pixabay_demo():
    print("\n" + "=" * 60)
    print("🟠 Pixabay SDK Demo")
    print("=" * 60)

    api_key = os.getenv("PIXABAY_API_KEY", "")
    if not api_key:
        print("⚠️  Set PIXABAY_API_KEY to run Pixabay examples.")
        return

    client = PixabayClient(api_key)

    # 1. Search Images
    print("\n1. Search Images: 'yellow flowers' (first 3)")
    result = client.search_images("yellow flowers", image_type="photo", per_page=3)
    for i, img in enumerate(result.hits, 1):
        print(f"  [{i}] {img.user}: {img.tags}")

    # 2. Get an Image
    print("\n2. Get Image by ID: 195893")
    img = client.get_image(195893)
    print(f"  {img.user}: {img.tags} (views: {img.views})")

    # 3. Filtered Search
    print("\n3. Filtered: 'ocean', horizontal, nature, latest")
    result = client.search_images(
        "ocean",
        orientation=Orientation.HORIZONTAL,
        category=Category.NATURE,
        order=Order.LATEST,
        per_page=3,
    )
    for img in result.hits:
        print(f"  {img.user}: {img.tags} ({img.image_width}x{img.image_height})")

    # 4. Search Videos
    print("\n4. Search Videos: 'city' (first 2)")
    result = client.search_videos("city", per_page=2)
    for video in result.hits:
        print(f"  [{video.duration}s] {video.user}: {video.tags}")
        print(f"     medium: {video.videos.medium.width}x{video.videos.medium.height}")

    # 5. Rate Limit
    print("\n5. Rate Limit Status")
    info = client.rate_limit_info
    if info:
        print(f"  Remaining: {info.remaining}/{info.limit}")

    # 6. Context manager
    print("\n6. Context manager")
    with PixabayClient(api_key) as ctx:
        img = ctx.get_image(195893)
        print(f"  Got image: {img.user} — {img.page_url}")


def main():
    pexels_demo()
    pixabay_demo()
    print("\n✅ All examples completed!")


if __name__ == "__main__":
    main()

"""
Pexels SDK — Basic Usage Examples
==================================

Set your API key as an environment variable or replace it below.

    $env:PEXELS_API_KEY="your_key_here"   # PowerShell
    export PEXELS_API_KEY="your_key_here"  # Bash
    python examples/basic_usage.py
"""

import os
import sys

# Add the parent directory to sys.path so we can import pexels_sdk
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pexels_sdk import (
    PexelsClient,
    Orientation,
    Size,
    Color,
    Locale,
    CollectionType,
    SortOrder,
)


def main():
    api_key = os.getenv("PEXELS_API_KEY", "")
    if not api_key:
        print("⚠️  Set PEXELS_API_KEY environment variable to run these examples.")
        print("   Get a free key at: https://www.pexels.com/api/")
        return

    client = PexelsClient(api_key)

    # ── 1. Search Photos ─────────────────────────────────────────────
    print("=" * 60)
    print("1. Search Photos: 'nature' (first 3 results)")
    print("=" * 60)
    result = client.search_photos("nature", per_page=3)
    for i, photo in enumerate(result.results, 1):
        print(f"  [{i}] {photo.photographer}: {photo.url}")
        print(f"      src.large: {photo.src.large}")
        print(f"      avg_color: {photo.avg_color}, alt: {photo.alt[:60]}...")
        print()

    # ── 2. Get a Single Photo ────────────────────────────────────────
    print("=" * 60)
    print("2. Get Photo by ID: 2014422")
    print("=" * 60)
    try:
        photo = client.get_photo(2014422)
        print(f"  Photographer: {photo.photographer}")
        print(f"  URL: {photo.url}")
        print(f"  Original: {photo.src.original}")
    except Exception as e:
        print(f"  Error: {e}")

    print()

    # ── 3. Search with Filters ───────────────────────────────────────
    print("=" * 60)
    print("3. Filtered Search: 'ocean', landscape, large, blue")
    print("=" * 60)
    result = client.search_photos(
        "ocean",
        orientation=Orientation.LANDSCAPE,
        size=Size.LARGE,
        color=Color.BLUE,
        per_page=3,
    )
    for photo in result.results:
        print(f"  {photo.photographer}: {photo.width}x{photo.height}")
    print()

    # ── 4. Curated Photos ────────────────────────────────────────────
    print("=" * 60)
    print("4. Curated Photos (first 3)")
    print("=" * 60)
    result = client.curated_photos(per_page=3)
    for photo in result.results:
        print(f"  {photo.photographer}: {photo.alt[:80] if photo.alt else '(no alt)'}")
    print()

    # ── 5. Search Videos ─────────────────────────────────────────────
    print("=" * 60)
    print("5. Search Videos: 'city' (first 3)")
    print("=" * 60)
    result = client.search_videos("city", per_page=3)
    for video in result.results:
        print(f"  [{video.duration}s] {video.user.name}: {video.url}")
        # Print available video qualities
        qualities = [vf.quality for vf in video.video_files if vf.quality]
        print(f"      Available qualities: {qualities}")
    print()

    # ── 6. Popular Videos ────────────────────────────────────────────
    print("=" * 60)
    print("6. Popular Videos (first 2)")
    print("=" * 60)
    result = client.popular_videos(per_page=2)
    for video in result.results:
        print(f"  [{video.duration}s] {video.user.name}")
        # Show thumbnail
        print(f"      thumbnail: {video.image}")
    print()

    # ── 7. Featured Collections ──────────────────────────────────────
    print("=" * 60)
    print("7. Featured Collections (first 3)")
    print("=" * 60)
    result = client.featured_collections(per_page=3)
    for col in result.results:
        print(f"  [{col.id}] {col.title}")
        print(f"      photos: {col.photos_count}, videos: {col.videos_count}")
    print()

    # ── 8. Rate Limit Info ───────────────────────────────────────────
    print("=" * 60)
    print("8. Rate Limit Status")
    print("=" * 60)
    info = client.rate_limit_info
    if info:
        print(f"  Limit: {info.limit}")
        print(f"  Remaining: {info.remaining}")
        print(f"  Reset: {info.reset}")
    print()

    # ── 9. Paginate through all results ──────────────────────────────
    print("=" * 60)
    print("9. Auto-paginate: 'sunset' (max 2 pages)")
    print("=" * 60)
    count = 0
    for page in client.search_photos_all("sunset", per_page=5, max_pages=2):
        for photo in page:
            count += 1
            print(f"  [{count}] {photo.photographer}: {photo.src.medium}")
    print(f"  Total: {count} photos across pages")
    print()

    # ── 10. Context manager ──────────────────────────────────────────
    print("=" * 60)
    print("10. Using client as context manager")
    print("=" * 60)
    with PexelsClient(api_key) as ctx_client:
        photo = ctx_client.get_photo(2014422)
        print(f"  Got photo: {photo.photographer} — {photo.url}")
    print("  (session closed)")

    print()
    print("✅ All examples completed!")


if __name__ == "__main__":
    main()

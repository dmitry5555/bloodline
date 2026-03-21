import requests
import re

def get_artist_photo(artist: str) -> dict | None:
    # форматируем имя для Wikipedia URL
    artist_slug = artist.replace(" ", "_")
    
    r = requests.get(
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{artist_slug}"
    )
    
    if r.status_code != 200:
        return None
    
    data = r.json()
    original = data.get("originalimage", {})
    
    if not original:
        return None
    
    # проверяем что это Wikimedia Commons (не fair use)
    source = original.get("source", "")
    if "/wikipedia/commons/" not in source:
        return None
    
    return {
        "photo_url": source,
        "width": original.get("width"),
        "height": original.get("height"),
        "description": data.get("description"),
        "extract": data.get("extract"),
    }


if __name__ == "__main__":
    result = get_artist_photo("George Michael")
    if result:
        print(f"✓ фото: {result['photo_url']}")
        print(f"  размер: {result['width']}x{result['height']}")
        print(f"  описание: {result['description']}")
    else:
        print("✗ фото не найдено или не Commons")
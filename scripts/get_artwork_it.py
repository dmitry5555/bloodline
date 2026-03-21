import requests

def get_artwork(artist: str, album: str) -> str | None:
    # шаг 1 — artistId
    r = requests.get(
        "https://itunes.apple.com/search",
        params={"term": artist, "entity": "musicArtist", "limit": 1}
    )
    artists = r.json().get("results", [])
    if not artists:
        return None
    artist_id = artists[0]["artistId"]

    # шаг 2 — все альбомы артиста
    r = requests.get(
        "https://itunes.apple.com/lookup",
        params={"id": artist_id, "entity": "album", "limit": 50}
    )
    results = r.json().get("results", [])

    # шаг 3 — fuzzy match по названию альбома
    match = next(
        (r for r in results
         if r.get("wrapperType") == "collection"
         and album.lower() in r.get("collectionName", "").lower()),
        None
    )

    if not match or not match.get("artworkUrl100"):
        return None

    # шаг 4 — апскейл до 1400x1400
    import re
    return re.sub(r'\d+x\d+bb\.jpg$', '1400x1400bb.jpg', match["artworkUrl100"])
# scripts/wiki.py
import requests
import time

HEADERS = {"User-Agent": "Bloodline/1.0 (music influence research project)"}

def fetch_wiki_text(query):
    search_url = "https://en.wikipedia.org/w/api.php"

    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json"
    }

    for attempt in range(3):
        try:
            response = requests.get(search_url, params=params, headers=HEADERS, timeout=10)
            data = response.json()
            break
        except Exception:
            if attempt < 2:
                print(f"  Retrying search ({attempt + 1}/3)...")
                time.sleep(5)
            else:
                return None, None

    if not data["query"]["search"]:
        return None, None

    page_title = data["query"]["search"][0]["title"]

    content_params = {
        "action": "query",
        "titles": page_title,
        "prop": "extracts",
        "explaintext": True,
        "format": "json"
    }

    for attempt in range(3):
        try:
            content = requests.get(search_url, params=content_params, headers=HEADERS, timeout=10)
            pages = content.json()["query"]["pages"]
            text = list(pages.values())[0].get("extract", "")
            break
        except Exception:
            if attempt < 2:
                print(f"  Retrying content ({attempt + 1}/3)...")
                time.sleep(5)
            else:
                return None, None

    time.sleep(1)
    return page_title, text

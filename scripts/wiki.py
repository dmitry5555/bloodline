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
    response = requests.get(search_url, params=params, headers=HEADERS)
    data = response.json()

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
    content = requests.get(search_url, params=content_params, headers=HEADERS)
    pages = content.json()["query"]["pages"]
    text = list(pages.values())[0].get("extract", "")

    time.sleep(1)
    return page_title, text

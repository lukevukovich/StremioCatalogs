import json, os, requests

SOURCES = {
    "slasher": "https://mdblist.com/lists/slander2328/slasher-movies/json"
}

def fetch_and_save(catalog_id, url):
    print(f"Updating {catalog_id} from {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    movies = resp.json()

    metas = [
        {
            "id": m["imdb_id"],
            "type": m["mediatype"],
            "name": m["title"],
            "year": m["release_year"]
        }
        for m in movies if m.get("imdb_id")
    ]

    os.makedirs(f"catalogs/movie", exist_ok=True)
    with open(f"catalogs/movie/{catalog_id}.json", "w", encoding="utf-8") as f:
        json.dump({"metas": metas}, f, ensure_ascii=False, indent=2)

for cid, src_url in SOURCES.items():
    fetch_and_save(cid, src_url)

print("All catalogs updated.")

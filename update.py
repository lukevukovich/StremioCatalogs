import json, os, requests, sys

CONTENT_TYPE = sys.argv[1]
if not CONTENT_TYPE:
    print("Content type is required")
    sys.exit(1)

SOURCES = json.loads(open(f"sources/{CONTENT_TYPE}_sources.json", "r", encoding="utf-8").read())

def priority_index(title_lc: str, sort: list) -> int:
    for i, term in enumerate(sort):
        if term in title_lc:
            return i
    return len(sort) + 1 

def fetch_and_save(catalog_id, url, sort):
    print(f"Updating '{catalog_id}' from {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    movies = resp.json()

    metas = [
        {
            "id": m["imdb_id"],
            "type": m["mediatype"],
            "name": m["title"],
            "year": m["release_year"] if m.get("release_year") else 0
        }
        for m in movies if m.get("imdb_id")
    ]
    if sort:
            top_matches = [m for m in metas if any(term in m["name"].lower() for term in sort)]
            others = [m for m in metas if m not in top_matches]
            top_matches.sort(key=lambda x: (priority_index(x["name"].lower(), sort), -x["year"]))
            others.sort(key=lambda x: (-x["year"], x["name"].lower()))
            metas = top_matches + others

    os.makedirs(f"catalog/{CONTENT_TYPE}", exist_ok=True)
    with open(f"catalog/{CONTENT_TYPE}/{catalog_id}.json", "w", encoding="utf-8") as f:
        json.dump({"metas": metas}, f, ensure_ascii=False, indent=2)

for cid in SOURCES.keys():
    fetch_and_save(cid, SOURCES[cid]["url"], SOURCES[cid]["sort"])

print("All catalogs updated.")

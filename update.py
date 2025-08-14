import json, os, requests, sys
import requests

API_KEY = "58ac8528f27601fabc47918b3eefc3c6"
TMDB_API_URL = f"https://api.themoviedb.org/3/find/{{imdb_id}}?api_key={API_KEY}&external_source=imdb_id"
TMDB_POSTER_URL = "https://image.tmdb.org/t/p/w500"

CONTENT_TYPE = sys.argv[1]
if not CONTENT_TYPE:
    print("Content type is required")
    sys.exit(1)

SOURCES = json.loads(open(f"sources/{CONTENT_TYPE}_sources.json", "r", encoding="utf-8").read())

def priority_index(title_lc: str, sort: list) -> int:
    """
    Get the priority index of a title based on the sort list.
    """
    for i, term in enumerate(sort):
        if term in title_lc:
            return i
    return len(sort) + 1

def get_poster_url(movie_id: str) -> str:
    """
    Get the poster URL for a movie by its ID.
    """
    url = TMDB_API_URL.format(imdb_id=movie_id)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        poster_path = data["movie_results"][0]["poster_path"] if data["movie_results"] else None
        return poster_path
    return None

def fetch_and_save(catalog_id, url, include):
    print(f"Updating '{catalog_id}' from {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    movies = resp.json()

    if include:
        keyword_map = {kw: [] for kw in include}

        for m in movies:
            for kw in include:
                title = m["title"]
                if kw.lower() in title.lower():
                    imdb_id = m["imdb_id"]
                    if not imdb_id:
                        continue

                    meta = {
                        "id": imdb_id,
                        "type": m["mediatype"],
                        "name": title,
                        "year": m.get("release_year", 0)
                    }

                    poster_path = get_poster_url(imdb_id)
                    if poster_path:
                        print(f"Got poster for `{title}`")
                        meta["poster"] = f"{TMDB_POSTER_URL}/{poster_path}"

                    if meta not in keyword_map[kw]:
                        keyword_map[kw].append(meta)

        metas = []
        for kw in include:
            metas.extend(keyword_map[kw])

    else:
        metas = []
        for m in movies:
            imdb_id = m.get("imdb_id")
            if not imdb_id:
                continue

            title = m["title"]
            meta = {
                "id": imdb_id,
                "type": m["mediatype"],
                "name": title,
                "year": m.get("release_year", 0)
            }

            poster_path = get_poster_url(imdb_id)
            if poster_path:
                print(f"Got poster for `{title}`")
                meta["poster"] = f"{TMDB_POSTER_URL}/{poster_path}"

            metas.append(meta)

    os.makedirs(f"catalog/{CONTENT_TYPE}", exist_ok=True)
    with open(f"catalog/{CONTENT_TYPE}/{catalog_id}.json", "w", encoding="utf-8") as f:
        json.dump({"metas": metas}, f, ensure_ascii=False, indent=2)
    print(f"Updated catalog '{catalog_id}'\n")

for cid in SOURCES.keys():
    fetch_and_save(cid, SOURCES[cid]["url"], SOURCES[cid]["include"])

print(f"All {CONTENT_TYPE} catalogs updated")

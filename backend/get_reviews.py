import json
import os
import time
from urllib.request import Request, urlopen
from urllib.error import URLError

def crawl_reviews(app_url, save_path):
    app_id = app_url.split("id=")[-1]
    country = "us"
    all_reviews = []
    for page in range(1, 11):
        url = f"https://itunes.apple.com/{country}/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"
        try:
            req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            response = urlopen(req, timeout=10)
            data = json.loads(response.read().decode("utf-8"))
            if "feed" not in data or "entry" not in data["feed"]:
                break
            entries = data["feed"]["entry"]
            for entry in entries:
                review = {
                    "rating": entry["im:rating"]["label"],
                    "title": entry["title"]["label"],
                    "review": entry["content"]["label"],
                    "author": entry["author"]["name"]["label"],
                    "updated": entry["updated"]["label"],
                    "version": entry.get("im:version", {}).get("label", "未知版本")
                }
                all_reviews.append(review)
            time.sleep(1)
        except (URLError, Exception):
            break
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(all_reviews, f, ensure_ascii=False, indent=2)
    return all_reviews
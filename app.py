from flask import Flask, render_template, request
import json
import random
import os
from datetime import datetime

app = Flask(__name__, template_folder="Templates")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def get_latest_posts():
    """Helper to reload all JSON files from disk on every request"""
    latest_posts = []
    post_files = [
        "nanotyrannus.json", "vaquita.json", "gravitational_waves.json", 
        "sea_otters.json", "football.json", "psychology.json",
        "finished_ncaa.json", "scheduled_ncaa.json",
        "finished_favorites.json", "scheduled_favorites.json"  # Added favorites
    ]
    
    for filename in post_files:
        full_path = os.path.join(BASE_DIR, "json", filename)
        try:
            if os.path.exists(full_path):
                with open(full_path, encoding="utf-8-sig") as f:
                    data = json.load(f)
                    for post in data:
                        post["source_file"] = filename
                    latest_posts.extend(data)
        except Exception as e:
            print(f"ERROR loading {filename}: {e}")
    return latest_posts

def attach_article_data(posts, articles_metadata):
    enriched = []
    for post in posts:
        article = articles_metadata.get(post["article_id"], {})
        first_page = post.get("pages", [{}])[0]
        
        enriched.append({
            "post_id": post.get("post_id"),
            "article_id": post.get("article_id"),
            "source_file": post.get("source_file"), # Carried over from loader
            "title": article.get("title", "Unknown Title"),
            "type": post.get("type") or article.get("type", "General"),
            "category": post.get("category") or article.get("category", "Uncategorized"),
            "theme": post.get("theme") or first_page.get("title", "General Overview"),
            "pages": post.get("pages", [])
        })
    return enriched

from datetime import datetime

def filter_and_sort(posts, types, categories, articles):
    results = posts
    if types:
        results = [p for p in results if p["type"] in types]
    if categories:
        results = [p for p in results if p["category"] in categories]
    if articles:
        results = [p for p in results if p["article_id"] in articles]

    # 1. TOP PRIORITY: Scheduled Favorites (Angels/Ducks upcoming)
    fav_scheduled = [p for p in results if p.get("source_file") == "scheduled_favorites.json"]
    
    # 2. SECOND PRIORITY: Scheduled NCAA (March Madness upcoming)
    ncaa_scheduled = [p for p in results if p.get("source_file") == "scheduled_ncaa.json"]

    # Sorting helper for time
    def get_start_time(post):
        time_str = post.get("pages", [{}])[0].get("status_display", "23:59")
        try:
            # Handles "07:05 PM" or "14:30"
            if "PM" in time_str or "AM" in time_str:
                return datetime.strptime(time_str, "%I:%M %p").time()
            return datetime.strptime(time_str, "%H:%M").time()
        except:
            return datetime.strptime("23:59", "%H:%M").time()

    fav_scheduled.sort(key=get_start_time)
    ncaa_scheduled.sort(key=get_start_time)

    # 3. POOL: Everything else (Including finished favorites)
    standard_results = [p for p in results if p.get("source_file") not in ["scheduled_favorites.json", "scheduled_ncaa.json"]]

    # Interleave logic
    grouped = {}
    for post in standard_results:
        aid = post["article_id"]
        # Boost finished favorites so they appear earlier in the shuffle
        is_fav_finished = post.get("source_file") == "finished_favorites.json"
        grouped.setdefault(aid, []).append(post)

    article_ids = list(grouped.keys())
    interleaved_standard = []
    
    if grouped:
        max_posts = max(len(p) for p in grouped.values())
        for i in range(max_posts):
            random.shuffle(article_ids)
            for aid in article_ids:
                if i < len(grouped[aid]):
                    interleaved_standard.append(grouped[aid][i])

    return fav_scheduled + ncaa_scheduled + interleaved_standard

@app.route("/")
def index():
    # 1. Load fresh Metadata
    articles_path = os.path.join(BASE_DIR, "articles.json")
    try:
        with open(articles_path, encoding="utf-8-sig") as f:
            articles_metadata = {a["article_id"]: a for a in json.load(f)}
    except:
        articles_metadata = {}

    # 2. Load fresh Posts and Enrich
    raw_posts = get_latest_posts()
    enriched_posts = attach_article_data(raw_posts, articles_metadata)

    # 3. Filter and Sort (Priority logic is in here)
    types = request.args.getlist("type")
    categories = request.args.getlist("category")
    articles = request.args.getlist("article")
    
    final_posts = filter_and_sort(enriched_posts, types, categories, articles)

    return render_template(
        "index.html",
        posts=final_posts,
        all_types=sorted({a["type"] for a in articles_metadata.values()}),
        all_categories=sorted({a["category"] for a in articles_metadata.values()}),
        all_articles=sorted({a["article_id"] for a in articles_metadata.values()})
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
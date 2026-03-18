from flask import Flask, render_template, request
import json
import random
import os


app = Flask(__name__, template_folder="templates")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Load article metadata
articles_path = os.path.join(BASE_DIR, "articles.json")
with open(articles_path, encoding="utf-8-sig") as f:
    ARTICLES = {a["article_id"]: a for a in json.load(f)}

# Load posts from separate files
POSTS = []
post_files = ["nanotyrannus.json", "vaquita.json", "gravitational_waves.json", "sea_otters.json", "football.json"]
for filename in post_files:
    full_path = os.path.join(BASE_DIR, "json", filename) 
    if os.path.exists(full_path):
        with open(full_path, encoding="utf-8-sig") as f:
            POSTS.extend(json.load(f))
    else:
        print(f"Warning: File not found at {full_path}")

def attach_article_data(posts):
    enriched = []
    for post in posts:
        article = ARTICLES.get(post["article_id"], {})
        
        # We keep the structure but ensure we aren't losing the new 
        # fields (theme, teaser, key_terms) during the enrichment process.
        enriched_post = {
            "post_id": post.get("post_id"),
            "article_id": post.get("article_id"),
            "title": article.get("title", "Unknown Title"),
            "type": article.get("type", "General"),
            "category": article.get("category", "Uncategorized"),
            "theme": post.get("pages", [{}])[0].get("title", "General Overview"), # New field from processor.py
            "pages": post.get("pages", [])
        }
        
        
        enriched.append(enriched_post)
    return enriched


POSTS = attach_article_data(POSTS)


def filter_posts(types, categories, articles):
    results = POSTS

    # 1. Apply initial filters
    if types:
        results = [p for p in results if p["type"] in types]
    if categories:
        results = [p for p in results if p["category"] in categories]
    if articles:
        results = [p for p in results if p["article_id"] in articles]

    # 2. Group posts by article_id (maintaining their relative order)
    grouped = {}
    for post in results:
        aid = post["article_id"]
        if aid not in grouped:
            grouped[aid] = []
        grouped[aid].append(post)

    # 3. Shuffle the ORDER of the groups themselves 
    # (So one session starts with Physics, another starts with Dinosaurs)
    article_ids = list(grouped.keys())
    random.shuffle(article_ids)

    # 4. Round Robin Interleaving
    interleaved_results = []
    max_posts = max([len(posts) for posts in grouped.values()]) if grouped else 0

    for i in range(max_posts):
        for aid in article_ids:
            # If this article still has a post at this index, add it
            if i < len(grouped[aid]):
                interleaved_results.append(grouped[aid][i])

    return interleaved_results


@app.route("/")
def index():

    types = request.args.getlist("type")
    categories = request.args.getlist("category")
    articles = request.args.getlist("article")

    posts = filter_posts(types, categories, articles)

    all_types = sorted({a["type"] for a in ARTICLES.values()})
    all_categories = sorted({a["category"] for a in ARTICLES.values()})
    all_articles = sorted({a["article_id"] for a in ARTICLES.values()})

    return render_template(
        "index.html",
        posts=posts,
        all_types=all_types,
        all_categories=all_categories,
        all_articles=all_articles
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
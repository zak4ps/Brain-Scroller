from flask import Flask, render_template, request
import json
import random

app = Flask(__name__)

# Load article metadata
with open("articles.json", encoding="utf-8") as f:
    ARTICLES = {a["article_id"]: a for a in json.load(f)}

# Load posts from separate files
POSTS = []
for filename in ["nanot.json", "vaquita.json", "physics.json", "glaciers.json"]:
    with open(filename, encoding="utf-8") as f:
        POSTS.extend(json.load(f))


def attach_article_data(posts):
    enriched = []

    for post in posts:

        article = ARTICLES.get(post["article_id"], {})

        enriched.append({
            "post_id": post["post_id"],
            "article_id": post["article_id"],
            "title": article.get("title"),
            "type": article.get("type"),
            "category": article.get("category"),
            "pages": post["pages"]
        })

    return enriched


POSTS = attach_article_data(POSTS)


def filter_posts(types, categories, articles):

    results = POSTS

    if types:
        results = [p for p in results if p["type"] in types]

    if categories:
        results = [p for p in results if p["category"] in categories]

    if articles:
        results = [p for p in results if p["article_id"] in articles]

    random.shuffle(results)

    return results


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
    app.run(host="0.0.0.0", port=5000, debug=True)
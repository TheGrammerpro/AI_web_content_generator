from flask import Flask, render_template
from article_generation import ArticleGenerate
import datetime as dt

app = Flask(__name__)


@app.route("/")
def homepage():
    year = dt.datetime.now().strftime("%Y")
    return render_template("index.html", year=year)


@app.route("/generic/<page_name>")
def generic(page_name):
    generate_article = ArticleGenerate(page_name)
    generate_article.create_article()
    generate_article.refine_article()
    article_ready = generate_article.make_html_ready()
    print(f"\nThe output:\n{article_ready}\n")
    article_titles = generate_article.titles
    article_authors = generate_article.authors
    article_descriptions = generate_article.descriptions
    article_urls = generate_article.urls
    article_images = generate_article.image_urls
    year = dt.datetime.now().strftime("%Y")
    return render_template("generic.html", article_ready=article_ready, titles=article_titles,
                           authors=article_authors, descriptions=article_descriptions, year=year,
                           urls=article_urls, topic=page_name, images=article_images)


@app.route("/landing")
def landing_page():
    year = dt.datetime.now().strftime("%Y")
    return render_template("landing.html", year=year)


@app.route("/elements")
def elements():
    year = dt.datetime.now().strftime("%Y")
    return render_template("elements.html", year=year)


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def fetch_latest_news():
    url = "https://ec.europa.eu/commission/presscorner/home/en"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    news_items = []
    latest_section = soup.find("section", {"aria-label": "Latest"})
    if not latest_section:
        return news_items

    articles = latest_section.find_all("article")[:5]

    for article in articles:
        title_tag = article.find("a")
        if not title_tag:
            continue
        title = title_tag.get_text(strip=True)
        link = "https://ec.europa.eu" + title_tag.get("href")
        news_items.append({"title": title, "link": link})
    return news_items

@app.route("/")
def index():
    return "Server is running"

@app.route("/news")
def news():
    news = fetch_latest_news()
    if not news:
        return jsonify({"message": "No news available"}), 404
    return jsonify(news)

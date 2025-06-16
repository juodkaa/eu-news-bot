from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def fetch_latest_news():
    url = "https://europospulsas.lt/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    news_items = []

    # На основе структуры сайта выбираем, где заголовки новостей
    articles = soup.select(".news-article__title")  # пример селектора для заголовков

    for article in articles[:5]:  # возьмем первые 5 новостей
        title = article.get_text(strip=True)
        link = article.find("a")["href"] if article.find("a") else None
        if link and not link.startswith("http"):
            link = url.rstrip("/") + "/" + link.lstrip("/")
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

# gunicorn будет запускать сервер, так что app.run() не нужен

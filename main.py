from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup
import os
import logging
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)

# Убираем предупреждение "This is a development server..."
app.wsgi_app = ProxyFix(app.wsgi_app)

def fetch_latest_news():
    url = "https://ec.europa.eu/commission/presscorner/home/en"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    news_items = []
    latest_section = soup.find("section", {"aria-label": "Latest"})
    if not latest_section:
        return news_items

    articles = latest_section.find_all("article")[:5]  # первые 5 новостей

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
        return jsonify({"message": "No news available"})
    return jsonify(news)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    # Отключаем логирование flask для чистоты вывода
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)

    app.run(host="0.0.0.0", port=port)

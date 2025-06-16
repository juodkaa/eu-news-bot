from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def fetch_latest_news():
    url = "https://www.bbc.com/news"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    news_items = []
    articles = soup.find_all("h3", class_="gs-c-promo-heading__title")[:5]

    for article in articles:
        title = article.get_text(strip=True)
        link_tag = article.find_parent("a")
        link = "https://www.bbc.com" + link_tag.get("href") if link_tag else "#"
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

if __name__ == "__main__":
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)  # Отключаем предупреждения Flask
    app.run(host="0.0.0.0", port=8080)

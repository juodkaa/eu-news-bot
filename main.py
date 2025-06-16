from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def fetch_latest_news():
    url = "https://europospulsas.lt/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    news_items = []
    # На основе структуры твоего сайта выбираем блок с новостями
    articles = soup.select("div#content div.entry-title a")[:5]  # первые 5 новостей

    for a in articles:
        title = a.get_text(strip=True)
        link = a.get("href")
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
    app.run(host="0.0.0.0", port=8080)

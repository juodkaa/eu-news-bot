from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route("/")
def index():
    return "Server is running"

@app.route("/news")
def news():
    url = "https://europospulsas.lt/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/90.0.4430.212 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return jsonify({"error": str(e)}), 500

    soup = BeautifulSoup(response.text, "html.parser")
    news_section = soup.find("div", class_="news-list")  # Подставьте правильный класс/тег для новостей
    if not news_section:
        return jsonify({"message": "No news available"})

    news_items = news_section.find_all("article", limit=5)  # Или другой тег, который у вас используется для новостей
    if not news_items:
        return jsonify({"message": "No news available"})

    news_list = []
    for item in news_items:
        title_tag = item.find("h2")  # Или нужный тег для заголовка новости
        link_tag = item.find("a")
        if title_tag and link_tag and link_tag.get("href"):
            news_list.append({
                "title": title_tag.get_text(strip=True),
                "link": link_tag["href"]
            })

    if not news_list:
        return jsonify({"message": "No news available"})

    return jsonify(news_list)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

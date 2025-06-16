from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

PRESS_CORNER_URL = "https://ec.europa.eu/commission/presscorner/home/en"

def fetch_press_news():
    try:
        response = requests.get(PRESS_CORNER_URL)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []

        # В пресс-центре новости в блоках с классом 'ec-press-release' (пример)
        # Нужно уточнить точный селектор под структуру сайта

        # Пример селектора для пресс-релизов:
        articles = soup.select('div.ec-press-release')

        for article in articles[:10]:  # берем максимум 10 новостей
            title_tag = article.select_one('h3 a')
            date_tag = article.select_one('time')
            link = title_tag['href'] if title_tag else None
            title = title_tag.get_text(strip=True) if title_tag else "No title"
            date = date_tag.get_text(strip=True) if date_tag else "No date"
            if link and not link.startswith("http"):
                link = "https://ec.europa.eu" + link

            news_list.append({
                "title": title,
                "date": date,
                "link": link
            })

        if not news_list:
            return {"message": "No news available"}

        return news_list

    except Exception as e:
        return {"message": f"Error fetching news: {str(e)}"}

@app.route("/news")
def news():
    news_data = fetch_press_news()
    return jsonify(news_data)

@app.route("/")
def index():
    return "Press center news API is running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

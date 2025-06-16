from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

PRESS_CORNER_URL = "https://ec.europa.eu/commission/presscorner/home/en"

def fetch_press_news():
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(PRESS_CORNER_URL, headers=headers)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        news_list = []

        # На странице новости обернуты в div с классом 'views-row'
        articles = soup.select('div.views-row')

        for article in articles[:10]:
            title_tag = article.select_one('h3 a')
            date_tag = article.select_one('span.date-display-single')
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

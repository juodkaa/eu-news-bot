from flask import Flask
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

def fetch_latest_news():
    url = "https://ec.europa.eu/commission/presscorner/home/en"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    news_items = []
    articles = soup.find_all("article")[:5]

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
    news = fetch_latest_news()
    if not news:
        return "<p>Нет новостей</p>"
    html = "<h1>Новости с пресс-центра ЕС</h1><ul>"
    for item in news:
        html += f'<li><a href="{item["link"]}" target="_blank">{item["title"]}</a></li>'
    html += "</ul>"
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

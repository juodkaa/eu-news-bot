from flask import Flask, jsonify, render_template_string
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

URL = 'https://www.bbc.com/news'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/114.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Referer': 'https://google.com/',
    'Connection': 'keep-alive'
}

@app.route("/")
def index():
    return "Server is running"

@app.route("/news")
def news():
    try:
        resp = requests.get(URL, headers=headers, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"message": "Failed to fetch news", "error": str(e)}), 500

    soup = BeautifulSoup(resp.text, 'html.parser')

    articles = soup.find_all('article', class_='elementor-post')

    news_list = []
    for article in articles:
        title_tag = article.find('h3', class_='elementor-post__title')
        link_tag = article.find('a', class_='elementor-post__read-more')
        date_tag = article.find('time')

        title = title_tag.text.strip() if title_tag else 'No title'
        link = link_tag['href'] if link_tag and link_tag.has_attr('href') else None
        date = date_tag.text.strip() if date_tag else 'No date'

        news_list.append({
            "title": title,
            "link": link,
            "date": date
        })

    if not news_list:
        return jsonify({"message": "No news available"})

    # Возвращаем JSON
    return jsonify(news_list)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

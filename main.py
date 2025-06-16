from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def index():
    return "Server is running"

@app.route('/news')
def news():
    url = "https://europospulsas.lt/"
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    news_list = []

    # Блок Recent News в правой колонке
    recent_news_section = soup.find('aside', class_='widget_recent_entries')
    if recent_news_section:
        items = recent_news_section.find_all('li')
        for item in items:
            a_tag = item.find('a')
            if a_tag:
                title = a_tag.get_text(strip=True)
                link = a_tag['href']
                news_list.append({'title': title, 'link': link})

    if not news_list:
        return jsonify({"message": "No news available"})

    return jsonify(news_list)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

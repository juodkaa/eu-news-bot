import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify

app = Flask(__name__)

URL = 'https://europospulsas.lt/naujienos-ir-straipsniai/'

@app.route('/')
def index():
    return "Server is running"

@app.route('/news')
def news():
    resp = requests.get(URL)
    if resp.status_code != 200:
        return jsonify({'message': 'Failed to fetch news'}), 500

    soup = BeautifulSoup(resp.text, 'html.parser')
    articles = soup.find_all('article', class_='elementor-post')

    news_list = []
    for article in articles:
        if 'category-nacionaliniai-projektai' not in article.get('class', []):
            continue

        title_tag = article.find('h3', class_='elementor-post__title')
        link_tag = title_tag.find('a') if title_tag else None
        date_tag = article.find('time', class_='elementor-post__meta-date')

        title = title_tag.text.strip() if title_tag else 'No title'
        link = link_tag['href'] if link_tag else '#'
        date = date_tag.text.strip() if date_tag else ''

        news_list.append({'title': title, 'link': link, 'date': date})

    if not news_list:
        return jsonify({'message': 'No news available'})

    return jsonify(news_list)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

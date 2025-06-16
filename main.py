from flask import Flask
import requests
from bs4 import BeautifulSoup
from requests.auth import HTTPBasicAuth
import os

# Настройки WordPress
WP_URL = "https://linale.lt/wp-json/wp/v2/posts"
WP_USER = "p3anjn"  # Замените
WP_APP_PASSWORD = "DeEu QF8K o4tj rULp nFw7 38Te"  # Замените

app = Flask(__name__)

def fetch_news():
    url = "https://ec.europa.eu/commission/presscorner/home/en"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    headlines = soup.find_all("a", class_="press-release-title")[:5]
    for item in headlines:
        title = item.text.strip()
        link = "https://ec.europa.eu" + item["href"]

        if not post_exists(title):
            publish_to_wordpress(title, link)

def post_exists(title):
    params = {"search": title}
    response = requests.get(WP_URL, auth=HTTPBasicAuth(WP_USER, WP_APP_PASSWORD), params=params)
    return any(post["title"]["rendered"] == title for post in response.json())

def publish_to_wordpress(title, link):
    post = {
        "title": title,
        "content": f"<p><a href='{link}'>{link}</a></p>",
        "status": "publish"
    }
    response = requests.post(WP_URL, auth=HTTPBasicAuth(WP_USER, WP_APP_PASSWORD), json=post)
    print(f"Posted: {title}, status: {response.status_code}")

@app.route('/')
def run_parser():
    fetch_news()
    return 'Done.'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from requests.auth import HTTPBasicAuth

# ==== НАСТРОЙКИ ====
WORDPRESS_URL = "https://linale.lt/wp-json/wp/v2/posts"
WORDPRESS_USER = "p3anjn"  # имя пользователя WordPress
WORDPRESS_APP_PASSWORD = "DeEu QF8K o4tj rULp nFw7 38Te"  # вставь сюда application password

SOURCE_URL = "https://ec.europa.eu/commission/presscorner/home/en"

def fetch_news():
    response = requests.get(SOURCE_URL)
    soup = BeautifulSoup(response.text, "html.parser")

    headlines = soup.find_all("a", class_="press-release-title")[:5]

    for item in headlines:
        title = item.text.strip()
        link = "https://ec.europa.eu" + item["href"]

        publish_post(title, link)

def publish_post(title, link):
    post_data = {
        "title": title,
        "content": f"<p>Источник: <a href='{link}'>{link}</a></p>",
        "status": "publish"
    }

    response = requests.post(
        WORDPRESS_URL,
        json=post_data,
        auth=HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_APP_PASSWORD)
    )

    if response.status_code == 201:
        print(f"[{datetime.now()}] ✔ Успешно опубликовано: {title}")
    else:
        print(f"[{datetime.now()}] ❌ Ошибка: {response.status_code} - {response.text}")

if __name__ == "__main__":
    fetch_news()

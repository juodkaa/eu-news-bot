import requests
from bs4 import BeautifulSoup
from datetime import datetime
from requests.auth import HTTPBasicAuth

# ==== НАСТРОЙКИ ====
WORDPRESS_URL = "https://linale.lt/wp-json/wp/v2/posts"
WORDPRESS_USER = "p3anjn"  # имя пользователя WordPress
WORDPRESS_APP_PASSWORD = "DeEu QF8K o4tj rULp nFw7 38Te"  # Application Password

SOURCE_URL = "https://ec.europa.eu/commission/presscorner/home/en"

def fetch_news():
    try:
        response = requests.get(SOURCE_URL)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[{datetime.now()}] Ошибка запроса к источнику: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    headlines = soup.find_all("a", class_="press-release-title")[:5]

    news = []
    for item in headlines:
        title = item.text.strip()
        link = "https://ec.europa.eu" + item.get("href", "")
        news.append({"title": title, "link": link})
    return news

def publish_post(title, link):
    post_data = {
        "title": title,
        "content": f"<p>Источник: <a href='{link}' target='_blank'>{link}</a></p>",
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

def main():
    news_list = fetch_news()
    if not news_list:
        print(f"[{datetime.now()}] Нет новостей для публикации.")
        return

    for news in news_list:
        print(f"[{datetime.now()}] Публикация новости: {news['title']}")
        publish_post(news["title"], news["link"])

if __name__ == "__main__":
    main()

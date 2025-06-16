import requests
from bs4 import BeautifulSoup

url = "https://europospulsas.lt/"
response = requests.get(url)
print("Status code:", response.status_code)

soup = BeautifulSoup(response.text, "html.parser")

articles = soup.select(".news-article__title")
print(f"Found {len(articles)} articles")

for article in articles[:5]:
    title = article.get_text(strip=True)
    link = article.find("a")["href"] if article.find("a") else None
    if link and not link.startswith("http"):
        link = url.rstrip("/") + "/" + link.lstrip("/")
    print(title, link)

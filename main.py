import requests
from bs4 import BeautifulSoup

url = "https://ec.europa.eu/commission/presscorner/home/en"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Ищем все ссылки внутри <h3> (судя по структуре сайта)
headlines = soup.select("h3 a")

print(f"Найдено новостей: {len(headlines)}")

for item in headlines[:5]:
    title = item.text.strip()
    link = item['href']
    if not link.startswith("http"):
        link = "https://ec.europa.eu" + link
    print("Заголовок:", title)
    print("Ссылка:", link)
    print()

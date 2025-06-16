import requests
from bs4 import BeautifulSoup

url = "https://ec.europa.eu/commission/presscorner/home/en"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Выведем все ссылки с классом press-release-title
headlines = soup.find_all("a", class_="press-release-title")

print(f"Найдено новостей: {len(headlines)}")

for item in headlines[:5]:
    print("Заголовок:", item.text.strip())
    print("Ссылка:", "https://ec.europa.eu" + item['href'])
    print()

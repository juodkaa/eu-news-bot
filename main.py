import requests
from bs4 import BeautifulSoup

url = "https://ec.europa.eu/commission/presscorner/detail/en/ip_25_1399"

response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

# Заголовок новости
title = soup.find("h1", class_="page-title").text.strip()

# Текст новости - на странице основное содержимое обычно в блоке с классом 'field-item'
content_block = soup.find("div", class_="field--name-body")
content = content_block.get_text(separator="\n").strip() if content_block else "Нет контента"

print("Заголовок:", title)
print("Содержание:")
print(content)

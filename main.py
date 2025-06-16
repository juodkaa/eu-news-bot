import requests
from bs4 import BeautifulSoup

def fetch_news():
    url = "https://ec.europa.eu/commission/presscorner/home/en"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    headlines = soup.find_all("a", class_="press-release-title")[:5]
    for item in headlines:
        print(item.text.strip(), "|", "https://ec.europa.eu" + item["href"])

if __name__ == "__main__":
    fetch_news()

from flask import Flask
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def fetch_news():
    url = "https://ec.europa.eu/commission/presscorner/home/en"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    headlines = soup.find_all("a", class_="press-release-title")[:5]
    output = []

    for item in headlines:
        title = item.text.strip()
        link = "https://ec.europa.eu" + item["href"]
        output.append(f"{title} | <a href='{link}'>{link}</a>")

    return "<br><br>".join(output)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

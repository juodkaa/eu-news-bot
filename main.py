import httpx
import json
from bs4 import BeautifulSoup, NavigableString, Tag
import requests
from requests.auth import HTTPBasicAuth

# 1. Получаем последние новости
def get_latest_news():
    url = "https://ec.europa.eu/commission/presscorner/api/latestnews?language=en&pagesize=30&pagenumber=1"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://ec.europa.eu/commission/presscorner/home/en"
    }

    with httpx.Client(headers=headers) as client:
        response = client.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data

# 2. Сохраняем refCode в файл
def save_refcodes_to_file(json_data, output_path):
    news_list = json_data.get('docuLanguageListResources', [])
    refcodes = [item.get('refCode', '') for item in news_list if item.get('refCode')]

    with open(output_path, 'w', encoding='utf-8') as f_out:
        for refcode in refcodes:
            f_out.write(refcode + '\n')

    print(f"Сохранено {len(refcodes)} refCode в файл {output_path}")
    return refcodes

# 3. Чистим HTML содержимое новости
def clean_html(html_content, title=None):
    soup = BeautifulSoup(html_content, "html.parser")

    def parse_element(el):
        if isinstance(el, NavigableString):
            return str(el)
        elif isinstance(el, Tag):
            if el.name == 'p':
                return parse_children(el) + "\n\n"
            elif el.name in ['strong', 'b']:
                text = parse_children(el).strip()
                if len(text) < 100:
                    return text.upper()
                else:
                    return text
            elif el.name in ['h1', 'h2', 'h3']:
                return f"\n=== {parse_children(el)} ===\n"
            elif el.name == 'br':
                return "\n"
            elif el.name in ['ul', 'ol']:
                items = []
                for li in el.find_all('li'):
                    items.append(f"- {parse_children(li)}")
                return "\n".join(items) + "\n\n"
            else:
                return parse_children(el)
        else:
            return ""

    def parse_children(el):
        return "".join(parse_element(c) for c in el.children)

    text = parse_children(soup).strip()

    if title:
        text = f"=== {title} ===\n\n" + text

    return text

# 4. Получаем детали новости по refCode
def get_document_details(refcode):
    url = f"https://ec.europa.eu/commission/presscorner/api/documents?reference={refcode}&language=en"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://ec.europa.eu/commission/presscorner/home/en"
    }
    with httpx.Client(headers=headers) as client:
        response = client.get(url)
        response.raise_for_status()
        data = response.json()

    if 'docuLanguageResource' not in data or data['docuLanguageResource'] is None:
        raise ValueError("Отсутствует docuLanguageResource в ответе")

    title = data['docuLanguageResource'].get('title', 'Без заголовка')
    html_content = data['docuLanguageResource'].get('htmlContent', '')

    clean_content = clean_html(html_content)

    return title, clean_content

# 5. Публикация на WordPress
def post_to_wordpress(title, content):
    url = "https://linale.lt/wp-json/wp/v2/posts"
    user = "p3anjn"
    app_password = "DeEu QF8K o4tj rULp nFw7 38Te"

    headers = {
        "Content-Type": "application/json"
    }

    post = {
        "title": title,
        "content": content,
        "status": "publish"
    }

    response = requests.post(url, json=post, headers=headers,
                             auth=HTTPBasicAuth(user, app_password))

    if response.status_code == 201:
        print(f"Публикация успешна: {title}")
    else:
        print(f"Ошибка публикации: {response.status_code} - {response.text}")

# Основной запуск
def main():
    # Получаем свежие новости и сохраняем JSON
    news_data = get_latest_news()
    with open("latest_news.json", "w", encoding="utf-8") as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    print("Данные сохранены в latest_news.json")

    # Сохраняем refCode в файл и получаем список
    refcodes = save_refcodes_to_file(news_data, "refcodes.txt")

    # Получаем и сохраняем каждую новость по refCode и публикуем на сайт
    for ref_code in refcodes:
        print(f"Fetching news {ref_code}...")
        try:
            title, content = get_document_details(ref_code)
        except Exception as e:
            print(f"Ошибка при загрузке новости {ref_code}: {e}")
            continue

        filename = ref_code.replace("/", "_") + ".txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"{title}\n\n{content}")

        # Публикуем на WordPress
        post_to_wordpress(title, content)

    print("Finished fetching and posting all news.")

if __name__ == "__main__":
    main()

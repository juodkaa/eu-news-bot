import httpx
import json
import base64
import re
from bs4 import BeautifulSoup, NavigableString, Tag

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

# 5. Публикация новости в WordPress
def publish_post_to_wp(title, content, username, application_password):
    wp_url = "https://linale.lt/wp-json/wp/v2/posts"

    credentials = f"{username}:{application_password}"
    token = base64.b64encode(credentials.encode())
    headers = {
        "Authorization": f"Basic {token.decode('utf-8')}",
        "Content-Type": "application/json"
    }

    post_data = {
        "title": title,
        "content": content,
        "status": "publish"
    }

    response = httpx.post(wp_url, headers=headers, json=post_data)
    if response.status_code == 201:
        print(f"Новость '{title}' опубликована успешно.")
    else:
        print(f"Ошибка публикации '{title}': {response.status_code} - {response.text}")

# Дополнительно: нормализация заголовка для сравнения
def normalize_title(title):
    text = BeautifulSoup(title, "html.parser").get_text()
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

# Получаем список уже опубликованных заголовков из WordPress
def get_published_titles(username, application_password):
    wp_url = "https://linale.lt/wp-json/wp/v2/posts?per_page=100"
    credentials = f"{username}:{application_password}"
    token = base64.b64encode(credentials.encode())
    headers = {
        "Authorization": f"Basic {token.decode('utf-8')}"
    }

    response = httpx.get(wp_url, headers=headers)
    if response.status_code == 200:
        posts = response.json()
        titles = [normalize_title(post['title']['rendered']) for post in posts]
        return set(titles)
    else:
        print(f"Ошибка при получении списка публикаций: {response.status_code}")
        return set()

# Основной запуск
def main():
    news_data = get_latest_news()
    with open("latest_news.json", "w", encoding="utf-8") as f:
        json.dump(news_data, f, ensure_ascii=False, indent=2)
    print("Данные сохранены в latest_news.json")

    refcodes = save_refcodes_to_file(news_data, "refcodes.txt")

    published_titles = get_published_titles("p3anjn", "DeEu QF8K o4tj rULp nFw7 38Te")

    for ref_code in refcodes:
        print(f"Fetching news {ref_code}...")
        try:
            title, content = get_document_details(ref_code)
        except Exception as e:
            print(f"Ошибка при загрузке новости {ref_code}: {e}")
            continue

        normalized_title = normalize_title(title)
        if normalized_title in published_titles:
            print(f"Новость '{title}' уже опубликована, пропускаем.")
            continue

        publish_post_to_wp(title, content, "p3anjn", "DeEu QF8K o4tj rULp nFw7 38Te")

    print("Finished fetching all news.")

if __name__ == "__main__":
    main()

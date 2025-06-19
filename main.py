import httpx
import json
from bs4 import BeautifulSoup, NavigableString, Tag
import base64
import os

REFCODES_FILE = "refcodes.txt"

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

def load_refcodes():
    if os.path.exists(REFCODES_FILE):
        with open(REFCODES_FILE, "r", encoding="utf-8") as f:
            refcodes = set(line.strip() for line in f if line.strip())
        print(f"Loaded {len(refcodes)} refCodes from file.")
        return refcodes
    return set()

def save_refcodes(refcodes):
    with open(REFCODES_FILE, "w", encoding="utf-8") as f:
        for ref in sorted(refcodes):
            f.write(ref + "\n")
    print(f"Saved {len(refcodes)} refCodes to file.")

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
        return True
    else:
        print(f"Ошибка публикации '{title}': {response.status_code} - {response.text}")
        return False

def main():
    refcodes_published = load_refcodes()

    news_data = get_latest_news()
    news_list = news_data.get('docuLanguageListResources', [])

    new_refcodes = [item['refCode'] for item in news_list if item.get('refCode') and item['refCode'] not in refcodes_published]

    if not new_refcodes:
        print("Нет новых новостей для публикации.")
        return

    for ref_code in new_refcodes:
        print(f"Обрабатываем новость {ref_code}...")
        try:
            title, content = get_document_details(ref_code)
        except Exception as e:
            print(f"Ошибка при загрузке новости {ref_code}: {e}")
            continue

        success = publish_post_to_wp(title, content, "p3anjn", "DeEu QF8K o4tj rULp nFw7 38Te")
        if success:
            refcodes_published.add(ref_code)

    save_refcodes(refcodes_published)
    print("Обработка новостей завершена.")

if __name__ == "__main__":
    main()

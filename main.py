from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time

def fetch_latest_news():
    # Настройки браузера (без головы — без графического окна)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Запуск драйвера
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        url = "https://ec.europa.eu/commission/presscorner/home/en"
        driver.get(url)

        # Ждем загрузки страницы и элементов (можно увеличить если сеть медленная)
        time.sleep(5)

        # Ищем блок Latest
        latest_block = driver.find_element(By.ID, "latest")

        # Ищем все новости в блоке
        news_items = latest_block.find_elements(By.CSS_SELECTOR, "article")

        print(f"Найдено новостей: {len(news_items)}")

        for item in news_items:
            title_element = item.find_element(By.CSS_SELECTOR, "h2 a")
            title = title_element.text
            link = title_element.get_attribute("href")

            print(f"Заголовок: {title}")
            print(f"Ссылка: {link}")
            print("---")

    except Exception as e:
        print("Ошибка при получении новостей:", e)
    finally:
        driver.quit()

if __name__ == "__main__":
    fetch_latest_news()

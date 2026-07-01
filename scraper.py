import os
import time
import schedule
import requests

from fake_useragent import UserAgent

from ai_assistant import analyze_vacancy_local_ollama
from pg_queries import save_all_data, find_new_vacancies
from process_hh import extract_vacancies_from_file, extract_description_from_content
from telegram_api import send_message
from dotenv import load_dotenv

load_dotenv()

RESPONSE_FILENAME = os.environ.get("HH_RESPONSE_FILENAME", "hh_response.txt")
RESUME = open('rs.txt', 'r').read()
STOP_FACTORS = ["Вакансия для тестировщика (QA Engineer, Тестирование, Тестировщик)",
                "В вакансии НЕ указан фреймворк Spring",
                "Вакансия НЕ для Java бэкенд разработчика"]
cities = ["Санкт-Петербург", "Москва"]


def get_headers() -> dict:
    """Генерирует реалистичные заголовки для обхода базовой защиты hh.ru"""
    ua = UserAgent()
    return {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0'
    }


def collect_java_vacancies(max_pages:int = 10):
    """Собирает ссылки и названия свежих вакансий за последние сутки"""
    base_url = "https://hh.ru/search/vacancy"

    # Очищаем содержимое файла
    with open(RESPONSE_FILENAME, "w"):
        pass

    # Инициализируем сессию для сохранения кук между запросами
    session = requests.Session()

    for page in range(max_pages):
        print(f"Парсим страницу {page + 1}...")

        params = {
            'text': 'Java разработчик',
            'search_period': 1,  # За последние 24 часа
            'page': page,  # Текущая страница (индексация с 0)
            'items_on_page': 30
        }

        try:
            # Делаем запрос с фальшивыми заголовками реального пользователя
            response = session.get(base_url, params=params, headers=get_headers(), timeout=10)

            time.sleep(5)
            if response.status_code == 403:
                print("Ошибка 403: Доступ заблокирован hh.ru (включилась защита Cloudflare/Капча).")
                continue

            if response.status_code != 200:
                print(f"Ошибка получения страницы: статус {response.status_code}")
                continue

            with open(RESPONSE_FILENAME, "a") as n_file:
                n_file.write(response.text)

        except Exception as e:
            print(f"Произошла ошибка при парсинге страницы {page}: {e}")
            continue

    print(f"Тело ответа записано в файл {RESPONSE_FILENAME}")

def parse_vacancy_description(url: str) -> list[str]:
    """Запрашивает и парсит описание вакансии"""
    session = requests.Session()
    response = session.get(url, headers=get_headers(), timeout=10)

    if response.status_code == 403:
        print("Ошибка 403: Доступ заблокирован hh.ru (включилась защита Cloudflare/Капча).")
        return []

    if response.status_code != 200:
        print(f"Ошибка получения страницы: статус {response.status_code}")
        return []

    return extract_description_from_content(response.text)


def main_job():
    print("Запуск парсера свежих Java-вакансий...")
    collect_java_vacancies()

    print(f"Анализируем файл {RESPONSE_FILENAME}...")
    vacancies = extract_vacancies_from_file(RESPONSE_FILENAME)

    if not vacancies:
        print("Вакансии не найдены. Проверьте имя файла или его содержимое.")
        return

    print("Удаляем ранее обработанные вакансии...")
    vacancies = find_new_vacancies(vacancies)

    print(f"Успешно извлечено вакансий: {len(vacancies)}\n")
    save_all_data(vacancies)

    for vacancy in vacancies:
        try:
            data = parse_vacancy_description(vacancy.get('url', ''))

            time.sleep(3)
            if len(data) == 0 or (len(data) > 1 and data[1] not in cities):
                continue

            description = vacancy.get('title', '') + '\n' + data[0]
            review = analyze_vacancy_local_ollama(RESUME, description, STOP_FACTORS)
            print(review)

            if review.get('should_apply', True) and review.get('relevance_percentage', 0) >= 50:
                send_message(vacancy.get('title', ''), vacancy.get('url', ''))

        except Exception as e:
            print(f"Произошла ошибка при получении описания вакансии {vacancy.get('title')}: {e}")


def main():
    # Настраиваем интервал
    schedule.every(5).minutes.do(main_job)
    print("Планировщик запущен. Ожидание задач...")

    while True:
        schedule.run_pending()
        time.sleep(30)


if __name__ == "__main__":
    main()

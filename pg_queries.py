import os
import psycopg

from typing import List

DB_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hh")

def save_data(vacancyId: int, title: str, url: str):
    """Открывает соединение и сохраняет запись в БД. Закрывает соединение после завершения операции"""
    try:
        # Открываем соединение и курсор
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                # SQL-запрос с защитой от SQL-инъекций
                cur.execute(
                    """INSERT INTO public.vacancies (vacancy_id, title, url) VALUES (%s, %s, %s) 
                        ON CONFLICT (vacancy_id) DO NOTHING;""",
                    (vacancyId, title, url))

        # При выходе из with-блока conn.commit() вызовется автоматически
    except Exception as e:
        print(e)

def save_all_data(data: List[dict]):
    """Открывает соединение и сохраняет все данные в БД. Закрывает соединение после завершения операции"""
    if not data:
        return

    try:
        # Открываем соединение и курсор
        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                # Используем именованные плейсхолдеры, совпадающие с ключами словаря
                query = """
                        INSERT INTO public.vacancies (vacancy_id, title, url)
                        VALUES (%(vacancyId)s, %(title)s, %(url)s);
                        """

                # В ЭТОТ МОМЕНТ база данных начинает транзакцию и выполняет в ней все вставки из списка.
                # executemany принимает строку запроса и список словарей
                cur.executemany(query, data)

        # При выходе из блока 'with psycopg.connect' автоматически вызовется conn.commit(),
        # и все записи сохранятся в базе ОДНИМ пакетом (в одной транзакции).
    except Exception as e:
        print(e)


def get_processed_vacancies(ids: List[int]) -> List[int]:
    """Возвращает список вакансий который уже были обработаны"""
    try:
        if not ids:
            return []

        with psycopg.connect(DB_URL) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT vacancy_id FROM public.vacancies WHERE vacancy_id = ANY(%s);",(ids, ))

                rows = cur.fetchall()
                data = []
                for row in rows:
                    vacancyId = row[0]
                    data.append(vacancyId)

                return data
    except Exception as e:
        print(e)
        return []


def main():
    # save_data(133258174, "Back end PHP разработчик", "https://hh.ru/vacancy/133258174")
    # data = get_processed_vacancies([133258174])
    # print(data)

    # Входные данные
    vacancies_data = [
        {"vacancyId": 101, "title": "Python Developer", "url": "https://hh.ru/vacancy/101"},
        {"vacancyId": 102, "title": "Data Scientist", "url": "https://hh.ru/vacancy/102"},
        {"vacancyId": 103, "title": "DevOps Engineer", "url": "https://hh.ru/vacancy/103"},
    ]
    save_all_data(vacancies_data)

if __name__ == "__main__":
    main()

import re
import json

from typing import List


def extract_vacancies_from_file(file_path: str)-> List[dict]:
    """Извлекает массив vacancies, корректно обрабатывая лишние данные на конце"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        ids = re.findall(r'"vacancyId"\s*:\s*(\d+)', content)
        names = re.findall(r'"vacancyId":\d+,"name"\s*:\s*"([^"]+)"', content)

        extracted_list = []

        for v_id, name in zip(ids, names):
            extracted_list.append({
                "vacancyId": int(v_id),
                "title": name,
                "url": f"https://hh.ru/vacancy/{v_id}"
            })
        return extracted_list

    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")
        return []


def extract_description_from_content(html_content: str) -> str:
    """Извлекает описание вакансии из html"""
    try:
        description = re.findall(r'data-qa="vacancy-description"><p>(.+?)</div></div>',
                                 html_content, flags=re.DOTALL)
        return description[0]
    except Exception as e:
        print(f"Ошибка при поиске описания вакансии: {e}")
        return ''


def main():
    # Имя сохраненного текстового файла
    file_name = "hh_response.txt"

    print(f"Анализируем файл {file_name}...")
    vacancies = extract_vacancies_from_file(file_name)

    if not vacancies:
        print("Вакансии не найдены. Проверьте имя файла или его содержимое.")
        return

    print(f"Успешно извлечено вакансий: {len(vacancies)}\n")

    with open("extracted_vacancies.json", "w", encoding="utf-8") as out_f:
        json.dump(vacancies, out_f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()

import json
from openai import OpenAI

# 1. Настраиваем клиента на локальный сервер Ollama
# По умолчанию Ollama работает на порту 11434
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama"  # Сюда можно вписать любую строку, Ollama её проигнорирует
)

def analyze_resume(resume: str) -> dict:
    prompt = f"""
    Ты — автоматический ассистент по оценке резюме. Мы ищем Java разработчика.
    Посмотри резюме и дай оценку кандидату от 0 до 100
    {{
        "relevance_percentage": <число от 0 до 100>,
        "should_apply": <true или false>,
        "reason": "<краткое объяснение>"
    }}
    РЕЗЮМЕ КАНДИДАТА:
    {resume}
    """

    response = client.chat.completions.create(
        model="llama3.1",
        messages=[
            {
                "role": "system",
                "content": "Ты — полезный ИИ-помощник. Твои ответы всегда состоят ТОЛЬКО из валидного JSON-объекта. Не пиши никакого текста до или после JSON."
            },
            {"role": "user", "content": prompt}
        ],
        # Включаем JSON-режим для Ollama
        response_format={"type": "json_object"},
        temperature=0.1  # Низкая температура, чтобы модель меньше фантазировала
    )
    # Парсим JSON
    content = response.choices[0].message.content
    result = json.loads(content)
    return result


def analyze_vacancy_local_ollama(resume: str, vacancy: str, stop_factors: list[str]) -> dict:
    stop_factors_text = "\n".join([f"- {factor}" for factor in stop_factors])

    # Формируем промпт и жестко требуем вернуть ТОЛЬКО JSON
    prompt = f"""
    Ты — автоматический ассистент по подбору вакансий. Сравни резюме и вакансию.
    Ты должен вернуть ответ строго в формате JSON, соответствующем этой структуре:
    {{
        "relevance_percentage": <число от 0 до 100>,
        "should_apply": <true или false>,
        "triggered_stop_factors": ["список", "сработавших", "стоп-факторов"],
        "reason": "<краткое объяснение>"
    }}

    КРИТИЧЕСКОЕ ПРАВИЛО:
    Перед анализом навыков проверь вакансию на наличие СТОП-ФАКТОРОВ. Если в вакансии обнаружен хотя бы один стоп-фактор из списка ниже, ты ОБЯЗАН:
    1. Установить relevance_percentage = 0
    2. Установить should_apply = false
    3. Добавить этот фактор в список triggered_stop_factors
    Игнорируй любые совпадения по навыкам, если сработал стоп-фактор.

    СПИСОК СТОП-ФАКТОРОВ:
    {stop_factors_text}

    РЕЗЮМЕ КАНДИДАТА:
    {resume}

    ОПИСАНИЕ ВАКАНСИИ:
    {vacancy}
    """

    try:
        # 2. Вызываем вашу локальную модель llama3.1 (в Ollama она называется 'llama3.1:3b' или 'llama3.1')
        # //TODO подумать как переиспользовать сессию
        response = client.chat.completions.create(
            model="llama3.1",
            messages=[
                {
                    "role": "system",
                    "content": "Ты — полезный ИИ-помощник. Твои ответы всегда состоят ТОЛЬКО из валидного JSON-объекта. Не пиши никакого текста до или после JSON."
                },
                {"role": "user", "content": prompt}
            ],
            # Включаем JSON-режим для Ollama
            response_format={"type": "json_object"},
            temperature=0.1  # Низкая температура, чтобы модель меньше фантазировала
        )

        # Парсим JSON
        content = response.choices[0].message.content
        result = json.loads(content)
        return result

    except Exception as e:
        print(f"Ошибка при работе с локальной Ollama: {e}")
        # Если модель добавила лишний текст вокруг JSON, покажем сырой ответ для отладки
        if 'response' in locals() and response.choices[0].message.content:
             print("Сырой ответ модели:", response.choices[0].message.content)
        return {}

def main():
    # --- ТЕСТИРОВАНИЕ ---
    my_resume = "Python разработчик. Опыт 2 года. Стек: FastAPI, PostgreSQL, Docker."
    test_vacancy = "Ищем QA Automation (Тестировщика). Писать тесты на Python для API."
    my_stop_factors = ["Вакансия для тестировщика (QA, Тестирование, Тестировщик)"]

    print("Запрос к локальной нейросети Ollama...")
    analysis_result = analyze_vacancy_local_ollama(my_resume, test_vacancy, my_stop_factors)
    print(analysis_result)

    print("Запрос к локальной нейросети Ollama...")
    test_vacancy = "Ищем бэкенд Python разработчика. Стэк: FastAPI API."
    analysis_result = analyze_vacancy_local_ollama(my_resume, test_vacancy, my_stop_factors)
    print(analysis_result)

if __name__ == "__main__":
    main()

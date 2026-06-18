import os
import requests

from dotenv import load_dotenv

load_dotenv()

CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
BOT_ID = os.environ.get("TELEGRAM_BOT_TOKEN")
PROXY_URL = os.environ.get("PROXY_URL")
URL = "https://{}/bot{}/sendMessage".format(PROXY_URL, BOT_ID)

def send_message(title: str, address: str) -> bool:
    """Отправляет информацию о вакансии в Telegram"""
    # Форматируем красивый текст сообщения с HTML-тегами
    message_text = (
        f"💼 <b>Вакансия: {title}</b>\n\n"
        f"📋 <b>Ссылка на вакансию:</b> {address}\n"
    )

    # Данные для отправки
    payload = {
        "chat_id": CHAT_ID,
        "text": message_text,
        "parse_mode": "HTML"  # Позволяет использовать теги <b>, <i>, <code>
    }

    try:
        # Отправляем POST-запрос с таймаутом 10 секунд (чтобы скрипт не завис при сбое сети)
        response = requests.post(URL, json=payload, timeout=10.0)

        # Если Telegram вернул статус ошибки (например, 400 или 404), сгенерируется исключение
        response.raise_for_status()
        return True
    except requests.exceptions.HTTPError as e:
        print(f"Ошибка со стороны Telegram API: {e.response.text}")
        return False
    except Exception as e:
        print('ERROR:', e)
        return False


def main():
    res = send_message("Senior Java Developer", "https://hh.ru/vacancy/134041627")
    if not res:
        print("The message was not sent!")


if __name__ == "__main__":
    main()


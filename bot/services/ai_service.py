import os
import json
from groq import AsyncGroq
from bot.data.catalog import get_catalog_text
from dotenv import load_dotenv

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """Ты — NomadJol AI, помощник для туристов в Кыргызстане.
Твоя задача — подобрать подходящих туроператоров из каталога под запрос туриста.

КАТАЛОГ ОПЕРАТОРОВ:
{catalog}


ПРАВИЛА ОТВЕТА:
- Рекомендуй 2-3 оператора которые подходят под запрос
- Учитывай: тип тура, регион, бюджет, количество дней
- Отвечай на том языке на котором пишет турист (RU/EN)
- НЕ выдумывай операторов которых нет в каталоге

СТРОГИЙ ФОРМАТ ОТВЕТА (всегда именно так):

[эмодзи тура] [Тип тура] в [Регион]! Вот лучшие варианты для тебя:

1. [Название оператора]
   📍 [Регион] | 💰 $[цена]/день | 👥 до [макс] чел | 📅 [длительность] дней
   📞 [телефон] | ✈️ [контакт]

2. [Название оператора]
   📍 [Регион] | 💰 $[цена]/день | 👥 до [макс] чел | 📅 [длительность] дней
   📞 [телефон] | ✈️ [контакт]

[1-2 предложения — почему именно эти операторы подходят]

💳 Оплата через NomadJol — безопасно, 30% депозит
"""


def get_registered_operators_text() -> str:
    """Читает зарегистрированных операторов из operators.json"""
    path = "operators.json"
    if not os.path.exists(path):
        return ""
    try:
        with open(path, encoding="utf-8") as f:
            ops = json.load(f)
        if not ops:
            return ""
        lines = []
        for op in ops:
            lines.append(
                f"ID:{op.get('id', '?')} | {op.get('name', '?')} | "
                f"{op.get('tour_type', '?')} | {op.get('region', '?')} | "
                f"${op.get('price_per_day', '?')}/день | "
                f"до {op.get('max_people', '?')} чел | "
                f"{op.get('duration', '?')} дней | "
                f"контакт: {op.get('contact', '?')} | "
                f"тел: {op.get('phone', '?')}"
            )
        return "\n".join(lines)
    except Exception:
        return ""


def get_full_catalog() -> str:
    """Объединяет хардкод + зарегистрированных операторов"""
    base = get_catalog_text()
    registered = get_registered_operators_text()
    if registered:
        return base + "\n\n--- НОВЫЕ ЗАРЕГИСТРИРОВАННЫЕ ОПЕРАТОРЫ ---\n" + registered
    return base


async def ask_ai(user_message: str, chat_history: list = None) -> str:
    catalog = get_full_catalog()  # <-- теперь видит всех
    system = SYSTEM_PROMPT.format(catalog=catalog)

    messages = []
    if chat_history:
        messages.extend(chat_history[-6:])
    messages.append({"role": "user", "content": user_message})

    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": system}] + messages,
        max_tokens=1024,
        temperature=0.7,
    )

    return response.choices[0].message.content
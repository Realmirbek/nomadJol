import os
from groq import AsyncGroq
from bot.data.catalog import get_catalog_text
from dotenv import load_dotenv

load_dotenv()

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """Ты — NomadJol AI, помощник для туристов в Кыргызстане.
Твоя задача — подобрать подходящих туроператоров из каталога под запрос туриста.

КАТАЛОГ ОПЕРАТОРОВ:
{catalog}

ПРАВИЛА:
- Рекомендуй 2-3 оператора из каталога которые подходят под запрос
- Учитывай: тип тура, регион, бюджет, количество дней
- Отвечай на том языке на котором пишет турист (RU/EN)
- Формат ответа — понятный, с эмодзи, показывай цену и контакт
- Если запрос непонятен — уточни что именно хочет турист
- НЕ выдумывай операторов которых нет в каталоге
- В конце всегда добавляй: "💳 Оплата через NomadJol — безопасно, 30% депозит"
"""


async def ask_ai(user_message: str, chat_history: list = None) -> str:
    catalog = get_catalog_text()
    system = SYSTEM_PROMPT.format(catalog=catalog)

    messages = []
    if chat_history:
        messages.extend(chat_history[-6:])  # последние 3 пары
    messages.append({"role": "user", "content": user_message})

    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "system", "content": system}] + messages,
        max_tokens=1024,
        temperature=0.7,
    )

    return response.choices[0].message.content
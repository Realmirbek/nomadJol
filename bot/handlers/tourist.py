import json
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.services.ai_service import ask_ai

router = Router()

STATS_FILE = "stats.json"


def load_stats() -> dict:
    if not os.path.exists(STATS_FILE):
        return {"total": 0, "unique_users": [], "countries": {}}
    try:
        with open(STATS_FILE, encoding="utf-8") as f:
            data = json.load(f)
            # на случай если старый stats.json без поля countries
            if "countries" not in data:
                data["countries"] = {}
            if "unique_users" not in data:
                data["unique_users"] = []
            return data
    except Exception:
        return {"total": 0, "unique_users": [], "countries": {}}


def save_stats(stats: dict):
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


chat_histories: dict = {}
stats: dict = load_stats()

COUNTRIES = [
    ("🇷🇺", "Россия", "RU"),
    ("🇩🇪", "Германия", "DE"),
    ("🇺🇸", "США", "US"),
    ("🇰🇿", "Казахстан", "KZ"),
    ("🇫🇷", "Франция", "FR"),
    ("🇬🇧", "Великобритания", "GB"),
    ("🇨🇳", "Китай", "CN"),
    ("🌍", "Другая", "OTHER"),
]


@router.message(CommandStart())
async def start(message: Message):
    # Кнопки выбора страны
    kb = InlineKeyboardBuilder()
    for flag, name, code in COUNTRIES:
        kb.button(text=f"{flag} {name}", callback_data=f"country_{code}")
    kb.adjust(2)

    await message.answer(
        f"👋 Привет! Я *NomadJol* — твой гид по Кыргызстану.\n\n"
        f"🌍 Откуда ты?",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )


@router.callback_query(F.data.startswith("country_"))
async def handle_country(callback: CallbackQuery):
    code = callback.data.replace("country_", "")

    # Сохраняем страну в статистику
    stats["countries"][code] = stats["countries"].get(code, 0) + 1

    # Уникальные пользователи
    user_id = str(callback.from_user.id)
    if user_id not in stats["unique_users"]:
        stats["unique_users"].append(user_id)

    save_stats(stats)

    # Показываем главное меню
    kb = InlineKeyboardBuilder()
    kb.button(text="🏔 Найти тур", callback_data="find_tour")
    kb.button(text="📋 Зарегистрировать услугу", callback_data="register_operator")
    kb.adjust(1)

    await callback.message.edit_text(
        f"👋 Привет! Я *NomadJol* — твой гид по Кыргызстану.\n\n"
        f"🏔 Треккинг, конные туры, кемпинг — подберу лучших операторов под твой запрос.\n\n"
        f"Просто напиши что хочешь — например:\n"
        f"_'Хочу конный тур 3 дня в Каракол, нас 2 человека'_\n"
        f"_'Looking for 5-day trekking, budget $200'_",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )
    await callback.answer()


@router.callback_query(F.data == "find_tour")
async def cb_find_tour(callback: CallbackQuery):
    await callback.message.answer(
        "Расскажи что хочешь:\n"
        "• Тип тура (треккинг / конный / кемпинг)\n"
        "• Регион или без разницы\n"
        "• Сколько дней\n"
        "• Сколько человек\n"
        "• Бюджет примерно\n\n"
        "Или пиши как хочешь — пойму 😊"
    )
    await callback.answer()


@router.message(Command("stats"))
async def stats_cmd(message: Message):
    total = stats.get("total", 0)
    unique = len(stats.get("unique_users", []))
    countries = stats.get("countries", {})

    country_names = {c[2]: f"{c[0]} {c[1]}" for c in COUNTRIES}
    countries_text = "\n".join(
        f"  {country_names.get(k, k)}: {v}"
        for k, v in sorted(countries.items(), key=lambda x: -x[1])
    ) or "  пока нет данных"

    await message.answer(
        f"📊 *Аналитика NomadJol*\n\n"
        f"🔍 Запросов туристов: *{total}*\n"
        f"👤 Уникальных пользователей: *{unique}*\n"
        f"🏔 Операторов в каталоге: *7*\n\n"
        f"🌍 *География:*\n{countries_text}",
        parse_mode="Markdown"
    )


@router.message(F.text)
async def handle_tourist_message(message: Message):
    user_id = message.from_user.id
    user_text = message.text

    # Счётчик запросов
    stats["total"] = stats.get("total", 0) + 1

    # Уникальные пользователи
    user_id_str = str(user_id)
    if user_id_str not in stats.get("unique_users", []):
        if "unique_users" not in stats:
            stats["unique_users"] = []
        stats["unique_users"].append(user_id_str)

    save_stats(stats)

    # История чата
    if user_id not in chat_histories:
        chat_histories[user_id] = []

    await message.bot.send_chat_action(message.chat.id, "typing")

    try:
        response = await ask_ai(user_text, chat_histories[user_id])

        chat_histories[user_id].append({"role": "user", "content": user_text})
        chat_histories[user_id].append({"role": "assistant", "content": response})

        kb = InlineKeyboardBuilder()
        kb.button(text="💳 Оплатить депозит 30%", callback_data="pay_deposit")
        kb.button(text="🔄 Другой вариант", callback_data="find_tour")
        kb.adjust(1)

        await message.answer(response, reply_markup=kb.as_markup())

    except Exception as e:
        await message.answer("⚠️ Что-то пошло не так, попробуй ещё раз.")
        print(f"AI Error: {e}")


@router.callback_query(F.data == "pay_deposit")
async def pay_deposit(callback: CallbackQuery):
    await callback.message.answer(
        "💳 *Оплата депозита*\n\n"
        "🔄 Интеграция с KICB Bank в разработке.\n\n"
        "Сейчас наш менеджер свяжется с тобой для подтверждения брони:\n"
        "📞 @nomadJol\_support",
        parse_mode="Markdown"
    )
    await callback.answer()
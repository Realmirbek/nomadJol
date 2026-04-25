from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.services.ai_service import ask_ai

router = Router()

# Простое хранение истории в памяти
chat_histories: dict = {}
request_counter: dict = {"total": 0}


@router.message(CommandStart())
async def start(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="🏔 Найти тур", callback_data="find_tour")
    kb.button(text="📋 Зарегистрировать услугу", callback_data="register_operator")
    kb.adjust(1)

    await message.answer(
        f"👋 Привет! Я *NomadJol* — твой гид по Кыргызстану.\n\n"
        f"🏔 Треккинг, конные туры, кемпинг — подберу лучших операторов под твой запрос.\n\n"
        f"Просто напиши что хочешь — например:\n"
        f"_'Хочу конный тур 3 дня в Каракол, нас 2 человека'_\n"
        f"_'Looking for 5-day trekking, budget $200'_",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )


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
async def stats(message: Message):
    total = request_counter.get("total", 0)
    unique_users = len(chat_histories)
    await message.answer(
        f"📊 *Аналитика NomadJol*\n\n"
        f"🔍 Запросов туристов: *{total}*\n"
        f"👤 Уникальных пользователей: *{unique_users}*\n"
        f"🏔 Операторов в каталоге: *7*",
        parse_mode="Markdown"
    )


@router.message(F.text)
async def handle_tourist_message(message: Message):
    user_id = message.from_user.id
    user_text = message.text

    # Счётчик запросов
    request_counter["total"] = request_counter.get("total", 0) + 1

    # История чата
    if user_id not in chat_histories:
        chat_histories[user_id] = []

    await message.bot.send_chat_action(message.chat.id, "typing")

    try:
        response = await ask_ai(user_text, chat_histories[user_id])

        # Сохраняем историю
        chat_histories[user_id].append({"role": "user", "content": user_text})
        chat_histories[user_id].append({"role": "assistant", "content": response})

        # Кнопка оплаты
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
        "📞 @nomadJol\\_support",
        parse_mode="Markdown"
    )
    await callback.answer()
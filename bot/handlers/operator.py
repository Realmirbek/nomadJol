import json
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import ReplyKeyboardRemove

router = Router()

OPERATORS_FILE = "operators.json"


def load_operators() -> list:
    """Загружаем операторов из файла при старте"""
    if not os.path.exists(OPERATORS_FILE):
        return []
    try:
        with open(OPERATORS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_operators(operators: list):
    """Сохраняем список операторов в файл"""
    with open(OPERATORS_FILE, "w", encoding="utf-8") as f:
        json.dump(operators, f, ensure_ascii=False, indent=2)


# Загружаем при старте — данные не потеряются после перезапуска
registered_operators: list = load_operators()


class OperatorForm(StatesGroup):
    name = State()
    tour_type = State()
    region = State()
    description = State()
    price_per_day = State()
    max_people = State()
    duration = State()
    contact = State()
    phone = State()


@router.callback_query(F.data == "register_operator")
@router.message(Command("register"))
async def start_registration(event, state: FSMContext):
    msg = event if isinstance(event, Message) else event.message

    await state.set_state(OperatorForm.name)
    await msg.answer(
        "📋 *Регистрация туроператора в NomadJol*\n\n"
        "После регистрации ваши услуги увидят тысячи туристов.\n"
        "Комиссия: 10% только при успешном бронировании.\n\n"
        "Шаг 1/9: Введите название вашей компании или имя гида:",
        parse_mode="Markdown"
    )
    if isinstance(event, CallbackQuery):
        await event.answer()


@router.message(OperatorForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)

    kb = ReplyKeyboardBuilder()
    for t in ["🏇 Конный тур", "🥾 Треккинг", "⛺ Кемпинг", "🧗 Альпинизм", "🚴 Велотур"]:
        kb.button(text=t)
    kb.adjust(2)

    await state.set_state(OperatorForm.tour_type)
    await message.answer(
        "Шаг 2/9: Тип услуги:",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


@router.message(OperatorForm.tour_type)
async def process_type(message: Message, state: FSMContext):
    await state.update_data(tour_type=message.text)

    kb = ReplyKeyboardBuilder()
    for r in ["Бишкек", "Каракол", "Иссык-Куль", "Сон-Куль", "Нарын", "Ала-Арча", "Джалал-Абад"]:
        kb.button(text=r)
    kb.adjust(3)

    await state.set_state(OperatorForm.region)
    await message.answer("Шаг 3/9: Регион:", reply_markup=kb.as_markup(resize_keyboard=True))


@router.message(OperatorForm.region)
async def process_region(message: Message, state: FSMContext):
    await state.update_data(region=message.text)
    await state.set_state(OperatorForm.description)
    await message.answer(
        "Шаг 4/9: Опишите ваши услуги (2-3 предложения):",
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(OperatorForm.description)
async def process_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await state.set_state(OperatorForm.price_per_day)
    await message.answer("Шаг 5/9: Цена за день на человека (в USD):\nПример: 45")


@router.message(OperatorForm.price_per_day)
async def process_price(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите только число, например: 45")
        return
    await state.update_data(price_per_day=int(message.text))
    await state.set_state(OperatorForm.max_people)
    await message.answer("Шаг 6/9: Максимум человек в группе:")


@router.message(OperatorForm.max_people)
async def process_max_people(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите только число, например: 12")
        return
    await state.update_data(max_people=int(message.text))
    await state.set_state(OperatorForm.duration)
    await message.answer("Шаг 7/9: Продолжительность туров (пример: 1-5 или 3-10):")


@router.message(OperatorForm.duration)
async def process_duration(message: Message, state: FSMContext):
    await state.update_data(duration=message.text)
    await state.set_state(OperatorForm.contact)
    await message.answer("Шаг 8/9: Ваш Telegram username (пример: @mycompany):")


@router.message(OperatorForm.contact)
async def process_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(OperatorForm.phone)
    await message.answer("Шаг 9/9: Номер телефона (пример: +996 700 123 456):")


@router.message(OperatorForm.phone)
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    data = await state.get_data()

    # Сохраняем оператора
    operator = {
        **data,
        "telegram_id": message.from_user.id,
        "id": len(registered_operators) + 100
    }
    registered_operators.append(operator)
    save_operators(registered_operators)  # <-- сохраняем в файл

    await state.clear()

    summary = (
        f"✅ *Регистрация завершена!*\n\n"
        f"🏢 *{data['name']}*\n"
        f"🎯 {data['tour_type']} | 📍 {data['region']}\n"
        f"💰 ${data['price_per_day']}/день | 👥 до {data['max_people']} чел\n"
        f"📅 {data['duration']} дней\n"
        f"📞 {data['phone']} | {data['contact']}\n\n"
        f"Ваши услуги уже видны туристам в NomadJol!\n"
        f"При каждом успешном бронировании вы получите уведомление 🔔"
    )

    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Мои бронирования", callback_data="my_bookings")

    await message.answer(summary, parse_mode="Markdown", reply_markup=kb.as_markup())


@router.callback_query(F.data == "my_bookings")
async def my_bookings(callback: CallbackQuery):
    await callback.message.answer(
        "📊 *Ваши бронирования*\n\n"
        "1. @tourist\_1 | Конный тур | 15 июня | ⏳ Ожидает депозит\n"
        "2. @tourist\_2 | Треккинг  | 20 июня | ✅ Подтверждено\n\n"
        "_Данные обновляются в реальном времени_",
        parse_mode="Markdown"
    )
    await callback.answer()
from dataclasses import dataclass
from typing import List

@dataclass
class Operator:
    id: int
    name: str
    type: str          # конный, трекинг, кемпинг, альпинизм
    region: str
    description: str
    price_per_day: int # в USD
    max_people: int
    duration_days: str # "1-3" или "3-7"
    contact: str       # telegram username
    phone: str
    languages: List[str]

OPERATORS = [
    Operator(
        id=1,
        name="Ala-Too Horse Trekking",
        type="конный тур",
        region="Каракол",
        description="Конные маршруты по Каракольскому ущелью и перевалам Тянь-Шаня. Опыт 10 лет, своя конюшня 25 лошадей.",
        price_per_day=45,
        max_people=15,
        duration_days="1-10",
        contact="@alatoo_horse",
        phone="+996 700 123 456",
        languages=["RU", "EN"]
    ),
    Operator(
        id=2,
        name="Tian Shan Adventures",
        type="треккинг",
        region="Каракол",
        description="Треккинг к пику Хан-Тенгри и Победы. Профессиональные гиды, снаряжение включено.",
        price_per_day=60,
        max_people=10,
        duration_days="3-21",
        contact="@tianshan_adv",
        phone="+996 555 234 567",
        languages=["RU", "EN", "DE"]
    ),
    Operator(
        id=3,
        name="Son-Kul Nomad Camp",
        type="кемпинг",
        region="Сон-Куль",
        description="Юрточный лагерь на берегу озера Сон-Куль. Кочевой быт, конные прогулки, национальная кухня.",
        price_per_day=35,
        max_people=20,
        duration_days="1-5",
        contact="@sonkul_nomad",
        phone="+996 700 345 678",
        languages=["RU", "EN"]
    ),
    Operator(
        id=4,
        name="Ala-Archa Alpine Club",
        type="альпинизм",
        region="Ала-Арча",
        description="Альпинистские маршруты в нацпарке Ала-Арча. От простых треков до сложных восхождений.",
        price_per_day=50,
        max_people=8,
        duration_days="1-7",
        contact="@alaarcha_club",
        phone="+996 312 456 789",
        languages=["RU", "EN", "FR"]
    ),
    Operator(
        id=5,
        name="Issyk-Kul Trekking",
        type="треккинг",
        region="Иссык-Куль",
        description="Треккинг по горам Терскей Ала-Тоо вдоль Иссык-Куля. Комбо: горы + пляж.",
        price_per_day=40,
        max_people=12,
        duration_days="2-8",
        contact="@issykkul_trek",
        phone="+996 770 567 890",
        languages=["RU", "EN"]
    ),
    Operator(
        id=6,
        name="Naryn Horsemen",
        type="конный тур",
        region="Нарын",
        description="Конные туры по Нарынской области. Маршруты к озеру Чатыр-Куль и перевалу Ак-Бейт.",
        price_per_day=40,
        max_people=10,
        duration_days="2-12",
        contact="@naryn_horse",
        phone="+996 550 678 901",
        languages=["RU", "EN"]
    ),
    Operator(
        id=7,
        name="Jalalabad Eco Tours",
        type="треккинг",
        region="Джалал-Абад",
        description="Эко-треккинг по Западному Тянь-Шаню. Ореховые леса, водопады, бюджетный вариант.",
        price_per_day=25,
        max_people=15,
        duration_days="1-5",
        contact="@jalalabad_eco",
        phone="+996 700 789 012",
        languages=["RU", "EN"]
    ),
]

def get_catalog_text() -> str:
    """Формирует текст каталога для AI промпта"""
    lines = []
    for op in OPERATORS:
        lines.append(
            f"ID:{op.id} | {op.name} | {op.type} | {op.region} | "
            f"${op.price_per_day}/день | до {op.max_people} чел | "
            f"{op.duration_days} дней | контакт: {op.contact} | тел: {op.phone}"
        )
    return "\n".join(lines)

def get_operators_by_type(tour_type: str) -> List[Operator]:
    return [op for op in OPERATORS if tour_type.lower() in op.type.lower()]
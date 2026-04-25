import json
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

STATS_FILE = "stats.json"
OPERATORS_FILE = "operators.json"

COUNTRY_INFO = {
    "RU": {"name": "Россия", "flag": "🇷🇺"},
    "DE": {"name": "Германия", "flag": "🇩🇪"},
    "US": {"name": "США", "flag": "🇺🇸"},
    "KZ": {"name": "Казахстан", "flag": "🇰🇿"},
    "FR": {"name": "Франция", "flag": "🇫🇷"},
    "GB": {"name": "Великобритания", "flag": "🇬🇧"},
    "CN": {"name": "Китай", "flag": "🇨🇳"},
    "OTHER": {"name": "Другая", "flag": "🌍"},
}


def load_json(path: str, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


@app.get("/api/stats")
async def get_stats():
    stats = load_json(STATS_FILE, {"total": 0, "unique_users": [], "countries": {}})
    operators = load_json(OPERATORS_FILE, [])

    total = stats.get("total", 0)
    unique = len(stats.get("unique_users", []))
    countries_raw = stats.get("countries", {})

    # Форматируем страны для дашборда
    countries = []
    for code, count in sorted(countries_raw.items(), key=lambda x: -x[1]):
        info = COUNTRY_INFO.get(code, {"name": code, "flag": "🌍"})
        countries.append({
            "code": code,
            "name": info["name"],
            "flag": info["flag"],
            "count": count
        })

    # Регионы из операторов
    regions = {}
    for op in operators:
        r = op.get("region", "Другой")
        regions[r] = regions.get(r, 0) + 1

    # Регионы из хардкода если нет зарегистрированных
    if not regions:
        regions = {
            "Каракол": 2, "Иссык-Куль": 1, "Сон-Куль": 1,
            "Нарын": 1, "Ала-Арча": 1, "Джалал-Абад": 1
        }

    return JSONResponse({
        "total_requests": total,
        "unique_users": unique,
        "total_operators": 7 + len(operators),
        "potential_revenue": round(total * 45 * 0.1),
        "regions": regions,
        "countries": countries
    })


@app.get("/api/operators")
async def get_operators():
    operators = load_json(OPERATORS_FILE, [])
    return JSONResponse(operators)


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    with open(html_path, encoding="utf-8") as f:
        return f.read()
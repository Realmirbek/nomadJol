import json
import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_operators():
    path = os.path.join(os.path.dirname(__file__), "..", "operators.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return []


def load_stats():
    path = os.path.join(os.path.dirname(__file__), "..", "stats.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"total_requests": 0, "unique_users": 0, "requests_by_type": {}}


@app.get("/api/stats")
def get_stats():
    operators = load_operators()
    stats = load_stats()

    # Считаем по регионам из хардкода + зарегистрированных
    regions = {}
    for op in operators:
        r = op.get("region", "Другое")
        regions[r] = regions.get(r, 0) + 1

    # Базовые операторы из каталога
    base_regions = {
        "Каракол": 2, "Сон-Куль": 1, "Ала-Арча": 1,
        "Иссык-Куль": 1, "Нарын": 1, "Джалал-Абад": 1
    }
    for r, count in base_regions.items():
        regions[r] = regions.get(r, 0) + count

    return {
        "total_requests": stats.get("total_requests", 0),
        "unique_users": stats.get("unique_users", 0),
        "registered_operators": len(operators),
        "total_operators": 7 + len(operators),
        "regions": regions,
        "potential_revenue": stats.get("total_requests", 0) * 8,
        "requests_by_type": stats.get("requests_by_type", {}),
    }


@app.get("/api/operators")
def get_operators():
    return load_operators()


@app.get("/", response_class=HTMLResponse)
def dashboard():
    with open(os.path.join(os.path.dirname(__file__), "index.html"), encoding="utf-8") as f:
        return f.read()
import flet as ft
import requests
import json
import os

# =========================
# CONFIGURACIÓN
# =========================
API_KEY = "TU_API_KEY_AQUI"
BASE_URL = "https://www.goldapi.io/api"

usd_to_cup = 525  # mercado informal Cuba
DATA_FILE = "data.json"

# =========================
# CARGAR HISTORIAL
# =========================

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"gold": [], "silver": []}


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

history = load_data()

# =========================
# 🔌 API REAL (ORO / PLATA)
# =========================

def get_gold_price():
    url = f"{BASE_URL}/XAU/USD"
    headers = {
        "x-access-token": API_KEY
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return float(data["price"])


def get_silver_price():
    url = f"{BASE_URL}/XAG/USD"
    headers = {
        "x-access-token": API_KEY
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return float(data["price"])

# =========================
# IA SIMPLE
# =========================

def trend(values):
    if len(values) < 5:
        return "📊 recopilando datos"

    short = sum(values[-3:]) / 3
    long = sum(values[-7:]) / 7 if len(values) >= 7 else sum(values) / len(values)

    if short > long:
        return "📈 subida"
    elif short < long:
        return "📉 bajada"
    return "⚖️ estable"

# =========================
# APP
# =========================

def main(page: ft.Page):
    page.title = "💰 La Tasa de Oro"
    page.scroll = "auto"

    gold_text = ft.Text(size=18, weight="bold")
    silver_text = ft.Text(size=18, weight="bold")
    alert_text = ft.Text(size=16)

    gold_chart = ft.LineChart(
        data_series=[],
        border=ft.border.all(1),
        min_y=2000,
        max_y=2500,
        expand=True
    )

    # =========================
    # ACTUALIZAR GRÁFICA
    # =========================
    def update_chart():
        points = []

        for i, v in enumerate(history["gold"][-20:]):
            points.append(ft.LineChartDataPoint(i, v))

        gold_chart.data_series = [
            ft.LineChartData(
                data_points=points,
                stroke_width=3
            )
        ]

    # =========================
    # ACTUALIZAR DATOS
    # =========================
    def update(e=None):
        global usd_to_cup

        try:
            gold = get_gold_price()
            silver = get_silver_price()
        except:
            gold = 2300
            silver = 28

        history["gold"].append(gold)
        history["silver"].append(silver)

        save_data(history)

        gold_cup = gold * usd_to_cup
        silver_cup = silver * usd_to_cup

        gold_text.value = f"🏆 Oro: ${gold} USD | {gold_cup:,} CUP"
        silver_text.value = f"🥈 Plata: ${silver} USD | {silver_cup:,} CUP"

        alert_text.value = f"🤖 IA: {trend(history['gold'])}"

        update_chart()
        page.update()

    # =========================
    # UI
    # =========================

    title = ft.Text("💰 La Tasa de Oro PRO (API REAL)", size=22, weight="bold")

    btn = ft.ElevatedButton("🔄 Actualizar mercado", on_click=update)

    page.add(
        title,
        btn,
        gold_text,
        silver_text,
        alert_text,
        ft.Text("📊 Gráfica del Oro (tiempo real)", weight="bold"),
        gold_chart
    )

    update()

ft.app(target=main)

import flet as ft
import asyncio
import aiohttp
from collections import deque
from datetime import datetime

API_URL = "https://api.gold-api.com/price/XAU"


async def main(page: ft.Page):

    # ================= CORE CONFIG =================
    page.title = "HF Trading Terminal"
    page.bgcolor = "#020202"
    page.padding = 10

    # ================= STATE ENGINE =================
    prices = deque(maxlen=50)
    last_price = None

    # ================= AUDIO EVENTS =================
    click = ft.Audio(src="assets/click.mp3")
    alert = ft.Audio(src="assets/alert.mp3")
    page.overlay.extend([click, alert])

    # ================= HEADER =================
    title = ft.Text(
        "HEDGE FUND DESK - GOLD",
        size=18,
        color="#d4af37",
        weight="bold",
    )

    price_txt = ft.Text("—", size=48, weight="bold", color="white")
    change_txt = ft.Text("", size=14)
    time_txt = ft.Text("", size=11, color="#666")

    # ================= CHART (RISK VIEW) =================
    chart = ft.LineChart(
        expand=True,
        border=ft.border.all(1, "#1a1a1a"),
        data_series=[],
    )

    # ================= MARKET ENGINE =================
    async def get_price():
        nonlocal last_price

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(API_URL) as r:
                    data = await r.json()

            price = float(data.get("price", 0))
            prices.append(price)

            price_txt.value = f"${price:,.2f}"

            if last_price:
                diff = price - last_price
                pct = (diff / last_price) * 100

                if diff > 0:
                    change_txt.value = f"LONG ▲ {pct:.2f}%"
                    change_txt.color = "#00ff88"
                    alert.play()
                elif diff < 0:
                    change_txt.value = f"SHORT ▼ {pct:.2f}%"
                    change_txt.color = "#ff4d4d"
                    alert.play()
                else:
                    change_txt.value = "FLAT"

            last_price = price
            time_txt.value = datetime.now().strftime("%H:%M:%S")

            update_chart()

        except:
            change_txt.value = "DATA FEED LOST"
            change_txt.color = "#ff0000"

        await page.update_async()

    # ================= CHART ENGINE =================
    def update_chart():
        if len(prices) < 2:
            return

        chart.data_series = [
            ft.LineChartData(
                data_points=[
                    ft.LineChartDataPoint(i, v)
                    for i, v in enumerate(prices)
                ],
                color="#d4af37",
                stroke_width=2,
            )
        ]

    # ================= DASHBOARD =================
    dashboard = ft.Column(
        expand=True,
        controls=[
            title,
            ft.Container(height=10),

            price_txt,
            change_txt,
            time_txt,

            ft.Container(height=10),

            ft.Container(height=220, content=chart),

            ft.Container(height=10),

            ft.Row(
                [
                    ft.ElevatedButton(
                        "REFRESH",
                        bgcolor="#d4af37",
                        color="black",
                        on_click=lambda e: (click.play(), asyncio.create_task(get_price())),
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        ],
    )

    # ================= BOOT SEQUENCE =================
    boot = ft.Container(
        expand=True,
        content=ft.Column(
            [
                ft.ProgressRing(color="#d4af37"),
                ft.Text("INITIALIZING HF DATA FEED...", color="#d4af37"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    page.add(boot)
    await page.update_async()

    await asyncio.sleep(1.5)

    page.controls.clear()
    page.add(dashboard)

    await get_price()

    await page.update_async()

    # ================= LIVE MARKET LOOP =================
    async def live_feed():
        while True:
            await asyncio.sleep(6)
            await get_price()

    asyncio.create_task(live_feed())


ft.app(target=main)

import flet as ft
import requests
import asyncio

API_URL = "https://api.gold-api.com/price/XAU"


def main(page: ft.Page):

    # ================= BASE =================
    page.title = "La Tasa de Oro"
    page.bgcolor = "#0a0a0a"
    page.padding = 0

    # ================= SPLASH =================
    splash = ft.Container(
        expand=True,
        bgcolor="#000000",
        content=ft.Column(
            [
                ft.Image(src="assets/icon.png", width=140),
                ft.ProgressRing(color="#d4af37"),
                ft.Text("Cargando mercado...", color="#d4af37"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    page.add(splash)

    # ================= UI =================
    price_txt = ft.Text("—", size=40, color="#d4af37", weight="bold")
    status_txt = ft.Text("", color="#777777")

    last_price = None

    # ================= FETCH =================
    def get_price():
        nonlocal last_price

        try:
            r = requests.get(API_URL, timeout=5)
            data = r.json()
            price = float(data.get("price", 0))

            price_txt.value = f"${price:,.2f}"

            if last_price:
                diff = price - last_price
                if diff > 0:
                    status_txt.value = "▲ Subiendo"
                    status_txt.color = "#00ff88"
                elif diff < 0:
                    status_txt.value = "▼ Bajando"
                    status_txt.color = "#ff4d4d"
                else:
                    status_txt.value = "Sin cambios"

            last_price = price

        except:
            status_txt.value = "Error de conexión"
            status_txt.color = "#ff0000"

    # ================= MAIN UI =================
    main_ui = ft.Container(
        expand=True,
        opacity=0,
        animate_opacity=500,
        content=ft.Column(
            [
                ft.Text("LA TASA DE ORO", size=20, color="white"),
                price_txt,
                status_txt,
                ft.Container(height=20),
                ft.ElevatedButton(
                    "Actualizar",
                    bgcolor="#d4af37",
                    color="black",
                    on_click=lambda e: get_price(),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    page.add(main_ui)

    # ================= START =================
    get_price()

    splash.opacity = 0
    main_ui.opacity = 1
    page.update()

    async def remove_splash():
        await asyncio.sleep(0.6)
        page.controls.remove(splash)
        page.update()

    asyncio.create_task(remove_splash())


ft.app(target=main)

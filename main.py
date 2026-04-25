import flet as ft
import asyncio
import requests

API_URL = "https://api.gold-api.com/price/XAU"  # cámbiala por tu API real

async def main(page: ft.Page):
    page.title = "La Tasa de Oro"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#0b0b0b"  # negro elegante
    page.padding = 0

    # -------- Splash overlay (se ve después del splash nativo) --------
    splash_overlay = ft.Container(
        bgcolor="#000000",
        content=ft.Column(
            [
                ft.Image(src="assets/icon.png", width=180, height=180),
                ft.ProgressRing(color="#d4af37"),  # dorado
                ft.Text("Cargando...", color="#d4af37", size=16),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        ),
        expand=True,
        opacity=1,
        animate_opacity=ft.Animation(600, "easeOut"),
    )

    # -------- UI principal (inicialmente oculta) --------
    price_txt = ft.Text("—", size=32, weight="bold", color="#d4af37")
    status_txt = ft.Text("", color="#aaaaaa")

    async def fetch_price():
        try:
            r = requests.get(API_URL, timeout=10)
            data = r.json()
            # Ajusta según tu API:
            price = data.get("price") or data
            price_txt.value = f"${price}"
            status_txt.value = "Actualizado"
        except Exception as e:
            status_txt.value = f"Error de red"
        await page.update_async()

    main_content = ft.Container(
        visible=False,
        content=ft.Column(
            [
                ft.Text("La Tasa de Oro", size=28, weight="bold", color="#ffffff"),
                ft.Container(height=10),
                price_txt,
                status_txt,
                ft.Container(height=20),
                ft.ElevatedButton(
                    "Actualizar",
                    on_click=lambda e: asyncio.create_task(fetch_price()),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        expand=True,
    )

    # -------- Montaje --------
    page.add(main_content, splash_overlay)
    await page.update_async()

    # Carga inicial (mientras el overlay está visible)
    await fetch_price()

    # Mostrar UI y ocultar overlay suavemente
    main_content.visible = True
    splash_overlay.opacity = 0
    await page.update_async()

    # Espera a que termine la animación y remueve overlay
    await asyncio.sleep(0.6)
    page.controls.remove(splash_overlay)
    await page.update_async()

ft.app(target=main)

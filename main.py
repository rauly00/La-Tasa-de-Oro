import flet as ft
import requests
import yfinance as yf
import pandas as pd

API_URL = "https://api.gold-api.com/price/XAU"
SYMBOL = "GC=F" # Símbolo del futuro del oro en Yahoo Finance

def main(page: ft.Page):
    # ================= BASE =================
    page.title = "La Tasa de Oro"
    page.bgcolor = "#0a0a0a"
    page.padding = 30
    page.scroll = ft.ScrollMode.AUTO # Por si la pantalla es muy pequeña

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
    status_txt = ft.Text("", color="#777777", size=16)
    last_price = None

    # --- CANVAS PARA LAS VELAS ---
    chart_canvas = ft.canvas.Canvas(
        expand=False,
        width=350,
        height=250,
    )

    # ================= FETCH PRECIO ACTUAL =================
    def get_price():
        nonlocal last_price
        try:
            r = requests.get(API_URL, timeout=10)
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
        except Exception as err:
            print(f"Error precio actual: {err}")
            status_txt.value = "Error de conexión API"
            status_txt.color = "#ff0000"

    # ================= DIBUJAR VELAS (CANVAS) =================
    def get_and_draw_candles():
        try:
            # Descargar últimos 30 días del oro
            gold = yf.Ticker(SYMBOL)
            hist = gold.history(period="30d")
            
            # Limpiar el canvas
            chart_canvas.shapes.clear()
            
            if hist.empty:
                chart_canvas.update()
                return

            # Extraer datos OHLC
            highs = hist['High'].tolist()
            lows = hist['Low'].tolist()
            opens = hist['Open'].tolist()
            closes = hist['Close'].tolist()

            min_val = min(lows) * 0.999
            max_val = max(highs) * 1.001
            rango = max_val - min_val

            c_width = 350
            c_height = 250
            candle_w = 8
            spacing = c_width / len(closes)

            # Función matemática para mapear precios a pixeles Y
            def get_y(precio):
                return c_height - ((precio - min_val) / rango) * c_height

            # Dibujar cada vela
            for i in range(len(closes)):
                x = (i * spacing) + (spacing / 2) # Centrar la vela
                o, h, l, c = opens[i], highs[i], lows[i], closes[i]

                color = "#00ff88" if c >= o else "#ff4d4d"

                # 1. Dibujar la mecha (línea de High a Low)
                chart_canvas.shapes.append(
                    ft.canvas.Line(
                        x1=x, y1=get_y(h), x2=x, y2=get_y(l),
                        paint=ft.paint.Paint(stroke_width=1.5, color=color)
                    )
                )

                # 2. Dibujar el cuerpo (Rectángulo de Open a Close)
                body_top = min(get_y(o), get_y(c))
                body_height = max(abs(get_y(o) - get_y(c)), 1) # Mínimo 1 pixel si es Doji
                
                chart_canvas.shapes.append(
                    ft.canvas.Rect(
                        x=x - (candle_w / 2),
                        y=body_top,
                        width=candle_w,
                        height=body_height,
                        paint=ft.paint.Paint(color=color) # Relleno sólido
                    )
                )
            
            chart_canvas.update()

        except Exception as err:
            print(f"Error dibujando velas: {err}")

    # ================= MAIN UI =================
    main_ui = ft.Container(
        expand=True,
        opacity=0,
        animate_opacity=500,
        content=ft.Column(
            [
                ft.Text("LA TASA DE ORO", size=20, color="white", weight="bold"),
                price_txt,
                status_txt,
                ft.Container(height=20),
                # Título del gráfico
                ft.Text("Gráfico 30 Días (OHLC)", size=14, color="#aaaaaa"),
                ft.Container(
                    bgcolor="#111111",
                    border_radius=10,
                    padding=10,
                    content=chart_canvas
                ),
                ft.Container(height=20),
                ft.ElevatedButton(
                    "Actualizar Datos",
                    bgcolor="#d4af37",
                    color="black",
                    on_click=lambda e: (
                        page.run_thread(get_price),
                        page.run_thread(get_and_draw_candles)
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    page.add(main_ui)

    # ================= START =================
    # Lanzamos ambas funciones en hilos secundarios para no congelar el Splash
    page.run_thread(get_price)
    page.run_thread(get_and_draw_candles)

    splash.opacity = 0
    main_ui.opacity = 1
    page.update()

    async def remove_splash():
        await asyncio.sleep(0.6)
        page.controls.remove(splash)
        page.update()

    page.run_task(remove_splash)


ft.app(target=main)

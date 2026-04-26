import flet as ft
import requests

# ========================================================
# CONFIGURACIÓN GENERAL
# ========================================================
TASA_USD_A_CUP = 300  # CAMBIA ESTE VALOR SEGÚN LA TASA ACTUAL
ONZA_A_GRAMOS = 31.1035

def main(page: ft.Page):
    # ================= BASE =================
    page.title = "La Tasa de Oro y Plata (Cuba)"
    page.bgcolor = "#0a0a0a"
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO

    # ================= FUNCIONES =================
    def calcular_precios(precio_onza_usd):
        precio_gramo_usd = precio_onza_usd / ONZA_A_GRAMOS
        precio_onza_cup = precio_onza_usd * TASA_USD_A_CUP
        precio_gramo_cup = precio_gramo_usd * TASA_USD_A_CUP
        return precio_gramo_usd, precio_onza_cup, precio_gramo_cup

    # NUEVA FUNCIÓN: Descarga datos de Yahoo SIN yfinance NI pandas
    def get_yahoo_data(symbol):
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=30d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10).json()
        
        result = r['chart']['result'][0]
        closes = result['indicators']['quote'][0]['close']
        opens = result['indicators']['quote'][0]['open']
        highs = result['indicators']['quote'][0]['high']
        lows = result['indicators']['quote'][0]['low']
        
        current_price = closes[-1] if closes[-1] else closes[-2]
        
        # Filtrar fines de semana (donde no hay datos y valen None)
        historical = [(o, h, l, c) for o, h, l, c in zip(opens, highs, lows, closes) if o is not None]
        
        return current_price, historical

    def dibujar_velas(canvas: ft.canvas.Canvas, data, color_subida: str, color_bajada: str):
        canvas.shapes.clear()
        if not data:
            canvas.update()
            return

        # Extraer máximos y mínimos para calcular el tamaño del gráfico
        all_highs = [d[1] for d in data]
        all_lows = [d[2] for d in data]
        min_val = min(all_lows) * 0.999
        max_val = max(all_highs) * 1.001
        rango = max_val - min_val

        c_width = 320
        c_height = 180
        candle_w = 6
        spacing = c_width / len(data)

        def get_y(precio):
            return c_height - ((precio - min_val) / rango) * c_height

        for i, (o, h, l, c) in enumerate(data):
            x = (i * spacing) + (spacing / 2)
            color = color_subida if c >= o else color_bajada

            # Mecha
            canvas.shapes.append(
                ft.canvas.Line(x1=x, y1=get_y(h), x2=x, y2=get_y(l), paint=ft.paint.Paint(stroke_width=1.5, color=color))
            )
            # Cuerpo
            body_top = min(get_y(o), get_y(c))
            body_height = max(abs(get_y(o) - get_y(c)), 1)
            canvas.shapes.append(
                ft.canvas.Rect(x=x - (candle_w / 2), y=body_top, width=candle_w, height=body_height, paint=ft.paint.Paint(color=color))
            )
        canvas.update()

    # ================= UI ELEMENTS =================
    loading_indicator = ft.ProgressRing(color="#d4af37", width=20, height=20)
    
    oro_onza_usd = ft.Text("Cargando...", size=18, color="#d4af37", weight="bold")
    oro_gramo_usd = ft.Text("", size=16, color="#cccccc")
    oro_onza_cup = ft.Text("", size=18, color="#d4af37", weight="bold")
    oro_gramo_cup = ft.Text("", size=16, color="#cccccc")

    plata_onza_usd = ft.Text("Cargando...", size=18, color="#c0c0c0", weight="bold")
    plata_gramo_usd = ft.Text("", size=16, color="#aaaaaa")
    plata_onza_cup = ft.Text("", size=18, color="#c0c0c0", weight="bold")
    plata_gramo_cup = ft.Text("", size=16, color="#aaaaaa")

    status_txt = ft.Text("Descargando datos del mercado...", color="#777777", size=14, text_align=ft.TextAlign.CENTER)

    chart_gold = ft.canvas.Canvas(expand=False, width=320, height=180)
    chart_silver = ft.canvas.Canvas(expand=False, width=320, height=180)

    # ================= FETCH =================
    def get_all_data():
        try:
            # Obtener datos puros con requests
            precio_oro, hist_oro = get_yahoo_data("GC=F")
            precio_plata, hist_plata = get_yahoo_data("SI=F")

            # Actualizar Oro
            gu, oc, gc = calcular_precios(precio_oro)
            oro_onza_usd.value = f"${precio_oro:,.2f} USD"
            oro_gramo_usd.value = f"${gu:,.2f} USD"
            oro_onza_cup.value = f"{oc:,.2f} CUP"
            oro_gramo_cup.value = f"{gc:,.2f} CUP"

            # Actualizar Plata
            gus, ocs, gcs = calcular_precios(precio_plata)
            plata_onza_usd.value = f"${precio_plata:,.2f} USD"
            plata_gramo_usd.value = f"${gus:,.2f} USD"
            plata_onza_cup.value = f"{ocs:,.2f} CUP"
            plata_gramo_cup.value = f"{gcs:,.2f} CUP"

            status_txt.value = f"Tasa aplicada: 1 USD = {TASA_USD_A_CUP} CUP"
            status_txt.color = "#00ff88"
            loading_indicator.visible = False

            # Dibujar velas con los datos crudos
            dibujar_velas(chart_gold, hist_oro, "#00ff88", "#ff4d4d")
            dibujar_velas(chart_silver, hist_plata, "#00ff88", "#ff4d4d")

        except Exception as err:
            print(f"Error general: {err}")
            status_txt.value = "Error de conexión. Toca para reintentar."
            status_txt.color = "#ff0000"
            loading_indicator.visible = False
        finally:
            page.update()

    # ================= DISEÑO TARJETAS =================
    def crear_tarjeta(titulo, color_titulo, onza_usd, gramo_usd, onza_cup, gramo_cup, chart_canvas):
        return ft.Card(
            elevation=5,
            bgcolor="#111111",
            margin=ft.margin.only(bottom=20),
            content=ft.Container(
                padding=15,
                content=ft.Column(
                    [
                        ft.Text(titulo, size=20, color=color_titulo, weight="bold"),
                        ft.Divider(color="#333333", height=1),
                        ft.Text("DÓLARES (USD)", size=11, color="#666666"),
                        ft.Row([ft.Text("Onza: ", color="#888888", size=14), onza_usd]),
                        ft.Row([ft.Text("Gramo: ", color="#888888", size=14), gramo_usd]),
                        ft.Container(height=5),
                        ft.Text("PESOS CUBANOS (CUP)", size=11, color="#666666"),
                        ft.Row([ft.Text("Onza: ", color="#888888", size=14), onza_cup]),
                        ft.Row([ft.Text("Gramo: ", color="#888888", size=14), gramo_cup]),
                        ft.Container(height=10),
                        ft.Text("Gráfico 30 Días", size=11, color="#555555"),
                        ft.Container(bgcolor="#0d0d0d", border_radius=8, padding=5, content=chart_canvas)
                    ],
                    spacing=3
                )
            )
        )

    # ================= MAIN UI =================
    main_ui = ft.Column(
        [
            ft.Image(src="assets/icon.png", width=100), 
            ft.Text("LA TASA DE ORO Y PLATA", size=20, color="white", weight="bold", text_align=ft.TextAlign.CENTER),
            ft.Container(height=10),
            loading_indicator, 
            ft.Container(height=20),
            crear_tarjeta("🥇 ORO", "#d4af37", oro_onza_usd, oro_gramo_usd, oro_onza_cup, oro_gramo_cup, chart_gold),
            crear_tarjeta("🥈 PLATA", "#c0c0c0", plata_onza_usd, plata_gramo_usd, plata_onza_cup, plata_gramo_cup, chart_silver),
            status_txt,
            ft.ElevatedButton(
                "ACTUALIZAR PRECIOS",
                bgcolor="#d4af37",
                color="black",
                width=300,
                on_click=lambda e: page.run_thread(get_all_data),
            ),
            ft.Container(height=20)
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    page.add(main_ui)
    page.run_thread(get_all_data)

ft.app(target=main)

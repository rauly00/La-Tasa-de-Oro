import flet as ft
import yfinance as yf

# ========================================================
# CONFIGURACIÓN GENERAL
# ========================================================
TASA_USD_A_CUP = 300  # CAMBIA ESTE VALOR SEGÚN LA TASA ACTUAL
ONZA_A_GRAMOS = 31.1035
SYMBOL_GOLD = "GC=F"
SYMBOL_SILVER = "SI=F"

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

    def dibujar_velas(canvas: ft.canvas.Canvas, symbol: str, color_subida: str, color_bajada: str):
        try:
            data = yf.Ticker(symbol).history(period="30d")
            canvas.shapes.clear()
            if data.empty:
                canvas.update()
                return

            highs = data['High'].tolist()
            lows = data['Low'].tolist()
            opens = data['Open'].tolist()
            closes = data['Close'].tolist()

            min_val = min(lows) * 0.999
            max_val = max(highs) * 1.001
            rango = max_val - min_val

            c_width = 320
            c_height = 180
            candle_w = 6
            spacing = c_width / len(closes)

            def get_y(precio):
                return c_height - ((precio - min_val) / rango) * c_height

            for i in range(len(closes)):
                x = (i * spacing) + (spacing / 2)
                o, h, l, c = opens[i], highs[i], lows[i], closes[i]
                color = color_subida if c >= o else color_bajada

                canvas.shapes.append(
                    ft.canvas.Line(x1=x, y1=get_y(h), x2=x, y2=get_y(l), paint=ft.paint.Paint(stroke_width=1.5, color=color))
                )
                body_top = min(get_y(o), get_y(c))
                body_height = max(abs(get_y(o) - get_y(c)), 1)
                canvas.shapes.append(
                    ft.canvas.Rect(x=x - (candle_w / 2), y=body_top, width=candle_w, height=body_height, paint=ft.paint.Paint(color=color))
                )
            canvas.update()
        except Exception as err:
            print(f"Error dibujando {symbol}: {err}")

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

    status_txt = ft.Text("Descargando datos del mercado internacional...", color="#777777", size=14, text_align=ft.TextAlign.CENTER)

    chart_gold = ft.canvas.Canvas(expand=False, width=320, height=180)
    chart_silver = ft.canvas.Canvas(expand=False, width=320, height=180)

    # ================= FETCH =================
    def get_all_data():
        try:
            # Forzamos un timeout para que si la red es mala, no se quede clavado por minutos
            gold_data = yf.Ticker(SYMBOL_GOLD).history(period="1d")
            silver_data = yf.Ticker(SYMBOL_SILVER).history(period="1d")

            if gold_data.empty or silver_data.empty:
                status_txt.value = "Mercado cerrado o sin conexión."
                status_txt.color = "#ffaa00"
                loading_indicator.visible = False
                page.update()
                return

            # Actualizar Oro
            po = gold_data['Close'].iloc[-1]
            gu, oc, gc = calcular_precios(po)
            oro_onza_usd.value = f"${po:,.2f} USD"
            oro_gramo_usd.value = f"${gu:,.2f} USD"
            oro_onza_cup.value = f"{oc:,.2f} CUP"
            oro_gramo_cup.value = f"{gc:,.2f} CUP"

            # Actualizar Plata
            ps = silver_data['Close'].iloc[-1]
            gus, ocs, gcs = calcular_precios(ps)
            plata_onza_usd.value = f"${ps:,.2f} USD"
            plata_gramo_usd.value = f"${gus:,.2f} USD"
            plata_onza_cup.value = f"{ocs:,.2f} CUP"
            plata_gramo_cup.value = f"{gcs:,.2f} CUP"

            status_txt.value = f"Tasa aplicada: 1 USD = {TASA_USD_A_CUP} CUP"
            status_txt.color = "#00ff88"
            
            # Ocultar el circulito de carga
            loading_indicator.visible = False

            # Dibujar velas
            dibujar_velas(chart_gold, SYMBOL_GOLD, "#00ff88", "#ff4d4d")
            dibujar_velas(chart_silver, SYMBOL_SILVER, "#00ff88", "#ff4d4d")

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

    # ================= MAIN UI (SE MUESTRA INMEDIATAMENTE) =================
    main_ui = ft.Column(
        [
            ft.Image(src="assets/icon.png", width=100), # Tu icono bien visible arriba
            ft.Text("LA TASA DE ORO Y PLATA", size=20, color="white", weight="bold", text_align=ft.TextAlign.CENTER),
            ft.Container(height=10),
            loading_indicator, # Circulito de carga mientras espera
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

    # Se añade directo, sin opacidades ni delays
    page.add(main_ui)

    # Se lanza la descarga en segundo plano
    page.run_thread(get_all_data)

ft.app(target=main)

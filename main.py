import flet as ft

def main(page: ft.Page):
    page.title = "La Tasa de Oro"
    page.bgcolor = "#000000"

    splash = ft.Container(
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Image(src="assets/splash.png", width=200),
                ft.Text("La Tasa de Oro", size=22, color="gold"),
            ],
        ),
        alignment=ft.alignment.center,
    )

    page.add(splash)

ft.app(target=main)

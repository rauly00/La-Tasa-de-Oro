import flet as ft

def main(page: ft.Page):
    page.title = "Prueba"
    page.bgcolor = "#000000"
    
    # Un texto bien grande y llamativo
    texto_prueba = ft.Text(
        "SI VES ESTO, FLUTTER FUNCIONA",
        color="#FFFF00",
        size=30,
        weight="bold"
    )
    
    # Lo añadimos a la página
    page.add(texto_prueba)

ft.app(target=main)

import flet as ft
from ui.ui_builder import build_database_ui
from ui.menu import create_menu

def main(page: ft.Page):
    # Configuración básica de la página
    page.title = "LunarisDB"
    page.padding = 0
    page.spacing = 0
    page.bgcolor = "#1a1a1a"

    # Crear primero el menú para que exista db_manager
    create_menu(page)
    # Luego crear la UI que utilizará db_manager
    build_database_ui(page)

ft.app(main)
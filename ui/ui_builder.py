import flet as ft
from .sql_editor import SQLEditorManager
from .result_table import ResultsTableManager

def build_database_ui(page: ft.Page):
    # Inicializamos el gestor de resultados
    results_manager = ResultsTableManager()
    results_table = results_manager.get_results_table()
    
    # 1. Panel de estructura de base de datos 
    database_tree = ft.Container(
        content=ft.Column([ 
            ft.Container(
                content=ft.Text("Database Structure", size=16, weight=ft.FontWeight.BOLD, color="#ffffff"),
                padding=10,
            ),
            ft.ListView(
                controls=[],
                spacing=2,
                expand=True,
            )
        ], expand=True),
        width=250,
        bgcolor="#222222",
        border=ft.border.only(right=ft.BorderSide(1, "#333333"))
    )

    if hasattr(page, 'db_manager'):
        page.db_manager.set_database_tree(database_tree)

    page.results_table = results_table

    

    def on_execute_query(query: str):
        if hasattr(page, 'db_manager'):
            page.db_manager.execute_query(query, results_table)
    
    sql_editor_manager = SQLEditorManager(page, on_execute_query)
    page.sql_editor_manager = sql_editor_manager
    
    # Función para redimensionar el panel
    def resize_panel(e, panel):
        new_width = panel.width + e.delta_x
        if 150 <= new_width <= 500:
            panel.width = new_width
            panel.update()

    # Barra de redimensionamiento
    resize_area = ft.GestureDetector(
        mouse_cursor=ft.MouseCursor.RESIZE_LEFT_RIGHT,
        on_pan_update=lambda e: resize_panel(e, database_tree),
        content=ft.Container(
            width=5,
            bgcolor="#333333",
            height=None,
        ),
    )

    sql_editor_manager.container.height = 300  # Un valor predeterminado adecuado


    def resize_vertical_panel(e):
        new_height = sql_editor_manager.container.height + e.delta_y
        min_height = 100
        max_height = page.height * 0.7  # 70% of page height
        
        if min_height <= new_height <= max_height:
            sql_editor_manager.container.height = new_height
            sql_editor_manager.container.update()
            page.update() 

    resize_divider = ft.GestureDetector(
        mouse_cursor=ft.MouseCursor.RESIZE_UP_DOWN,
        on_pan_update=resize_vertical_panel,
        content=ft.Container(
            height=5,  # Altura de la barra de separación
            bgcolor="#333333",
            expand=True,
        )
    )


    # Main content layout modification
    main_content = ft.Container(
        content=ft.Column([
            # SQL Editor container with fixed height
            ft.Container(
                content=sql_editor_manager.container,
                padding=20,
            ),
            
            # Resize divider - make sure it's visible and interactive
            ft.GestureDetector(
                mouse_cursor=ft.MouseCursor.RESIZE_UP_DOWN,
                on_pan_update=resize_vertical_panel,
                content=ft.Container(
                    height=5,
                    bgcolor="#333333",
                    expand=True,
                    border=ft.border.all(1, "#444444"),  # Added border for better visibility
                )
            ),
            
            # Results container that expands to fill remaining space
            ft.Container(
                content=results_manager.get_results_tabs(),
                expand=True
            )
        ], spacing=0),  # Reduce spacing between elements
        expand=True,
        bgcolor="#1a1a1a"
    )

    # Layout principal
    layout = ft.Row([ 
        database_tree,
        resize_area,
        ft.VerticalDivider(width=1, color="#333333"),
        main_content
    ], expand=True)
    
    page.add(layout)
    page.update()
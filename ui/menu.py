import flet as ft
from ui.ui_events import handle_about_click
from db.connection import DatabaseManager
from utils.erd_generator import generate_erd, generate_erd_dialog

# Define la función `create_menu` que crea y configura un menú dentro de la página
# La función toma dos parámetros:
# - `page`: un objeto `ft.Page` que representa la página de la interfaz de usuario en la que se creará el menú.
# - `database_tree`: un valor opcional (por defecto es None) que, si se proporciona, se usará para configurar el árbol de base de datos.
def create_menu(page: ft.Page, database_tree=None):
    # Crea una instancia de `DatabaseManager` pasando la página como parámetro
    db_manager = DatabaseManager(page)
    
    # Si se proporciona un árbol de base de datos (database_tree), se configura en el `db_manager`
    if database_tree:
        db_manager.set_database_tree(database_tree)
    
    # Asocia el `db_manager` a la página como un atributo `db_manager`
    page.db_manager = db_manager

    def handle_open_sql_file(e):
        def on_file_picked(e: ft.FilePickerResultEvent):
            if e.files and len(e.files) > 0:
                file_path = e.files[0].path
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        if hasattr(page, 'sql_editor_manager'):
                            try:
                                # Usar el nuevo método para abrir en un nuevo editor
                                page.sql_editor_manager.open_file_in_new_editor(file_path, content)
                            except Exception as ex:
                                page.show_snack_bar(
                                    ft.SnackBar(
                                        content=ft.Text(f"Error al abrir el archivo: {str(ex)}"),
                                        bgcolor=ft.colors.RED_400
                                    )
                                )
                except Exception as ex:
                    page.show_snack_bar(
                        ft.SnackBar(
                            content=ft.Text(f"Error al leer el archivo: {str(ex)}"),
                            bgcolor=ft.colors.RED_400
                        )
                    )

        file_picker = ft.FilePicker(
            on_result=on_file_picked
        )
        page.overlay.append(file_picker)
        page.update()
        
        file_picker.pick_files(
            allowed_extensions=["sql", "txt"],
            dialog_title="Seleccionar archivo SQL o texto"
        )
        



    # Barra de estado moderna
    connection_status = ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(
                    name=ft.icons.CIRCLE,
                    color=ft.colors.RED,
                    size=12
                ),
                ft.Text(
                    "Desconectado",
                    size=12,
                    color=ft.colors.RED,
                    weight=ft.FontWeight.W_500
                )
            ],
            spacing=5,
            alignment=ft.MainAxisAlignment.START
        ),
        padding=ft.padding.only(left=10)
    )

    def update_connection_status(connected: bool):
        icon_color = ft.colors.GREEN if connected else ft.colors.RED
        status_text = "Conectado" if connected else "Desconectado"
        connection_status.content.controls[0].color = icon_color
        connection_status.content.controls[1].value = status_text
        connection_status.content.controls[1].color = icon_color
        page.update()

    db_manager.set_status_callback(update_connection_status)

    # Handlers
    def handle_connect_db(e):
        db_manager.connect_db()

    def handle_create_db(e):
        db_name = "new_database"
        file_name = f"{db_name}.db"
        db_manager.create_db(file_name)

    def handle_export_db_to_sql(e):
        db_manager.export_db_with_picker()

    def handle_disconnect_db(e):
        if db_manager.disconnect():
            update_connection_status(False)

    def handle_generate_erd(e):
        if db_manager.db_path:
            generate_erd_dialog(page, db_manager, generate_erd)
        else:
            page.show_snack_bar(
                ft.SnackBar(
                    content=ft.Text("Debe conectarse a una base de datos primero"),
                    bgcolor=ft.colors.RED_400
                )
            )

    # Toolbar moderno con iconos
    toolbar = ft.Container(
        content=ft.Row(
            controls=[
                ft.IconButton(
                    icon=ft.icons.FOLDER_OPEN,
                    tooltip="Abrir Base de Datos",
                    on_click=handle_connect_db,
                    icon_color="#1976d2",
                ),
                ft.IconButton(
                    icon=ft.icons.CREATE_NEW_FOLDER,
                    tooltip="Crear Base de Datos",
                    on_click=handle_create_db,
                    icon_color="#1976d2",
                ),

                ft.VerticalDivider(width=1, color="#424242"),
                ft.IconButton(
                    icon=ft.icons.SCHEMA,
                    tooltip="Generar ERD",
                    on_click=handle_generate_erd,
                    icon_color="#1976d2",
                ),
                ft.IconButton(
                    icon=ft.icons.IMPORT_EXPORT,
                    tooltip="Exportar BD a SQL",
                    on_click=handle_export_db_to_sql,
                    icon_color="#1976d2",
                ),
                ft.IconButton(
                icon=ft.icons.FILE_OPEN,
                tooltip="Abrir archivo SQL",
                on_click=handle_open_sql_file,
                icon_color="#1976d2",
            ),
            ],
            spacing=0,
        ),
        bgcolor="#1a1a1a",
        padding=5,
    )

    # Menú tradicional pero más compacto
    menu = ft.MenuBar(
        controls=[
            ft.SubmenuButton(
                content=ft.Text("Archivo", size=13),
                controls=[
                    ft.MenuItemButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.FOLDER_OPEN, size=16),
                            ft.Text("Abrir Base de Datos")
                        ]),
                        on_click=handle_connect_db,
                    ),
                    ft.MenuItemButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.CREATE_NEW_FOLDER, size=16),
                            ft.Text("Crear Base de Datos")
                        ]),
                        on_click=handle_create_db,
                    ),
                    ft.Divider(),
                    ft.MenuItemButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.LOGOUT, size=16),
                            ft.Text("Desconectar")
                        ]),
                        on_click=handle_disconnect_db,
                    ),
                ],
            ),
            ft.SubmenuButton(
                content=ft.Text("Herramientas", size=13),
                controls=[
                    ft.MenuItemButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.SCHEMA, size=16),
                            ft.Text("Generar ERD")
                        ]),
                        on_click=handle_generate_erd,
                    ),
                    ft.MenuItemButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.IMPORT_EXPORT, size=16),
                            ft.Text("Exportar BD a SQL")
                        ]),
                        on_click=handle_export_db_to_sql,
                    ),
                ],
            ),
            ft.SubmenuButton(
                content=ft.Text("Ayuda", size=13),
                controls=[
                    ft.MenuItemButton(
                        content=ft.Row([
                            ft.Icon(ft.icons.INFO, size=16),
                            ft.Text("Acerca de")
                        ]),
                        on_click=handle_about_click,
                    ),
                ],
            ),
        ]
    )

    # Layout principal
    main_layout = ft.Column(
        controls=[
            menu,
            toolbar,
            ft.Divider(height=1, color="#e0e0e0"),
            connection_status,
        ],
        spacing=0,
    )

    page.add(main_layout)
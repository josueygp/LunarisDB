# Importa el módulo Flet como ft para crear la interfaz de usuario
import flet as ft

# Define la función `create_table_item` que crea un elemento visual para representar una tabla en la interfaz de usuario
# La función toma los siguientes parámetros:
# - `page`: un objeto `ft.Page` que representa la página en la que se mostrará el elemento.
# - `name`: el nombre de la tabla, utilizado para generar la consulta SQL y mostrar el nombre en la interfaz.
# - `sql_editor_manager`: un objeto encargado de gestionar el editor SQL, que se usa para configurar el texto de la consulta SQL.
# - `results_table`: una tabla de resultados en la que se mostrarán los datos obtenidos de la consulta SQL.
def create_table_item(page: ft.Page, name: str, sql_editor_manager, results_table):
    
    # Define la función `handle_click` que se ejecuta cuando el usuario hace clic en el elemento de la tabla
    def handle_click(e):
        # Verifica si la página tiene un objeto `db_manager` para ejecutar la consulta SQL
        if hasattr(page, 'db_manager'):
            # Crea una consulta SQL para obtener los primeros 100 registros de la tabla seleccionada
            query = f"SELECT * FROM {name} LIMIT 100"
            # Establece el texto de la consulta en el editor SQL
            sql_editor_manager.set_query_text(query)
            # Ejecuta la consulta y pasa la tabla de resultados para mostrar los datos
            page.db_manager.execute_query(query, results_table)
    
    # Define la función `handle_hover` que se ejecuta cuando el usuario pasa el mouse sobre el elemento
    def handle_hover(e):
        # Cambia el color de fondo del control según si el mouse está sobre el elemento
        e.control.bgcolor = "#2d2d2d" if e.data == "true" else "#222222"
        # Actualiza el control para reflejar el cambio de color de fondo
        e.control.update()
    
    # Crea un contenedor visual para el elemento de la tabla con un ícono y el nombre de la tabla
    return ft.Container(
        content=ft.Row([  # Define el contenido de la fila dentro del contenedor
            ft.Icon(ft.icons.TABLE_CHART, size=16, color="#b3b3b3"),  # Ícono de tabla
            ft.Text(
                name,  # Nombre de la tabla
                size=14,
                color="#e0e0e0",  # Color del texto
                expand=True,  # Hace que el texto ocupe el espacio disponible
                overflow=ft.TextOverflow.ELLIPSIS,  # Muestra puntos suspensivos si el texto se desborda
            )
        ],
        spacing=10),  # Espaciado entre el ícono y el texto
        padding=ft.padding.symmetric(horizontal=10, vertical=5),  # Espaciado interior
        bgcolor="#222222",  # Color de fondo del contenedor
        on_click=handle_click,  # Asocia la función `handle_click` al evento de clic
        on_hover=handle_hover,  # Asocia la función `handle_hover` al evento de hover
        expand=True,  # Expande el contenedor para llenar el espacio disponible
        width=None,  # El ancho no se especifica, se ajusta automáticamente
    )

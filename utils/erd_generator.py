import sqlite3
from graphviz import Digraph
import flet as ft
import os

def generate_erd_dialog(page: ft.Page, db_manager, generate_erd_func):
    """
    Muestra un diálogo de Flet para seleccionar dónde guardar el diagrama ERD.
    
    Parameters:
    - page: Página de Flet
    - db_manager: Instancia del DatabaseManager
    - generate_erd_func: Función para generar el diagrama ERD
    """
    def handle_save_result(e: ft.FilePickerResultEvent):
        if e.path:
            file_path = e.path
            if not file_path.lower().endswith(('.png', '.pdf')):
                file_path += '.png'
            
            file_format = 'png' if file_path.endswith('.png') else 'pdf'
            try:
                # Crear nueva conexión en este thread
                with sqlite3.connect(db_manager.db_path) as temp_conn:
                    generate_erd_func(temp_conn, file_path, file_format)
                page.open(
                    ft.SnackBar(
                        content=ft.Text(f"ERD guardado en: {os.path.basename(file_path)}"),
                        bgcolor=ft.colors.GREEN_400
                    )
                )
            except Exception as err:
                page.open(
                    ft.SnackBar(
                        content=ft.Text(f"Error al generar ERD: {str(err)}"),
                        bgcolor=ft.colors.RED_400
                    )
                )

    save_file_picker = ft.FilePicker(
        on_result=handle_save_result
    )
    
    page.overlay.append(save_file_picker)
    page.update()
    
    save_file_picker.save_file(
        allowed_extensions=["png", "pdf"],
        dialog_title="Guardar ERD"
    )
    
def generate_erd(db_connection, save_path, file_format='png'):
    """
    Genera un diagrama ERD y lo guarda en un archivo.
    
    Parameters:
    - db_connection: Conexión a la base de datos SQLite
    - save_path: Ruta donde se guardará el diagrama
    - file_format: Formato del archivo ('png' o 'pdf')
    """
    cursor = db_connection.cursor()
    
    dot = Digraph(comment='ERD Diagram')
    dot.attr(rankdir='BT')

    # Obtener tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Procesar tablas
    for (table_name,) in tables:
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()

        table_label = f"{table_name}|"
        for column in columns:
            column_name = column[1]
            column_type = column[2]
            is_primary = column[5]
            pk_label = "PK" if is_primary else ""
            table_label += f"{column_name} : {column_type} {pk_label}\\l"

        dot.node(table_name, label=f"{{{table_label}}}", shape='record')

    # Procesar relaciones
    for (table_name,) in tables:
        cursor.execute(f"PRAGMA foreign_key_list({table_name});")
        foreign_keys = cursor.fetchall()
        
        for fk in foreign_keys:
            from_table = table_name
            from_column = fk[3]
            to_table = fk[2]
            to_column = fk[4]
            dot.edge(
                f"{from_table}:{from_column}", 
                f"{to_table}:{to_column}", 
                arrowhead='normal', 
                color='blue', 
                label='FK'
            )

    # Guardar diagrama
    dot.render(save_path, format=file_format, cleanup=True)
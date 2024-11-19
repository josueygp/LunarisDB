import sqlite3
from graphviz import Digraph
import flet as ft
import os
import tempfile
import shutil

def generate_erd_dialog(page: ft.Page, db_manager, generate_erd_func):
    """
    Muestra un diálogo de Flet para seleccionar dónde guardar el diagrama ERD.
    """
    def handle_save_result(e: ft.FilePickerResultEvent):
        if e.path:
            file_path = e.path
            if not file_path.lower().endswith(('.png', '.pdf')):
                file_path += '.png'
            
            file_format = 'png' if file_path.endswith('.png') else 'pdf'
            try:
                # Crear directorio temporal
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_path = os.path.join(temp_dir, 'temp_erd')
                    
                    # Crear nueva conexión en este thread
                    with sqlite3.connect(db_manager.db_path) as temp_conn:
                        # Generar el ERD en el directorio temporal
                        generate_erd_func(temp_conn, temp_path, file_format)
                        
                        # Mover el archivo final a la ubicación deseada
                        output_file = f"{temp_path}.{file_format}"
                        if os.path.exists(output_file):
                            shutil.move(output_file, file_path)
                        else:
                            raise FileNotFoundError(f"No se pudo generar el archivo {file_format}")

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
    """
    try:
        cursor = db_connection.cursor()
        
        dot = Digraph(comment='ERD Diagram', format=file_format)
        dot.attr(rankdir='BT')

        # Obtener tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            raise ValueError("No se encontraron tablas en la base de datos")

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
                    from_table, 
                    to_table, 
                    arrowhead='normal', 
                    color='blue', 
                    label=f'FK ({from_column} → {to_column})'
                )

        # Guardar diagrama sin cleanup automático
        dot.render(save_path, cleanup=False)
        
        # Limpiar el archivo DOT manualmente
        dot_file = f"{save_path}"
        if os.path.exists(dot_file):
            try:
                os.remove(dot_file)
            except:
                pass  # Ignorar errores al limpiar
                
    except Exception as e:
        raise Exception(f"Error al generar ERD: {str(e)}")
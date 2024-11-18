import sqlite3
import flet as ft
import os
import threading
from typing import Callable
from db.db_events import DatabaseEvents
from utils.exporter import export_database_to_sql

class DatabaseManager:
    def __init__(self, page: ft.Page):
        self.db_connection = None
        self.db_path = None
        self.page = page
        self._status_callback = None
        self.database_tree = None
        self._lock = threading.Lock()
        self._connection_thread_id = None
        
        self.file_picker = ft.FilePicker(
            on_result=self._handle_file_picked
        )
        self.save_file_picker = ft.FilePicker(
            on_result=self._handle_file_save
        )
        
        self.page.overlay.extend([self.file_picker, self.save_file_picker])
        self.page.update()

    def execute_query(self, query: str, results_table: ft.DataTable):
        """Ejecuta una o múltiples consultas SQL y actualiza la tabla de resultados"""
        try:
            conn = self._get_connection()
            if not conn:
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text("No hay conexión a la base de datos"),
                        bgcolor=ft.colors.RED_400
                    )
                )
                return False

            cursor = conn.cursor()
            
            # Verificar si hay múltiples statements
            statements = [stmt.strip() for stmt in query.split(';') if stmt.strip()]
            
            if len(statements) > 1:
                # Usar executescript para múltiples statements
                cursor.executescript(query)
                
                # Verificar si algún statement modificó la estructura
                should_update = any(
                    keyword in stmt.lower() 
                    for stmt in statements 
                    for keyword in ['create', 'drop', 'alter']
                )
                
                if should_update:
                    self.update_database_structure()
                
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text("Script SQL ejecutado exitosamente"),
                        bgcolor=ft.colors.GREEN_400
                    )
                )
                
                results_table.columns = [ft.DataColumn(ft.Text("No hay resultados"))]
                results_table.rows = []
                results_table.update()
                return True
            else:
                # Analizar si la query modifica la estructura
                query_lower = query.lower().strip()
                modifies_structure = any(
                    keyword in query_lower 
                    for keyword in ['create', 'drop', 'alter']
                )
                
                # Ejecutar la query
                cursor.execute(query)
                
                # Solo procesar resultados si la query retorna datos (SELECT, etc.)
                if cursor.description:
                    # Obtener los nombres de las columnas
                    column_names = [description[0] for description in cursor.description]
                    
                    # Crear las columnas del DataTable
                    results_table.columns = [
                        ft.DataColumn(ft.Text(name, color="#ffffff"))
                        for name in column_names
                    ]
                    
                    # Obtener y formatear los resultados
                    rows = cursor.fetchall()
                    results_table.rows = [
                        ft.DataRow(
                            cells=[
                                ft.DataCell(ft.Text(str(cell), color="#e0e0e0"))
                                for cell in row
                            ]
                        )
                        for row in rows
                    ]
                    
                    # Actualizar la tabla
                    results_table.update()
                    
                    # Mostrar mensaje con número de filas
                    self.page.open(
                        ft.SnackBar(
                            content=ft.Text(f"Query ejecutada exitosamente. {len(rows)} filas recuperadas."),
                            bgcolor=ft.colors.GREEN_400
                        )
                    )
                else:
                    # Query ejecutada pero sin resultados (INSERT, UPDATE, etc.)
                    results_table.columns = [ft.DataColumn(ft.Text("No hay resultados"))]
                    results_table.rows = []
                    results_table.update()
                    
                    self.page.open(
                        ft.SnackBar(
                            content=ft.Text("Query ejecutada exitosamente"),
                            bgcolor=ft.colors.GREEN_400
                        )
                    )
                
                # Hacer commit si no es una query de solo lectura
                if not query.lower().strip().startswith('select'):
                    conn.commit()
                    
                return True

        except Exception as e:
            # En caso de error, mantener al menos una columna
            results_table.columns = [ft.DataColumn(ft.Text("Error"))]
            results_table.rows = []
            results_table.update()
            
            self.page.open(
                ft.SnackBar(
                    content=ft.Text(f"Error al ejecutar la query: {str(e)}"),
                    bgcolor=ft.colors.RED_400
                )
            )
            return False

    def _get_connection(self):
        """Obtiene una conexión segura para el hilo actual"""
        current_thread = threading.get_ident()
        if self.db_path:
            if self._connection_thread_id != current_thread:
                # Crear una nueva conexión si estamos en un hilo diferente
                if self.db_connection:
                    try:
                        self.db_connection.close()
                    except:
                        pass
                self.db_connection = sqlite3.connect(self.db_path, check_same_thread=False)
                self._connection_thread_id = current_thread
            return self.db_connection
        return None


    def set_status_callback(self, callback: Callable[[bool], None]):
        self._status_callback = callback
        if callback:
            callback(False)

    def set_database_tree(self, tree_container):
        self.database_tree = tree_container

    def update_database_structure(self):
        """Actualiza la estructura de la base de datos en la UI"""
        if self.db_path and self.database_tree:
            try:
                conn = self._get_connection()
                if conn:
                    # Obtener la estructura
                    items = DatabaseEvents.get_database_structure(conn)
                    tree_items = DatabaseEvents.create_tree_items(items)
                    
                    # Actualizar el ListView en el database_tree
                    if isinstance(self.database_tree.content, ft.Column):
                        for control in self.database_tree.content.controls:
                            if isinstance(control, ft.ListView):
                                control.controls = tree_items
                                control.update()
                                break
                    
                    self.database_tree.update()
            except Exception as e:
                print(f"Error actualizando estructura: {e}")

    def connect_db(self):
        self.file_picker.pick_files(
            allowed_extensions=["db", "sqlite3"],
            dialog_title="Selecciona una base de datos existente"
        )

    def create_db(self, default_name="new_database"):
        """Crear una nueva base de datos"""
        self.save_file_picker.save_file(
            # Quitamos initial_file_name ya que no está soportado
            dialog_title="Guardar nueva base de datos"
        )

    def disconnect(self):
        """Desconecta la base de datos y limpia la interfaz"""
        with self._lock:
            if self.db_connection:
                try:
                    self.db_connection.close()
                except Exception as e:
                    print(f"Error al cerrar conexión: {e}")
                finally:
                    self.db_connection = None
                    self._connection_thread_id = None
                    self.db_path = None
                    
                    # Limpiar la estructura visual
                    if self.database_tree:
                        if isinstance(self.database_tree.content, ft.Column):
                            for control in self.database_tree.content.controls:
                                if isinstance(control, ft.ListView):
                                    control.controls = []
                                    control.update()
                                    break
                        self.database_tree.update()
                    
                    self.page.open(
                        ft.SnackBar(
                            content=ft.Text("Desconectado de la base de datos"),
                            bgcolor=ft.colors.BLUE_400
                        )
                    )
                    if self._status_callback:
                        self._status_callback(False)
                    return True
            return False

    def _handle_file_picked(self, e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            file_path = e.files[0].path
            try:
                with self._lock:
                    if self.db_connection:
                        try:
                            self.db_connection.close()
                        except:
                            pass
                    
                    self.db_connection = sqlite3.connect(file_path)
                    self.db_path = file_path
                    self._connection_thread_id = threading.get_ident()
                    
                    # Actualizar la estructura visual
                    self.update_database_structure()
                    
                    self.page.open(
                        ft.SnackBar(
                            content=ft.Text(f"Conectado a la base de datos: {os.path.basename(file_path)}"),
                            bgcolor=ft.colors.GREEN_400
                        )
                    )
                    if self._status_callback:
                        self._status_callback(True)
                    return True
            except Exception as e:
                self.page.open(
                    ft.SnackBar(
                        content=ft.Text(f"Error de conexión: {str(e)}"),
                        bgcolor=ft.colors.RED_400
                    )
                )
                if self._status_callback:
                    self._status_callback(False)
        return False

    def _handle_file_save(self, e: ft.FilePickerResultEvent):
        if not e.path:
            return
            
        try:
            # Determinar el tipo de operación basado en el contexto
            is_sql_export = hasattr(self, '_exporting_sql') and self._exporting_sql
            
            # Obtener el path base sin extensión
            base_path = os.path.splitext(e.path)[0]
            
            # Agregar la extensión apropiada
            final_path = f"{base_path}.sql" if is_sql_export else f"{base_path}.db"
            
            if is_sql_export:
                # Exportar a SQL
                success = export_database_to_sql(self.db_path, final_path)
                if success:
                    self.page.open(
                        ft.SnackBar(
                            content=ft.Text(f"Base de datos exportada exitosamente a {os.path.basename(final_path)}"),
                            bgcolor=ft.colors.GREEN_400
                        )
                    )
                else:
                    self.page.open(
                        ft.SnackBar(
                            content=ft.Text("Error al exportar la base de datos"),
                            bgcolor=ft.colors.RED_400
                        )
                    )
            else:
                # Crear nueva base de datos
                with self._lock:
                    if self.db_connection:
                        try:
                            self.db_connection.close()
                        except:
                            pass
                    
                    self.db_connection = sqlite3.connect(final_path)
                    self.db_path = final_path
                    self._connection_thread_id = threading.get_ident()
                    
                    self.update_database_structure()
                    
                    self.page.open(
                        ft.SnackBar(
                            content=ft.Text(f"Base de datos creada en: {os.path.basename(final_path)}"),
                            bgcolor=ft.colors.GREEN_400
                        )
                    )
                    if self._status_callback:
                        self._status_callback(True)
                    
        except Exception as ex:
            self.page.open(
                ft.SnackBar(
                    content=ft.Text(f"Error en la operación: {str(ex)}"),
                    bgcolor=ft.colors.RED_400
                )
            )
        finally:
            # Limpiar el flag de exportación
            if hasattr(self, '_exporting_sql'):
                del self._exporting_sql

        
    
    def export_db_with_picker(self):
        """Abre el FilePicker para elegir la ruta de exportación del archivo SQL"""
        if not self.db_path:
            self.page.open(
                ft.SnackBar(
                    content=ft.Text("Primero debes conectar una base de datos"),
                    bgcolor=ft.colors.RED_400
                )
            )
            return
            
        # Establecer flag para indicar que estamos exportando SQL
        self._exporting_sql = True
        
        self.save_file_picker.save_file(
            dialog_title="Guardar exportación de la base de datos SQL"
        )
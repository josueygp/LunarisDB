import flet as ft
from typing import Optional, List, Callable

class SQLEditorManager:
    def __init__(self, page: ft.Page, on_execute_query: Callable[[str], None]):
        self.page = page
        self.on_execute_query = on_execute_query
        self.editors: List[dict] = []
        self.current_editor_id = 0
        self.active_editor_id: Optional[int] = None
        
        self._init_ui_components()

    def open_file_in_new_editor(self, file_path: str, content: str):
        """Abre el contenido del archivo en un nuevo editor"""
        # Crear un nuevo editor
        editor_id = self.current_editor_id
        self.current_editor_id += 1
        
        # Crear el campo de texto para el nuevo editor
        text_field = ft.TextField(
            multiline=True,
            min_lines=10,
            max_lines=30,
            value=content,
            expand=True,
            border_color=ft.colors.TRANSPARENT,
            bgcolor="#2b2b2b",
            text_style=ft.TextStyle(
                color=ft.colors.WHITE,
                font_family="Consolas"
            )
        )

        # Crear el botón de ejecución
        execute_button = ft.ElevatedButton(
            "Execute SQL",
            icon=ft.icons.PLAY_ARROW,
            color="#ffffff",
            bgcolor="#1976d2",
            on_click=lambda e: self.execute_query(text_field.value)
        )

        # Crear el contenedor del editor con el botón
        editor_container = ft.Column([
            text_field,
            ft.Container(
                content=execute_button,
                alignment=ft.alignment.center_right,
                padding=ft.padding.only(top=10)
            )
        ], spacing=10, expand=True)

        # Obtener el nombre del archivo sin la ruta completa
        file_name = file_path.split('/')[-1].split('\\')[-1]
        
        # Crear el contenido de la pestaña
        tab_content = ft.Row([
            ft.Text(file_name, size=14),
            ft.IconButton(
                icon=ft.icons.CLOSE,
                icon_size=16,
                icon_color="#808080",
                tooltip="Close Editor",
                on_click=lambda e, eid=editor_id: self.remove_editor(eid),
                data=editor_id,
            )
        ], spacing=5)

        # Crear la nueva pestaña con el contenedor que incluye el editor y el botón
        new_tab = ft.Tab(
            tab_content=tab_content,
            content=ft.Container(
                content=editor_container,
                padding=10,
                bgcolor="#1a1a1a",
                expand=True
            )
        )

        # Agregar el editor a la lista
        self.editors.append({
            'id': editor_id,
            'tab': new_tab,
            'text_field': text_field,
            'file_path': file_path
        })

        # Agregar la pestaña y activarla
        self.tabs.tabs.append(new_tab)
        self.tabs.selected_index = len(self.tabs.tabs) - 1
        self.active_editor_id = editor_id
        
        # Actualizar la UI
        self.tabs.update()
        
    def _init_ui_components(self):
        """Inicializa los componentes principales de la UI."""
        self.tabs = ft.Tabs(
            selected_index=0,
            on_change=self._handle_tab_change,
            tabs=[],
            expand=True
        )
        
        self.add_tab_button = ft.Container(
            content=ft.IconButton(
                icon=ft.icons.ADD,
                tooltip="New SQL Editor",
                on_click=self.add_editor,
                icon_color="#1976d2",
                icon_size=20,
            ),
            padding=ft.padding.only(left=5)
        )
        
        self.tabs_row = ft.Row([
            self.tabs,
            self.add_tab_button
        ], expand=True, alignment=ft.MainAxisAlignment.START)
        
        self.container = ft.Column([
            self.tabs_row,
        ], expand=True)
        
        # Crear el primer editor por defecto
        self.add_editor()

    def _create_editor_tab_content(self, editor_id: int) -> ft.Row:
        """Crea el contenido de la pestaña con el botón de cerrar."""
        close_button = ft.IconButton(
            icon=ft.icons.CLOSE,
            icon_size=16,
            icon_color="#808080",
            tooltip="Close Editor",
            on_click=lambda e, eid=editor_id: self.remove_editor(eid),
            data=editor_id,
        )
        
        # Creamos una lista de controles y solo incluimos el botón de cerrar si no es el único editor
        controls = [ft.Text(f"SQL Editor {editor_id + 1}", size=14)]
        if len(self.editors) > 0:
            controls.append(close_button)
        
        return ft.Row(
            controls,
            spacing=5,
        )

    def _create_editor_content(self) -> ft.Column:
        """Crea el contenido de un nuevo editor SQL."""
        editor = ft.TextField(
            multiline=True,
            min_lines=15,
            max_lines=30,
            border_radius=4,
            bgcolor="#2d2d2d",
            text_size=14,
            color="#ffffff",
            hint_text="Enter your SQL query here...",
            hint_style=ft.TextStyle(color="#808080"),
            border_color="#404040",
            focused_border_color="#1976d2",
            expand=True,
            height=300,
        )
        
        execute_button = ft.ElevatedButton(
            "Execute SQL",
            icon=ft.icons.PLAY_ARROW,
            color="#ffffff",
            bgcolor="#1976d2",
            on_click=lambda e: self.execute_query(editor.value)
        )
        
        return ft.Column([
            editor,
            ft.Container(
                content=execute_button,
                alignment=ft.alignment.center_right,
                padding=ft.padding.only(top=10)
            )
        ], spacing=10, expand=True)

    def add_editor(self, e: Optional[ft.ControlEvent] = None):
        """Agrega un nuevo editor SQL."""
        editor_id = self.current_editor_id
        self.current_editor_id += 1
        
        editor_content = self._create_editor_content()
        tab_content = self._create_editor_tab_content(editor_id)
        
        tab = ft.Tab(
            tab_content=tab_content,
            content=ft.Container(
                content=editor_content,
                padding=10,
                bgcolor="#1a1a1a",
                expand=True
            ),
        )
        
        self.editors.append({
            "id": editor_id,
            "tab": tab,
            "content": editor_content,
        })
        
        self.tabs.tabs.append(tab)
        self.active_editor_id = editor_id
        self.tabs.selected_index = len(self.tabs.tabs) - 1
        self.page.update()

    def remove_editor(self, editor_id: int):
        """Elimina un editor SQL específico."""
        if len(self.editors) <= 1:
            self.page.show_snack_bar(
                ft.SnackBar(content=ft.Text("Cannot remove the last editor."))
            )
            return
        
        editor_index = next(
            (i for i, ed in enumerate(self.editors) if ed["id"] == editor_id),
            None
        )
        
        if editor_index is not None:
            self.editors.pop(editor_index)
            self.tabs.tabs.pop(editor_index)
            
            # Actualizar el editor activo
            new_index = min(editor_index, len(self.tabs.tabs) - 1)
            self.tabs.selected_index = new_index
            self.active_editor_id = self.editors[new_index]["id"]
            self.page.update()

    def _handle_tab_change(self, e: ft.ControlEvent):
        """Maneja el cambio entre pestañas de editores."""
        index = int(e.data) if e.data is not None else 0
        if 0 <= index < len(self.editors):
            self.active_editor_id = self.editors[index]["id"]

    def execute_query(self, query: str):
        """Ejecuta la consulta SQL del editor activo."""
        if not query.strip():
            self.page.open(
                ft.SnackBar(
                    content=ft.Text("Please enter a valid SQL query."),
                    bgcolor=ft.colors.RED_400
                )
            )
            return
        
        self.on_execute_query(query)

    def get_current_editor(self) -> Optional[dict]:
        """Retorna el editor actualmente seleccionado."""
        return next(
            (ed for ed in self.editors if ed["id"] == self.active_editor_id),
            None
        )

    def set_query_text(self, query: str):
        """Establece el texto de la consulta en el editor actual."""
        current_editor = self.get_current_editor()
        if current_editor:
            editor_field = current_editor["content"].controls[0]
            editor_field.value = query
            self.page.update()

    def set_current_editor_content(self, content: str):
        """Establece el contenido del editor activo."""
        if self.active_editor_id is not None:
            for editor in self.editors:
                if editor['id'] == self.active_editor_id:
                    # Asumiendo que el editor actual tiene un TextField o CodeEditor
                    if 'text_field' in editor and editor['text_field'] is not None:
                        editor['text_field'].value = content
                        editor['text_field'].update()
                        return
            raise Exception("No se pudo encontrar el campo de texto en el editor activo")
        else:
            raise Exception("No hay un editor activo")

    
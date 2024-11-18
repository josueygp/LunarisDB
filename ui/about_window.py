import flet as ft

class AboutWindow:
    """
    Clase que crea y gestiona la ventana 'Acerca de' de la aplicación LunarisDB usando Flet.
    Muestra información sobre la aplicación, el desarrollador y enlaces relevantes.
    """
    def __init__(self, page):
        """
        Inicializa y muestra el cuadro de diálogo 'Acerca de'.
        Args:
            page: Página principal de la aplicación en Flet
        """
        self.page = page
        self.dialog = None
        self.show_dialog()

    def close_dialog(self, e=None):
        """
        Cierra el diálogo de manera controlada
        """
        try:
            if self.dialog:
                self.dialog.open = False
                self.page.update()
                # Eliminar el diálogo del overlay después de cerrarlo
                if self.dialog in self.page.overlay:
                    self.page.overlay.remove(self.dialog)
                self.dialog = None
        except Exception as e:
            print(f"Error al cerrar el diálogo: {e}")

    def show_dialog(self):
        """
        Muestra un cuadro de diálogo modal 'Acerca de'.
        """
        try:
            # Cerrar cualquier diálogo existente antes de crear uno nuevo
            self.close_dialog()
            
            content = ft.Container(
                content=ft.Column(
                    [
                        ft.Text("LunarisDB", 
                               style=ft.TextStyle(
                                   size=24,
                                   weight=ft.FontWeight.BOLD
                               )),
                        ft.Text("Versión 1.0.0", 
                               style=ft.TextStyle(
                                   size=14,
                                   color=ft.colors.GREY_500
                               )),
                        ft.Divider(),
                        ft.Text(
                            "Desarrollado por:\nJosue Yael Guerrero Priego",
                            text_align=ft.TextAlign.CENTER,
                            size=14,
                        ),
                        ft.Text(
                            "Propósito:\nHerramienta de gestión y consulta de bases de datos SQLite\n"
                            "con interfaz gráfica intuitiva para facilitar el trabajo\n"
                            "con bases de datos relacionales.",
                            text_align=ft.TextAlign.CENTER,
                            size=14,
                        ),
                        ft.Row(
                            [
                                ft.ElevatedButton(
                                    text="Visitar repositorio en GitHub",
                                    icon=ft.icons.LINK,
                                    on_click=lambda _: self.open_github(),
                                ),
                                ft.ElevatedButton(
                                    text="Cerrar",
                                    on_click=self.close_dialog
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
                padding=ft.padding.all(20),
            )

            # Crear un nuevo diálogo
            self.dialog = ft.AlertDialog(
                modal=True,
                title=ft.Text(
                    "Acerca de LunarisDB",
                    weight=ft.FontWeight.BOLD,
                    size=20,
                    text_align=ft.TextAlign.CENTER
                ),
                content=content,
                actions_alignment=ft.MainAxisAlignment.END,
                on_dismiss=self.close_dialog
            )

            # Agregar el diálogo al overlay y mostrarlo
            self.page.overlay.append(self.dialog)
            self.dialog.open = True
            self.page.update()

        except Exception as e:
            print(f"Error al mostrar el diálogo: {e}")

    def open_github(self):
        """
        Abre el enlace al repositorio de GitHub.
        """
        try:
            self.page.launch_url("https://github.com/josueygp/LunarisDB")
        except Exception as e:
            print(f"Error al abrir el enlace de GitHub: {e}")
from ui.about_window import AboutWindow

# Define la función `handle_about_click` que manejará el evento cuando se haga clic en el botón o elemento vinculado al "Acerca de"
# La función toma un parámetro `e` que representa el evento que se activa
def handle_about_click(e):
    # Obtiene la página del evento `e` (generalmente asociada al elemento que se ha activado)
    page = e.page
    # Crea una instancia de `AboutWindow` pasándole la página como parámetro, para mostrar o manejar la ventana "Acerca de"
    AboutWindow(page)


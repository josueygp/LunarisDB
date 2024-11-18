import flet as ft

class DatabaseEvents:
    @staticmethod
    def get_database_structure(connection):
        """Obtiene la estructura de la base de datos agrupada por tipo"""
        cursor = connection.cursor()
        
        # Primero obtenemos las tablas
        cursor.execute("""
            SELECT 
                m.name, 
                m.type,
                CASE 
                    WHEN m.type = 'table' THEN (
                        SELECT COUNT(*) 
                        FROM sqlite_master 
                        WHERE type = 'index' 
                        AND tbl_name = m.name
                    )
                    ELSE 0
                END as index_count
            FROM sqlite_master m
            WHERE m.type IN ('table', 'view', 'trigger', 'index')
            AND m.name NOT LIKE 'sqlite_%'
            ORDER BY 
                CASE m.type
                    WHEN 'table' THEN 1
                    WHEN 'view' THEN 2
                    WHEN 'trigger' THEN 3
                    WHEN 'index' THEN 4
                    ELSE 5
                END,
                m.name
        """)
        
        return cursor.fetchall()

    @staticmethod
    def create_tree_items(items):
        """Crea los items del árbol con estilos y comportamientos específicos por tipo"""
        tree_items = []
        
        # Definir los estilos por tipo
        type_styles = {
            'table': {
                'icon': ft.icons.TABLE_CHART,
                'color': "#4CAF50",  # Verde para tablas
                'hover_enabled': True
            },
            'view': {
                'icon': ft.icons.VIEW_LIST,
                'color': "#2196F3",  # Azul para vistas
                'hover_enabled': True
            },
            'trigger': {
                'icon': ft.icons.BOLT,
                'color': "#FFC107",  # Amarillo para triggers
                'hover_enabled': False
            },
            'index': {
                'icon': ft.icons.FORMAT_LIST_NUMBERED,
                'color': "#9E9E9E",  # Gris para índices
                'hover_enabled': False
            }
        }

        def create_item(name, type_, index_count=0):
            style = type_styles.get(type_, {
                'icon': ft.icons.QUESTION_MARK,
                'color': "#757575",
                'hover_enabled': False
            })

            def handle_hover(e):
                if style['hover_enabled']:
                    e.control.bgcolor = "#2d2d2d" if e.data == "true" else "#222222"
                    e.control.update()

            # Crear el contenido del item
            row_controls = [
                ft.Icon(style['icon'], size=16, color=style['color']),
                ft.Text(name, size=14, color="#e0e0e0")
            ]

            # Añadir contador de índices para tablas
            if type_ == 'table' and index_count > 0:
                row_controls.append(
                    ft.Container(
                        content=ft.Text(
                            f"{index_count} idx",
                            size=12,
                            color="#757575"
                        ),
                        margin=ft.margin.only(left=5)
                    )
                )

            container = ft.Container(
                content=ft.Row(
                    controls=row_controls,
                    spacing=10
                ),
                padding=ft.padding.symmetric(horizontal=10, vertical=5),
                bgcolor="#222222",
                on_hover=handle_hover if style['hover_enabled'] else None,
                # Solo hacemos clickeable si es tabla o vista
                on_click=lambda e, n=name: e.page.db_manager.execute_query(
                    f"SELECT * FROM {n} LIMIT 100",
                    e.page.results_table
                ) if type_ in ['table', 'view'] else None
            )

            return container

        # Procesar los items agrupados por tipo
        current_type = None
        for name, type_, index_count in items:
            # Si cambiamos de tipo, añadir un separador
            if current_type != type_:
                if current_type is not None:  # No añadir separador antes del primer grupo
                    tree_items.append(ft.Divider(height=1, color="#333333"))
                current_type = type_
            
            tree_items.append(create_item(name, type_, index_count))

        return tree_items
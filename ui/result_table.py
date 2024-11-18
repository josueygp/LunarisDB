import flet as ft

class ResultsTableManager:
    def __init__(self):
        self.results_table = ft.DataTable(
            bgcolor="#2d2d2d",
            border=ft.border.all(1, "#404040"),
            columns=[
                ft.DataColumn(ft.Text("Results will appear here", color="#ffffff")),
                ft.DataColumn(ft.Text("Additional Column", color="#ffffff")),
            ],
            rows=[
                ft.DataRow(cells=[ft.DataCell(ft.Text("Select a table or write a query", color="#808080")), ft.DataCell(ft.Text("Placeholder"))])
            ]
        )

    def get_results_tabs(self):
        console_output = ft.TextField(
            multiline=True,
            read_only=True,
            min_lines=5,
            max_lines=5,
            bgcolor="#2d2d2d",
            border_color="#404040",
            color="#00ff00",
            value="Ready for queries...",
        )

        # Usar Column y Row para habilitar el desplazamiento en ambas direcciones
        scrollable_table_column = ft.Column(
            [self.results_table],
            scroll=True
        )
        scrollable_table_container = ft.Row(
            [scrollable_table_column],
            scroll=True,
            expand=1,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        return ft.Tabs(
            selected_index=0,
            tabs=[
                ft.Tab(
                    text="Results",
                    content=ft.Container(
                        content=scrollable_table_container,
                        padding=10,
                        bgcolor="#1a1a1a"
                    ),
                ),
                ft.Tab(
                    text="Console",
                    content=ft.Container(
                        content=console_output,
                        padding=10,
                        bgcolor="#1a1a1a"
                    ),
                ),
            ]
        )

    def get_results_table(self):
        return self.results_table

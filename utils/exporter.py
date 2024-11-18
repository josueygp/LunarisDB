import sqlite3
import os

def export_database_to_sql(db_path: str, export_path: str) -> bool:
    """
    Exporta toda la base de datos a un archivo SQL.

    :param db_path: Ruta de la base de datos SQLite (.db).
    :param export_path: Ruta donde se guardará el archivo de exportación (.sql).
    :return: True si la exportación es exitosa, False en caso de error.
    """
    if not os.path.exists(db_path):
        print(f"Error: No se encontró la base de datos en {db_path}")
        return False

    try:
        # Conectarse a la base de datos
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Abrir el archivo de exportación
        with open(export_path, 'w', encoding='utf-8') as f:
            # Usar iterdump para volcar toda la base de datos a un archivo SQL
            for line in conn.iterdump():
                f.write(f"{line}\n")

        print(f"Base de datos exportada exitosamente a {export_path}")
        return True

    except Exception as e:
        print(f"Error al exportar la base de datos: {str(e)}")
        return False

    finally:
        # Cerrar la conexión a la base de datos
        if conn:
            conn.close()

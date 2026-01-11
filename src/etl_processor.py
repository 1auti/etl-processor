"""
Procesador ETL principal.
Orquesta el proceso de extracción, transformación y carga de logs.
"""

from pathlib import Path
from typing import List, Dict
from src.config import Config
from src.log_parser import LogParser
from src.db_manager import DatabaseManager


class ETLProcessor:
    """
    Procesador ETL que lee archivos de log, parsea las líneas
    y carga los datos en PostgreSQL en lotes (batches).
    """

    def __init__(self, log_file_path: str = None, batch_size: int = None):
        """
        Inicializa el procesador ETL.

        Args:
            log_file_path (str, optional): Ruta del archivo de logs
            batch_size (int, optional): Tamaño del lote para inserts
        """
        self.log_file_path = log_file_path or Config.LOG_FILE_PATH
        self.batch_size = batch_size or Config.BATCH_SIZE
        self.parser = LogParser()
        self.db = DatabaseManager()

        # Estadísticas del proceso
        self.stats = {
            'total_lines': 0,
            'parsed_successfully': 0,
            'parse_errors': 0,
            'inserted': 0
        }

    def extract(self) -> List[str]:
        """
        Extrae las líneas del archivo de log.

        Returns:
            list: Lista de líneas del archivo

        Raises:
            FileNotFoundError: Si el archivo no existe
        """
        log_path = Path(self.log_file_path)

        if not log_path.exists():
            raise FileNotFoundError(f"Archivo de log no encontrado: {self.log_file_path}")

        print(f" Leyendo archivo: {self.log_file_path}")

        with open(log_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        self.stats['total_lines'] = len(lines)
        print(f" Total de líneas leídas: {len(lines)}")

        return lines

    def transform(self, lines: List[str]) -> List[Dict]:
        """
        Transforma las líneas de log en diccionarios estructurados.

        Args:
            lines (list): Líneas crudas del archivo de log

        Returns:
            list: Lista de diccionarios con datos parseados
        """
        print(f" Parseando {len(lines)} líneas...")

        parsed_records = []

        for line_num, line in enumerate(lines, start=1):
            # Parsear línea
            record = self.parser.parse_line(line.strip())

            if record:
                parsed_records.append(record)
                self.stats['parsed_successfully'] += 1
            else:
                self.stats['parse_errors'] += 1
                # Log de error solo para las primeras 5 líneas fallidas
                if self.stats['parse_errors'] <= 5:
                    print(f"  Error en línea {line_num}: formato inválido")

        print(f" Parseadas correctamente: {self.stats['parsed_successfully']}")
        print(f" Errores de parsing: {self.stats['parse_errors']}")

        return parsed_records

    def load(self, records: List[Dict]):
        """
        Carga los registros parseados en PostgreSQL usando batches.

        Args:
            records (list): Lista de diccionarios con datos parseados
        """
        if not records:
            print("  No hay registros para insertar")
            return

        print(f" Insertando {len(records)} registros en la base de datos...")

        # Conectar a la base de datos
        self.db.connect()

        try:
            # Asegurar que las tablas existen
            self.db.create_tables()

            # Insertar en batches
            total_inserted = 0

            for i in range(0, len(records), self.batch_size):
                batch = records[i:i + self.batch_size]
                inserted = self.db.insert_batch(batch)
                total_inserted += inserted

                # Mostrar progreso
                progress = (i + len(batch)) / len(records) * 100
                print(f"  Progreso: {progress:.1f}% ({i + len(batch)}/{len(records)})")

            self.stats['inserted'] = total_inserted
            print(f" Total insertado: {total_inserted} registros")

        finally:
            # Siempre desconectar, incluso si hay error
            self.db.disconnect()

    def run(self):
        """
        Ejecuta el proceso ETL completo: Extract → Transform → Load.

        Returns:
            dict: Estadísticas del proceso
        """
        print("=" * 60)
        print(" INICIANDO PROCESO ETL")
        print("=" * 60)

        try:
            # 1. EXTRACT - Leer archivo de logs
            lines = self.extract()

            # 2. TRANSFORM - Parsear líneas
            records = self.transform(lines)

            # 3. LOAD - Insertar en PostgreSQL
            self.load(records)

            # Mostrar resumen
            self.print_summary()

            return self.stats

        except Exception as e:
            print(f" Error en proceso ETL: {e}")
            raise

    def print_summary(self):
        """Imprime un resumen del proceso ETL."""
        print("\n" + "=" * 60)
        print(" RESUMEN DEL PROCESO ETL")
        print("=" * 60)
        print(f"  Total de líneas procesadas: {self.stats['total_lines']}")
        print(f"  Parseadas exitosamente:     {self.stats['parsed_successfully']}")
        print(f"  Errores de parsing:         {self.stats['parse_errors']}")
        print(f"  Registros insertados:       {self.stats['inserted']}")

        if self.stats['total_lines'] > 0:
            success_rate = (self.stats['parsed_successfully'] / self.stats['total_lines']) * 100
            print(f"  Tasa de éxito:              {success_rate:.2f}%")

        print("=" * 60)


# Testing directo del módulo
if __name__ == "__main__":
    processor = ETLProcessor()
    processor.run()

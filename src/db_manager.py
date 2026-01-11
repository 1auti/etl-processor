"""
Gestor de conexion y operacion de PostgresSQL
Manejo de conexiones , cracion de tablas y inserciones de datos
"""


import psycopg2
from psycopg2.extras import execute_batch
from typing import List, Dict, Optional
from src.config import Config

class DatabaseManager:
    """
    Gestor de operaciones con PostgreSQL.
    Maneja la conexión, creación de schema e inserción de datos en batch.
    """

    def __init__(self):
        """
        Inicializa el gestor de base de datos.
        La conexión se establece cuando se llama a connect().
        """
        self.conn: Optional[psycopg2.extensions.connection] = None
        self.cursor: Optional[psycopg2.extensions.cursor] = None

    def connect(self):
        """
        Establece conexión con PostgreSQL usando configuración de Config.

        Raises:
            psycopg2.Error: Si no se puede conectar a la base de datos
        """
        try:
            conn_params = Config.get_db_connection_string()
            self.conn = psycopg2.connect(**conn_params)
            self.cursor = self.conn.cursor()
            print(f" Conectado a PostgreSQL: {conn_params['database']}@{conn_params['host']}")
        except psycopg2.Error as e:
            print(f" Error conectando a PostgreSQL: {e}")
            raise

    def disconnect(self):
        """
        Cierra la conexión con PostgreSQL.
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            print(" Desconectado de PostgreSQL")

    def create_tables(self):
        """
        Crea las tablas necesarias si no existen.

        Tabla web_logs:
        - id: Identificador único auto-incremental
        - ip: Dirección IP del cliente
        - timestamp: Momento del request
        - method: Método HTTP (GET, POST, etc.)
        - url: Ruta solicitada
        - status: Código de estado HTTP
        - bytes: Bytes transferidos
        - created_at: Timestamp de inserción en BD
        """
        create_table_query = """
        CREATE TABLE IF NOT EXISTS web_logs (
            id BIGSERIAL PRIMARY KEY,
            ip VARCHAR(45) NOT NULL,
            timestamp TIMESTAMP NOT NULL,
            method VARCHAR(10) NOT NULL,
            url VARCHAR(500) NOT NULL,
            status SMALLINT NOT NULL,
            bytes INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        -- Índices para optimizar consultas
        CREATE INDEX IF NOT EXISTS idx_web_logs_timestamp ON web_logs(timestamp);
        CREATE INDEX IF NOT EXISTS idx_web_logs_ip ON web_logs(ip);
        CREATE INDEX IF NOT EXISTS idx_web_logs_url ON web_logs(url);
        CREATE INDEX IF NOT EXISTS idx_web_logs_status ON web_logs(status);
        """

        try:
            self.cursor.execute(create_table_query)
            self.conn.commit()
            print(" Tablas verificadas/creadas correctamente")
        except psycopg2.Error as e:
            self.conn.rollback()
            print(f" Error creando tablas: {e}")
            raise

    def insert_batch(self, records: List[Dict]) -> int:
        """
        Inserta un lote de registros en la tabla web_logs.
        Usa execute_batch para mejor performance.

        Args:
            records (list): Lista de diccionarios con los datos parseados

        Returns:
            int: Cantidad de registros insertados

        Raises:
            psycopg2.Error: Si hay error en la inserción
        """
        if not records:
            return 0

        insert_query = """
        INSERT INTO web_logs (ip, timestamp, method, url, status, bytes)
        VALUES (%(ip)s, %(timestamp)s, %(method)s, %(url)s, %(status)s, %(bytes)s)
        """

        try:
            # execute_batch es más eficiente que executemany
            execute_batch(self.cursor, insert_query, records)
            self.conn.commit()

            count = len(records)
            print(f" Insertados {count} registros en la base de datos")
            return count

        except psycopg2.Error as e:
            self.conn.rollback()
            print(f" Error insertando batch: {e}")
            raise

    def get_total_records(self) -> int:
        """
        Obtiene el total de registros en la tabla web_logs.

        Returns:
            int: Cantidad total de registros
        """
        try:
            self.cursor.execute("SELECT COUNT(*) FROM web_logs")
            count = self.cursor.fetchone()[0]
            return count
        except psycopg2.Error as e:
            print(f" Error obteniendo total de registros: {e}")
            return 0

    def __enter__(self):
        """Soporte para context manager (with statement)."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cierra conexión automáticamente al salir del context manager."""
        self.disconnect()


# Testing directo del módulo
if __name__ == "__main__":
    print("Testing DatabaseManager...")

    try:
        with DatabaseManager() as db:
            db.create_tables()
            total = db.get_total_records()
            print(f"Total de registros en DB: {total}")
    except Exception as e:
        print(f"Error en testing: {e}")

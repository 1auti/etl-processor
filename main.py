"""
Sistema de Análisis de Tráfico Web - ETL Processor
Punto de entrada principal del procesador de logs.
"""

import sys

from src.config import Config
from src.etl_processor import ETLProcessor


def main():
    """Función principal que ejecuta el ETL."""
    print("=" * 60)
    print(" SISTEMA DE ANÁLISIS DE TRÁFICO WEB - ETL")
    print("   Versión: 1.0.0")
    print("=" * 60)

    try:
        # Validar configuración
        print("\n🔧 Validando configuración...")
        Config.validate()

        # Crear y ejecutar procesador ETL
        processor = ETLProcessor()
        stats = processor.run()

        # Finalizar con éxito
        print("\n Proceso ETL completado exitosamente!")
        sys.exit(0)

    except FileNotFoundError as e:
        print(f"\n Error: {e}")
        print(" Asegurate de que el archivo de logs existe")
        sys.exit(1)

    except Exception as e:
        print(f"\n Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

class MessageConstants:
    """Mensajes estándar del sistema."""

    # Mensajes de éxito
    MSG_ETL_SUCCESS = "✅ Proceso ETL completado exitosamente"
    MSG_DB_CONNECTED = "✅ Conectado a PostgreSQL"
    MSG_TABLES_CREATED = "✅ Tablas verificadas/creadas correctamente"
    MSG_METRICS_SENT = "📊 Métricas enviadas a PostgreSQL"

    # Mensajes de error
    MSG_FILE_NOT_FOUND = "❌ Archivo de log no encontrado"
    MSG_DB_CONNECTION_FAILED = "❌ Error conectando a PostgreSQL"
    MSG_PARSE_ERROR = "⚠️  Error parseando línea"
    MSG_INSERT_ERROR = "❌ Error insertando datos"

    # Mensajes informativos
    MSG_READING_FILE = "📂 Leyendo archivo"
    MSG_PARSING_LINES = "🔄 Parseando líneas"
    MSG_INSERTING_RECORDS = "💾 Insertando registros"
    MSG_VALIDATING_CONFIG = "🔧 Validando configuración"

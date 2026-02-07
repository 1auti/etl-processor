```plaintext

python-etl/
├── src/
│   ├── __init__.py
│   │
│   ├── core/                          # Núcleo del sistema
│   │   ├── __init__.py
│   │   ├── config.py                  # Configuración centralizada
│   │   ├── logger.py                  # Logging profesional
│   │   └── exceptions.py              # Excepciones custom
│   │
│   ├── models/                        # Modelos de datos
│   │   ├── __init__.py
│   │   ├── log_entry.py               # Dataclass para logs
│   │   └── processing_result.py       # Resultado del procesamiento
│   │
│   ├── parsers/                       # Parsers especializados
│   │   ├── __init__.py
│   │   ├── base_parser.py             # Parser abstracto
│   │   ├── apache_parser.py           # Parser Apache
│   │   ├── nginx_parser.py            # Parser Nginx
│   │   └── parser_factory.py          # Factory pattern
│   │
│   ├── validators/                    # Validadores de datos
│   │   ├── __init__.py
│   │   ├── base_validator.py
│   │   ├── ip_validator.py
│   │   ├── url_validator.py
│   │   └── timestamp_validator.py
│   │
│   ├── enrichers/                     # Enriquecimiento de datos
│   │   ├── __init__.py
│   │   ├── geo_enricher.py            # Geolocalización de IPs
│   │   ├── user_agent_enricher.py     # Parseo de User-Agent
│   │   └── threat_enricher.py         # Detección de amenazas
│   │
│   ├── storage/                       # Capa de persistencia
│   │   ├── __init__.py
│   │   ├── base_storage.py            # Interface abstracta
│   │   ├── postgres_storage.py        # Implementación PostgreSQL
│   │   ├── connection_pool.py         # Pool de conexiones
│   │   └── migration_manager.py       # Migraciones de BD
│   │
│   ├── processors/                    # Procesadores del pipeline
│   │   ├── __init__.py
│   │   ├── pipeline.py                # Orquestador del pipeline
│   │   ├── batch_processor.py         # Procesamiento por lotes
│   │   ├── deduplicator.py            # Eliminación de duplicados
│   │   └── checkpoint_manager.py      # Checkpoints de progreso
│   │
│   ├── monitoring/                    # Monitoreo y métricas
│   │   ├── __init__.py
│   │   ├── metrics_collector.py       # Colector de métricas
│   │   ├── health_checker.py          # Health checks
│   │   └── alerting.py                # Sistema de alertas
│   │
│   └── utils/                         # Utilidades
│       ├── __init__.py
│       ├── retry.py                   # Decorador de reintentos
│       ├── file_utils.py              # Operaciones con archivos
│       └── date_utils.py              # Utilidades de fechas
│
├── tests/                             # Tests completos
│   ├── __init__.py
│   ├── unit/                          # Tests unitarios
│   ├── integration/                   # Tests de integración
│   └── fixtures/                      # Datos de prueba
│
├── migrations/                        # Migraciones de BD
│   └── V001__initial_schema.sql
│
├── config/                            # Configs por ambiente
│   ├── dev.yaml
│   ├── prod.yaml
│   └── test.yaml
│
├── logs/                              # Logs de la aplicación
├── data/                              # Datos de entrada
│   ├── raw/                           # Logs sin procesar
│   ├── processed/                     # Logs procesados
│   └── failed/                        # Logs con errores
│
├── scripts/                           # Scripts auxiliares
│   ├── setup_db.py
│   └── generate_sample_data.py
│
├── main.py                            # Punto de entrada
├── requirements.txt                   # Dependencias base
├── requirements-dev.txt               # Dependencias de desarrollo
├── pytest.ini                         # Config de pytest
├── .env.example                       # Ejemplo de variables
└── README.md                          # Documentación
```

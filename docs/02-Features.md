#### **Feature 1: Restructuración y Arquitectura Base**

**Objetivo:** Crear la estructura de carpetas profesional y configuración base

**Tareas:**
- [x] Crear nueva estructura de carpetas
- [x]  Implementar sistema de configuración multi-ambiente (dev/test/prod)
- [x] Setup de logging estructurado con `structlog`
- [x]  Crear excepciones custom
- [x]  Implementar base classes abstractas
- [] Setup de testing con pytest
- [] Configurar pre-commit hooks
- [] Crear base abstracta donde los componentes van a hederar
- [] Crear un sistema de reintentos ( decorador para reinentso automaticos
- [] colector de metricas que se guarden en la base de datos
- [] constantes que persistan en la la base de datos o no ver
- [] crear type aliases : type hints customizados para mejor la doc

```plaintext
src/
├── core/
│   ├── config.py          # Config con YAML + env vars
│   ├── logger.py          # Structured logging
│   ├── exceptions.py      # Custom exceptions
│   ├── base.py            # Base classes abstractas
    ├── retry
    ├── constants
    ├── metrics
    ├── types
```


#### **Feature 2: Sistema de Modelos con Pydantic** ⭐ SEGUNDO

**Objetivo:** Validación automática de datos con type safety

**Tareas:**

- [x] Crear modelo `LogEntry` con Pydantic
- [x] Validadores custom para IP, URL, timestamp
- [x]Modelo `ProcessingResult` para métricas
- [x] Modelo `ValidationError` para errores
- [] Modelo `EnrichedLogEntry` (con geo, user-agent, etc)
- [] Serialización/Deserialización automática
- [] Tests unitarios de validación


```plaintext
src/
├── models/
│   ├── log_entry.py       # LogEntry con validaciones
│   ├── results.py         # ProcessingResult, ValidationError
│   └── enriched.py        # EnrichedLogEntry

```


#### **Feature 3: Parsers Profesionales con Factory Pattern**

**Objetivo:** Sistema extensible de parsers que detecta formato automáticamente

**Tareas:**
- []  Crear `BaseParser` (clase abstracta)
- [] Implementar `ApacheParser` robusto
- []  Implementar `NginxParser` robusto
- []  Crear `ParserFactory` que detecta formato automático
- []  Parser context manager para manejo de archivos
- []  Streaming parser (procesa línea por línea sin cargar todo)
- []  Tests con fixtures de logs reales

```plaintext


src/
├── parsers/
│ ├── base.py # BaseParser abstracto
│ ├── apache.py # ApacheParser
│ ├── nginx.py # NginxParser
│ ├── factory.py # ParserFactory (auto-detect)
│ └── streaming.py # StreamingParser


```

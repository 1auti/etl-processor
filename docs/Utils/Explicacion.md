La carpeta `utils/` contiene **utilidades y helpers** reutilizables para todo el sistema ETL. Siguiendo el principio **DRY** (Don't Repeat Yourself), centraliza funcionalidades comunes que son usadas por múltiples componentes.

```text
src/core/utils/
├── __init__.py              # Exporta todas las utilidades
├── retry_decorators.py      # Decoradores para reintentos automáticos
├── async_retry.py
├── retry_contexts.py          # Validación de datos y configuraciones
├── retry_contexts_database      # Context managers personalizados
├── retry_advanced        # Utilidades para métricas y estadísticas

```

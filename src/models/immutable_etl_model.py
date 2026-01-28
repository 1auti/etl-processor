from base import BaseETLModel
from pydantic import ConfigDict


class ImmutableETLModel(BaseETLModel):
    """Sirve para datos que no tienen que cambiar:
    Como  - resultados de procesamiento
          - Estadisticas
          - Configuraciones"""

    model_config = ConfigDict(**BaseETLModel.model_config, frozen=True)

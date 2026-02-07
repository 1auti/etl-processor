"""
Modelo base con Pydantic para todas las entidades del ETL.

Proporciona validación automática, serialización y métodos de conversión
para todas las clases de modelos del sistema.
"""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, ConfigDict


class BaseETLModel(BaseModel):
    model_config = ConfigDict(
        strict=True,  # Validacion estricta de los datos
        validate_assignment=True,  # Validacion en tiempos de asignacion
        extra="forbid",  # Campos extras estan prohidos
        # La serialiazacion del datetime como ISO string
        json_encoders={datetime: lambda v: v.isoformat() if v else None},
        # Usar valores de enum en serializacion
        use_enum_values=True,
        # Permite utilizar el alias
        populate_by_name=True,
        # Validar valores por defecto
        validate_default=True,
    )

    def to_log_record(self) -> Dict[str, Any]:
        """Convierte a log_record  ( type: alias , Dict[str , any ])"""
        return self.model_dump()

    def to_json(self, **kwargs) -> str:
        return self.model_dump_json(**kwargs)

    def to_dict(self) -> Dict[str, Any]:
        """Alias de to_log_record() para conveniencia."""
        return self.to_log_record()

    """ Creamos una instancia valida desde LogRecord (Dict sin validacion)
        Args:
             record: Log parseado ( sin validacion )
        Returns:
             Instancia validad por el modelo
    """

    @classmethod
    def from_log_record(cls, record: Dict[str, Any]):
        return cls.model_validate(record)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Alias de from_log_record() para conveniencia."""
        return cls.from_log_record(data)

    @classmethod
    def from_json(cls, json_str: str):
        return cls.model_validate_json(json_str)

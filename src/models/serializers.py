"""
Serializers avanzados para modelos ETL.
Provee serialización a múltiples formatos.
"""

import csv
import json
from datetime import datetime
from io import StringIO
from typing import Any, Dict, List

from .base import BaseETLModel


class ModelSerializer:
    """
    Serializador avanzado para modelos ETL.
    Soporta múltiples formatos de salida.
    """

    @staticmethod
    def to_csv_row(model: BaseETLModel, fields: List[str] = None) -> str:
        """
        Serializa modelo a fila CSV.

        Args:
            model: Modelo a serializar
            fields: Lista de campos a incluir (None = todos)

        Returns:
            str: Fila CSV

        Example:
            >>> log = LogEntry(...)
            >>> csv_row = ModelSerializer.to_csv_row(log)
            >>> # "192.168.1.1,2024-01-15T10:00:00,GET,/api/users,200,1234"
        """
        data = model.to_dict()

        if fields:
            data = {k: data[k] for k in fields if k in data}

        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=data.keys())
        writer.writerow(data)

        return output.getvalue().strip()

    @staticmethod
    def to_csv_batch(models: List[BaseETLModel], include_header: bool = True) -> str:
        """
        Serializa batch de modelos a CSV completo.

        Args:
            models: Lista de modelos
            include_header: Si incluir header

        Returns:
            str: CSV completo

        Example:
            >>> logs = [LogEntry(...), LogEntry(...)]
            >>> csv_data = ModelSerializer.to_csv_batch(logs)
        """
        if not models:
            return ""

        output = StringIO()

        # Usar campos del primer modelo
        first_dict = models[0].to_dict()
        fieldnames = list(first_dict.keys())

        writer = csv.DictWriter(output, fieldnames=fieldnames)

        if include_header:
            writer.writeheader()

        for model in models:
            writer.writerow(model.to_dict())

        return output.getvalue()

    @staticmethod
    def to_yaml(model: BaseETLModel, **kwargs) -> str:
        """
        Serializa modelo a YAML.

        Args:
            model: Modelo a serializar
            **kwargs: Argumentos para yaml.dump()

        Returns:
            str: YAML string

        Example:
            >>> log = LogEntry(...)
            >>> yaml_str = ModelSerializer.to_yaml(log)
        """
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML no instalado. Ejecutar: pip install pyyaml")

        data = model.to_dict()

        # Convertir datetime a string para YAML
        def convert_datetime(obj):
            if isinstance(obj, dict):
                return {k: convert_datetime(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_datetime(item) for item in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        data = convert_datetime(data)

        return yaml.dump(data, **kwargs)

    @staticmethod
    def to_xml(model: BaseETLModel, root_tag: str = "log_entry") -> str:
        """
        Serializa modelo a XML.

        Args:
            model: Modelo a serializar
            root_tag: Tag raíz del XML

        Returns:
            str: XML string

        Example:
            >>> log = LogEntry(...)
            >>> xml_str = ModelSerializer.to_xml(log)
        """
        from xml.dom import minidom
        from xml.etree.ElementTree import Element, SubElement, tostring

        data = model.to_dict()

        root = Element(root_tag)

        def dict_to_xml(parent, data_dict):
            for key, value in data_dict.items():
                if isinstance(value, dict):
                    child = SubElement(parent, key)
                    dict_to_xml(child, value)
                elif isinstance(value, list):
                    for item in value:
                        child = SubElement(parent, key)
                        if isinstance(item, dict):
                            dict_to_xml(child, item)
                        else:
                            child.text = str(item)
                else:
                    child = SubElement(parent, key)
                    child.text = str(value) if value is not None else ""

        dict_to_xml(root, data)

        # Pretty print
        rough_string = tostring(root, encoding="unicode")
        reparsed = minidom.parseString(rough_string)

        return reparsed.toprettyxml(indent="  ")

    @staticmethod
    def to_msgpack(model: BaseETLModel) -> bytes:
        """
        Serializa modelo a MessagePack (formato binario eficiente).

        Args:
            model: Modelo a serializar

        Returns:
            bytes: Datos en formato MessagePack

        Example:
            >>> log = LogEntry(...)
            >>> msgpack_bytes = ModelSerializer.to_msgpack(log)
        """
        try:
            import msgpack
        except ImportError:
            raise ImportError("msgpack no instalado. Ejecutar: pip install msgpack")

        data = model.to_dict()

        # Convertir datetime a timestamp
        def convert_for_msgpack(obj):
            if isinstance(obj, dict):
                return {k: convert_for_msgpack(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_for_msgpack(item) for item in obj]
            elif isinstance(obj, datetime):
                return obj.timestamp()
            return obj

        data = convert_for_msgpack(data)

        return msgpack.packb(data, use_bin_type=True)

    @staticmethod
    def to_parquet_row(model: BaseETLModel) -> Dict[str, Any]:
        """
        Convierte modelo a formato compatible con Parquet.

        Args:
            model: Modelo a serializar

        Returns:
            Dict compatible con PyArrow/Pandas
        """
        data = model.to_dict()

        # Convertir datetime a timestamp para Parquet
        def convert_for_parquet(obj):
            if isinstance(obj, dict):
                return {k: convert_for_parquet(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_for_parquet(item) for item in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            return obj

        return convert_for_parquet(data)


class ModelDeserializer:
    """
    Deserializador avanzado para modelos ETL.
    Soporta múltiples formatos de entrada.
    """

    @staticmethod
    def from_csv_row(model_class, csv_row: str, fieldnames: List[str]) -> BaseETLModel:
        """
        Crea modelo desde fila CSV.

        Args:
            model_class: Clase del modelo (ej: LogEntry)
            csv_row: Fila CSV
            fieldnames: Nombres de campos

        Returns:
            Instancia del modelo
        """
        reader = csv.DictReader(StringIO(csv_row), fieldnames=fieldnames)
        row_dict = next(reader)

        return model_class.from_dict(row_dict)

    @staticmethod
    def from_yaml(model_class, yaml_str: str) -> BaseETLModel:
        """
        Crea modelo desde YAML.

        Args:
            model_class: Clase del modelo
            yaml_str: String YAML

        Returns:
            Instancia del modelo
        """
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML no instalado. Ejecutar: pip install pyyaml")

        data = yaml.safe_load(yaml_str)
        return model_class.from_dict(data)

    @staticmethod
    def from_msgpack(model_class, msgpack_bytes: bytes) -> BaseETLModel:
        """
        Crea modelo desde MessagePack.

        Args:
            model_class: Clase del modelo
            msgpack_bytes: Bytes en formato MessagePack

        Returns:
            Instancia del modelo
        """
        try:
            import msgpack
        except ImportError:
            raise ImportError("msgpack no instalado. Ejecutar: pip install msgpack")

        data = msgpack.unpackb(msgpack_bytes, raw=False)
        return model_class.from_dict(data)

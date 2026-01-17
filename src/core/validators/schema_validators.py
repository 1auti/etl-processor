"""
Data schema validators.
"""

import re
import json
from typing import Dict, Any, List, Union, Optional
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError


class ValidatorModel(BaseModel):
    """Base Pydantic model para validación de datos."""

    class Config:
        extra = 'forbid'
        validate_assignment = True


def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """Valida datos contra un esquema simple."""
    errors = []

    if not isinstance(data, dict):
        return ["Data must be a dictionary"]

    if not isinstance(schema, dict):
        return ["Schema must be a dictionary"]

    for field_name, field_schema in schema.items():
        is_required = field_schema.get('required', False)
        field_value = data.get(field_name)

        if is_required and field_value is None:
            errors.append(f"{field_name}: Field is required")
            continue

        if field_value is None:
            continue

        expected_type = field_schema.get('type')
        if expected_type and not isinstance(field_value, expected_type):
            errors.append(f"{field_name}: Expected type {expected_type.__name__}, got {type(field_value).__name__}")
            continue

        if isinstance(field_value, (int, float)):
            min_val = field_schema.get('min')
            max_val = field_schema.get('max')

            if min_val is not None and field_value < min_val:
                errors.append(f"{field_name}: Value {field_value} is less than minimum {min_val}")

            if max_val is not None and field_value > max_val:
                errors.append(f"{field_name}: Value {field_value} is greater than maximum {max_val}")

        if isinstance(field_value, (str, list)):
            min_len = field_schema.get('min_length')
            max_len = field_schema.get('max_length')

            if min_len is not None and len(field_value) < min_len:
                errors.append(f"{field_name}: Length {len(field_value)} is less than minimum {min_len}")

            if max_len is not None and len(field_value) > max_len:
                errors.append(f"{field_name}: Length {len(field_value)} is greater than maximum {max_len}")

        if isinstance(field_value, str):
            pattern = field_schema.get('regex')
            if pattern and not re.match(pattern, field_value):
                errors.append(f"{field_name}: Value does not match pattern")

        allowed_values = field_schema.get('allowed')
        if allowed_values and field_value not in allowed_values:
            errors.append(f"{field_name}: Value {field_value} not in allowed values {allowed_values}")

        nested_schema = field_schema.get('schema')
        if nested_schema and isinstance(field_value, dict):
            nested_errors = validate_schema(field_value, nested_schema)
            errors.extend([f"{field_name}.{error}" for error in nested_errors])

    return errors


def validate_json_schema(json_data: Union[str, Dict],
                        schema: Dict[str, Any]) -> List[str]:
    """Valida JSON contra un esquema JSON Schema."""
    try:
        import jsonschema
    except ImportError:
        return ["jsonschema package is required for JSON schema validation"]

    try:
        if isinstance(json_data, str):
            data = json.loads(json_data)
        else:
            data = json_data

        jsonschema.validate(instance=data, schema=schema)
        return []

    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {str(e)}"]
    except jsonschema.ValidationError as e:
        return [f"Validation error: {e.message} at {'.'.join(map(str, e.path))}"]
    except Exception as e:
        return [f"Validation error: {str(e)}"]


def create_validator_model(fields: Dict[str, Any]) -> type:
    """Crea dinámicamente un modelo Pydantic para validación."""
    from typing import get_type_hints

    field_definitions = {}
    annotations = {}

    for field_name, field_config in fields.items():
        if isinstance(field_config, tuple):
            field_type = field_config[0]
            field_args = field_config[1] if len(field_config) > 1 else {}
        else:
            field_type = field_config
            field_args = {}

        field_definitions[field_name] = Field(**field_args)
        annotations[field_name] = field_type

    Validator = type(
        'DynamicValidator',
        (ValidatorModel,),
        {
            '__annotations__': annotations,
            **field_definitions
        }
    )

    return Validator

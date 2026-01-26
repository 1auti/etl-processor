#!/bin/bash
cd /home/lauti/Documentos/Python/python-etl

echo "Corrigiendo importaciones en todos los archivos..."

# Lista de correcciones comunes
declare -A corrections
corrections["from config"]="from src.core.config"
corrections["import config"]="import src.core.config"
corrections["from core\.exceptions"]="from src.core.exceptions"
corrections["import core\.exceptions"]="import src.core.exceptions"
corrections["from core\."]="from src.core."
corrections["import core\."]="import src.core."

# Aplicar correcciones
for pattern in "${!corrections[@]}"; do
    replacement="${corrections[$pattern]}"
    echo "Corrigiendo: $pattern -> $replacement"
    find src/ -name "*.py" -type f -exec sed -i "s/^$pattern/$replacement/g" {} \;
done

echo "=== Verificación ==="
echo "Archivos que aún tienen importaciones simples (sin src.):"
find src/ -name "*.py" -type f -exec grep -l "^from [a-z_][a-z0-9_]* import" {} \; | head -10

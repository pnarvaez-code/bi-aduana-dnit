"""
Configuración específica del módulo ETL
"""

import sys
from pathlib import Path

# Agregar ruta del proyecto al path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from config import *

# Configuración específica ETL
ETL_CONFIG = {
    "encoding": ENCODING,
    "chunk_size": CHUNK_SIZE,
    "date_format": DATE_FORMAT,
    "null_values": ["", "NULL", "N/A", "None", "nan"],
    "drop_duplicates": True,
    "validate_schema": True,
}

# Mapeo de tipos de datos
DTYPES_MAPPING = {
    "fecha": "datetime64[ns]",
    "cantidad": "float64",
    "valor_cif": "float64",
    "valor_fob": "float64",
    "precio_unitario": "float64",
}

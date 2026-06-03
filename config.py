"""
Configuración global del proyecto BI - Aduana DNIT
"""

import os
from pathlib import Path

# Rutas
PROJECT_ROOT = Path(__file__).parent.absolute()
DATA_LAKE_ROOT = PROJECT_ROOT / "data_lake"
DATA_LAKE_BRONZE = DATA_LAKE_ROOT / "bronze"
DATA_LAKE_SILVER = DATA_LAKE_ROOT / "silver"
DATA_LAKE_GOLD = DATA_LAKE_ROOT / "gold"
SQL_DIR = PROJECT_ROOT / "sql"
ETL_DIR = PROJECT_ROOT / "etl"
LOGS_DIR = ETL_DIR / "logs"

# Crear directorios si no existen
for directory in [DATA_LAKE_BRONZE, DATA_LAKE_SILVER, DATA_LAKE_GOLD, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Base de datos
# Opciones: "duckdb" o "postgresql"
DB_TYPE = os.getenv("DB_TYPE", "duckdb")

# DuckDB
DUCKDB_PATH = os.getenv("DUCKDB_PATH", str(DATA_LAKE_GOLD / "aduana.duckdb"))

# PostgreSQL
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", 5432)
POSTGRES_DB = os.getenv("POSTGRES_DB", "aduana_bi")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")

# Archivos de entrada
INPUT_ITEM_CSV = DATA_LAKE_BRONZE / "nivel_item.csv"
INPUT_SUBITEM_XLSX = DATA_LAKE_BRONZE / "nivel_subitem.xlsx"

# Archivos de salida (Data Lake Silver)
OUTPUT_ITEM_SILVER = DATA_LAKE_SILVER / "item_limpio.parquet"
OUTPUT_SUBITEM_SILVER = DATA_LAKE_SILVER / "subitem_limpio.parquet"

# Archivos de salida (Data Lake Gold)
OUTPUT_FACT_ITEM_GOLD = DATA_LAKE_GOLD / "fact_aduana_item.parquet"
OUTPUT_FACT_SUBITEM_GOLD = DATA_LAKE_GOLD / "fact_aduana_subitem.parquet"
OUTPUT_DIM_FECHA = DATA_LAKE_GOLD / "dim_fecha.parquet"
OUTPUT_DIM_PRODUCTO = DATA_LAKE_GOLD / "dim_producto.parquet"
OUTPUT_DIM_PAIS = DATA_LAKE_GOLD / "dim_pais.parquet"
OUTPUT_DIM_ADUANA = DATA_LAKE_GOLD / "dim_aduana.parquet"
OUTPUT_DIM_REGIMEN = DATA_LAKE_GOLD / "dim_regimen.parquet"
OUTPUT_DIM_OPERACION = DATA_LAKE_GOLD / "dim_operacion.parquet"

# Logging
LOG_FILE = LOGS_DIR / "etl.log"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ETL
ENCODING = "utf-8"
CHUNK_SIZE = 50000  # Procesar en chunks

# Fechas
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

print(f"✓ Configuración cargada desde {PROJECT_ROOT}")
print(f"  - Base de datos: {DB_TYPE}")
print(f"  - Data Lake: {DATA_LAKE_ROOT}")

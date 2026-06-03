"""
Script principal de ETL para datos de Aduana DNIT
Procesa datos desde archivos CSV/XLSX a Data Warehouse
"""

import sys
from pathlib import Path
import logging
from loguru import logger

# Configurar logging
logger.remove()
logger.add(
    "etl/logs/etl.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
    rotation="500 MB",
    retention="10 days"
)
logger.add(sys.stdout, format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}")

# Importar módulos
from config import *
from utils.data_loader import DataLoader
from utils.data_cleaner import DataCleaner
from utils.data_transformer import DataTransformer
from utils.db_loader import DatabaseLoader


def main():
    """Función principal del ETL"""
    
    logger.info("=" * 80)
    logger.info("INICIANDO ETL - DATOS ADUANA DNIT")
    logger.info("=" * 80)
    
    try:
        # ========== PASO 1: INGESTA (BRONZE) ==========
        logger.info("\n[PASO 1] INGESTA DE DATOS (BRONZE LAYER)")
        logger.info("-" * 80)
        
        loader = DataLoader()
        
        logger.info("Cargando archivo de ítems...")
        df_items = loader.load_csv(INPUT_ITEM_CSV)
        logger.info(f"Ítems cargados: {df_items.shape}")
        
        logger.info("Cargando archivo de subitems...")
        df_subitems = loader.load_excel(INPUT_SUBITEM_XLSX)
        logger.info(f"Subitems cargados: {df_subitems.shape}")
        
        # ========== PASO 2: LIMPIEZA (SILVER) ==========
        logger.info("\n[PASO 2] LIMPIEZA Y NORMALIZACIÓN (SILVER LAYER)")
        logger.info("-" * 80)
        
        cleaner = DataCleaner()
        
        # Limpiar items
        logger.info("Limpiando datos de ítems...")
        df_items_clean = cleaner.clean_dataframe(df_items)
        df_items_clean = cleaner.standardize_columns(df_items_clean)
        
        # Convertir tipos de datos
        numeric_cols = ['cantidad', 'valor_cif', 'valor_fob', 'precio_unitario']
        df_items_clean = cleaner.convert_numeric(df_items_clean, numeric_cols)
        
        date_cols = ['fecha_operacion']
        df_items_clean = cleaner.convert_dates(df_items_clean, date_cols)
        
        # Guardar datos limpios (SILVER)
        df_items_clean.to_parquet(OUTPUT_ITEM_SILVER, index=False)
        logger.info(f"✓ Datos de ítems limpios guardados: {OUTPUT_ITEM_SILVER}")
        
        # Limpiar subitems
        logger.info("Limpiando datos de subitems...")
        df_subitems_clean = cleaner.clean_dataframe(df_subitems)
        df_subitems_clean = cleaner.standardize_columns(df_subitems_clean)
        
        # Guardar subitems limpios (SILVER)
        df_subitems_clean.to_parquet(OUTPUT_SUBITEM_SILVER, index=False)
        logger.info(f"✓ Datos de subitems limpios guardados: {OUTPUT_SUBITEM_SILVER}")
        
        # Generar reporte de calidad
        logger.info("\nReporte de Calidad - Ítems:")
        report = cleaner.get_data_quality_report(df_items_clean)
        logger.info(f"  Total de filas: {report['total_filas']}")
        logger.info(f"  Total de columnas: {report['total_columnas']}")
        logger.info(f"  Memoria usada: {report['memoria_mb']:.2f} MB")
        
        # ========== PASO 3: TRANSFORMACIÓN (GOLD) ==========
        logger.info("\n[PASO 3] TRANSFORMACIÓN A ESQUEMA DIMENSIONAL (GOLD LAYER)")
        logger.info("-" * 80)
        
        transformer = DataTransformer()
        
        # Crear dimensiones
        dim_fecha = transformer.create_dim_fecha()
        dim_fecha.to_parquet(OUTPUT_DIM_FECHA, index=False)
        
        dim_producto = transformer.create_dim_producto(df_items_clean)
        dim_producto.to_parquet(OUTPUT_DIM_PRODUCTO, index=False)
        
        dim_pais = transformer.create_dim_pais(df_items_clean)
        dim_pais.to_parquet(OUTPUT_DIM_PAIS, index=False)
        
        dim_aduana = transformer.create_dim_aduana(df_items_clean)
        dim_aduana.to_parquet(OUTPUT_DIM_ADUANA, index=False)
        
        dim_regimen = transformer.create_dim_regimen(df_items_clean)
        dim_regimen.to_parquet(OUTPUT_DIM_REGIMEN, index=False)
        
        dim_operacion = transformer.create_dim_operacion(df_items_clean)
        dim_operacion.to_parquet(OUTPUT_DIM_OPERACION, index=False)
        
        # Crear tabla de hechos
        fact_item = transformer.create_fact_aduana_item(
            df_items_clean,
            dim_fecha,
            dim_producto,
            dim_pais,
            dim_aduana,
            dim_regimen,
            dim_operacion
        )
        fact_item.to_parquet(OUTPUT_FACT_ITEM_GOLD, index=False)
        
        # ========== PASO 4: CARGA A BASE DE DATOS ==========
        logger.info("\n[PASO 4] CARGA A BASE DE DATOS")
        logger.info("-" * 80)
        
        if DB_TYPE == "duckdb":
            db_loader = DatabaseLoader(db_type="duckdb")
            db_loader.connect_duckdb(DUCKDB_PATH)
        else:
            db_loader = DatabaseLoader(db_type="postgresql")
            db_loader.connect_postgresql(
                POSTGRES_HOST,
                POSTGRES_PORT,
                POSTGRES_DB,
                POSTGRES_USER,
                POSTGRES_PASSWORD
            )
        
        # Cargar dimensiones
        logger.info("Cargando dimensiones...")
        db_loader.load_dataframe(dim_fecha, "dim_fecha")
        db_loader.load_dataframe(dim_producto, "dim_producto")
        db_loader.load_dataframe(dim_pais, "dim_pais")
        db_loader.load_dataframe(dim_aduana, "dim_aduana")
        db_loader.load_dataframe(dim_regimen, "dim_regimen")
        db_loader.load_dataframe(dim_operacion, "dim_operacion")
        
        # Cargar tabla de hechos
        logger.info("Cargando tabla de hechos...")
        db_loader.load_dataframe(fact_item, "fact_aduana_item")
        
        # Ejecutar SQL de índices y vistas
        logger.info("Creando índices y vistas...")
        sql_indexes = SQL_DIR / "04_indexes.sql"
        if sql_indexes.exists():
            db_loader.execute_sql_file(str(sql_indexes))
        
        sql_views = SQL_DIR / "05_olap_views.sql"
        if sql_views.exists():
            db_loader.execute_sql_file(str(sql_views))
        
        db_loader.close()
        
        # ========== RESUMEN FINAL ==========
        logger.info("\n" + "=" * 80)
        logger.info("ETL COMPLETADO EXITOSAMENTE")
        logger.info("=" * 80)
        logger.info(f"✓ Datos cargados en: {DUCKDB_PATH}")
        logger.info(f"✓ Tabla de hechos: {len(fact_item)} registros")
        logger.info(f"✓ Dimensiones creadas: 6")
        logger.info(f"✓ Log guardado en: {LOG_FILE}")
        logger.info("=" * 80 + "\n")
        
    except Exception as e:
        logger.error(f"\n✗ ERROR EN ETL: {str(e)}")
        logger.error(f"Revisar log en: {LOG_FILE}")
        sys.exit(1)


if __name__ == "__main__":
    main()

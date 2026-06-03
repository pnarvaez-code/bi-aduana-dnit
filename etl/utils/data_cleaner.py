"""
Módulo para limpieza y validación de datos
"""

import pandas as pd
import numpy as np
from loguru import logger


class DataCleaner:
    """Limpiador y validador de datos"""
    
    def __init__(self, null_values=None):
        self.null_values = null_values or ["", "NULL", "N/A", "None", "nan"]
    
    def clean_dataframe(self, df: pd.DataFrame, drop_duplicates=True, remove_nulls_threshold=0.5) -> pd.DataFrame:
        """
        Limpieza general del DataFrame
        
        Args:
            df: DataFrame a limpiar
            drop_duplicates: Si True, elimina duplicados
            remove_nulls_threshold: Umbral para eliminar columnas con muchos nulos (0-1)
            
        Returns:
            DataFrame limpio
        """
        logger.info("Iniciando limpieza de datos...")
        
        # Registrar estado inicial
        logger.info(f"  Estado inicial: {len(df)} filas, {len(df.columns)} columnas")
        
        # Reemplazar valores nulos
        for null_val in self.null_values:
            df = df.replace(null_val, np.nan)
        
        # Eliminar filas completamente nulas
        initial_rows = len(df)
        df = df.dropna(how='all')
        logger.info(f"  ✓ Filas completamente nulas eliminadas: {initial_rows - len(df)}")
        
        # Eliminar columnas con muchos nulos
        null_threshold = int(len(df) * remove_nulls_threshold)
        cols_to_drop = df.columns[df.isnull().sum() > null_threshold].tolist()
        if cols_to_drop:
            logger.warning(f"  ⚠ Columnas con >50% nulos eliminadas: {cols_to_drop}")
            df = df.drop(columns=cols_to_drop)
        
        # Eliminar duplicados
        if drop_duplicates:
            initial_rows = len(df)
            df = df.drop_duplicates()
            logger.info(f"  ✓ Filas duplicadas eliminadas: {initial_rows - len(df)}")
        
        # Limpiar espacios en blanco
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].str.strip() if df[col].dtype == 'object' else df[col]
        
        logger.info(f"  Estado final: {len(df)} filas, {len(df.columns)} columnas")
        return df
    
    @staticmethod
    def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
        """
        Estandariza nombres de columnas (lowercase, sin espacios)
        
        Args:
            df: DataFrame
            
        Returns:
            DataFrame con columnas estandarizadas
        """
        df.columns = (df.columns
                      .str.lower()
                      .str.replace(' ', '_')
                      .str.replace('-', '_')
                      .str.replace('.', '_'))
        logger.info(f"✓ Columnas estandarizadas: {list(df.columns)}")
        return df
    
    @staticmethod
    def convert_numeric(df: pd.DataFrame, columns: list) -> pd.DataFrame:
        """
        Convierte columnas a tipo numérico
        
        Args:
            df: DataFrame
            columns: Lista de columnas a convertir
            
        Returns:
            DataFrame con conversiones realizadas
        """
        for col in columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    null_count = df[col].isnull().sum()
                    if null_count > 0:
                        logger.warning(f"  ⚠ Columna '{col}': {null_count} valores no convertibles")
                except Exception as e:
                    logger.error(f"  ✗ Error al convertir '{col}': {str(e)}")
        return df
    
    @staticmethod
    def convert_dates(df: pd.DataFrame, columns: list, date_format="%Y-%m-%d") -> pd.DataFrame:
        """
        Convierte columnas a tipo datetime
        
        Args:
            df: DataFrame
            columns: Lista de columnas a convertir
            date_format: Formato de fecha esperado
            
        Returns:
            DataFrame con conversiones realizadas
        """
        for col in columns:
            if col in df.columns:
                try:
                    df[col] = pd.to_datetime(df[col], format=date_format, errors='coerce')
                    null_count = df[col].isnull().sum()
                    if null_count > 0:
                        logger.warning(f"  ⚠ Columna '{col}': {null_count} fechas inválidas")
                except Exception as e:
                    logger.error(f"  ✗ Error al convertir fecha '{col}': {str(e)}")
        return df
    
    @staticmethod
    def remove_outliers(df: pd.DataFrame, columns: list, std_threshold=3) -> pd.DataFrame:
        """
        Elimina outliers usando desviación estándar
        
        Args:
            df: DataFrame
            columns: Columnas numéricas a analizar
            std_threshold: Número de desviaciones estándar (default: 3)
            
        Returns:
            DataFrame sin outliers
        """
        initial_rows = len(df)
        
        for col in columns:
            if col in df.columns:
                mean = df[col].mean()
                std = df[col].std()
                lower_bound = mean - (std_threshold * std)
                upper_bound = mean + (std_threshold * std)
                df = df[(df[col] >= lower_bound) & (df[col] <= upper_bound)]
                logger.info(f"  ✓ Outliers removidos en '{col}': {initial_rows - len(df)} filas")
        
        return df
    
    @staticmethod
    def get_data_quality_report(df: pd.DataFrame) -> dict:
        """
        Genera reporte de calidad de datos
        
        Args:
            df: DataFrame
            
        Returns:
            Diccionario con métricas de calidad
        """
        report = {
            "total_filas": len(df),
            "total_columnas": len(df.columns),
            "memoria_mb": df.memory_usage(deep=True).sum() / (1024 * 1024),
            "columnas": {}
        }
        
        for col in df.columns:
            report["columnas"][col] = {
                "tipo": str(df[col].dtype),
                "nulos": int(df[col].isnull().sum()),
                "nulos_pct": round(df[col].isnull().sum() / len(df) * 100, 2),
                "unicos": int(df[col].nunique()),
                "duplicados": int(len(df[col]) - df[col].nunique()),
            }
        
        return report

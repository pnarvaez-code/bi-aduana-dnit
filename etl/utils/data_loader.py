"""
Módulo para cargar datos desde archivos CSV y Excel
"""

import pandas as pd
from pathlib import Path
from loguru import logger


class DataLoader:
    """Cargador de datos desde archivos CSV y Excel"""
    
    def __init__(self, encoding="utf-8"):
        self.encoding = encoding
    
    def load_csv(self, file_path: str | Path, dtype=None, parse_dates=None) -> pd.DataFrame:
        """
        Carga datos desde archivo CSV
        
        Args:
            file_path: Ruta al archivo CSV
            dtype: Diccionario de tipos de datos
            parse_dates: Lista de columnas a parsear como fechas
            
        Returns:
            DataFrame con los datos cargados
        """
        try:
            logger.info(f"Cargando CSV: {file_path}")
            df = pd.read_csv(
                file_path,
                encoding=self.encoding,
                dtype=dtype,
                parse_dates=parse_dates
            )
            logger.info(f"✓ CSV cargado: {len(df)} filas, {len(df.columns)} columnas")
            return df
        except Exception as e:
            logger.error(f"✗ Error al cargar CSV {file_path}: {str(e)}")
            raise
    
    def load_excel(self, file_path: str | Path, sheet_name=0, dtype=None, parse_dates=None) -> pd.DataFrame:
        """
        Carga datos desde archivo Excel
        
        Args:
            file_path: Ruta al archivo Excel
            sheet_name: Nombre o índice de la hoja
            dtype: Diccionario de tipos de datos
            parse_dates: Lista de columnas a parsear como fechas
            
        Returns:
            DataFrame con los datos cargados
        """
        try:
            logger.info(f"Cargando Excel: {file_path} (sheet: {sheet_name})")
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                dtype=dtype,
                parse_dates=parse_dates
            )
            logger.info(f"✓ Excel cargado: {len(df)} filas, {len(df.columns)} columnas")
            return df
        except Exception as e:
            logger.error(f"✗ Error al cargar Excel {file_path}: {str(e)}")
            raise
    
    @staticmethod
    def get_file_info(file_path: str | Path) -> dict:
        """
        Obtiene información del archivo
        
        Args:
            file_path: Ruta al archivo
            
        Returns:
            Diccionario con información del archivo
        """
        path = Path(file_path)
        return {
            "nombre": path.name,
            "ruta": str(path),
            "tamaño_mb": path.stat().st_size / (1024 * 1024),
            "existe": path.exists(),
        }

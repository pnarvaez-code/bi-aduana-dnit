"""
Módulo para transformación de datos a esquema dimensional
"""

import pandas as pd
from datetime import datetime
from loguru import logger


class DataTransformer:
    """Transformador de datos al esquema estrella"""
    
    @staticmethod
    def create_dim_fecha(start_year=2020, end_year=2026) -> pd.DataFrame:
        """
        Crea tabla de dimensión Fecha
        
        Args:
            start_year: Año inicial
            end_year: Año final
            
        Returns:
            DataFrame con dimensión Fecha
        """
        logger.info("Creando Dim_Fecha...")
        
        dates = pd.date_range(start=f'{start_year}-01-01', end=f'{end_year}-12-31', freq='D')
        
        df_fecha = pd.DataFrame({
            'fecha_id': range(1, len(dates) + 1),
            'fecha': dates,
            'año': dates.year,
            'mes': dates.month,
            'trimestre': (dates.month - 1) // 3 + 1,
            'semana': dates.isocalendar().week,
            'dia_semana': dates.dayofweek,
            'nombre_mes': dates.strftime('%B'),
            'nombre_dia': dates.strftime('%A'),
            'es_fin_semana': dates.dayofweek >= 5,
            'es_feriado': False,  # Se puede actualizar con calendario real
        })
        
        logger.info(f"✓ Dim_Fecha creada: {len(df_fecha)} registros")
        return df_fecha
    
    @staticmethod
    def create_dim_producto(df_items: pd.DataFrame) -> pd.DataFrame:
        """
        Crea tabla de dimensión Producto
        
        Args:
            df_items: DataFrame con datos de ítems
            
        Returns:
            DataFrame con dimensión Producto
        """
        logger.info("Creando Dim_Producto...")
        
        dim_producto = df_items[['item_id', 'descripcion_item', 'partida', 'capitulo']].drop_duplicates()
        dim_producto['producto_id'] = range(1, len(dim_producto) + 1)
        
        logger.info(f"✓ Dim_Producto creada: {len(dim_producto)} registros")
        return dim_producto[['producto_id', 'item_id', 'descripcion_item', 'partida', 'capitulo']]
    
    @staticmethod
    def create_dim_pais(df_items: pd.DataFrame) -> pd.DataFrame:
        """
        Crea tabla de dimensión País
        
        Args:
            df_items: DataFrame con datos de ítems
            
        Returns:
            DataFrame con dimensión País
        """
        logger.info("Creando Dim_Pais...")
        
        # Extraer países únicos (origen de la mercancía)
        paises_unicos = df_items[['pais_origen']].drop_duplicates().reset_index(drop=True)
        paises_unicos['pais_id'] = range(1, len(paises_unicos) + 1)
        paises_unicos = paises_unicos.rename(columns={'pais_origen': 'nombre_pais'})
        
        logger.info(f"✓ Dim_Pais creada: {len(paises_unicos)} registros")
        return paises_unicos[['pais_id', 'nombre_pais']]
    
    @staticmethod
    def create_dim_aduana(df_items: pd.DataFrame) -> pd.DataFrame:
        """
        Crea tabla de dimensión Aduana
        
        Args:
            df_items: DataFrame con datos de ítems
            
        Returns:
            DataFrame con dimensión Aduana
        """
        logger.info("Creando Dim_Aduana...")
        
        aduanas_unicas = df_items[['aduana']].drop_duplicates().reset_index(drop=True)
        aduanas_unicas['aduana_id'] = range(1, len(aduanas_unicas) + 1)
        aduanas_unicas = aduanas_unicas.rename(columns={'aduana': 'nombre_aduana'})
        
        logger.info(f"✓ Dim_Aduana creada: {len(aduanas_unicas)} registros")
        return aduanas_unicas[['aduana_id', 'nombre_aduana']]
    
    @staticmethod
    def create_dim_regimen(df_items: pd.DataFrame) -> pd.DataFrame:
        """
        Crea tabla de dimensión Régimen
        
        Args:
            df_items: DataFrame con datos de ítems
            
        Returns:
            DataFrame con dimensión Régimen
        """
        logger.info("Creando Dim_Regimen...")
        
        regimenes_unicos = df_items[['regimen']].drop_duplicates().reset_index(drop=True)
        regimenes_unicos['regimen_id'] = range(1, len(regimenes_unicos) + 1)
        regimenes_unicos = regimenes_unicos.rename(columns={'regimen': 'nombre_regimen'})
        
        logger.info(f"✓ Dim_Regimen creada: {len(regimenes_unicos)} registros")
        return regimenes_unicos[['regimen_id', 'nombre_regimen']]
    
    @staticmethod
    def create_dim_operacion(df_items: pd.DataFrame) -> pd.DataFrame:
        """
        Crea tabla de dimensión Operación
        
        Args:
            df_items: DataFrame con datos de ítems
            
        Returns:
            DataFrame con dimensión Operación
        """
        logger.info("Creando Dim_Operacion...")
        
        operaciones_unicas = df_items[['tipo_operacion']].drop_duplicates().reset_index(drop=True)
        operaciones_unicas['operacion_id'] = range(1, len(operaciones_unicas) + 1)
        operaciones_unicas = operaciones_unicas.rename(columns={'tipo_operacion': 'nombre_operacion'})
        
        logger.info(f"✓ Dim_Operacion creada: {len(operaciones_unicas)} registros")
        return operaciones_unicas[['operacion_id', 'nombre_operacion']]
    
    @staticmethod
    def create_fact_aduana_item(df_items: pd.DataFrame, 
                                dim_fecha: pd.DataFrame,
                                dim_producto: pd.DataFrame,
                                dim_pais: pd.DataFrame,
                                dim_aduana: pd.DataFrame,
                                dim_regimen: pd.DataFrame,
                                dim_operacion: pd.DataFrame) -> pd.DataFrame:
        """
        Crea tabla de hechos Fact_Aduana_Item
        
        Args:
            df_items: DataFrame con datos de ítems
            dim_*: DataFrames de dimensiones
            
        Returns:
            DataFrame con tabla de hechos
        """
        logger.info("Creando Fact_Aduana_Item...")
        
        fact = df_items.copy()
        
        # Merge con dimensiones para obtener IDs sustitutas
        fact = fact.merge(
            dim_fecha[['fecha_id', 'fecha']],
            left_on='fecha_operacion',
            right_on='fecha',
            how='left'
        )
        
        fact = fact.merge(
            dim_producto[['producto_id', 'item_id']],
            on='item_id',
            how='left'
        )
        
        fact = fact.merge(
            dim_pais[['pais_id', 'nombre_pais']],
            left_on='pais_origen',
            right_on='nombre_pais',
            how='left'
        )
        
        fact = fact.merge(
            dim_aduana[['aduana_id', 'nombre_aduana']],
            left_on='aduana',
            right_on='nombre_aduana',
            how='left'
        )
        
        fact = fact.merge(
            dim_regimen[['regimen_id', 'nombre_regimen']],
            left_on='regimen',
            right_on='nombre_regimen',
            how='left'
        )
        
        fact = fact.merge(
            dim_operacion[['operacion_id', 'nombre_operacion']],
            left_on='tipo_operacion',
            right_on='nombre_operacion',
            how='left'
        )
        
        # Seleccionar columnas de la tabla de hechos
        fact_aduana_item = fact[[
            'fecha_id',
            'producto_id',
            'pais_id',
            'aduana_id',
            'regimen_id',
            'operacion_id',
            'cantidad',
            'valor_cif',
            'valor_fob',
            'precio_unitario',
            'numero_declaracion',
            'numero_item'
        ]].copy()
        
        # Agregar fact_id
        fact_aduana_item.insert(0, 'fact_item_id', range(1, len(fact_aduana_item) + 1))
        
        logger.info(f"✓ Fact_Aduana_Item creada: {len(fact_aduana_item)} registros")
        return fact_aduana_item

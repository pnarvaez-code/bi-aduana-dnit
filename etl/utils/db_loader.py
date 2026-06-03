"""
Módulo para cargar datos a base de datos
"""

import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
import duckdb


class DatabaseLoader:
    """Cargador de datos a base de datos"""
    
    def __init__(self, db_type="duckdb", connection_params=None):
        """
        Inicializa el cargador
        
        Args:
            db_type: Tipo de base de datos ("duckdb" o "postgresql")
            connection_params: Parámetros de conexión
        """
        self.db_type = db_type
        self.connection_params = connection_params or {}
        self.engine = None
        self.conn = None
    
    def connect_duckdb(self, db_path: str):
        """Conecta a DuckDB"""
        try:
            self.conn = duckdb.connect(db_path)
            logger.info(f"✓ Conectado a DuckDB: {db_path}")
        except Exception as e:
            logger.error(f"✗ Error al conectar a DuckDB: {str(e)}")
            raise
    
    def connect_postgresql(self, host, port, database, user, password):
        """Conecta a PostgreSQL"""
        try:
            connection_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"
            self.engine = create_engine(connection_string)
            logger.info(f"✓ Conectado a PostgreSQL: {database}@{host}")
        except Exception as e:
            logger.error(f"✗ Error al conectar a PostgreSQL: {str(e)}")
            raise
    
    def execute_sql_file(self, sql_file: str):
        """
        Ejecuta un archivo SQL
        
        Args:
            sql_file: Ruta al archivo SQL
        """
        try:
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            if self.db_type == "duckdb":
                self.conn.execute(sql_content)
            else:
                with self.engine.connect() as conn:
                    conn.execute(text(sql_content))
                    conn.commit()
            
            logger.info(f"✓ SQL ejecutado: {sql_file}")
        except Exception as e:
            logger.error(f"✗ Error al ejecutar SQL {sql_file}: {str(e)}")
            raise
    
    def load_dataframe(self, df: pd.DataFrame, table_name: str, if_exists='replace'):
        """
        Carga un DataFrame a la base de datos
        
        Args:
            df: DataFrame a cargar
            table_name: Nombre de la tabla
            if_exists: Acción si la tabla existe ('replace', 'append', 'fail')
        """
        try:
            if self.db_type == "duckdb":
                if if_exists == 'replace':
                    self.conn.execute(f"DROP TABLE IF EXISTS {table_name}")
                
                self.conn.register(table_name, df)
                self.conn.execute(f"CREATE TABLE {table_name} AS SELECT * FROM {table_name}")
                logger.info(f"✓ {len(df)} filas cargadas a '{table_name}'")
            else:
                df.to_sql(table_name, self.engine, if_exists=if_exists, index=False)
                logger.info(f"✓ {len(df)} filas cargadas a '{table_name}'")
        except Exception as e:
            logger.error(f"✗ Error al cargar '{table_name}': {str(e)}")
            raise
    
    def load_parquet(self, parquet_file: str, table_name: str):
        """
        Carga un archivo Parquet a la base de datos
        
        Args:
            parquet_file: Ruta al archivo Parquet
            table_name: Nombre de la tabla
        """
        try:
            df = pd.read_parquet(parquet_file)
            self.load_dataframe(df, table_name)
            logger.info(f"✓ Parquet cargado: {parquet_file} → {table_name}")
        except Exception as e:
            logger.error(f"✗ Error al cargar Parquet {parquet_file}: {str(e)}")
            raise
    
    def query(self, sql: str) -> pd.DataFrame:
        """
        Ejecuta una consulta y retorna resultado como DataFrame
        
        Args:
            sql: Consulta SQL
            
        Returns:
            DataFrame con resultados
        """
        try:
            if self.db_type == "duckdb":
                result = self.conn.execute(sql).fetchall()
                columns = [desc[0] for desc in self.conn.description]
                return pd.DataFrame(result, columns=columns)
            else:
                return pd.read_sql(sql, self.engine)
        except Exception as e:
            logger.error(f"✗ Error al ejecutar query: {str(e)}")
            raise
    
    def close(self):
        """Cierra la conexión"""
        try:
            if self.conn:
                self.conn.close()
            if self.engine:
                self.engine.dispose()
            logger.info("✓ Conexión cerrada")
        except Exception as e:
            logger.error(f"✗ Error al cerrar conexión: {str(e)}")

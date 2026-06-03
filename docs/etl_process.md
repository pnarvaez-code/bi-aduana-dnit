# Proceso ETL - Data Warehouse Aduana DNIT

## 📋 Descripción General

El proceso ETL (Extracción, Transformación y Carga) automatiza la ingesta de datos desde archivos DNIT hasta el Data Warehouse analítico, garantizando calidad, validación e integridad en cada etapa.

---

## 🔄 Fases del ETL

```
INGESTA → LIMPIEZA → TRANSFORMACIÓN → CARGA → OLAP
├─ BRONZE  ├─ SILVER   ├─ GOLD        ├─ DWH   ├─ VISTAS
```

---

## FASE 1: INGESTA (BRONZE LAYER)

### Objetivo
Capturar datos originales sin transformar, manteniendo histórico completo.

### Entrada
- `data_lake/bronze/nivel_item.csv` - Operaciones a nivel de ítem
- `data_lake/bronze/nivel_subitem.xlsx` - Detalles de subitems

### Proceso
```python
# Lectura de archivos
loader = DataLoader()
df_items = loader.load_csv('nivel_item.csv')
df_subitems = loader.load_excel('nivel_subitem.xlsx')
```

### Validaciones
- ✅ Archivo existe y es accesible
- ✅ Formato correcto (CSV/XLSX)
- ✅ Codificación UTF-8
- ✅ Estructura de columnas válida

### Salida
- Archivos sin cambios en BRONZE
- Log de ingesta con timestamps
- Conteo de filas procesadas

### Resultado
```
✓ 500,000 filas - nivel_item.csv
✓ 150,000 filas - nivel_subitem.xlsx
```

---

## FASE 2: LIMPIEZA (SILVER LAYER)

### Objetivo
Asegurar calidad de datos y normalizaciones.

### Procesos

#### 2.1 Estandarización de Columnas
```python
df = cleaner.standardize_columns(df)
# Convierte:
# "Fecha Operación" → "fecha_operacion"
# "Valor CIF" → "valor_cif"
# "País-Origen" → "pais_origen"
```

**Reglas:**
- Lowercase
- Reemplaza espacios por guiones bajos
- Elimina caracteres especiales
- Sin tildes ni acentos

#### 2.2 Eliminación de Duplicados
```python
inicial = len(df)
df = df.drop_duplicates()
eliminados = inicial - len(df)
# Resultado: 2,500 duplicados encontrados
```

#### 2.3 Manejo de Valores Nulos
```python
# Reemplaza valores nulos
null_values = ["", "NULL", "N/A", "None", "nan"]
for val in null_values:
    df = df.replace(val, np.nan)

# Elimina columnas con >50% nulos
df = df.dropna(thresh=0.5)

# Rellena nulos críticos
df['pais'].fillna('DESCONOCIDO', inplace=True)
```

#### 2.4 Conversión de Tipos de Datos
```python
# Numéricos
numeric_cols = ['cantidad', 'valor_cif', 'valor_fob', 'precio_unitario']
df = cleaner.convert_numeric(df, numeric_cols)

# Fechas
date_cols = ['fecha_operacion']
df = cleaner.convert_dates(df, date_cols, format='%Y-%m-%d')

# Categorías
df['regimen'] = df['regimen'].astype('category')
```

#### 2.5 Limpieza de Espacios
```python
# Elimina espacios en blanco antes/después
df = df.apply(lambda x: x.str.strip() if isinstance(x, str) else x)
```

#### 2.6 Manejo de Outliers
```python
# Usa desviación estándar (3-sigma)
df = cleaner.remove_outliers(df, 
                             columns=['precio_unitario'],
                             std_threshold=3)
```

### Validaciones
- ✅ Tipos de datos correctos
- ✅ Rangos válidos (cantidad > 0, precios > 0)
- ✅ Fechas en rango válido (2020-2026)
- ✅ Países conocidos
- ✅ Aduanas válidas
- ✅ Regímenes reconocidos

### Reporte de Calidad
```
Total de filas: 500,000
Total de columnas: 45
Memoria usada: 250 MB

Por columna:
- cantidad: 500,000 válidas, 0 nulas
- valor_cif: 498,500 válidas, 1,500 nulas
- fecha_operacion: 500,000 válidas, 0 nulas
...
```

### Salida
- `data_lake/silver/item_limpio.parquet`
- `data_lake/silver/subitem_limpio.parquet`
- Log de limpieza con estadísticas

### Resultado
```
Estado inicial: 500,000 filas
Duplicados eliminados: 2,500
Outliers removidos: 150
Estado final: 497,350 filas (99.47% retención)
```

---

## FASE 3: TRANSFORMACIÓN (GOLD LAYER)

### Objetivo
Estructurar datos en esquema dimensional estrella.

### Procesos

#### 3.1 Creación de Dimensión Fecha
```python
dim_fecha = transformer.create_dim_fecha(
    start_year=2020, 
    end_year=2026
)
# Resultado: 2,557 registros (1 por día)
```

**Campos generados:**
- fecha_id (1-2557)
- fecha (dates)
- año, mes, trimestre, semana
- nombre_mes, nombre_día
- es_fin_semana, es_feriado

#### 3.2 Creación de Dimensión Producto
```python
dim_producto = transformer.create_dim_producto(df_items)
# Extrae valores únicos de item_id, descripción, partida, capítulo
# Resultado: ~3,500 productos únicos
```

**Mapeo:**
```
item_id → producto_id (sustituta)
```

#### 3.3 Creación de Dimensión País
```python
dim_pais = transformer.create_dim_pais(df_items)
# Extrae valores únicos de pais_origen
# Resultado: ~180 países
```

#### 3.4 Creación de Dimensión Aduana
```python
dim_aduana = transformer.create_dim_aduana(df_items)
# Extrae aduanas del país
# Resultado: ~12 aduanas
```

#### 3.5 Creación de Dimensión Régimen
```python
dim_regimen = transformer.create_dim_regimen(df_items)
# Extrae regímenes aduanales
# Resultado: ~8 regímenes
```

#### 3.6 Creación de Dimensión Operación
```python
dim_operacion = transformer.create_dim_operacion(df_items)
# Extrae tipos de operación
# Resultado: 3 operaciones (importación, exportación, tránsito)
```

#### 3.7 Creación de Tabla de Hechos
```python
fact_item = transformer.create_fact_aduana_item(
    df_items_clean,
    dim_fecha,
    dim_producto,
    dim_pais,
    dim_aduana,
    dim_regimen,
    dim_operacion
)
```

**Proceso:**
1. Para cada registro en items_limpio
2. Busca fecha_operacion en Dim_Fecha → obtiene fecha_id
3. Busca item_id en Dim_Producto → obtiene producto_id
4. Busca pais_origen en Dim_País → obtiene pais_id
5. Busca aduana en Dim_Aduana → obtiene aduana_id
6. Busca régimen en Dim_Régimen → obtiene regimen_id
7. Busca operación en Dim_Operación → obtiene operacion_id
8. Crea registro de hecho con todas las claves sustitutas

### Validaciones Dimensionales
- ✅ Todas las claves sustitutas son validas
- ✅ Sin huérfanos (facts sin dimensión)
- ✅ Medidas son no-negativas
- ✅ Integridad referencial garantizada

### Salida (Parquet comprimido)
- `data_lake/gold/dim_fecha.parquet`
- `data_lake/gold/dim_producto.parquet`
- `data_lake/gold/dim_pais.parquet`
- `data_lake/gold/dim_aduana.parquet`
- `data_lake/gold/dim_regimen.parquet`
- `data_lake/gold/dim_operacion.parquet`
- `data_lake/gold/fact_aduana_item.parquet`

### Resultado
```
Dimensiones creadas:
✓ Dim_Fecha: 2,557 registros
✓ Dim_Producto: 3,500 registros
✓ Dim_País: 180 registros
✓ Dim_Aduana: 12 registros
✓ Dim_Régimen: 8 registros
✓ Dim_Operación: 3 registros

Hechos creados:
✓ Fact_Aduana_Item: 497,350 registros
```

---

## FASE 4: CARGA (DATA WAREHOUSE)

### Objetivo
Cargar datos estructurados en base de datos para análisis.

### Configuración
```python
# Opción 1: DuckDB (recomendado para laboratorio)
db_loader = DatabaseLoader(db_type="duckdb")
db_loader.connect_duckdb("data_lake/gold/aduana.duckdb")

# Opción 2: PostgreSQL (entorno empresarial)
db_loader = DatabaseLoader(db_type="postgresql")
db_loader.connect_postgresql(
    host="localhost",
    port=5432,
    database="aduana_bi",
    user="postgres",
    password="***"
)
```

### Proceso de Carga
```python
# 1. Crear esquema
db_loader.execute_sql_file("sql/01_schema_setup.sql")

# 2. Cargar dimensiones
for dim_name, dim_df in [
    ('dim_fecha', dim_fecha),
    ('dim_producto', dim_producto),
    ('dim_pais', dim_pais),
    ('dim_aduana', dim_aduana),
    ('dim_regimen', dim_regimen),
    ('dim_operacion', dim_operacion),
]:
    db_loader.load_dataframe(dim_df, dim_name)

# 3. Cargar tabla de hechos
db_loader.load_dataframe(fact_item, 'fact_aduana_item')

# 4. Crear índices
db_loader.execute_sql_file("sql/04_indexes.sql")

# 5. Crear vistas OLAP
db_loader.execute_sql_file("sql/05_olap_views.sql")
```

### Validaciones Post-Carga
```sql
-- Verificar integridad
SELECT COUNT(*) FROM fact_aduana_item;  -- 497,350
SELECT COUNT(DISTINCT fecha_id) FROM fact_aduana_item;  -- <2,557
SELECT COUNT(DISTINCT pais_id) FROM fact_aduana_item;   -- <180

-- Buscar huérfanos (no debería haber)
SELECT * FROM fact_aduana_item f
WHERE f.pais_id NOT IN (SELECT pais_id FROM dim_pais);  -- 0 filas
```

### Resultado
```
Dimensiones cargadas:
✓ dim_fecha: 2,557 registros
✓ dim_producto: 3,500 registros
✓ dim_pais: 180 registros
✓ dim_aduana: 12 registros
✓ dim_regimen: 8 registros
✓ dim_operacion: 3 registros

Hechos cargados:
✓ fact_aduana_item: 497,350 registros

Total de tablas: 7
Total de registros: 509,408
Índices creados: 12+
Vistas OLAP: 20+
```

---

## FASE 5: ANÁLISIS OLAP

### Vistas Analíticas Creadas

#### Análisis Temporales
- `vw_operaciones_mensuales` - Evolución por mes
- `vw_tendencia_anual` - Tendencias anuales
- `vw_estacionalidad_trimestre` - Patrones por trimestre

#### Análisis Geográficos
- `vw_paises_mayor_volumen` - Top países
- `vw_concentracion_paises` - Distribución de importaciones
- `vw_paises_por_operacion` - Países por tipo

#### Análisis de Productos
- `vw_productos_mayor_cif` - Top productos
- `vw_categorias_productos` - Análisis por capítulo
- `vw_diversificacion_productos` - Variedad de productos

#### Análisis Operativos
- `vw_volumen_por_aduana` - Performance de aduanas
- `vw_eficiencia_regimen` - Análisis por régimen
- `vw_relacion_cif_fob` - Análisis de márgenes

### Ejemplo de Consulta OLAP
```sql
-- ¿Cuál es la evolución mensual de importaciones de Brasil?
SELECT 
    df.año,
    df.mes,
    df.nombre_mes,
    SUM(f.valor_cif) as total_cif
FROM fact_aduana_item f
JOIN dim_fecha df ON f.fecha_id = df.fecha_id
JOIN dim_pais dp ON f.pais_id = dp.pais_id
WHERE dp.nombre_pais = 'Brasil'
    AND do.nombre_operacion = 'Importación'
GROUP BY df.año, df.mes, df.nombre_mes
ORDER BY df.año, df.mes;
```

---

## 🛠️ Ejecución del ETL

### Instalación de Dependencias
```bash
pip install -r requirements.txt
```

### Ejecución
```bash
python etl/etl_aduana.py
```

### Output Esperado
```
================================================================================
INICIANDO ETL - DATOS ADUANA DNIT
================================================================================

[PASO 1] INGESTA DE DATOS (BRONZE LAYER)
--------
Cargando archivo de ítems...
✓ CSV cargado: 500,000 filas, 45 columnas

Cargando archivo de subitems...
✓ Excel cargado: 150,000 filas, 30 columnas

[PASO 2] LIMPIEZA Y NORMALIZACIÓN (SILVER LAYER)
--------
Limpiando datos de ítems...
Iniciando limpieza de datos...
✓ Filas completamente nulas eliminadas: 0
✓ Filas duplicadas eliminadas: 2,500
✓ Columnas estandarizadas: 45
✓ Datos de ítems limpios guardados: data_lake/silver/item_limpio.parquet

[PASO 3] TRANSFORMACIÓN A ESQUEMA DIMENSIONAL (GOLD LAYER)
--------
Creando Dim_Fecha...
✓ Dim_Fecha creada: 2,557 registros

Creando Dim_Producto...
✓ Dim_Producto creada: 3,500 registros

... (más dimensiones)

[PASO 4] CARGA A BASE DE DATOS
--------
Cargando dimensiones...
✓ 2,557 filas cargadas a 'dim_fecha'
✓ 3,500 filas cargadas a 'dim_producto'
... (más dimensiones)

Cargando tabla de hechos...
✓ 497,350 filas cargadas a 'fact_aduana_item'

Creando índices y vistas...
✓ SQL ejecutado: sql/04_indexes.sql
✓ SQL ejecutado: sql/05_olap_views.sql

================================================================================
ETL COMPLETADO EXITOSAMENTE
================================================================================
✓ Datos cargados en: data_lake/gold/aduana.duckdb
✓ Tabla de hechos: 497,350 registros
✓ Dimensiones creadas: 6
✓ Log guardado en: etl/logs/etl.log
================================================================================
```

---

## 📊 Monitoreo y Logs

### Archivo de Log
- **Ubicación:** `etl/logs/etl.log`
- **Formato:** ISO 8601 con timestamps
- **Niveles:** INFO, WARNING, ERROR

### Ejemplo de Log
```
2026-06-03 14:30:15 | INFO    | Cargando CSV: data_lake/bronze/nivel_item.csv
2026-06-03 14:30:20 | INFO    | ✓ CSV cargado: 500,000 filas, 45 columnas
2026-06-03 14:30:21 | INFO    | Iniciando limpieza de datos...
2026-06-03 14:30:25 | WARNING | ⚠ Columna 'precio_unitario': 150 valores no convertibles
2026-06-03 14:30:30 | INFO    | ✓ Filas duplicadas eliminadas: 2,500
```

---

## ⚙️ Configuración Avanzada

### Variables de Entorno (.env)
```bash
DB_TYPE=duckdb
DUCKDB_PATH=data_lake/gold/aduana.duckdb
LOG_LEVEL=INFO
CHUNK_SIZE=50000
```

### Parámetros de Ejecución
```python
# config.py
ENCODING = "utf-8"              # Codificación de archivos
CHUNK_SIZE = 50000              # Procesar en chunks de 50K filas
DATE_FORMAT = "%Y-%m-%d"        # Formato de fechas
NULL_VALUES = ["", "NULL", ...]  # Valores considerados nulos
```

---

## 🔍 Troubleshooting

### Problema: "File not found"
**Solución:** Verificar ruta en config.py y que archivos existan en bronze

### Problema: "Connection refused"
**Solución:** Si usa PostgreSQL, verificar que servidor esté corriendo

### Problema: "Out of memory"
**Solución:** Aumentar CHUNK_SIZE o usar máquina con más RAM

### Problema: "Type conversion error"
**Solución:** Revisar log y aplicar validación manual en datos fuente

---

## 📈 Rendimiento

| Operación | Tiempo | Registros |
|-----------|--------|-----------|
| Ingesta | ~2 min | 500K |
| Limpieza | ~3 min | 497K |
| Transformación | ~5 min | 497K hechos |
| Carga | ~2 min | 509K total |
| **Total** | **~12 min** | **~500K** |

---

## ✅ Checklist de Validación

Antes de considerar ETL como exitoso:

- [ ] Todos los pasos completados sin errores
- [ ] Logs sin mensajes de error crítico
- [ ] Cantidad de registros de salida >= entrada (con tolerancia)
- [ ] No hay huérfanos en tabla de hechos
- [ ] Todas las claves sustitutas son válidas
- [ ] Vistas OLAP se crean correctamente
- [ ] Base de datos tiene 7 tablas + 20+ vistas
- [ ] Queries de muestra devuelven resultados esperados


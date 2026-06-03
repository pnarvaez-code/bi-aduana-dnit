# BI Aduana DNIT - Trabajo Final de Inteligencia de Negocios

**Carrera:** Ingeniería en Sistemas  
**Institución:** Universidad Columbia del Paraguay  
**Materia:** Inteligencia de Negocios (BI)  
**Estudiante:** Pedro Pablo Narváez Benitez
**Año:** 2026  

---

## 📋 Descripción del Proyecto

Desarrollo de una solución completa de **Inteligencia de Negocios (BI)** utilizando datos reales de la **DNIT (Aduana del Paraguay)**, que incluye:

- ✅ Data Lake estructurado (Bronze/Silver/Gold)
- ✅ Data Warehouse con esquema estrella
- ✅ ETL desarrollado en Python
- ✅ Estructuras OLAP para análisis multidimensional
- ✅ Dashboard interactivo en Power BI
- ✅ Análisis estratégicos y conclusiones

---

## 🎯 Objetivos

1. **Construcción de Data Lake:** Organizar datos crudos, limpios y procesados
2. **Diseño de DWH:** Implementar modelo dimensional en esquema estrella
3. **Desarrollo ETL:** Automatizar ingesta, transformación y carga de datos
4. **Análisis OLAP:** Estructuras analíticas multidimensionales
5. **Visualización:** Dashboard ejecutivo con KPIs y análisis

---

## 📁 Estructura del Proyecto

```
bi-aduana-dnit/
├── README.md                          # Este archivo
├── .gitignore                         # Ignora archivos locales
├── requirements.txt                   # Dependencias Python
├── config.py                          # Configuración global
│
├── data_lake/                         # Data Lake estructurado
│   ├── bronze/                        # Datos originales (sin modificar)
│   │   ├── nivel_item.csv
│   │   └── nivel_subitem.xlsx
│   ├── silver/                        # Datos limpios y normalizados
│   │   ├── item_limpio.parquet
│   │   └── subitem_limpio.parquet
│   └── gold/                          # Datos estructurados para análisis
│       ├── fact_aduana_item.parquet
│       └── fact_aduana_subitem.parquet
│
├── etl/                               # Scripts ETL
│   ├── etl_aduana.py                  # Script principal ETL
│   ├── config.py                      # Configuración ETL
│   ├── utils/
│   │   ├── data_loader.py             # Lectura de archivos
│   │   ├── data_cleaner.py            # Limpieza de datos
│   │   ├── data_transformer.py        # Transformaciones
│   │   └── db_loader.py               # Carga a base de datos
│   └── logs/
│       └── etl.log                    # Log de ejecución
│
├── sql/                               # Scripts SQL
│   ├── 01_schema_setup.sql            # Creación de esquema
│   ├── 02_dim_tables.sql              # Tablas de dimensiones
│   ├── 03_fact_tables.sql             # Tablas de hechos
│   ├── 04_indexes.sql                 # Índices y constraints
│   ├── 05_olap_views.sql              # Vistas OLAP
│   ├── 06_sample_queries.sql          # Consultas de muestra
│   └── dictionary/
│       └── data_dictionary.md         # Diccionario de datos
│
├── notebooks/                         # Jupyter Notebooks
│   ├── 01_exploratory_analysis.ipynb  # Análisis exploratorio
│   ├── 02_data_quality.ipynb          # Validación de datos
│   └── 03_olap_analysis.ipynb         # Análisis OLAP
│
├── docs/                              # Documentación
│   ├── arquitectura.md                # Arquitectura del sistema
│   ├── modelo_datos.md                # Modelo de datos
│   ├── etl_process.md                 # Proceso ETL
│   ├── olap_cubes.md                  # Cubos OLAP
│   └── analisis_resultados.md         # Análisis y conclusiones
│
└── power_bi/                          # Visualización
    ├── dashboard_aduana.pbix          # Dashboard Power BI
    └── README_POWERBI.md              # Guía de uso

```

---

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|-----------|----------|
| **Lenguaje ETL** | Python 3.8+ |
| **Base de Datos** | DuckDB o PostgreSQL |
| **Transformación de Datos** | Pandas, NumPy |
| **SQL** | ANSI SQL estándar |
| **Visualización** | Power BI Desktop |
| **Control de Versiones** | Git & GitHub |

---

## 📦 Dependencias Python

```bash
pandas==2.0.0
numpy==1.24.0
duckdb==0.8.0
sqlalchemy==2.0.0
psycopg==3.1.0
openpyxl==3.10.0
python-dotenv==1.0.0
loguru==0.7.0
```

---

## 🚀 Inicio Rápido

### 1. Clonar el repositorio
```bash
git clone https://github.com/pnarvaez-code/bi-aduana-dnit.git
cd bi-aduana-dnit
```

### 2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos
Editar `config.py` con los parámetros de conexión:
```python
DB_TYPE = "duckdb"  # o "postgresql"
DB_PATH = "data/aduana.duckdb"
```

### 5. Ejecutar ETL
```bash
python etl/etl_aduana.py
```

### 6. Abrir Power BI
Abrir `power_bi/dashboard_aduana.pbix` en Power BI Desktop

---

## 📊 Análisis Obligatorios

### Temporales (5+)
- Evolución de operaciones mensuales/anuales
- Tendencias de importación/exportación
- Estacionalidad por período

### Geográficos (5+)
- Países con mayor volumen de operaciones
- Distribución de importaciones por país
- Ranking de países por valor CIF/FOB

### Por Producto (5+)
- Productos con mayor valor CIF
- Categorías más importadas
- Análisis de diversificación

### Operativos (5+)
- Volumen por aduana
- Eficiencia por régimen aduanal
- Relación CIF vs FOB

---

## 📈 Modelo de Datos - Esquema Estrella

### Tablas de Hechos
- **Fact_Aduana_Item:** Hechos a nivel de ítem
- **Fact_Aduana_Subitem:** Hechos a nivel de subítem

### Dimensiones
- **Dim_Fecha:** Calendario (año, mes, trimestre, semana)
- **Dim_Producto:** Información de productos/ítems
- **Dim_Pais:** Países de origen/destino
- **Dim_Aduana:** Aduanas del país
- **Dim_Regimen:** Regímenes aduanales
- **Dim_Operacion:** Tipos de operación

---

## 📋 Checklist de Entregables

- [ ] Data Lake (Bronze/Silver/Gold)
- [ ] Scripts SQL (Esquema Estrella)
- [ ] ETL en Python (completo y funcional)
- [ ] Consultas OLAP (vistas analíticas)
- [ ] Dashboard Power BI
- [ ] Análisis estratégicos
- [ ] Documento final (PDF/Word)
- [ ] Código limpio y documentado
- [ ] Manejo de errores en ETL
- [ ] Insights reales y concluyentes

---

## 👤 Autor

**Pedro Pablo Narváez Benitez**  
Ingeniería en Sistemas - Universidad Columbia del Paraguay  
2026

---

## 📝 Licencia

MIT License - Proyecto académico

---

## 📞 Contacto

Para preguntas o sugerencias sobre este proyecto, contactar al autor.

---

**Estado del Proyecto:** 🚀 En Desarrollo

Última actualización: Junio 2026

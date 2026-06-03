-- ============================================================================
-- ESQUEMA DE BASE DE DATOS - DATA WAREHOUSE ADUANA DNIT
-- ============================================================================
-- Script para crear el esquema dimensional en formato estrella
-- Soporta DuckDB y PostgreSQL
-- ============================================================================

-- Dimensión Fecha
CREATE TABLE IF NOT EXISTS dim_fecha (
    fecha_id INTEGER PRIMARY KEY,
    fecha DATE NOT NULL,
    año INTEGER NOT NULL,
    mes INTEGER NOT NULL,
    trimestre INTEGER NOT NULL,
    semana INTEGER NOT NULL,
    dia_semana INTEGER NOT NULL,
    nombre_mes VARCHAR(20) NOT NULL,
    nombre_dia VARCHAR(10) NOT NULL,
    es_fin_semana BOOLEAN NOT NULL,
    es_feriado BOOLEAN NOT NULL
);

-- Dimensión Producto
CREATE TABLE IF NOT EXISTS dim_producto (
    producto_id INTEGER PRIMARY KEY,
    item_id VARCHAR(50) NOT NULL,
    descripcion_item VARCHAR(500) NOT NULL,
    partida VARCHAR(10),
    capitulo VARCHAR(10)
);

-- Dimensión País
CREATE TABLE IF NOT EXISTS dim_pais (
    pais_id INTEGER PRIMARY KEY,
    nombre_pais VARCHAR(100) NOT NULL UNIQUE
);

-- Dimensión Aduana
CREATE TABLE IF NOT EXISTS dim_aduana (
    aduana_id INTEGER PRIMARY KEY,
    nombre_aduana VARCHAR(100) NOT NULL UNIQUE
);

-- Dimensión Régimen
CREATE TABLE IF NOT EXISTS dim_regimen (
    regimen_id INTEGER PRIMARY KEY,
    nombre_regimen VARCHAR(100) NOT NULL UNIQUE
);

-- Dimensión Operación
CREATE TABLE IF NOT EXISTS dim_operacion (
    operacion_id INTEGER PRIMARY KEY,
    nombre_operacion VARCHAR(100) NOT NULL UNIQUE
);

-- Tabla de Hechos: Aduana Item
CREATE TABLE IF NOT EXISTS fact_aduana_item (
    fact_item_id INTEGER PRIMARY KEY,
    fecha_id INTEGER NOT NULL,
    producto_id INTEGER NOT NULL,
    pais_id INTEGER NOT NULL,
    aduana_id INTEGER NOT NULL,
    regimen_id INTEGER NOT NULL,
    operacion_id INTEGER NOT NULL,
    cantidad DECIMAL(18, 4) NOT NULL,
    valor_cif DECIMAL(18, 2) NOT NULL,
    valor_fob DECIMAL(18, 2) NOT NULL,
    precio_unitario DECIMAL(18, 4),
    numero_declaracion VARCHAR(50),
    numero_item VARCHAR(10)
);

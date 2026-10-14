import unicodedata
import pandas as pd

# 1. Cargar los archivos CSV
df_atenciones = pd.read_csv('atenciones_por_tipo.csv')
df_uv = pd.read_csv('unidades_vecinales.csv')
df_comunas = pd.read_csv('info_comunas_chile.csv')


def normalize_text(text: str) -> str:
    """Normaliza texto eliminando acentos, espacios extra y pasando a minusculas."""
    if not isinstance(text, str):
        return ""
    clean = unicodedata.normalize('NFD', text)
    clean = ''.join(c for c in clean if unicodedata.category(c) != 'Mn')
    return clean.strip().lower()


# 2. Función de mapeo integral: Comuna/Región/Provincia -> Servicio de Salud oficial (MINSAL)
def comuna_a_servicio_salud(region: str, provincia: str, comuna: str) -> str:
    com_clean = normalize_text(comuna)
    reg_clean = normalize_text(region)
    prov_clean = normalize_text(provincia)

    if 'arica' in reg_clean:
        return 'Arica'
    elif 'tarapaca' in reg_clean:
        return 'Iquique'
    elif 'antofagasta' in reg_clean:
        return 'Antofagasta'
    elif 'atacama' in reg_clean:
        return 'Atacama'
    elif 'coquimbo' in reg_clean:
        return 'Coquimbo'
    elif "o'higgins" in reg_clean or 'ohiggins' in reg_clean:
        return "O'Higgins"
    elif 'maule' in reg_clean:
        return 'Maule'
    elif 'nuble' in reg_clean:
        return 'Ñuble'
    elif 'los rios' in reg_clean:
        return 'Valdivia'
    elif 'aysen' in reg_clean:
        return 'Aisén'
    elif 'magallanes' in reg_clean:
        return 'Magallanes'
    elif 'araucania' in reg_clean:
        return 'Araucanía Norte' if prov_clean == 'malleco' else 'Araucanía Sur'
    elif 'los lagos' in reg_clean:
        if prov_clean == 'osorno':
            return 'Osorno'
        elif 'chilo' in prov_clean:
            return 'Chiloé'
        else:
            return 'Del Reloncaví'
    elif 'biobio' in reg_clean:
        if prov_clean == 'arauco':
            return 'Arauco'
        elif prov_clean == 'biobio':
            return 'Biobío'
        else:
            return 'Talcahuano' if com_clean in ['talcahuano', 'hualpen', 'penco', 'tome'] else 'Concepción'
    elif 'valparaiso' in reg_clean:
        if prov_clean in ['san felipe', 'los andes']:
            return 'Aconcagua'
        elif prov_clean in ['quillota', 'petorca', 'marga marga']:
            return 'Viña del Mar Quillota'
        elif prov_clean in ['san antonio', 'isla de pascua']:
            return 'Valparaíso San Antonio'
        elif prov_clean == 'valparaiso':
            return 'Viña del Mar Quillota' if com_clean in ['vina del mar', 'concon', 'puchuncavi', 'quintero'] else 'Valparaíso San Antonio'
    elif 'metropolitana' in reg_clean:
        if prov_clean == 'chacabuco':
            return 'Metropolitano Norte'
        elif prov_clean == 'cordillera':
            return 'Metropolitano Sur Oriente'
        elif prov_clean == 'maipo':
            return 'Metropolitano Sur'
        elif prov_clean in ['melipilla', 'talagante']:
            return 'Metropolitano Occidente'
        elif prov_clean == 'santiago':
            if com_clean in ['huechuraba', 'independencia', 'recoleta', 'conchali', 'quilicura']:
                return 'Metropolitano Norte'
            elif com_clean in ['santiago', 'cerrillos', 'estacion central', 'maipu', 'pedro aguirre cerda']:
                return 'Metropolitano Central'
            elif com_clean in ['cerro navia', 'lo prado', 'pudahuel', 'quinta normal', 'renca']:
                return 'Metropolitano Occidente'
            elif com_clean in ['providencia', 'las condes', 'vitacura', 'lo barnechea', 'la reina', 'nunoa', 'macul', 'penalolen']:
                return 'Metropolitano Oriente'
            elif com_clean in ['san miguel', 'la cisterna', 'san ramon', 'la granja', 'el bosque', 'lo espejo', 'san joaquin']:
                return 'Metropolitano Sur'
            elif com_clean in ['la florida', 'la pintana']:
                return 'Metropolitano Sur Oriente'
    return None


# 3. Mapear todas las comunas a su Servicio de Salud oficial
df_comunas['comuna_norm'] = df_comunas['comuna'].apply(normalize_text)
df_comunas['servicio_salud'] = df_comunas.apply(
    lambda r: comuna_a_servicio_salud(r['region'], r['provincia'], r['comuna']),
    axis=1
)

# Diccionario unificado para mapear cualquier comuna a su SS sin riesgo de inconsistencias
comuna_to_ss = dict(zip(df_comunas['comuna_norm'], df_comunas['servicio_salud']))

# 4. Mapear cada unidad vecinal a su Servicio de Salud
df_uv['comuna_norm'] = df_uv['NOMBRE COMUNA'].apply(normalize_text)
df_uv['servicio_salud'] = df_uv['comuna_norm'].map(comuna_to_ss)

# Identificar que comunas cuentan con datos de unidades vecinales
comunas_uv_set = set(df_uv['comuna_norm'].unique())
df_comunas['en_uv'] = df_comunas['comuna_norm'].isin(comunas_uv_set)

# 5. Agrupar la superficie de áreas verdes (m² y hectáreas) y cantidad de UVs por Servicio de Salud
areas_verdes_ss = df_uv.groupby('servicio_salud').agg(
    total_area_verde_m2=('ÁREA VERDE', 'sum'),
    total_unidades_vecinales=('ID_UNIDAD_VECINAL', 'count'),
    comunas_con_datos=('NOMBRE COMUNA', 'nunique')
).reset_index()

areas_verdes_ss['total_area_verde_ha'] = areas_verdes_ss['total_area_verde_m2'] / 10000.0

# 6. Agrupar metricas comunales y demograficas por Servicio de Salud
superficie_ss = df_comunas.groupby('servicio_salud').agg(
    total_habitantes=('habitantes', 'sum'),
    habitantes_comunas_con_datos=('habitantes', lambda s: s[df_comunas.loc[s.index, 'en_uv']].sum()),
    superficie_total_km2=('superficie_km2', 'sum'),
    superficie_comunas_con_datos_km2=('superficie_km2', lambda s: s[df_comunas.loc[s.index, 'en_uv']].sum()),
    total_comunas=('comuna', 'count')
).reset_index()

# 7. Obtener la lista de Servicios de Salud unicos (omitiendo 'SNSS' que representa el total nacional)
servicios_salud_df = df_atenciones[df_atenciones['servicio_salud'] != 'SNSS'][['servicio_salud']].drop_duplicates()

# 8. Fusionar para obtener la tabla final por Servicio de Salud
df_resultado = pd.merge(servicios_salud_df, areas_verdes_ss, on='servicio_salud', how='left')
df_resultado = pd.merge(df_resultado, superficie_ss, on='servicio_salud', how='left')

# 9. Calcular indicadores:
# a) m² por habitante en comunas censadas en UV (estandar OMS / urbanismo, libre de dilucion rural)
df_resultado['m2_hab_comunas_con_datos'] = (
    df_resultado['total_area_verde_m2'] / df_resultado['habitantes_comunas_con_datos']
)

# b) m² por habitante sobre la poblacion total del servicio de salud
df_resultado['m2_hab_total_servicio'] = (
    df_resultado['total_area_verde_m2'] / df_resultado['total_habitantes']
)

# c) Porcentaje territorial sobre superficie geografica total (para compatibilidad previa)
df_resultado['pct_area_verde'] = (
    df_resultado['total_area_verde_m2'] / (df_resultado['superficie_total_km2'] * 1000000.0)
) * 100.0

# d) Porcentaje territorial sobre superficie de comunas censadas
df_resultado['pct_area_verde_comunas_con_datos'] = (
    df_resultado['total_area_verde_m2'] / (df_resultado['superficie_comunas_con_datos_km2'] * 1000000.0)
) * 100.0

# Reordenar columnas segun relevancia analitica
cols_orden = [
    'servicio_salud',
    'm2_hab_comunas_con_datos',
    'm2_hab_total_servicio',
    'pct_area_verde',
    'pct_area_verde_comunas_con_datos',
    'total_area_verde_ha',
    'total_area_verde_m2',
    'habitantes_comunas_con_datos',
    'total_habitantes',
    'superficie_comunas_con_datos_km2',
    'superficie_total_km2',
    'comunas_con_datos',
    'total_comunas',
    'total_unidades_vecinales'
]
df_resultado = df_resultado[cols_orden]

# Ordenar por defecto de mayor a menor m² de area verde por habitante censado
df_resultado = df_resultado.sort_values(by='m2_hab_comunas_con_datos', ascending=False).reset_index(drop=True)

# 10. Guardar el resultado en el CSV
df_resultado.to_csv('areas_verdes_por_servicio_salud.csv', index=False)
print(f"Generado areas_verdes_por_servicio_salud.csv con {len(df_resultado)} servicios de salud.")

import pandas as pd

# 1. Cargar los archivos CSV
df_atenciones = pd.read_csv('atenciones_por_tipo.csv')
df_uv = pd.read_csv('unidades_vecinales.csv')

# 2. Diccionario de mapeo: Comuna -> Servicio de Salud
comuna_a_ss = {
    # Arica y Parinacota / Tarapacá / Antofagasta / Atacama / Coquimbo
    'ARICA': 'Arica', 'PUTRE': 'Arica',
    'IQUIQUE': 'Iquique', 'ALTO HOSPICIO': 'Iquique', 'POZO ALMONTE': 'Iquique',
    'ANTOFAGASTA': 'Antofagasta', 'CALAMA': 'Antofagasta', 'TOCOPILLA': 'Antofagasta',
    'COPIAPO': 'Atacama', 'VALLENAR': 'Atacama', 'CHAÑARAL': 'Atacama',
    'LA SERENA': 'Coquimbo', 'COQUIMBO': 'Coquimbo', 'OVALLE': 'Coquimbo', 'ILLAPEL': 'Coquimbo',
    
    # Valparaíso
    'VALPARAÍSO': 'Valparaíso San Antonio', 'SAN ANTONIO': 'Valparaíso San Antonio', 'ISLA DE PASCUA': 'Valparaíso San Antonio',
    'VIÑA DEL MAR': 'Viña del Mar Quillota', 'CONCÓN': 'Viña del Mar Quillota', 
    'QUILPUE': 'Viña del Mar Quillota', 'VILLA ALEMANA': 'Viña del Mar Quillota', 
    'QUILLOTA': 'Viña del Mar Quillota', 'LA LIGUA': 'Viña del Mar Quillota',
    'SAN FELIPE': 'Aconcagua', 'LOS ANDES': 'Aconcagua',
    
    # Región Metropolitana
    'INDEPENDENCIA': 'Metropolitano Norte', 'RECOLETA': 'Metropolitano Norte', 
    'CONCHALÍ': 'Metropolitano Norte', 'HUECHURABA': 'Metropolitano Norte', 
    'QUILICURA': 'Metropolitano Norte', 'COLINA': 'Metropolitano Norte', 'LAMPA': 'Metropolitano Norte',
    
    'SANTIAGO': 'Metropolitano Central', 'CERRILLOS': 'Metropolitano Central', 
    'ESTACION CENTRAL': 'Metropolitano Central', 'MAIPU': 'Metropolitano Central', 
    'PEDRO AGUIRRE CERDA': 'Metropolitano Central',
    
    'CERRO NAVIA': 'Metropolitano Occidente', 'LO PRADO': 'Metropolitano Occidente', 
    'PUDAHUEL': 'Metropolitano Occidente', 'QUINTA NORMAL': 'Metropolitano Occidente', 
    'RENCA': 'Metropolitano Occidente', 'PADRE HURTADO': 'Metropolitano Occidente', 
    'PENAFLOR': 'Metropolitano Occidente', 'MELIPILLA': 'Metropolitano Occidente', 
    'TALAGANTE': 'Metropolitano Occidente',
    
    'PROVIDENCIA': 'Metropolitano Oriente', 'LAS CONDES': 'Metropolitano Oriente', 
    'VITACURA': 'Metropolitano Oriente', 'LO BARNECHEA': 'Metropolitano Oriente', 
    'LA REINA': 'Metropolitano Oriente', 'NUNOA': 'Metropolitano Oriente', 
    'MACUL': 'Metropolitano Oriente', 'PENALOLEN': 'Metropolitano Oriente',
    
    'SAN MIGUEL': 'Metropolitano Sur', 'LA CISTERNA': 'Metropolitano Sur', 
    'SAN RAMÓN': 'Metropolitano Sur', 'LA GRANJA': 'Metropolitano Sur', 
    'EL BOSQUE': 'Metropolitano Sur', 'SAN BERNARDO': 'Metropolitano Sur', 
    'LO ESPEJO': 'Metropolitano Sur', 'SAN JOAQUIN': 'Metropolitano Sur',
    
    'PUENTE ALTO': 'Metropolitano Sur Oriente', 'PIRQUE': 'Metropolitano Sur Oriente', 
    'SAN JOSÉ DE MAIPO': 'Metropolitano Sur Oriente', 'LA FLORIDA': 'Metropolitano Sur Oriente', 
    'LA PINTANA': 'Metropolitano Sur Oriente',
    
    # Zona Sur y Austral
    'RANCAGUA': "O'Higgins", 'REQUINOA': "O'Higgins", 'MACHALÍ': "O'Higgins", 
    'PICHILEMU': "O'Higgins", 'OLIVAR': "O'Higgins", 'SAN FERNANDO': "O'Higgins",
    
    'TALCA': 'Maule', 'MAULE': 'Maule', 'CAUQUENES': 'Maule', 'LINARES': 'Maule', 'CURICO': 'Maule',
    'CHILLAN': 'Ñuble', 'CHILLAN VIEJO': 'Ñuble', 'QUIRIHUE': 'Ñuble', 'SAN CARLOS': 'Ñuble',
    
    'CONCEPCIÓN': 'Concepción', 'CHIGUAYANTE': 'Concepción', 'SAN PEDRO DE LA PAZ': 'Concepción', 'CORONEL': 'Concepción',
    'TALCAHUANO': 'Talcahuano', 'HUALPEN': 'Talcahuano', 'PENCO': 'Talcahuano',
    'LEBU': 'Arauco', 'LOS ANGELES': 'Biobío',
    
    'ANGOL': 'Araucanía Norte', 'TEMUCO': 'Araucanía Sur', 'PADRE LAS CASAS': 'Araucanía Sur',
    'VALDIVIA': 'Valdivia', 'LA UNIÓN': 'Valdivia', 'OSORNO': 'Osorno',
    'PUERTO MONTT': 'Del Reloncaví', 'CHAITÉN': 'Del Reloncaví', 'CASTRO': 'Chiloé',
    
    'COYHAIQUE': 'Aisén', 'AYSEN': 'Aisén', 'COCHRANE': 'Aisén', 'CHILE CHICO': 'Aisén',
    'PUNTA ARENAS': 'Magallanes', 'PORVENIR': 'Magallanes', 'NATALES': 'Magallanes', 'CABO DE HORNOS': 'Magallanes'
}

# 3. Mapear cada unidad vecinal a su Servicio de Salud
df_uv['servicio_salud'] = df_uv['NOMBRE COMUNA'].map(comuna_a_ss)

# 4. Agrupar la superficie de áreas verdes (m² y hectáreas) y cantidad de UVs por Servicio de Salud
areas_verdes_ss = df_uv.groupby('servicio_salud').agg(
    total_area_verde_m2=('ÁREA VERDE', 'sum'),
    total_unidades_vecinales=('ID_UNIDAD_VECINAL', 'count')
).reset_index()

# Agregar cálculo en Hectáreas (1 ha = 10.000 m²)
areas_verdes_ss['total_area_verde_ha'] = areas_verdes_ss['total_area_verde_m2'] / 10000.0

# 5. Obtener la lista de Servicios de Salud únicos (omitiendo 'SNSS' que representa el total nacional)
servicios_salud_df = df_atenciones[df_atenciones['servicio_salud'] != 'SNSS'][['servicio_salud']].drop_duplicates()

# 6. Fusionar para obtener la tabla final por Servicio de Salud
df_resultado = pd.merge(servicios_salud_df, areas_verdes_ss, on='servicio_salud', how='left')

# Ordenar de mayor a menor superficie de área verde
df_resultado = df_resultado.sort_values(by='total_area_verde_m2', ascending=False).reset_index(drop=True)

# 7. Guardar el resultado en un nuevo CSV
df_resultado.to_csv('areas_verdes_por_servicio_salud.csv', index=False)


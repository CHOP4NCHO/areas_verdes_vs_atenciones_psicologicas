# areas_verdes_vs_atenciones_psicologicas

# Explicaciones sobre el dashboard de áreas verdes

### 1. ¿Qué significa que una comuna sea "censada" y de qué parte del CSV salió?                                          
                                                                                                                            
  La palabra "censada" (o catastrada) en este contexto significa simplemente: **que la comuna aparece con registros en el   
  archivo unidades_vecinales.csv**.                                                                                         
                                                                                                                            
  ¿De dónde sale exactamente?                                                                                               
                                                                                                                            
  1. En Chile existen 346 comunas en total (todas listadas en info_comunas_chile.csv).                                      
  2. Sin embargo, si revisas la columna NOMBRE COMUNA en unidades_vecinales.csv, verás que solo vienen 109 comunas distintas
  (principalmente capitales regionales y grandes ciudades). Las otras 237 comunas del país no tienen ninguna fila en ese    
  archivo.                                                                                                                  
  3. ¿Por qué importa esto para el cálculo?                                                                                 
      • Si un Servicio de Salud como Osorno abarca 7 comunas, pero en unidades_vecinales.csv la única comuna que tiene datos
      es Osorno (las otras 6 comunas rurales como Puyehue, San Pablo, Purranque no fueron catastradas):                     
          • Población censada / con datos: Solo se divide por los habitantes de la comuna de Osorno (166.455 hab), donde sí 
          se midieron las plazas y parques.                                                                                 
          • Población total del servicio: Se divide por los habitantes de las 7 comunas (239.107 hab). Al hacer esto, se    
          asume erróneamente que los habitantes de las comunas no catastradas tienen "cero" metros de áreas verdes,         
          diluyendo el número artificialmente.                                                                              
                                                                                                                                   
  ──────                                                                                                                    
  ### 2. ¿Cómo se hizo el mapeo?                                                                                            
                                                                                                                            
  El mapeo consiste en asignar cada comuna de Chile a su Servicio de Salud oficial del Ministerio de Salud (MINSAL):        
                                                                                                                            
  1. Estructura oficial del MINSAL:                                                                                         
      • La red de salud pública en Chile no se organiza solo por regiones, sino por 29 Servicios de Salud.                  
      • En regiones con un solo Servicio de Salud, toda la región va al mismo servicio (ej: Región de Tarapacá → SS Iquique,
      Maule → SS Maule, Magallanes → SS Magallanes).                                                                        
      • En regiones grandes o con varios servicios, la división se hace por provincias o comunas específicas:               
          • Por ejemplo, en la Región de Los Lagos: la provincia de Osorno va al SS Osorno, la provincia de Chiloé al SS    
          Chiloé, y las provincias de Llanquihue y Palena al SS Del Reloncaví.                                              
          • En la Región Metropolitana: las comunas se agrupan en 6 servicios (ej. Santiago Centro, Maipú y Estación Central
          van al SS Metropolitano Central; Las Condes, Providencia y Vitacura van al SS Metropolitano Oriente).             
                                                                                                                            
  2. Cómo se implementó en el código (merge_csvs.py:9-85):                                                                  
      • Se toma cada fila de info_comunas_chile.csv (que contiene region, provincia y comuna).                              
      • Se limpian los textos con una función de normalización (quita tildes y pasa todo a minúsculas, por ejemplo "Viña Del
      Mar" pasa a "vina del mar").                                                                                          
      • La función comuna_a_servicio_salud aplica la regla territorial oficial del MINSAL y devuelve el nombre exacto del   
      Servicio de Salud.                                                                                                    
      • Con esto se crea un diccionario unificado de las 346 comunas de Chile. Luego, a cada unidad vecinal de              
      unidades_vecinales.csv se le asigna su Servicio de Salud buscando su NOMBRE COMUNA en dicho diccionario.              
                                                                                                                            
  ──────                                                                                                                    
  ### 3. ¿Qué debería interpretar de una correlación negativa?                                                              
                                                                                                                            
  Una correlación negativa (r < 0 o ρ < 0) entre las dos variables:                                                         
                                                                                                                            
  • Eje X: Disponibilidad de áreas verdes (m² por habitante).                                                               
  • Eje Y: Porcentaje de atenciones de psicología sobre el total de atenciones de salud (% Psicología).                     
                                                                                                                            
  #### Interpretación matemática directa:                                                                                   
                                                                                                                            
  Indica una relación inversa:                                                                                              
                                                                                                                            
  │ A mayor disponibilidad de áreas verdes por habitante, menor tiende a ser la proporción de atenciones de psicología en   
  ese
  │ Servicio de Salud (y a la inversa, en zonas con menor disponibilidad de áreas verdes, la psicología representa un mayor 
  │ porcentaje del total de atenciones).
  
  #### Posibles interpretaciones teóricas y de investigación:
  
  1. Hipótesis de protección ambiental y bienestar mental:
      • Existe abundante literatura en epidemiología urbana y salud ambiental (incluyendo recomendaciones de la OMS) que    
      documenta que el acceso a entornos naturales y áreas verdes reduce los niveles de cortisol (estrés), disminuye        
      síntomas de ansiedad/depresión y fomenta la actividad física y el encuentro social.
      • Desde esta perspectiva, una correlación negativa podría sugerir que un entorno con mayor presencia de áreas verdes  
      se asocia con una menor necesidad relativa de consultas de salud mental en la población.
  2. Factores de contexto urbano (estresores de la gran ciudad):
      • Los Servicios de Salud más urbanizados y congestionados (como zonas densas de Santiago) suelen tener menores áreas  
      verdes por habitante y, al mismo tiempo, una mayor carga de estresores urbanos (hacinamiento, tiempos de traslado,    
      ruido), lo que empuja la demanda de salud mental hacia arriba.
      • En cambio, zonas del sur o con mayor amplitud espacial presentan condiciones ambientales distintas.

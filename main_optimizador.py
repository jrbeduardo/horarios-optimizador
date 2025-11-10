
import pandas as pd
from optimizador import * 

# ----------------- INPUTS POR PARTE DEL GERENTE ---------------------------------------------

id_tienda = 13 # El id de la tienda
fecha_inicio_str = '2025-07-07' # Esta fecha debe ser la fecha del lunes siempre
primera_hora_comida = 11  # La hora a la que se puede empezar a enviar gente a comer
ultima_hora_comida = 17  # la última hora a la que se puede empezar a enviar gente a comer
dias_con_surtido = ['Lunes', 'Miercoles', 'Viernes'] # Se introduce los días donde se prefiere hacer surtido. 
# Aquí se introducen las areas en orden de importancia. Nunca se introducen CAJA, PUERTA o SURTIDO, esas se manejan automaticamente
areas_rankeadas = ['ZAPATERIA', 'BLANCOS', 'BEBES', 'DAMAS', 'NIÑAS', 'PERF/COSM', ] 

# Argumentos de empleados: se introducen los nombres como keys y las especialidades como una lista de las áreas en las que es capaz atender. 
especialidad_empleado = {
    'Maria Garcia': ['CAJA'],
    'Jose Hernandez': ['CAJA', 'NIÑAS', 'PUERTA'],
    'Ana Perez': ['BEBES', 'CAJA', 'PUERTA'],
    'Luis Gonzalez': ['DAMAS', 'CAJA', 'BLANCOS', 'PUERTA'],
    'Sofia Ramirez': ['NIÑAS', 'CAJA', 'PUERTA', 'DAMAS', 'BLANCOS'],
    'Carlos Sanchez': ['NIÑAS', 'CAJA', 'DAMAS', 'PUERTA'],
    'Valeria Torres': ['PERF/COSM', 'CAJA', 'PUERTA'],
    'Daniel Rodriguez': ['PERF/COSM', 'PUERTA', 'CAJA', 'SURTIDO', 'BLANCOS', 'ZAPATERIA', 'BEBES', 'DAMAS', 'NIÑAS'],
    'Marta Lopez': ['BEBES', 'CAJA', 'PUERTA', 'SURTIDO', 'BLANCOS', 'ZAPATERIA', 'DAMAS', 'NIÑAS', 'PERF/COSM'],
    'Jorge Diaz': ['BEBES', 'CAJA', 'PERF/COSM', 'PUERTA', 'SURTIDO', 'ZAPATERIA', 'BLANCOS', 'DAMAS', 'NIÑAS'],
    'Elena Gomez': ['ZAPATERIA', 'PUERTA', 'SURTIDO', 'BLANCOS', 'BEBES', 'DAMAS', 'CAJA', 'NIÑAS', 'PERF/COSM'],
    'Pedro Chavez': ['ZAPATERIA', 'PUERTA', 'SURTIDO', 'BLANCOS', 'BEBES', 'DAMAS', 'CAJA', 'NIÑAS', 'PERF/COSM'],
    'Laura Vargas': ['ZAPATERIA', 'PUERTA', 'SURTIDO', 'BLANCOS', 'BEBES', 'DAMAS', 'CAJA', 'NIÑAS', 'PERF/COSM'],
    'Ricardo Morales': ['ZAPATERIA', 'PUERTA', 'SURTIDO', 'BLANCOS', 'BEBES', 'DAMAS', 'CAJA', 'NIÑAS', 'PERF/COSM'],
    'Carmen Flores': ['CAJA', 'PUERTA', 'ZAPATERIA', 'BLANCOS'],
    'Manuel Jimenez': ['CAJA', 'PUERTA', 'ZAPATERIA', 'BLANCOS'],
    'Beatriz Castro': ['CAJA', 'PUERTA', 'ZAPATERIA', 'BLANCOS'],
}

# ----------------- INPUTS FIJOS -----------------------------------------------------------------
# ESTOS INPUTS DEBEN SER AUTOMÁTICOS Y JAMÁS CAMBIAR 

# Se leera el pronóstico de operaciones y demanda de cajas como csv. 
df_pronostico = pd.read_csv("pronostico.csv")
df_cajas = pd.read_csv("cajas.csv")
# Se designa la dirección del solver
solverpath_exe = 'Cbc-releases.2.10.11-msvs-w64-mingw64\\bin\\cbc'
solvername= 'cbc'
# Se crea el objeto fecha 
fecha = date.fromisoformat(fecha_inicio_str) # Esto se realiza en automático

# ------------------ OPTIMIZACIÓN DE LOS DESCANSOS SEMANALES --------------------------------------

horas_por_dia, horas_comida, empleados, demanda_cajas_dia, demanda_caja_hora, areas, empleados_por_area, dias, demanda = procesar_inputs(primera_hora_comida, ultima_hora_comida,
                                                                                            especialidad_empleado,df_pronostico,df_cajas,
                                                                                            id_tienda, fecha_inicio_str, fecha)


df_resultado_semana,df_resultado = optimizar_semana(areas, empleados, empleados_por_area, horas_comida, 
                     horas_por_dia, dias, solverpath_exe, solvername,especialidad_empleado,demanda_cajas_dia,demanda)

# ----------------- OPTIMIZACION DIARIA: COMIDAS Y AREAS ASIGNADAS EN CADA DÍA -------------------------
resultados_diarios = {}
for i in dias[:]:
    if i in dias_con_surtido:
        resultado_diario, modelo_diario = optimizacion_diaria(df_resultado,demanda_caja_hora,dia = i, areas_rankeadas=areas_rankeadas,demanda = demanda, solvername=solvername, solverpath_exe=solverpath_exe)
        resultados_diarios[i] = get_resultado_dataframe(modelo_diario,resultado_diario,i)
    else:
        resultado_diario, modelo_diario = optimizacion_diaria(df_resultado,demanda_caja_hora,dia = i, areas_rankeadas=areas_rankeadas, con_surtido=False, demanda = demanda,solvername=solvername, solverpath_exe=solverpath_exe)
        resultados_diarios[i] = get_resultado_dataframe(modelo_diario,resultado_diario,i)

# ------------- OUTPUTS -------------------------- # 
"""
optimizar_semana()
    df_resultado_semana: este es el dataframe con el resultado final de la programación de toda la semana, 
                         quienes descansan y quienes trabajan en cada día.

ouput del for con optimizacion_diaria():
    resultados_diarios: Este es un diccionario con dataframes. Las keys son el nombre del día, y cada uno
                        tiene su dataframe de horarios programados para ese día. 
                        Ejemplo: resultados_diarios['Lunes'] te dará el dataframe de ese día. 
"""


# %%

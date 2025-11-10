from pyomo.environ import *
from collections import defaultdict
import pandas as pd
from datetime import date, timedelta


def procesar_inputs(primera_hora_comida, ultima_hora_comida,especialidad_empleado,df_pronostico,df_cajas,
                 id_tienda, fecha_inicio_str, fecha):
    if fecha.weekday() == 0:
        delta = timedelta(days=6)
        fecha_final = fecha + delta
        fecha_final_str = fecha_final.strftime('%Y-%m-%d')


        # selecionamos los datos de la semana a optimizar
        df_pronostico = df_pronostico[(df_pronostico.tienda == id_tienda) & (df_pronostico.fecha.between(fecha_inicio_str,fecha_final_str))]

        apertura_tienda = df_pronostico[(df_pronostico['tienda'] == id_tienda) & (df_pronostico['fecha'] == fecha_inicio_str)]['hora'].min()

        cierre_tienda = df_pronostico[(df_pronostico['tienda'] == id_tienda) & (df_pronostico['fecha'] == fecha_inicio_str)]['hora'].max()
        
        apertura_domingo = df_pronostico[(df_pronostico['tienda'] == id_tienda) & (df_pronostico['fecha'] == fecha_final_str)]['hora'].min()

        cierre_domingo = df_pronostico[(df_pronostico['tienda'] == id_tienda) & (df_pronostico['fecha'] == fecha_final_str)]['hora'].max()

        # poner dia de la semana
        df_pronostico['dia_semana'] = df_pronostico.apply(lambda x: pd.to_datetime(x.fecha).strftime('%A'), axis = 1)

        # Crear un mapeo para traducir los nombres de los días
        dias_en_espanol = {
            'Monday': 'Lunes',
            'Tuesday': 'Martes',
            'Wednesday': 'Miercoles',
            'Thursday': 'Jueves',
            'Friday': 'Viernes',
            'Saturday': 'Sabado',
            'Sunday': 'Domingo'
        }

        # Obtener el nombre del día en inglés y luego mapearlo a español
        df_pronostico['dia_semana'] = df_pronostico.dia_semana.map(dias_en_espanol)

        # Establecer 'dia_semana' y 'hora' como el índice del DataFrame
        df_pronostico = df_pronostico.set_index(['dia_semana', 'hora'])

        # Convertir el DataFrame a un diccionario
        demanda = df_pronostico['predicciones'].to_dict()

        # selecionamos los datos de la semana a optimizar
        df_cajas = df_cajas[(df_cajas.tienda == id_tienda) & (df_cajas.fecha.between(fecha_inicio_str,fecha_final_str))]

        # poner dia de la semana
        df_cajas['dia_semana'] = df_cajas.apply(lambda x: pd.to_datetime(x.fecha).strftime('%A'), axis = 1)

        # Obtener el nombre del día en inglés y luego mapearlo a español
        df_cajas['dia_semana'] = df_cajas.dia_semana.map(dias_en_espanol)

        # Establecer 'dia_semana' y 'hora' como el índice del DataFrame
        df_cajas = df_cajas.set_index(['dia_semana', 'hora'])

        # Convertir el DataFrame a un diccionario
        demanda_caja_hora = df_cajas['cajas'].to_dict()
        dias = ['Lunes', 'Martes', 'Miercoles', 'Jueves', 'Viernes', 'Sabado', 'Domingo']

        horas_por_dia = {
            d: list(range(apertura_tienda, cierre_tienda)) if d != 'Domingo' else list(range(apertura_domingo, cierre_domingo))
            for d in dias
        }

        horas_comida = list(range(primera_hora_comida, ultima_hora_comida))


        empleados = [i for i, x in especialidad_empleado.items()] 

        def get_max_per_day(demanda_caja_hora):
            max_por_dia = {}
            for (dia, hora), valor in demanda_caja_hora.items():
                max_por_dia[dia] = max(max_por_dia.get(dia, 0), valor)
            return max_por_dia

        demanda_cajas_dia = get_max_per_day(demanda_caja_hora)


        empleados_por_area = defaultdict(list)
        for emps, areas in especialidad_empleado.items():
            for a in areas:
                empleados_por_area[a].append(emps)
        areas = list(empleados_por_area.keys())
        
        return  horas_por_dia, horas_comida, empleados, demanda_cajas_dia, demanda_caja_hora, areas, empleados_por_area, dias, demanda

    else:
        return f"La fecha {fecha_inicio_str} no es un lunes"



def optimizar_semana(areas, empleados, empleados_por_area, horas_comida, 
                     horas_por_dia, dias, solverpath_exe, solvername,especialidad_empleado,demanda_cajas_dia,demanda):
    modelo = ConcreteModel()
    modelo.trabaja = Var(empleados, dias, domain=Binary)
    modelo.come = Var(empleados, dias, horas_comida, domain=Binary)
    modelo.presente = Var(empleados, dias, range(9, 19), domain=Binary)
    modelo.exceso = Var(dias, range(9, 19), domain=NonNegativeReals)
    modelo.falta = Var(dias, range(9, 19), domain=NonNegativeReals)
    modelo.restricciones = ConstraintList()

    # Restricciones de comida y presencia
    for e in empleados:
        for d in dias:
            horas_validas_comida = [h for h in horas_comida if h in horas_por_dia[d]]
            modelo.restricciones.add(
                sum(modelo.come[e, d, h] for h in horas_validas_comida) == modelo.trabaja[e, d]
            )
            for h in horas_por_dia[d]:
                if h in horas_comida:
                    modelo.restricciones.add(
                        modelo.presente[e, d, h] == modelo.trabaja[e, d] - modelo.come[e, d, h]
                    )
                else:
                    modelo.restricciones.add(
                        modelo.presente[e, d, h] == modelo.trabaja[e, d]
                    )
            for h in set(range(9, 19)) - set(horas_por_dia[d]):
                modelo.restricciones.add(modelo.presente[e, d, h] == 0)

    # Horas totales
    for e in empleados:
        total_horas = sum(modelo.presente[e, d, h] for d in dias for h in horas_por_dia[d])
        modelo.restricciones.add(total_horas >= 43)
        modelo.restricciones.add(total_horas <= 45)

    # Dos días de descanso no consecutivos
    for e in empleados:
        modelo.restricciones.add(sum(1 - modelo.trabaja[e, d] for d in dias) == 2)
        for i in range(len(dias)):
            d1 = dias[i]
            d2 = dias[(i + 1) % len(dias)]
            modelo.restricciones.add(modelo.trabaja[e, d1] + modelo.trabaja[e, d2] >= 1)

    # Mínimo de empleados por día
    min_empleados_dia = int(len(empleados) * 5 / 7)
    for d in dias:
        modelo.restricciones.add(sum(modelo.trabaja[e, d] for e in empleados) >= min_empleados_dia)

    # Al menos 60% del personal presente cada hora
    for d in dias:
        for h in horas_por_dia[d]:
            empleados_trabajan_dia = sum(modelo.trabaja[e, d] for e in empleados)
            empleados_presentes_hora = sum(modelo.presente[e, d, h] for e in empleados)
            modelo.restricciones.add(empleados_presentes_hora >= (2 / 3) * empleados_trabajan_dia)

    # Cada área debe estar cubierta por un especialista cada día
    for area in areas:
        for d in dias:
            modelo.restricciones.add(
                sum(modelo.trabaja[e, d] for e in empleados_por_area[area]) >= 3
            )

    # Cada caja debe estar cubierta por un especialista cada día
    for d in dias:
            modelo.restricciones.add(
                sum(modelo.trabaja[e, d] for e in empleados_por_area['CAJA']) >= demanda_cajas_dia[d] * 2
            )

    # Restricciones de balance entre demanda y personal
    for d in dias:
        for h in horas_por_dia[d]:
            modelo.restricciones.add(
                sum(modelo.presente[e, d, h] for e in empleados) + modelo.falta[d, h] - modelo.exceso[d, h] == demanda.get((d, h), 0)
            )

    # Objetivo: minimizar penalidad por falta y exceso
    modelo.objetivo = Objective(
        expr=sum(2 * modelo.falta[d, h] + modelo.exceso[d, h] for d in dias for h in horas_por_dia[d]),
        sense=minimize
    )

    # Resolver
    solver= SolverFactory(solvername,executable=solverpath_exe)
    resultado = solver.solve(modelo, tee=True)


    datos_empleados = []

    for e in empleados:
        dias_descanso = sum(1 for d in dias if value(modelo.trabaja[e, d]) < 0.5)
        horas_trabajo = 0
        for d in dias:
            for h in horas_por_dia[d]:
                horas_trabajo += value(modelo.presente[e, d, h])
        datos_empleados.append({
            'Empleado': e,
            'Días_Descanso': int(round(dias_descanso)),
            'Horas_Trabajo': round(horas_trabajo, 1)
        })

    df_empleados = pd.DataFrame(datos_empleados)

    # Crear DataFrame de resultados
    columnas = ['Especialidad'] + dias + ['Horas semana']
    df_resultado = pd.DataFrame(index=empleados, columns=columnas)
    df_resultado['Especialidad'] = df_resultado.index.map(especialidad_empleado)

    # Calcular información para cada empleado
    for e in empleados:
        horas_totales = 0
        for d in dias:
            if value(modelo.trabaja[e, d]) < 0.5:
                df_resultado.loc[e, d] = 'DESCANSA'
            else:
                entrada = min(h for h in horas_por_dia[d] if value(modelo.presente[e, d, h]) > 0.5)
                salida = max(h for h in horas_por_dia[d] if value(modelo.presente[e, d, h]) > 0.5) + 1
                try:
                    hora_comida = next(h for h in horas_comida if h in horas_por_dia[d] and value(modelo.come[e, d, h]) > 0.5)
                except StopIteration:
                    hora_comida = 'N/A'
                df_resultado.loc[e, d] = f"{entrada}:00-{salida}:00 / Comida {hora_comida}:00"
                horas_totales += (salida - entrada - 1 if hora_comida != 'N/A' else salida - entrada)

        df_resultado.loc[e, 'Horas semana'] = horas_totales

    # Ajustar índice
    df_resultado.reset_index(inplace=True)
    df_resultado.rename(columns={'index': 'Empleado'}, inplace=True)

    # Crear DataFrame base
    columnas = ['Especialidad'] + dias + ['Horas semana']
    df_resultado = pd.DataFrame(index=empleados, columns=columnas)
    df_resultado['Especialidad'] = df_resultado.index.map(especialidad_empleado)

    # Llenar el DataFrame con descanso o hora de comida
    for e in empleados:
        horas_totales = 0
        for d in dias:
            if value(modelo.trabaja[e, d]) < 0.5:
                df_resultado.loc[e, d] = 'DESCANSA'
            else:
                try:
                    hora_comida = next(
                        h for h in horas_comida if h in horas_por_dia[d] and value(modelo.come[e, d, h]) > 0.5
                    )
                    df_resultado.loc[e, d] = f"Comida {hora_comida}:00"
                except StopIteration:
                    df_resultado.loc[e, d] = "Comida N/A"
                # Contar horas trabajadas (sin comida)
                horas_dia = sum(value(modelo.presente[e, d, h]) for h in horas_por_dia[d])
                horas_totales += int(horas_dia)

        df_resultado.loc[e, 'Horas semana'] = horas_totales

    # Ajustar índice
    df_resultado.reset_index(inplace=True)
    df_resultado.rename(columns={'index': 'Empleado'}, inplace=True)
    df_resultado.set_index('Empleado', inplace=True)


    df_resultado_semana = df_resultado.copy()
    df_resultado_semana.drop(columns=['Especialidad','Horas semana'], inplace = True)
    mask = df_resultado_semana != 'DESCANSA'
    df_resultado_semana[mask] = 'TRABAJA'
    return df_resultado_semana, df_resultado

def calcula_pesos(ranked_list):
    """
    Calcula pesos con base al ranking de las áreas
    """
    num_items = len(ranked_list)
    scores = {item: num_items - i for i, item in enumerate(ranked_list)}
    total_score = sum(scores.values())
    weights = {item: score / total_score for item, score in scores.items()}

    return weights

def optimizacion_diaria(df_resultado,demanda_caja_hora, areas_rankeadas, dia = 'Sabado', solverpath_exe = None, solvername = None, con_surtido = True, demanda = None):
    auto_pesos = False # True para que todas las áreas tengan la misma importancia
    empleados = df_resultado[df_resultado[dia] != 'DESCANSA'].index
    empleados_disponibles = df_resultado.loc[empleados][['Especialidad',dia]]
    horas_dia = [hora for dia_, hora in demanda_caja_hora.keys() if dia_ == dia]
    horas_surtido = horas_dia[:2][:]

    emps = empleados_disponibles.copy()
    emps = dict(emps['Especialidad'])
    emps_por_area = defaultdict(list)
    for emp, areas in emps.items():
        for a in areas:
            emps_por_area[a].append(emp)
    areas = list(emps_por_area.keys()) + ['COMIDA']

    # Modelo
    modelo_diario = ConcreteModel()
    modelo_diario.horario_diario = Var(horas_dia, empleados_disponibles.index, areas, domain=Binary)

    # Variables para lograr una optimización equilibrada
    modelo_diario.sobre_asignacion = Var(areas, domain=NonNegativeReals)
    modelo_diario.sub_asignacion = Var(areas, domain=NonNegativeReals)
    modelo_diario.restricciones = ConstraintList()

    # No se asignará SURTIDO en ninguna otra hora que las dos primeras de la mañana
    for i, row in empleados_disponibles.iterrows():
        for hora in horas_dia[2:]:
            emp = i
            modelo_diario.horario_diario[hora, emp, 'SURTIDO'].fix(0)

    # Las cajas siempre deben ser exactamente las que se requieren, ni más ni menos.
    for h in horas_dia:
        modelo_diario.restricciones.add(
            sum(modelo_diario.horario_diario[h, e, 'CAJA'] for e in emps_por_area['CAJA']) == demanda_caja_hora[dia, h]
        )

    # Todas las áreas deben tener al menos una persona (SURTIDO, COMIDA Y PUERTA se gestionan de forma diferente)
    areas_regla = list(set(areas) - set(['SURTIDO', 'COMIDA', 'PUERTA', 'CAJA']))

    for h in horas_dia:
        for area in areas_regla:
            modelo_diario.restricciones.add(
                sum(modelo_diario.horario_diario[h, e, area] for e in emps_por_area[area]) >= 1
            )

    # La puerta siempre debe estar cubierta
    for h in horas_dia:
        modelo_diario.restricciones.add(
            sum(modelo_diario.horario_diario[h, e, 'PUERTA'] for e in emps_por_area['PUERTA']) == 1
        )

    # Surtido en las primeras dos hrs de la mañana, al menos dos personas dedicadas a eso
    for h in horas_surtido:
        modelo_diario.restricciones.add(
            sum(modelo_diario.horario_diario[h, e, 'SURTIDO'] for e in emps_por_area['SURTIDO']) == 2
        )

    # Todos deben tener una hr de comida entre las 11 y las 18
    lunch_hours = [h for h in horas_dia if 11 <= h <= 17]

    for emp in empleados_disponibles.index:
        modelo_diario.restricciones.add(
            sum(modelo_diario.horario_diario[h, emp, 'COMIDA'] for h in lunch_hours) == 1
        )

    # No COMIDA fuera del rango establecido
    non_lunch_hours = [h for h in horas_dia if h not in lunch_hours]

    for emp in empleados_disponibles.index:
        for h in non_lunch_hours:
            modelo_diario.horario_diario[h, emp, 'COMIDA'].fix(0)

    # No se puede estar en varios lugares a la vez
    for h in horas_dia:
        for emp in empleados_disponibles.index:
            modelo_diario.restricciones.add(
                sum(modelo_diario.horario_diario[h, emp, area] for area in areas) == 1
            )

    # Un empleado solo puede ser asignado a áreas de su especialidad, excluyendo la hora de comida
    for emp in empleados_disponibles.index:
        for area in areas:
            # Exclude the 'COMIDA' area from the specialty check
            if area != 'COMIDA' and area not in emps[emp]:
                for h in horas_dia:
                    modelo_diario.restricciones.add(modelo_diario.horario_diario[h, emp, area] == 0)

    # No 2 hrs consecutivas de PUERTA 
    for emp in empleados_disponibles.index:
        for i in range(len(horas_dia) - 1):
            h1 = horas_dia[i]
            h2 = horas_dia[i + 1]

            modelo_diario.restricciones.add(
                modelo_diario.horario_diario[h1, emp, 'PUERTA'] +
                modelo_diario.horario_diario[h2, emp, 'PUERTA'] <= 1
            )

    if con_surtido:
        areas_regla_original = areas_rankeadas[:] + ['CAJA', 'SURTIDO', 'PUERTA']
    else:
        areas_regla_original = areas_rankeadas[:] + ['CAJA', 'PUERTA']

    if auto_pesos:
        num_categories = len(areas_regla_original)
        equal_weight = 1 / num_categories
        pesos = dict(zip(areas_regla_original, [equal_weight] * num_categories))
    else:
        pesos = calcula_pesos(areas_regla_original)
        print(pesos)

    # Empleados disponibles en el turno
    empleados_total = len(empleados_disponibles.index)

    # Definir target de personal por área en función de las áreas rankeadas
    target_empleados_por_area = {area: pesos[area] * empleados_total for area in areas_regla_original}


    for area in areas_regla_original:
        actual_empleados_area = sum(modelo_diario.horario_diario[hora, emp, area]
                                    for emp in empleados_disponibles.index
                                    for hora in horas_dia)

        modelo_diario.restricciones.add(
            actual_empleados_area - target_empleados_por_area[area] == modelo_diario.sobre_asignacion[area] - modelo_diario.sub_asignacion[area]
        )

  # Combinación de objetivos: maximizar la presencia de personas en las áreas más importantes y
  # minimizar la cantidad de personas que van a comer en las horas de mayor demanda entre las 11:00 y las 18:00

  # Aquí declaro el objetivo de maximizar la presencia de personas en las áreas más importantes
    deviation_expr = sum(modelo_diario.sobre_asignacion[area] + modelo_diario.sub_asignacion[area]
                         for area in areas_regla_original)

  # Aquí va el objetivo dos, minimizar la cantidad de personas que van a comer en horas de mayor demanda
    demanda_dia = {k[1]: v for k, v in demanda.items() if k[0] == dia}
    break_demand_expr = sum(
        demanda_dia[h] * sum(modelo_diario.horario_diario[h, e, 'COMIDA']
                             for e in empleados_disponibles.index)
        for h in lunch_hours
    )

    alpha = 0.5  # 0.5 para balancear objetivos

    modelo_diario.objetivo = Objective(
        expr=(alpha * deviation_expr) + ((1 - alpha) * break_demand_expr),
        sense=minimize
    )


    solver= SolverFactory(solvername,executable=solverpath_exe)
    resultado_diario = solver.solve(modelo_diario, tee=False)
    return resultado_diario, modelo_diario

def get_resultado_dataframe(modelo_diario,resultado_diario, dia ):
    "Formatea el resultado de la optimización para regresarla como dataframe"
    if (resultado_diario.solver.status == SolverStatus.ok and
        resultado_diario.solver.termination_condition == TerminationCondition.optimal):

        horario_resultante = []
        for hora in modelo_diario.horario_diario.index_set():
            if value(modelo_diario.horario_diario[hora]) == 1:
                horario_resultante.append([hora[0], hora[1], hora[2]])
            horario_df = pd.DataFrame(horario_resultante, columns=['Hora', 'Empleado', 'Area'])

        horario_pivote = horario_df.pivot_table(
            index='Empleado',
            columns='Hora',
            values='Area',
            aggfunc=lambda x: ', '.join(x)
        )
        return horario_pivote
    else: 
        return {f"No se encontró solución para el día {dia}. Se recomienda agregar nuevas especialidades a los colaboradores con menos especialidades"}



# %%

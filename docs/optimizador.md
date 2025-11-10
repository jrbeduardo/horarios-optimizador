# Documentación Técnica del Optimizador de Horarios

## Descripción General
Sistema de optimización en dos niveles para generar horarios óptimos en tiendas retail. Utiliza Pyomo (Python Optimization Modeling Objects) con CBC solver para resolver problemas de programación lineal entera mixta (MILP).

## Arquitectura del Sistema

El optimizador trabaja en dos fases:
1. **Fase Semanal**: Determina qué empleados trabajan cada día y sus horas de comida
2. **Fase Diaria**: Asigna empleados a áreas específicas por hora

## Componentes Principales

### 1. Procesamiento de Inputs (`procesar_inputs`)

**Propósito**: Preparar y transformar datos de entrada para la optimización

**Entradas**:
- `primera_hora_comida`: Inicio del rango de comidas (ej: 11)
- `ultima_hora_comida`: Fin del rango de comidas (ej: 17)
- `especialidad_empleado`: Diccionario {empleado: [áreas]}
- `df_pronostico`: DataFrame con predicciones de demanda por hora
- `df_cajas`: DataFrame con número de cajas requeridas por hora
- `id_tienda`: Identificador de la tienda
- `fecha_inicio_str`: Fecha del lunes (YYYY-MM-DD)
- `fecha`: Objeto datetime de la fecha de inicio

**Proceso**:
1. Valida que la fecha sea lunes
2. Calcula fecha final (domingo) sumando 6 días
3. Filtra datos por tienda y rango de fechas
4. Extrae horarios de apertura/cierre (diferenciados para domingo)
5. Traduce días de inglés a español
6. Convierte DataFrames a diccionarios indexados por (día, hora)
7. Calcula demanda máxima de cajas por día
8. Genera estructura de empleados por área

**Salidas**:
- `horas_por_dia`: {día: [horas_operación]}
- `horas_comida`: Lista de horas válidas para comida
- `empleados`: Lista de IDs de empleados
- `demanda_cajas_dia`: {día: max_cajas}
- `demanda_caja_hora`: {(día, hora): num_cajas}
- `areas`: Lista de áreas únicas
- `empleados_por_area`: {área: [empleados]}
- `dias`: Lista de días de la semana
- `demanda`: {(día, hora): predicción}

### 2. Optimización Semanal (`optimizar_semana`)

**Propósito**: Determinar días de trabajo, descanso y horas de comida para la semana

**Variables de Decisión**:
- `trabaja[e, d]`: Binaria - si empleado e trabaja el día d
- `come[e, d, h]`: Binaria - si empleado e come a las h del día d
- `presente[e, d, h]`: Binaria - si empleado e está presente (no comiendo) hora h del día d
- `exceso[d, h]`: Real - personal extra sobre demanda
- `falta[d, h]`: Real - personal faltante bajo demanda

**Restricciones Principales**:

1. **Comida y Presencia**:
   - Cada empleado que trabaja debe tener exactamente 1 hora de comida
   - Presente = Trabaja - Come (en horas de comida)
   - Presente = Trabaja (fuera de horas de comida)

2. **Jornada Laboral**:
   - 43 ≤ horas_semanales ≤ 45 por empleado
   - Exactamente 2 días de descanso por semana
   - Días de descanso NO consecutivos

3. **Cobertura General**:
   - Mínimo ⌊empleados_totales × 5/7⌋ trabajan cada día
   - ≥60% de empleados que trabajan están presentes cada hora
   
4. **Cobertura por Área**:
   - Mínimo 3 especialistas por área trabajando cada día
   - Cajas: ≥2 × demanda_máxima_cajas especialistas por día

5. **Balance de Personal**:
   - Personal_presente + Falta - Exceso = Demanda

**Función Objetivo**:
Minimizar: 2×Falta + Exceso (penaliza el doble la falta de personal)

**Salidas**:
- `df_resultado_semana`: DataFrame con estado TRABAJA/DESCANSA
- `df_resultado`: DataFrame con horarios de comida y horas totales

### 3. Optimización Diaria (`optimizacion_diaria`)

**Restricciones Específicas**:

1. **Surtido**: Solo primeras 2 horas, exactamente 2 personas
2. **Cajas**: Exactamente demanda_caja_hora personas
3. **Puerta**: Exactamente 1 persona, no más de 1 hora consecutiva
4. **Comida**: 1 hora entre 11-17 por empleado
5. **Áreas**: Mínimo 1 persona por hora

**Función Objetivo Multi-criterio**:
- 50% Desviación de distribución ideal por área
- 50% Personal comiendo en horas de alta demanda

## Flujo de Ejecución

1. Cargar CSVs (pronostico, cajas)
2. procesar_inputs() → estructuras de datos
3. optimizar_semana() → horarios semanales
4. Loop: optimizacion_diaria() por cada día

## Tecnologías

- **Pyomo 6.7.3**: Modelado algebraico
- **CBC Solver**: Programación lineal entera mixta
- **Pandas 2.2.2**: Manipulación de datos
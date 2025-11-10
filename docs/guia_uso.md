# Guía de Uso del Optimizador

## Preparación de Datos

### 1. Archivo de Pronóstico (`pronostico.csv`)
Debe contener:
- tienda: ID de la tienda
- fecha: Fecha en formato YYYY-MM-DD
- hora: Hora del día (0-23)
- predicciones: Número estimado de personal necesario

### 2. Archivo de Cajas (`cajas.csv`)
Debe contener:
- tienda: ID de la tienda
- fecha: Fecha en formato YYYY-MM-DD
- hora: Hora del día (0-23)
- cajas: Número de cajas necesarias

### 3. Configuración de Empleados
Diccionario con:
- Clave: ID del empleado
- Valor: Lista de especialidades (CAJA, SURTIDO, PUERTA, etc.)

## Ejecución del Optimizador

1. **Optimización Semanal**
```python
# Ejemplo de uso
resultado_semanal, detalle = optimizar_semana(
    areas=areas,
    empleados=empleados,
    empleados_por_area=empleados_por_area,
    horas_comida=range(11, 18),
    horas_por_dia=horas_por_dia,
    dias=dias,
    solverpath_exe='ruta_al_solver',
    solvername='cbc',
    especialidad_empleado=especialidad_empleado,
    demanda_cajas_dia=demanda_cajas_dia,
    demanda=demanda
)
```

2. **Optimización Diaria**
```python
# Ejemplo de uso
resultado_diario, modelo = optimizacion_diaria(
    df_resultado=resultado_semanal,
    demanda_caja_hora=demanda_caja_hora,
    areas_rankeadas=['AREA1', 'AREA2'],
    dia='Lunes',
    solverpath_exe='ruta_al_solver',
    solvername='cbc',
    con_surtido=True,
    demanda=demanda
)
```

## Interpretación de Resultados

### Resultado Semanal
- DataFrame con horarios semanales
- Indica días de descanso y turnos de trabajo
- Muestra horas totales por semana

### Resultado Diario
- Asignación detallada por hora
- Áreas cubiertas por cada empleado
- Horarios de comida
- Cobertura de áreas especiales (surtido, cajas, puerta)
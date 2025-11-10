# Documentación del Optimizador de Horarios

## Descripción General
El optimizador es una herramienta de programación lineal diseñada para generar horarios optimizados para empleados de una tienda, considerando múltiples restricciones y objetivos.

## Componentes Principales

### 1. Procesamiento de Inputs (`procesar_inputs`)
- Procesa datos de entrada para una semana completa
- Maneja información de:
  - Horarios de comida
  - Especialidades de empleados
  - Pronósticos de demanda
  - Datos de cajas necesarias
  - Horarios de apertura y cierre

### 2. Optimización Semanal (`optimizar_semana`)
Genera un horario semanal optimizado considerando:

#### Restricciones Principales:
- **Horarios de Trabajo**:
  - 43-45 horas semanales por empleado
  - Dos días de descanso no consecutivos
  - Horas de comida asignadas

#### Cobertura:
- Mínimo de empleados por día (5/7 del total)
- 60% del personal presente cada hora
- Cada área debe tener al menos 3 especialistas por día
- Cobertura de cajas según demanda (doble del número requerido)

### 3. Optimización Diaria (`optimizacion_diaria`)
Realiza una optimización detallada por día considerando:

#### Reglas Específicas:
- **Surtido**: 2 personas en primeras horas
- **Comidas**: Entre 11:00 y 17:00
- **Puerta**: Siempre cubierta, no más de 1 hora consecutiva
- **Cajas**: Según demanda por hora
- **Áreas**: Mínimo una persona por área

### 4. Cálculo de Pesos (`calcula_pesos`)
- Asigna pesos a las áreas según su prioridad
- Permite balancear la importancia relativa de cada área

## Características Técnicas
- Utiliza Pyomo para modelado matemático
- Implementa programación lineal entera mixta (MILP)
- Soporta múltiples solvers (CBC por defecto)
- Manejo de restricciones duras y blandas

## Entrada de Datos
- **Pronóstico**: Demanda por hora y día
- **Cajas**: Número de cajas necesarias por hora
- **Empleados**: Lista con especialidades
- **Horarios**: Apertura, cierre y comidas

## Salida
- Horarios semanales por empleado
- Asignaciones diarias detalladas por área
- Balanceo de carga de trabajo
- Cumplimiento de restricciones laborales
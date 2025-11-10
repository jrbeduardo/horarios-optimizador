# Optimizador de Horarios para Retail

Sistema de optimización de horarios semanales y diarios para empleados de tiendas retail. Utiliza programación lineal entera mixta (MILP) con Pyomo y el solver CBC para generar horarios optimizados que cumplen restricciones laborales y de negocio.

## Características Principales

- **Optimización Semanal**: Asigna días de trabajo y descanso respetando jornadas laborales de 43-45 horas
- **Optimización Diaria**: Distribuye empleados por áreas según demanda y especialidades
- **Gestión de Especialidades**: Asigna personal según sus capacidades en diferentes áreas
- **Balance de Demanda**: Ajusta cobertura según pronósticos de tráfico y necesidad de cajas
- **Horarios de Comida**: Optimiza breaks para minimizar impacto en horas de mayor demanda

## Requisitos

- Python 3.11+
- uv (gestor de paquetes y ambientes virtuales)
- CBC Solver (incluido en el proyecto)

## Instalación

1. Instalar uv (si no está instalado):
```powershell
python -m pip install uv
```

2. Crear y activar el ambiente virtual:
```powershell
uv venv
.venv\Scripts\Activate.ps1
```

3. Instalar dependencias:
```powershell
uv pip install -r requirements.txt
```

## Estructura del Proyecto

```
optimizador/
├── main_optimizador.py          # Punto de entrada con configuración
├── optimizador.py               # Motor de optimización (Pyomo)
├── cajas.csv                    # Demanda de cajas por hora/día
├── pronostico.csv               # Pronóstico de tráfico/demanda
├── requirements.txt             # Dependencias Python
├── README.md                    # Este archivo
├── docs/                        # Documentación detallada
│   ├── optimizador.md          # Descripción técnica
│   ├── guia_uso.md             # Guía de uso
│   └── mejoras_propuestas.md   # Mejoras futuras
└── Cbc-releases.../             # Solver CBC incluido
```

## Uso

### Configuración Básica

Edita `main_optimizador.py` con los parámetros de tu tienda:

```python
id_tienda = 13
fecha_inicio_str = '2025-07-07'  # Debe ser lunes
primera_hora_comida = 11
ultima_hora_comida = 17
areas_rankeadas = ['ZAPATERIA', 'BLANCOS', 'BEBES', 'DAMAS', 'NIÑAS', 'PERF/COSM']

# Especialidades de cada empleado
especialidad_empleado = {
    'Juan Perez': ['CAJA', 'PUERTA', 'ZAPATERIA'],
    'Maria Lopez': ['CAJA', 'DAMAS', 'BEBES'],
    # ... más empleados
}
```

### Ejecutar Optimización

```powershell
python main_optimizador.py
```

### Salida

El programa genera:
- `df_resultado`: Horarios semanales con días de descanso y horas de comida
- `resultados_diarios`: Diccionario con asignaciones por área para cada día

## Restricciones del Modelo

### Semanales
- 43-45 horas de trabajo por empleado
- 2 días de descanso no consecutivos
- Mínimo 5/7 del personal trabajando cada día
- Al menos 60% del personal presente en cada hora
- Cobertura mínima por área según especialidades

### Diarias
- Horarios de comida entre 11:00-17:00
- Surtido solo en primeras 2 horas (días específicos)
- Puerta siempre cubierta (sin 2 horas consecutivas por persona)
- Cajas según demanda exacta
- Personal asignado solo a sus áreas de especialidad

## Dependencias

- **Pyomo 6.7.3**: Framework de optimización matemática
- **Pandas 2.2.2**: Procesamiento de datos
- **CBC Solver**: Solver de programación lineal entera mixta

## Documentación

Para más detalles, consulta la carpeta `docs/`:
- **optimizador.md**: Descripción técnica completa
- **guia_uso.md**: Guía de uso detallada
- **mejoras_propuestas.md**: Roadmap de mejoras

## Autor

Jose Rodriguez

## Licencia

Proyecto interno - Uso restringido
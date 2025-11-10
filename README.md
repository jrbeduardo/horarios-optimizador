# Optimizador de Cajas

Este proyecto implementa un optimizador que utiliza programación lineal para resolver problemas de optimización relacionados con cajas. El proyecto utiliza CBC (COIN-OR Branch and Cut) como solver de programación lineal.

## Requisitos

- Python 3.8+
- uv (gestor de paquetes y ambientes virtuales)

## Instalación

1. Instalar uv (si no está instalado):
```powershell
pip install uv
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

- `main_optimizador.py`: Punto de entrada principal del programa
- `optimizador.py`: Implementación de la lógica de optimización
- `cajas.csv`: Datos de entrada con información de las cajas
- `pronostico.csv`: Datos de pronóstico para la optimización
- `requirements.txt`: Lista de dependencias del proyecto

## Uso

Para ejecutar el optimizador:

```powershell
python main_optimizador.py
```

## Dependencias Principales

- CBC Solver (COIN-OR Branch and Cut)
- PuLP para modelado de programación lineal
- Pandas para manejo de datos
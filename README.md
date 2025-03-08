# Simulador de Tráfico

Este proyecto implementa un simulador de tráfico utilizando FastAPI para la interfaz web.

## Requisitos

- Python 3.8+
- Dependencias listadas en requirements.txt

## Instalación

1. Clonar el repositorio
2. Crear un entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```
3. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Uso

1. Iniciar el servidor:
   ```bash
   uvicorn app.main:app --reload
   ```

2. Acceder a la API en `http://localhost:8000`

## Endpoints

- POST `/start`: Inicia una nueva simulación

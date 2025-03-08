## Christian Mendoza

# Simulador de Ecosistema

Este proyecto implementa un simulador de ecosistema utilizando FastAPI para la interfaz web.

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

## Endpoints y Ejemplos de Uso

### Iniciar Simulación (POST /start)

#### Usando Postman:
- Método: `POST`
- URL: `http://localhost:8000/start`
- Query Params:
  ```
  ticks: 150           (requerido, número de ticks para la simulación)
  num_animals: 32      (opcional, default=5)
  num_plants: 86       (opcional, default=10)
  num_fungi: 26        (opcional, default=3)
  ```

Ejemplo de URL completa:

 http://localhost:8000/start?ticks=150&num_animals=32&num_plants=84&num_fungi=26

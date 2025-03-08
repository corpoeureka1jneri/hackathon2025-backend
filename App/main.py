from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from .map_generator import MapGenerator
from .simulation import Simulation
import os

app = FastAPI(title="Simulador de Ecosistema")
simulation = None

# Asegurar que el directorio output existe
os.makedirs("output", exist_ok=True)

@app.post("/start")
def start_simulation(
    ticks: int = Query(..., description="Número de ticks para la simulación"),
    num_animals: int = Query(5, description="Número inicial de animales"),
    num_plants: int = Query(10, description="Número inicial de plantas"),
    num_fungi: int = Query(3, description="Número inicial de hongos")
):
    """Inicia la simulación con un número de ticks y entidades iniciales."""
    global simulation
    
    # Generar mapa
    map_gen = MapGenerator()
    map_gen.generate_map()
    
    # Añadir entidades adicionales según los parámetros
    map_gen.add_random_entities(
        num_animals=num_animals,
        num_plants=num_plants,
        num_fungi=num_fungi
    )
    
    # Iniciar simulación
    simulation = Simulation(map_gen.grid, ticks)
    simulation.run()
    
    return {"message": "Simulación completada", "ticks": ticks}

@app.get("/download")
def download_results():
    """Descarga el archivo XLS con los resultados de la simulación."""
    if not simulation:
        return {"error": "No hay resultados de simulación disponibles"}
        
    file_path = "output/simulation_results.xlsx"
    if os.path.exists(file_path):
        return FileResponse(
            file_path, 
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="ecosystem_simulation_results.xlsx"
        )
    return {"error": "Archivo de resultados no encontrado"}

@app.get("/")
def read_root():
    return {
        "title": "Simulador de Ecosistema",
        "description": "API para simular un ecosistema con animales, plantas y hongos",
        "endpoints": [
            {"path": "/start", "method": "POST", "description": "Inicia una nueva simulación"},
            {"path": "/download", "method": "GET", "description": "Descarga los resultados en formato Excel"}
        ]
    }

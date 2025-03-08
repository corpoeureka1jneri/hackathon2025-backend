import pandas as pd
from .grid import Grid
from .models import Animal, Plant, Fungi

class Simulation:
    """Controla la ejecución de la simulación."""
    
    def __init__(self, grid: Grid, ticks: int):
        self.grid = grid  # Cuadrícula de 24x24
        self.ticks = ticks  # Número total de ticks a ejecutar
        self.current_tick = 0  # Contador de tiempo
        self.history = []  # Almacena estados de la simulación

    def run(self):
        """Ejecuta la simulación por el número de ticks configurado."""
        print(f"Iniciando simulación por {self.ticks} ticks...")

        # Guardar estado inicial
        self.save_state()

        for tick in range(1, self.ticks + 1):
            self.current_tick = tick
            self.update_grid()
            self.save_state()
        
        print("Simulación completada.")
        self.generate_report()

    def update_grid(self):
        """Actualiza todas las entidades y celdas en la cuadrícula."""
        self.grid.update()

    def save_state(self):
        """Guarda el estado actual de la cuadrícula."""
        state = []
        for x in range(self.grid.size):
            row = []
            for y in range(self.grid.size):
                tile = self.grid.tiles[x][y]
                cell_info = {
                    "tile_type": tile.type,
                    "entity": None,
                    "entity_state": None,
                    "entity_size": None,
                    "entity_hp": None
                }
                
                # Entidad principal en la celda
                if tile.entity:
                    cell_info["entity"] = type(tile.entity).__name__
                    cell_info["entity_state"] = tile.entity.state
                    
                    if isinstance(tile.entity, (Animal, Plant)):
                        cell_info["entity_size"] = tile.entity.size
                        
                    if isinstance(tile.entity, (Plant, Fungi)):
                        cell_info["entity_hp"] = tile.entity.hp
                
                # Entidades adicionales (hongos sobre entidades muertas)
                additional_entities = []
                for entity in self.grid.get_entities_at(x, y):
                    if entity != tile.entity:  # Evitar duplicados
                        entity_info = {
                            "type": type(entity).__name__,
                            "state": entity.state
                        }
                        if isinstance(entity, Fungi):
                            entity_info["hp"] = entity.hp
                        additional_entities.append(entity_info)
                
                if additional_entities:
                    cell_info["additional_entities"] = additional_entities
                
                row.append(cell_info)
            state.append(row)
        
        self.history.append(state)

    def get_current_state(self):
        """Devuelve el estado actual de la simulación en formato legible."""
        if not self.history:
            return {"error": "No hay datos de simulación disponibles"}
            
        current_state = self.history[-1]
        
        # Contar entidades por tipo y estado
        counts = {
            "animal_small": 0,
            "animal_big": 0,
            "plant_low": 0,
            "plant_high": 0,
            "fungi": 0,
            "dead_entities": 0
        }
        
        for row in current_state:
            for cell in row:
                if cell["entity"] == "Animal":
                    if cell["entity_size"] == "animal-small":
                        counts["animal_small"] += 1
                    else:
                        counts["animal_big"] += 1
                elif cell["entity"] == "Plant":
                    if cell["entity_size"] == "plant-low":
                        counts["plant_low"] += 1
                    else:
                        counts["plant_high"] += 1
                elif cell["entity"] == "Fungi":
                    counts["fungi"] += 1
                    
                if cell["entity_state"] == "dead":
                    counts["dead_entities"] += 1
        
        return {
            "tick": self.current_tick,
            "total_ticks": self.ticks,
            "entity_counts": counts
        }

    def generate_report(self):
        """Genera un archivo XLS con los resultados de la simulación."""
        print("Generando reporte...")
        file_path = "output/simulation_results.xlsx"

        # Crear un Excel Writer
        writer = pd.ExcelWriter(file_path, engine='openpyxl')

        # Para cada tick, crear una hoja con el estado
        for tick, state in enumerate(self.history):
            # Convertir el estado a un formato más simple para Excel
            simplified_state = []
            for x in range(self.grid.size):
                row = []
                for y in range(self.grid.size):
                    cell = state[x][y]
                    cell_repr = cell["tile_type"]
                    
                    if cell["entity"]:
                        if cell["entity"] == "Animal":
                            cell_repr += f":{cell['entity_size']}:{cell['entity_state']}"
                        elif cell["entity"] == "Plant":
                            cell_repr += f":{cell['entity_size']}:{cell['entity_state']}:{cell['entity_hp']}"
                        elif cell["entity"] == "Fungi":
                            cell_repr += f":fungi:{cell['entity_state']}:{cell['entity_hp']}"
                    
                    # Añadir entidades adicionales si existen
                    if "additional_entities" in cell:
                        for add_entity in cell["additional_entities"]:
                            cell_repr += f" + {add_entity['type']}:{add_entity['state']}"
                    
                    row.append(cell_repr)
                simplified_state.append(row)
            
            # Crear DataFrame y guardar en Excel
            df = pd.DataFrame(simplified_state)
            df.to_excel(writer, sheet_name=f'Tick {tick}')

        # Crear una hoja de resumen
        summary_data = self.generate_summary()
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Resumen')

        writer.close()
        print(f"Reporte guardado en {file_path}")

    def generate_summary(self):
        """Genera un resumen de la simulación para incluir en el reporte."""
        summary = []
        
        for tick, state in enumerate(self.history):
            # Contar entidades por tipo
            counts = {
                "tick": tick,
                "animal_small": 0,
                "animal_big": 0,
                "plant_low": 0,
                "plant_high": 0,
                "fungi": 0,
                "dead_entities": 0,
                "water_tiles": 0,
                "rock_tiles": 0,
                "soil_tiles": 0,
                "soil+_tiles": 0
            }
            
            for x in range(self.grid.size):
                for y in range(self.grid.size):
                    cell = state[x][y]
                    
                    # Contar tipos de suelo
                    counts[f"{cell['tile_type']}_tiles"] += 1
                    
                    # Contar entidades
                    if cell["entity"] == "Animal":
                        if cell["entity_size"] == "animal-small":
                            counts["animal_small"] += 1
                        else:
                            counts["animal_big"] += 1
                    elif cell["entity"] == "Plant":
                        if cell["entity_size"] == "plant-low":
                            counts["plant_low"] += 1
                        else:
                            counts["plant_high"] += 1
                    elif cell["entity"] == "Fungi":
                        counts["fungi"] += 1
                        
                    if cell["entity_state"] == "dead":
                        counts["dead_entities"] += 1
            
            summary.append(counts)
        
        return summary

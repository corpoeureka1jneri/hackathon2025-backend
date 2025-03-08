import random
from .grid import Grid, Tile
from .models import Animal, Plant, Fungi

class MapGenerator:
    
    TILE_TYPES = ["rock", "soil", "water", "soil+"]

    def __init__(self):
        self.grid = Grid() 

    def generate_map(self):
        """Genera un mapa aleatorio con distribución de tipos de suelo."""
        # Generar tipos de suelo aleatorios
        for x in range(self.grid.size):
            for y in range(self.grid.size):
                tile_type = self.get_random_tile_type()
                self.grid.tiles[x][y] = Tile(x, y, tile_type)

        # Asegurar que haya al menos una casilla de cada tipo requerido
        self.ensure_minimum_tiles()

        # Colocar entidades iniciales mínimas requeridas
        self.place_initial_entities()

    def get_random_tile_type(self):
        """Devuelve un tipo de suelo aleatorio según las probabilidades definidas."""
        probabilities = {
            "water": 0.1,
            "rock": 0.2,
            "soil": 0.5,
            "soil+": 0.2
        }
        return random.choices(
            list(probabilities.keys()),
            weights=list(probabilities.values()),
            k=1
        )[0]

    def ensure_minimum_tiles(self):
        """Asegura que haya al menos una casilla de cada tipo requerido (rock, soil, water)."""
        required_types = ["rock", "soil", "water"]  # Tipos mínimos requeridos
        placed = {tile_type: False for tile_type in required_types}

        # Verificar qué tipos ya existen
        for x in range(self.grid.size):
            for y in range(self.grid.size):
                tile_type = self.grid.tiles[x][y].type
                if tile_type in placed:
                    placed[tile_type] = True

        # Colocar los tipos faltantes
        for tile_type, exists in placed.items():
            if not exists:
                # Intentar varias posiciones hasta encontrar una adecuada
                for _ in range(10):  # Intentar hasta 10 veces
                    x, y = random.randint(0, self.grid.size-1), random.randint(0, self.grid.size-1)
                    # Evitar sobrescribir una celda que ya tiene un tipo requerido diferente
                    current_type = self.grid.tiles[x][y].type
                    if current_type not in required_types or all(placed.values()):
                        self.grid.tiles[x][y].type = tile_type
                        placed[tile_type] = True
                        break

    def place_initial_entities(self):
        """Coloca al menos 2 entidades iniciales: 1 animal y 1 planta (requisito mínimo)."""
        # Colocar al menos un animal
        animal_count = 0
        plant_count = 0
        
        # Intentar colocar 2 animales
        while animal_count < 2:
            x, y = random.randint(0, self.grid.size-1), random.randint(0, self.grid.size-1)
            tile = self.grid.tiles[x][y]
            
            # Crear animal con water_born si nace en agua
            water_born = (tile.type == "water")
            animal = Animal(x, y, water_born)
            
            if self.grid.place_entity(x, y, animal):
                animal_count += 1
                
            # Evitar bucle infinito si no hay espacio
            if animal_count == 1 and self._count_empty_tiles() < 1:
                break

        # Colocar al menos 2 plantas (no en roca)
        while plant_count < 2:
            x, y = random.randint(0, self.grid.size-1), random.randint(0, self.grid.size-1)
            tile = self.grid.tiles[x][y]
            
            if tile.type != "rock" and not tile.entity:
                plant = Plant(x, y)
                if self.grid.place_entity(x, y, plant):
                    plant_count += 1
                    
            if plant_count == 1 and self._count_empty_tiles() < 1:
                break

    def _count_empty_tiles(self):
        """Cuenta el número de celdas vacías en el mapa."""
        count = 0
        for x in range(self.grid.size):
            for y in range(self.grid.size):
                if not self.grid.tiles[x][y].entity:
                    count += 1
        return count

    def add_random_entities(self, num_animals=5, num_plants=10, num_fungi=3):
        """Añade un número específico de entidades aleatorias al mapa."""
        # Añadir animales
        for _ in range(num_animals):
            for attempt in range(10):  # Intentar 10 veces
                x, y = random.randint(0, self.grid.size-1), random.randint(0, self.grid.size-1)
                water_born = (self.grid.tiles[x][y].type == "water")
                animal = Animal(x, y, water_born)
                if self.grid.place_entity(x, y, animal):
                    break

        # Añadir plantas
        for _ in range(num_plants):
            for attempt in range(10):
                x, y = random.randint(0, self.grid.size-1), random.randint(0, self.grid.size-1)
                if self.grid.tiles[x][y].type != "rock" and not self.grid.tiles[x][y].entity:
                    plant = Plant(x, y)
                    if self.grid.place_entity(x, y, plant):
                        break

        # Añadir hongos
        for _ in range(num_fungi):
            for attempt in range(10):
                x, y = random.randint(0, self.grid.size-1), random.randint(0, self.grid.size-1)
                if self.grid.tiles[x][y].type != "rock" and not self.grid.tiles[x][y].entity:
                    fungi = Fungi(x, y)
                    if self.grid.place_entity(x, y, fungi):
                        break

    def show_grid(self):
        for row in self.grid.tiles:
            for tile in row:
                print(tile.type, end=" ")
            print()



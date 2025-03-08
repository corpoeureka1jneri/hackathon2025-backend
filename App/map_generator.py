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


    def add_random_entities(self, num_animals, num_plants, num_fungi):
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



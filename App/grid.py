from random import *
from .models import Animal, Plant, Fungi
import random

class Tile:
    
    SOIL_CYCLE = ["rock", "soil", "soil+"]  # Ciclo del suelo

    def __init__(self, x, y, tile_type="soil"):
        self.x = x
        self.y = y
        self.type = tile_type  
        self.entity = None  

    def upgrade_soil(self):
        """Avanza en el ciclo de tierra si es posible."""
        if self.type in self.SOIL_CYCLE and self.type != "soil+":
            current_index = self.SOIL_CYCLE.index(self.type)
            if current_index < len(self.SOIL_CYCLE) - 1:
                self.type = self.SOIL_CYCLE[current_index + 1]

    def degrade_soil(self):
        """Retrocede en el ciclo de tierra si es posible."""
        if self.type in self.SOIL_CYCLE and self.type != "rock":
            current_index = self.SOIL_CYCLE.index(self.type)
            if current_index > 0:
                self.type = self.SOIL_CYCLE[current_index - 1]

    def is_walkable(self, entity):
        """Determina si una entidad puede moverse a esta celda."""
        # Si hay una entidad viva o una planta alta, no se puede mover ahí
        if self.entity and (self.entity.state == "live" or 
                           (isinstance(self.entity, Plant) and 
                            self.entity.size == "plant-high")):
            return False
            
        # Reglas específicas por tipo de entidad
        if isinstance(entity, Animal):
            if self.type == "water" and not entity.water_born:
                return False
        elif isinstance(entity, Plant):
            if self.type == "rock":
                return False
        elif isinstance(entity, Fungi):
            if self.type == "rock":
                return False
                
        return True

class Grid:
    """Representa el ecosistema como una cuadrícula de 24x24."""

    def __init__(self):
        self.size = 24
        self.tiles = [[Tile(x, y, self.random_tile_type()) for y in range(self.size)] for x in range(self.size)]
        self.dead_entities = []  # Lista para rastrear entidades muertas
        self.entities_to_remove = []  # Lista para entidades que deben ser eliminadas

    def random_tile_type(self):
        """Genera un tipo de tile aleatorio según la distribución inicial."""
        types = ["water", "rock", "soil", "soil+"]
        probabilities = [0.1, 0.2, 0.5, 0.2] 
        return random.choices(types, weights=probabilities, k=1)[0]

    def place_entity(self, x, y, entity):
        """Coloca una entidad en una celda si es válida."""
        if 0 <= x < self.size and 0 <= y < self.size:
            tile = self.tiles[x][y]
            
            # Verificar reglas específicas
            if (isinstance(entity, Plant) and tile.type == "rock"):
                return False
                
            if not tile.entity:
                tile.entity = entity
                entity.x, entity.y = x, y
                
                # Si es un animal y nace en agua, marcar como water_born
                if isinstance(entity, Animal) and tile.type == "water":
                    entity.water_born = True
                    
                return True
        return False

    def update(self):
        """Avanza un tick en la simulación, actualizando entidades y suelo."""
        # Actualizar todas las entidades
        for x in range(self.size):
            for y in range(self.size):
                tile = self.tiles[x][y]
                if tile.entity:
                    if tile.entity.state == "live":
                        tile.entity.update(self)
                    elif tile.entity.state == "remove":
                        self.entities_to_remove.append(tile.entity)
        
        # Actualizar entidades muertas
        for entity in list(self.dead_entities):
            if entity.state == "remove":
                self.entities_to_remove.append(entity)
        
        # Eliminar entidades marcadas para remoción
        self.remove_marked_entities()
        
        # Procesar entidades muertas y posible aparición de hongos
        self.process_dead_entities()

    def remove_marked_entities(self):
        """Elimina las entidades marcadas con estado 'remove'."""
        for entity in self.entities_to_remove:
            if entity in self.dead_entities:
                self.dead_entities.remove(entity)
            elif self.tiles[entity.x][entity.y].entity == entity:
                self.tiles[entity.x][entity.y].entity = None

    def process_dead_entities(self):
        """Procesa entidades muertas y genera hongos aleatoriamente."""
        for x in range(self.size):
            for y in range(self.size):
                tile = self.tiles[x][y]
                
                # Si hay una entidad muerta, 10% de posibilidad de generar un hongo
                if tile.entity and tile.entity.state == "dead" and random.random() < 0.1:
                    # Verificar si ya hay un hongo en esta posición
                    has_fungi = False
                    for entity in self.get_entities_at(x, y):
                        if isinstance(entity, Fungi):
                            has_fungi = True
                            break
                            
                    if not has_fungi:
                        new_fungi = Fungi(x, y)
                        self.dead_entities.append(new_fungi)

    def get_entities_at(self, x, y):
        """Obtiene todas las entidades en una posición."""
        entities = []
        
        # Entidad principal en la celda
        if self.tiles[x][y].entity:
            entities.append(self.tiles[x][y].entity)
            
        # Entidades muertas o hongos en la misma posición
        for entity in self.dead_entities:
            if entity.x == x and entity.y == y:
                entities.append(entity)
                
        return entities

    def get_dead_entities_at(self, x, y):
        """Obtiene entidades muertas en una posición específica."""
        dead_entities = []
        
        # Entidad principal si está muerta
        if self.tiles[x][y].entity and self.tiles[x][y].entity.state == "dead":
            dead_entities.append(self.tiles[x][y].entity)
            
        # Otras entidades muertas en la misma posición
        for entity in self.dead_entities:
            if entity.x == x and entity.y == y and entity.state == "dead":
                dead_entities.append(entity)
                
        return dead_entities

import random

class Entity:
    """Clase base para todas las entidades del ecosistema."""
    # Estados posibles
    LIVE = "live"    # Estado activo, permite movimiento, colisión y reproducción
    DEAD = "dead"    # Estado inerte, pero aún existente en la grilla
    REMOVE = "remove"  # La entidad debe ser eliminada de la grilla
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = self.LIVE  # Estado inicial: vivo
        self.ticks_alive = 0

    def update(self):
        self.ticks_alive += 1

class Animal(Entity):
    def __init__(self, x, y, water_born=False):
        super().__init__(x, y)
        self.size = "animal-small"
        self.hunger_counter = 0
        self.water_born = water_born
        # Vida máxima de 24 ticks con desviación de 1 tick
        self.max_life = random.randint(23, 25)
        self.reproduction_counter = 0

    def move(self, grid):
        # Se mueve aleatoriamente 1-3 celdas en dirección aleatoria
        if self.state != self.LIVE:
            return

        steps = random.randint(1, 3)
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        direction = random.choice(directions)
        
        for _ in range(steps):
            new_x = self.x + direction[0]
            new_y = self.y + direction[1]
            
            # Verificar límites del mapa
            if 0 <= new_x < grid.size and 0 <= new_y < grid.size:
                tile = grid.tiles[new_x][new_y]
                
                # Verificar si puede moverse a esa casilla
                if not tile.entity and self.can_move_to(tile):
                    # Eliminar de la posición actual
                    grid.tiles[self.x][self.y].entity = None
                    # Actualizar posición
                    self.x, self.y = new_x, new_y
                    # Colocar en nueva posición
                    tile.entity = self
                else:
                    break
            else:
                break

    def can_move_to(self, tile):
        # Si nació en agua, no puede moverse a través de otras
        if tile.type == "water" and not self.water_born:
            return False
        return True

    def eat(self, grid):
        if self.state != self.LIVE:
            return
            
        # Buscar plantas/hongos alrededor
        food_found = False
        adjacent_cells = []
        
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                nx, ny = self.x + dx, self.y + dy
                if 0 <= nx < grid.size and 0 <= ny < grid.size:
                    if grid.tiles[nx][ny].entity and grid.tiles[nx][ny].entity != self:
                        adjacent_cells.append(grid.tiles[nx][ny])
        
        # Filtrar entidades comestibles
        food = []
        for tile in adjacent_cells:
            entity = tile.entity
            if isinstance(entity, Plant) and entity.state == self.LIVE:
                if self.size == "animal-big" or (self.size == "animal-small" and entity.size == "plant-low"):
                    food.append(entity)
            elif isinstance(entity, Fungi) and entity.state == self.LIVE and self.size == "animal-small":
                food.append(entity)
        
        if food:
            food_found = True
            target = random.choice(food)
            
            # Consumir según las reglas
            if self.size == "animal-big":
                if isinstance(target, Plant):
                    if target.size == "plant-high":
                        target.hp -= 1
                    elif target.size == "plant-low":
                        target.hp -= 2
                elif isinstance(target, Fungi):
                    target.hp -= 2
            else:  # animal-small
                target.hp -= 1
            
            # Verificar si la entidad consumida murió
            if target.hp <= 0:
                target.state = self.DEAD
            
            self.hunger_counter = 0
        else:
            self.hunger_counter += 1
            
        # Si no come en 3 ticks consecutivos, muere
        if self.hunger_counter >= 3:
            self.state = self.DEAD
            
        return food_found

    def reproduce(self, grid):
        if self.state != self.LIVE:
            return
            
        self.reproduction_counter += 1
        
        # Cada 6 ticks, 50% de posibilidad de reproducirse si hay otro animal cerca
        if self.reproduction_counter >= 6:
            self.reproduction_counter = 0
            
            # Buscar otros animales alrededor
            has_neighbor = False
            empty_cells = []
            
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = self.x + dx, self.y + dy
                    if 0 <= nx < grid.size and 0 <= ny < grid.size:
                        tile = grid.tiles[nx][ny]
                        if tile.entity and isinstance(tile.entity, Animal) and tile.entity.state == self.LIVE:
                            has_neighbor = True
                        elif not tile.entity and tile.type != "rock":
                            empty_cells.append((nx, ny))
            
            if has_neighbor and empty_cells and random.random() < 0.5:
                # Crear un nuevo animal pequeño
                x, y = random.choice(empty_cells)
                new_animal = Animal(x, y, water_born=(grid.tiles[x][y].type == "water"))
                grid.tiles[x][y].entity = new_animal

    def update(self, grid):
        super().update()
        
        # Verificar si debe morir por edad
        if self.ticks_alive >= self.max_life:
            self.state = self.DEAD
            return
            
        # A los 12 ticks se convierte en animal grande
        if self.ticks_alive == 12 and self.state == self.LIVE:
            self.size = "animal-big"
            
        # Primero se mueve
        self.move(grid)
        
        # Luego intenta comer
        self.eat(grid)
        
        # Finalmente intenta reproducirse
        self.reproduce(grid)

class Plant(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.size = "plant-low"
        self.hp = 5
        # Vida máxima de 30 ticks con desviación de 3 ticks
        self.max_life = random.randint(27, 33)
        self.reproduction_counter = 0

    def grow(self, tile):
        # Se convierte en plant-high después de 24 ticks (o 16 en soil+)
        if self.size == "plant-low" and self.state == self.LIVE:
            threshold = 16 if tile.type == "soil+" else 24
            if self.ticks_alive >= threshold:
                self.size = "plant-high"

    def reproduce(self, grid):
        if self.state != self.LIVE:
            return
            
        self.reproduction_counter += 1
        
        # Cada 8 ticks, 30% de posibilidad de generar una planta baja alrededor
        if self.reproduction_counter >= 8:
            self.reproduction_counter = 0
            
            if random.random() < 0.3:
                # Buscar celdas vacías alrededor
                empty_cells = []
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        nx, ny = self.x + dx, self.y + dy
                        if 0 <= nx < grid.size and 0 <= ny < grid.size:
                            tile = grid.tiles[nx][ny]
                            # Verificar que no haya plantas y que no sea roca
                            if not tile.entity and tile.type != "rock":
                                empty_cells.append((nx, ny))
                
                if empty_cells:
                    x, y = random.choice(empty_cells)
                    new_plant = Plant(x, y)
                    grid.tiles[x][y].entity = new_plant

    def update(self, grid):
        super().update()
        
        tile = grid.tiles[self.x][self.y]
        
        # Verificar si debe morir por edad
        if self.ticks_alive >= self.max_life:
            self.state = self.DEAD
            # Si es plant-high, degrada la tierra al morir
            if self.size == "plant-high":
                tile.degrade_soil()
            return
            
        # Crecer
        self.grow(tile)
        
        # Reproducirse
        self.reproduce(grid)
        
        # Si pierde todo su HP, muere
        if self.hp <= 0:
            self.state = self.DEAD
            # Si es plant-high, degrada la tierra al morir
            if self.size == "plant-high":
                tile.degrade_soil()

class Fungi(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 3
        self.tick_counter = 0

    def update(self, grid):
        super().update()
        
        if self.hp <= 0:
            self.state = self.REMOVE
            return
            
        tile = grid.tiles[self.x][self.y]
        
        # Buscar entidad muerta debajo
        dead_entity_below = False
        for entity in grid.get_dead_entities_at(self.x, self.y):
            dead_entity_below = True
            break
            
        if dead_entity_below:
            self.tick_counter += 1
            
            # Ganar 1 HP cada 2 ticks si hay una entidad muerta debajo
            if self.tick_counter % 2 == 0:
                self.hp += 1
                
            # Cada 2 ticks, 20% de posibilidad de remover entidad muerta y mejorar el suelo
            if self.tick_counter % 2 == 0 and random.random() < 0.2:
                for entity in grid.get_dead_entities_at(self.x, self.y):
                    grid.remove_entity(entity)
                    tile.upgrade_soil()
                    break








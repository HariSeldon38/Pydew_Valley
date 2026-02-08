"""
Key system of the soil is the grid.
it is create in SoilLayer.create_soil_grid
it is a grid representing the whole map

Access a specific cell from a rect :
    x = rect.x // TILE_SIZE
    y = rect.y // TILE_SIZE
    SoilLayer.grid[y][x]

A cell is a list, can have the following states :
    Empty if not farmable
    F append if farmable (cannot change OK)
    X append if labored
    W if watered (can have more that one 'W') (CANNOT APPEAR ON SAVE NORMAL CAUSE RESET EACH DAY)
    P_{seed}_{age} if a seed is planted (for instance P_corn_1)

SoilLayer.create_hit_rects : create a invisible rect for each cell containing "F" but not "X"
SoilLayer.soil_sprites are all the sprites for labored cells
To access a soil_sprite based on grid position :
    SoilLayer.soil_sprites_map[(index_col, index_row)]

WARNING:
    All the soil system is not based on the grid as it was implemented after the fact.
    The collisions with target position of the player are checked against the sprites themselves, not the cell
"""

from pytmx.util_pygame import load_pygame
from random import choice, randint
from settings import *
from support import *

class SoilTile(pygame.sprite.Sprite):

    tile_dict = {}

    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        pixel_position = (pos[0]*TILE_SIZE, pos[1]*TILE_SIZE)
        self.rect = self.image.get_rect(topleft = pixel_position)
        self.z = LAYERS['soil']
        SoilTile.tile_dict[pos] = self

    @staticmethod
    def kill_tile(pos):
        # remove from map before killing so other code won't find a dead sprite
        tile = SoilTile.tile_dict.pop(pos, None)
        tile.kill()

class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil water']

class Plant(pygame.sprite.Sprite):
    def __init__(self, plant_type, groups, soil, check_watered, grid_pos, age=0):
        super().__init__(groups)
        self.plant_type = plant_type
        self.row_index = grid_pos[0]
        self.col_index = grid_pos[1]
        self.frames = import_folder(f'../graphics/fruit/{plant_type}')
        self.soil = soil
        self.check_watered = check_watered

        #plant growing
        self.age = age
        self.max_age = len(self.frames) - 1
        self.grow_speed = GROW_SPEED[plant_type]
        self.harvestable = False

        #sprite setup
        self.image = self.frames[self.age]
        self.y_offset = pygame.math.Vector2(0, -10) if plant_type == 'corn' else pygame.math.Vector2(0, -5)
        self.rect = self.image.get_rect(midbottom = self.soil.rect.midbottom + self.y_offset)
        self.z = LAYERS['ground plant']
        if int(self.age) > 0:
            self.z = LAYERS['main']
            self.hitbox = self.rect.copy().inflate(-26, -self.rect.height * 0.4)

    def grow(self):
        if self.check_watered(self.rect.center):
            self.age += self.grow_speed
            if int(self.age) > 0:
                self.z = LAYERS['main']
                self.hitbox = self.rect.copy().inflate(-26, -self.rect.height * 0.4)

            if self.age >= self.max_age:
                self.age = self.max_age
                self.harvestable = True
            self.image = self.frames[int(self.age)]
            self.rect = self.image.get_rect(midbottom = self.soil.rect.midbottom + self.y_offset)

class SoilLayer:
    def __init__(self, all_sprites, collision_sprites, sound_manager):

        #sprite groups
        self.all_sprites = all_sprites
        self.collision_sprites = collision_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.soil_sprites_map = dict() #this is use to map grid coordinate to sprites
        self.water_sprites = pygame.sprite.Group()
        self.plant_sprites = pygame.sprite.Group()

        #graphics
        self.soil_surfs = import_folder_with_names('../graphics/soil')
        self.soil_water = import_folder('../graphics/soil_water')

        self.init_soil_grid()
        self.create_hit_rects()

        self.sound_manager = sound_manager

    def init_soil_grid(self):
        ground = pygame.image.load('../graphics/world/ground.png')
        h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() //TILE_SIZE #need to be hardcoded when dev is over and get rid of the ground load

        self.grid = [ [[] for columns in range(h_tiles)] for rows in range(v_tiles)]
        for x,y, _ in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append("F")

    def create_soil_tiles(self, pos=None):
        """
        TILING SYSTEM
        If arg position is not None : go through the 8 neighboors of the corresponding cell to adjust the soil tiles
        Else, recreate ALL the soil_tiles
        """
        if pos:
            target_col = pos[0]
            target_row = pos[1]
            vertical_range = range(target_row - 1, target_row + 2)
            horizontal_range = range(target_col - 1, target_col + 2)
        else:
            vertical_range = range(0, len(self.grid))
            horizontal_range = range(0, len(self.grid[0]))

        for index_row in vertical_range:
            for index_col in horizontal_range:

                row = self.grid[index_row]
                cell = row[index_col]
                if 'X' in cell:

                    t = 'X' in self.grid[index_row - 1][index_col]
                    b = 'X' in self.grid[index_row + 1][index_col]
                    r = 'X' in row[index_col + 1]
                    l = 'X' in row[index_col - 1]

                    tile_type = 'o'
                    if all((t,r,b,l)): tile_type = 'x'
                    if l and not any((t,r,b)): tile_type = 'r' #horizontal
                    if r and not any((t, l, b)): tile_type = 'l'
                    if all((l,r)) and not any((t,b)): tile_type = 'lr'
                    if t and not any((l,r,b)): tile_type = 'b' #vertical
                    if b and not any((t, l, r)): tile_type = 't'
                    if all((t,b)) and not any((r,l)): tile_type = 'tb'
                    if l and b and not any((t,r)): tile_type = 'tr' #corner
                    if r and b and not any((t,l)): tile_type = 'tl'
                    if l and t and not any((b,r)): tile_type = 'br'
                    if r and t and not any((b,l)): tile_type = 'bl'
                    if all((t,b,r)) and not l: tile_type = 'tbr' #Tshape
                    if all((t,b,l)) and not r: tile_type = 'tbl'
                    if all((l,r,t)) and not b: tile_type = 'lrb'
                    if all((l,b,r)) and not t: tile_type = 'lrt'

                    if SoilTile.tile_dict.get((index_col,index_row), False):
                        SoilTile.kill_tile((index_col,index_row))

                    self.soil_sprites_map[(index_col,index_row)] = SoilTile(
                        pos = (index_col,index_row),
                        surf = self.soil_surfs[tile_type],
                        groups = [self.all_sprites, self.soil_sprites])

    def create_hit_rects(self):
        """Create an invisible rect for each farmable cell (cell containing "F")"""
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'F' in cell and not 'X' in cell:
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    rect = pygame.Rect(x,y,TILE_SIZE,TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE

                if 'F' in self.grid[y][x]:
                    if not 'X' in self.grid[y][x]:
                        self.grid[y][x].append('X')
                        self.create_soil_tiles((x,y))
                        return True
                    else:
                        self.grid[y][x].remove('X')
                        SoilTile.kill_tile((x,y))
                        self.create_soil_tiles((x,y))
                        return True
        return False

    def get_watered(self, target_pos):
        """for now it is possible to water crops thrice but the sprite added is random each time
        so sometime we don't see a different after watering more than once, that is because of that randomness"""
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target_pos):
                x = soil_sprite.rect.x // TILE_SIZE
                y = soil_sprite.rect.y // TILE_SIZE
                if self.grid[y][x].count("W") < 3:
                    self.grid[y][x].append("W")
                    WaterTile((soil_sprite.rect.x,soil_sprite.rect.y),choice(self.soil_water), [self.water_sprites, self.all_sprites])

    def water_all(self, rain_level):
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'X' in cell and cell.count('W') < 3:
                    if randint(1,3600//rain_level) == 1:
                        cell.append('W')
                        x = index_col * TILE_SIZE
                        y = index_row * TILE_SIZE
                        WaterTile((x,y), choice(self.soil_water), [self.all_sprites, self.water_sprites])

    def remove_water(self):
        for sprite in self.water_sprites.sprites():
            sprite.kill()
        for row in self.grid:
            for cell in row:
                if 'W' in cell:
                    cell.remove('W')

    def check_watered(self, pos):
        x = pos[0] // TILE_SIZE
        y = pos[1] // TILE_SIZE
        cell = self.grid[y][x]
        is_watered = 'W' in cell
        return is_watered

    def plant_seed(self, target, seed):
        for soil_sprite in self.soil_sprites.sprites():
            if soil_sprite.rect.collidepoint(target):
                col_index = soil_sprite.rect.x // TILE_SIZE
                row_index = soil_sprite.rect.y // TILE_SIZE
                if 'P' not in [symbol.split("_")[0] for symbol in self.grid[row_index][col_index]]:
                    self.grid[row_index][col_index].append(f'P_{seed}_0')
                    Plant(seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], soil_sprite, self.check_watered, (row_index, col_index))
                    self.sound_manager.play('plant')
                    return True
        return False

    def load_plants(self):
        for index_row in range(0, len(self.grid)):
            for index_col in range(0, len(self.grid[0])):
                row = self.grid[index_row]
                cell = [symbol for symbol in row[index_col] if symbol.startswith("P_")]
                if len(cell) == 1:
                    _, seed, age = cell[0].split("_")
                    Plant(seed, [self.all_sprites, self.plant_sprites, self.collision_sprites], self.soil_sprites_map[(index_col, index_row)],
                          self.check_watered, (index_row, index_col), age=int(age))
                elif len(cell) > 1:
                    print("A cell contains more than one P (plant)")

    def update_plants(self):
        for row in self.grid:
            for cell in row:
                cell = [symbol for symbol in cell if not symbol.startswith("P_")]
        for plant in self.plant_sprites.sprites():
            plant.grow()
            self.grid[plant.row_index][plant.col_index] = [symbol for symbol in self.grid[plant.row_index][plant.col_index] if not symbol.startswith("P_")]
            self.grid[plant.row_index][plant.col_index].append(f"P_{plant.plant_type}_{plant.age}")

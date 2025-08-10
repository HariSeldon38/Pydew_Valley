import pygame
from pytmx.util_pygame import load_pygame
from random import choice, randint
from settings import *
from support import *

class SoilTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil']

class WaterTile(pygame.sprite.Sprite):
    def __init__(self, pos, surf, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(topleft = pos)
        self.z = LAYERS['soil water']


class SoilLayer:
    def __init__(self, all_sprites):

        #sprite groups
        self.all_sprites = all_sprites
        self.soil_sprites = pygame.sprite.Group()
        self.water_sprites = pygame.sprite.Group()

        #graphics
        self.soil_surfs = import_folder_with_names('../graphics/soil')
        self.soil_water = import_folder('../graphics/soil_water')

        self.create_soil_grid()
        self.create_hit_rects()

    def create_soil_grid(self):
        ground = pygame.image.load('../graphics/world/ground.png')
        h_tiles, v_tiles = ground.get_width() // TILE_SIZE, ground.get_height() //TILE_SIZE #need to be hardcoded when dev is over and get rid of the ground load

        self.grid = [ [[] for columns in range(h_tiles)] for rows in range(v_tiles)]
        for x,y, _ in load_pygame('../data/map.tmx').get_layer_by_name('Farmable').tiles():
            self.grid[y][x].append("F")

    def create_hit_rects(self):
        self.hit_rects = []
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
                if 'F' in cell:
                    x = index_col * TILE_SIZE
                    y = index_row * TILE_SIZE
                    rect = pygame.Rect(x,y,TILE_SIZE,TILE_SIZE)
                    self.hit_rects.append(rect)

    def get_hit(self, point):
        for rect in self.hit_rects:
            if rect.collidepoint(point):
                x = rect.x // TILE_SIZE
                y = rect.y // TILE_SIZE

                if 'F' in self.grid[y][x] and not 'X' in self.grid[y][x]:
                    self.grid[y][x].append('X')
                    self.create_soil_tiles()
                #if self.raining:
                    #self.get_watered(point)

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
                    if randint(1,1500//rain_level) == 1:
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

    def create_soil_tiles(self):
        self.soil_sprites.empty()
        for index_row, row in enumerate(self.grid):
            for index_col, cell in enumerate(row):
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


                    SoilTile(
                        pos = (index_col*TILE_SIZE,index_row*TILE_SIZE),
                        surf = self.soil_surfs[tile_type],
                        groups = [self.all_sprites, self.soil_sprites])






"""there is a lot of thing I'm not really sure of in this file of the tutorial : first we are checking twice if farmable with "F"
we convert px to tiles then tiles to px...
"""
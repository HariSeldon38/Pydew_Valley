import pygame 
from settings import *
from support import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree
from pytmx.util_pygame import load_pygame

class Level:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()

		# sprite groups
		self.all_sprites = CameraGroup()

		self.setup()
		self.overlay = Overlay(self.player)

	def setup(self):
		tmx_data = load_pygame('../data/map.tmx')

		#house
		for layer in ['HouseFloor', 'HouseFurnitureBottom']: #for now order of the list matter
			for x,y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x*TILE_SIZE,y*TILE_SIZE), surf, self.all_sprites, LAYERS['house bottom'])
		for layer in ['HouseWalls', 'HouseFurnitureTop']: #for now order of the list matter
			for x,y, surf in tmx_data.get_layer_by_name(layer).tiles():
				Generic((x*TILE_SIZE,y*TILE_SIZE), surf, self.all_sprites, LAYERS['main'])

		#fence
		for x,y, surf in tmx_data.get_layer_by_name('Fence').tiles():
			Generic((x*TILE_SIZE,y*TILE_SIZE), surf, self.all_sprites, LAYERS['main'])

		#water
		water_frames = import_folder('../graphics/water')
		for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
			Water((x*TILE_SIZE,y*TILE_SIZE), water_frames, self.all_sprites)

		#widflowers
		for obj in tmx_data.get_layer_by_name('Decoration'):
			WildFlower((obj.x,obj.y), obj.image, self.all_sprites)

		#trees
		for obj in tmx_data.get_layer_by_name('Trees'):
			Tree((obj.x,obj.y), obj.image, self.all_sprites, obj.name)


		self.player = Player((640,360), self.all_sprites)
		Generic(
			pos=(0,0),
			surface=pygame.image.load('../graphics/world/ground.png').convert_alpha(),
			groups = [self.all_sprites],
			z = LAYERS['ground']
			)

	def run(self,dt):
		self.display_surface.fill('black')
		self.all_sprites.custom_draw(self.player)
		self.all_sprites.update(dt)
		self.overlay.display()

class CameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.offset = pygame.math.Vector2()

	def custom_draw(self, player):
		self.offset.x = player.rect.centerx - SCREEN_WIDTH/2
		self.offset.y = player.rect.centery - SCREEN_HEIGHT/2
		for layer in LAYERS.values():
			for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
				if sprite.z == layer:
					offseted_rect = sprite.rect.copy()
					offseted_rect.center -= self.offset
					self.display_surface.blit(sprite.image, offseted_rect)


import pygame
from pytmx.util_pygame import load_pygame
from random import randint
from settings import *
from support import *
from player import Player
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Fence, Interaction, Particle
from transition import Transition
from soil import SoilLayer
from sky import Rain, Sky
from debug import debug

class Level:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()

		# sprite groups
		self.all_sprites = CameraGroup()
		self.collision_sprites = pygame.sprite.Group()
		self.tree_sprites = pygame.sprite.Group()
		self.interaction_sprites = pygame.sprite.Group()

		#sky
		self.sky = Sky()
		self.rain = Rain(self.all_sprites, rain_level=0, sky=self.sky)

		self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites)
		self.setup()
		self.overlay = Overlay(self.player)
		self.transition = Transition(self.reset, self.player)

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
			Fence((x*TILE_SIZE,y*TILE_SIZE), surf, [self.all_sprites, self.collision_sprites])

		#water
		water_frames = import_folder('../graphics/water')
		for x, y, surf in tmx_data.get_layer_by_name('Water').tiles():
			Water((x*TILE_SIZE,y*TILE_SIZE), water_frames, self.all_sprites)

		#widflowers
		for obj in tmx_data.get_layer_by_name('Decoration'):
			WildFlower((obj.x,obj.y), obj.image, [self.all_sprites, self.collision_sprites])

		#trees
		for obj in tmx_data.get_layer_by_name('Trees'):
			tree = Tree(
				pos = (obj.x,obj.y),
				surf = obj.image,
				groups = [self.all_sprites, self.collision_sprites, self.tree_sprites],
				name = obj.name,
				all_sprites = self.all_sprites,
				player_add = self.player_add)

		#collision tiles
		for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
			Generic((x*TILE_SIZE,y*TILE_SIZE), pygame.Surface((TILE_SIZE,TILE_SIZE)), self.collision_sprites)

		#player
		for obj in tmx_data.get_layer_by_name('Player'):
			if obj.name == 'Start':
				self.player = self.player = Player(
					(obj.x,obj.y),
					self.all_sprites,
					self.collision_sprites,
					self.tree_sprites,
					interaction = self.interaction_sprites,
					soil_layer = self.soil_layer,
					rain = self.rain) #-------------------------------------------------------------maybe delete rain here
			if obj.name == 'Bed':
				Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

		Generic(
			pos=(0,0),
			surface=pygame.image.load('../graphics/world/ground.png').convert_alpha(),
			groups = [self.all_sprites],
			z = LAYERS['ground']
			)

	def reset(self):
		#plants
		self.soil_layer.update_plants() #will change that so that during the day the plan can grow (see main comment)

		#apples on the trees
		for tree in self.tree_sprites.sprites():
			if tree.alive:
				for apple in tree.apple_sprites.sprites():
					apple.kill()
				tree.create_fruit()

		#soil
		self.soil_layer.remove_water()          #find a way to not call that funct if it rain before night as well as after night
		self.rain.rain_level = 0 #for now just make it impossible to rain in the beginning of the day
		self.sky.update_rain_color(0)

		#sky
		self.sky.current_color = self.sky.day_color #maybe will put it in setting idk or now

	def player_add(self, item):
		self.player.item_inventory[item] += 1

	def plant_collision(self):
		if self.soil_layer.plant_sprites:
			for plant in self.soil_layer.plant_sprites.sprites():
				if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
					self.player_add(plant.plant_type)
					plant.kill()
					Particle(plant.rect.topleft, plant.image, self.all_sprites, z=LAYERS['main'])
					self.soil_layer.grid[plant.rect.centery//TILE_SIZE][plant.rect.centerx//TILE_SIZE].remove('P')

	def run(self,dt):
		self.display_surface.fill('black')
		self.all_sprites.custom_draw(self.player)
		self.all_sprites.update(dt)
		self.plant_collision()
		self.overlay.display()

		self.rain.random_update_rain_status()
		if self.rain.rain_level:
			self.rain.update()
			self.soil_layer.water_all(rain_level=self.rain.rain_level)
		self.sky.display_weather(dt, self.rain.rain_level)
		debug(self.rain.rain_level)

		#daytime
		self.sky.display_night(dt)

		if self.player.sleep:
			self.transition.play()

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

					#analytics
					if sprite == player:
						pygame.draw.rect(self.display_surface, 'red', offseted_rect, 5)
						hitbox_rect = player.hitbox.copy()
						hitbox_rect.topleft -= self.offset
						pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 5)
						target_pos = offseted_rect.center + PLAYER_TOOL_OFFSET[player.selected_tool][player.status.split("_")[0]]
						pygame.draw.circle(self.display_surface, 'blue', target_pos, 5)


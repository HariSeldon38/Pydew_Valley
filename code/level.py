import random
import copy
import pygame, sys
import json
from pytmx.util_pygame import load_pygame
from random import randint
from settings import *
from support import *
from player import Player
from npcs import NPC
from overlay import Overlay
from sprites import Generic, Water, WildFlower, Tree, Fence, Interaction, Particle, CollisionShift
from transition import Transition
from timer import Timer
from soil import SoilLayer
from sky import Rain, Sky
from sound import SoundManager
from state_manager import StateManager
from loader import ItemCSVLoader
from debug import debug

class Level:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()
		self.mini_font = pygame.font.Font('../font/LycheeSoda.ttf', 20)

		self.item_loader = ItemCSVLoader('../data/items_fr.csv')

		#sound
		self.sound_manager = SoundManager()
		self.sound_manager.play("music", loops=-1)

		# sprite groups
		self.all_sprites = CameraGroup()
		self.collision_sprites = pygame.sprite.Group()
		self.tree_sprites = pygame.sprite.Group()
		self.water_sprites = pygame.sprite.Group()
		self.interaction_sprites = pygame.sprite.Group()
		self.npc_sprites = pygame.sprite.Group()

		#sky
		self.sky = Sky()
		self.rain = Rain(self.all_sprites, rain_level=0, sky=self.sky)
		self.start_evening_timer = Timer(20000)
		self.stop_evening_timer = Timer(40000)

		self.soil_layer = SoilLayer(self.all_sprites, self.collision_sprites, sound_manager=self.sound_manager)
		self.setup()
		self.state_manager = StateManager(self.player, self.item_loader)
		self.overlay = Overlay(self.player, self.state_manager)
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
			Water((x*TILE_SIZE,y*TILE_SIZE), water_frames, [self.all_sprites, self.water_sprites])

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
				player_add = self.player_add,
				sound_manager = self.sound_manager)

		#collision tiles
		for x, y, surf in tmx_data.get_layer_by_name('Collision').tiles():
			Generic((x*TILE_SIZE,y*TILE_SIZE), pygame.Surface((TILE_SIZE,TILE_SIZE)), self.collision_sprites)
		for x, y, surf in tmx_data.get_layer_by_name('CollisionShiftLeft').tiles():
			CollisionShift((x*TILE_SIZE,y*TILE_SIZE), pygame.Surface((TILE_SIZE,TILE_SIZE)), self.collision_sprites,(-15,0),(-14,0))
		for x, y, surf in tmx_data.get_layer_by_name('CollisionShiftRight').tiles():
			CollisionShift((x*TILE_SIZE,y*TILE_SIZE), pygame.Surface((TILE_SIZE,TILE_SIZE)), self.collision_sprites,(15,0),(-14,0))
		for x, y, surf in tmx_data.get_layer_by_name('CollisionShiftDown').tiles():
			CollisionShift((x*TILE_SIZE,y*TILE_SIZE), pygame.Surface((TILE_SIZE,TILE_SIZE)), self.collision_sprites,(0,40),(0,0))

		#player
		for obj in tmx_data.get_layer_by_name('Player'):
			if obj.name == 'Start':
				self.player = self.player = Player(
					(obj.x,obj.y),
					self.all_sprites,
					self.collision_sprites,
					self.npc_sprites,
					self.tree_sprites,
					self.water_sprites,
					interaction = self.interaction_sprites,
					soil_layer = self.soil_layer,
					rain = self.rain, #-------------------------------------------------------------maybe delete rain here
					sound_manager = self.sound_manager,
					item_loader = self.item_loader,
					player_add = self.player_add,
					all_sprites=self.all_sprites,
					npc_sprites=self.npc_sprites,
				)
				self.player.timers['day'].activate()
			if obj.name == 'Bed':
				Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)
			if obj.name == 'Trader':
				Interaction((obj.x, obj.y), (obj.width, obj.height), self.interaction_sprites, obj.name)

		saved_data = self.load_save()

		# NPC when uptdate the creation method need also to update it in reset (maybe create a creation method)
		# don't forget to load save even in the beginning
		list_record = [
				r'..\recordings\Kate\recording0_200speed_60fps_2025_11_07__13-53-11.txt',
				r'..\recordings\Kate\recording1_200speed_60fps_2025_11_07__14-03-14.txt',
				r'..\recordings\Kate\recordingINVITE_200speed_60fps_2025_11_07__13-59-01.txt',
		]
		NPC(
				list_record[2],
				[self.all_sprites, self.npc_sprites],
				self.collision_sprites,
				name = 'Kate',
				saved_data=saved_data
		)


		Generic(
			pos=(0,0),
			surface=pygame.image.load('../graphics/world/ground.png').convert_alpha(),
			groups = [self.all_sprites],
			z = LAYERS['ground']
			)

	def reset(self):
		self.player.pos.x, self.player.pos.y = (1440,1400)

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

		#sky
		self.rain.rain_level = 0 #for now just make it impossible to rain in the beginning of the day
		self.rain.update_rain_color(0)
		self.sky.current_color = self.sky.day_color.copy() #maybe will put it in setting idk or now
		self.player.timers['day'].activate()

		saved_data = self.write_save()

		#clearing the npc
		for npc in self.npc_sprites:
			npc.kill()
		self.npc_sprites.empty()
		self.player.talkable_npcs = set()

		list_record = [
				r'..\recordings\Kate\recording0_200speed_60fps_2025_11_07__13-53-11.txt',
				r'..\recordings\Kate\recording1_200speed_60fps_2025_11_07__14-03-14.txt',
				r'..\recordings\Kate\recordingINVITE_200speed_60fps_2025_11_07__13-59-01.txt',
		]
		NPC(
				list_record[2],
				[self.all_sprites, self.npc_sprites],
				self.collision_sprites,
				name = 'Kate',
				saved_data=saved_data
		)

	def write_save(self):

		# saving npc dialogue state
		try:
			with open('../save/save.json', "r") as saving_file:
				data = json.load(saving_file)
		except FileNotFoundError:
			print("Warning: save.json is not found. Starting fresh.")
			data = {}
		except json.JSONDecodeError:
			print("ERROR ! : save.json is invalid, make sure to fix it.")
			#sys.exit()
			data = {}
		for npc in self.npc_sprites:
			if npc.flags.get('next_day', False):
				npc.encounter += 1
				npc.flags['next_day'] = False  # now it concern already the next day so for now it's False again

			# update npc saved values
			entry = data.setdefault(npc.name, {})
			# simple and explicit
			entry['next'] = npc.next[:-6] + '_ldm' if npc.next.endswith('_again') else npc.next
			entry['encounter'] = npc.encounter
			entry.setdefault('flags', {})  # keep existing dict if present

			entry['flags'].update(copy.deepcopy(npc.flags))  # merges npc.flags into existing flags
			npc.flags.update(entry['flags']) # That workaround of updating both to 'merge' make sens only in dev mode during play, save cannot have more flags that the game

		# update player saved values
		player_entry = data.setdefault('PLAYER', {})
		if isinstance(player_entry, dict):
			player_entry.update(self.player.flags)  # will also tranfert to data["PLAYER"]
			self.player.flags.update(player_entry)
		else:
			data['PLAYER'] = copy.deepcopy(self.player.flags)

		# save the file
		with open('../save/save.json', "w") as saving_file:
			json.dump(data, saving_file, indent=4)

		return data

	def load_save(self):
		"""Load a save file and put every data in the right attribute
		Except for NPC which depends on the NPC name and are handled outside of this method"""

		# Open the save file
		try:
			with open('../save/save.json', "r") as saving_file:
				data = json.load(saving_file)
		except FileNotFoundError:
			print("Warning: save.json is not found. Starting fresh.")
			data = {}
		except json.JSONDecodeError:
			print("ERROR ! : save.json is invalid, make sure to fix it.")
			#sys.exit()
			data = {}

		# Put data in the right places
		self.player.flags = data.setdefault('PLAYER', {})

		return data

	def player_add(self, item):
		self.player.item_inventory.setdefault(item, 0)
		self.player.item_inventory[item] += 1
		self.sound_manager.play("pickup")

	def display_player_speech(self, text):
		for idx, line in enumerate(text.split('\n')):
			render = self.mini_font.render(line, False, 'black')
			self.display_surface.blit(render, (SCREEN_WIDTH//2+45, SCREEN_HEIGHT//2-60+idx*20))

	def plant_collision(self):
		if self.soil_layer.plant_sprites:
			for plant in self.soil_layer.plant_sprites.sprites():
				if plant.harvestable and plant.rect.colliderect(self.player.hitbox):
					self.player_add(plant.plant_type)
					plant.kill()
					Particle(plant.rect.topleft, plant.image, self.all_sprites, z=LAYERS['main'])
					self.soil_layer.grid[plant.rect.centery//TILE_SIZE][plant.rect.centerx//TILE_SIZE].remove('P')

	def run(self, events, dt):

		#drawing logic
		self.display_surface.fill('black')
		self.all_sprites.custom_draw(self.player, self.npc_sprites) #passing npc here is just to debug the hitbox

		#visual ambiance
		self.sky.display_daylight()
		self.sky.display_weather(dt, self.rain.rain_level)
		debug(self.rain.rain_level)
		debug(f"Recording = {self.player.record}", y=50, x=10)
		debug(f"day timer : {self.player.timers['day'].active}", y=70, x=10)
		debug(f"evening timer : {self.player.timers['evening'].active}", y=90, x=10)

		# manage states
		for event in events:
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_i and not self.state_manager.active_state:
					self.state_manager.open_state("inventory")
				elif event.key == pygame.K_RETURN and self.player.trader_nearby() and not self.state_manager.active_state:
					self.state_manager.open_state("shop")
				elif event.key == pygame.K_RETURN and self.player.talkable_npcs and not self.state_manager.active_state and not self.player.timers['tool use'].active and not self.player.sleep:
					self.state_manager.open_state("dialogue", dt)
					self.player.talking = True
				elif event.key == pygame.K_p and not self.state_manager.active_state:  # before release change this to ESCAPE if not self.menu_manager.active_menu
					self.state_manager.open_state(
						"pause")  # here would need to be able to stack menu but for now I will not implement that
				elif event.key == pygame.K_k:  # before release change this to ESCAPE
					self.state_manager.close_state()
				elif event.key == pygame.K_ESCAPE:
					pygame.quit()
					sys.exit()

		# menu
		if self.state_manager.active_state:
			self.state_manager.handle_input(events)
			self.state_manager.update()
			self.state_manager.draw(self.display_surface)

		#game
		else:
			self.sky.update_daylight(dt)
			self.all_sprites.update(dt)
			self.plant_collision()

			#weather
			self.rain.random_update_rain_status()
			if self.rain.rain_level:
				self.rain.update()
				self.soil_layer.water_all(rain_level=self.rain.rain_level)

			if self.player.timers['slowing'].active and not self.player.sleep:
				self.display_player_speech(self.player.speech)

		if self.player.sleep:
			self.transition.play()

		self.overlay.display()

class CameraGroup(pygame.sprite.Group):
	def __init__(self):
		super().__init__()
		self.display_surface = pygame.display.get_surface()
		self.offset = pygame.math.Vector2()

	def custom_draw(self, player, npc_sprites):
		self.offset.x = player.rect.centerx - SCREEN_WIDTH/2
		self.offset.y = player.rect.centery - SCREEN_HEIGHT/2
		for layer in LAYERS.values():
			for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
				if sprite.z == layer:
					offseted_rect = sprite.rect.copy()
					offseted_rect.center -= self.offset
					self.display_surface.blit(sprite.image, offseted_rect)

					"""#analytics
					if sprite in npc_sprites or sprite == player:
						pygame.draw.rect(self.display_surface, 'red', offseted_rect, 5)
						hitbox_rect = sprite.hitbox.copy()
						hitbox_rect.topleft -= self.offset
						pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 2)
						#target_pos = offseted_rect.center + PLAYER_TOOL_OFFSET[player.selected_tool][player.status.split("_")[0]]
						#pygame.draw.circle(self.display_surface, 'blue', target_pos, 5)
			for sprite in player.collision_sprites.sprites():
				if hasattr(sprite, 'hitbox'):
					hitbox_rect = sprite.hitbox.copy()
					hitbox_rect.topleft -= self.offset
					pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 2)"""


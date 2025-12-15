import os
import random
import copy
import pygame, sys
import json
from pytmx.util_pygame import load_pygame
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

class Level:
	def __init__(self):
		self.display_surface = pygame.display.get_surface()
		self.mini_font = pygame.font.Font('../font/LycheeSoda.ttf', 20)

		self.item_loader = ItemCSVLoader('../data/items_fr.csv')

		#day event
		self.day_nb = 0
		self.queue = [ #the behavior after last
			(None, 'salmon garden'),
			(None, None),
			('Kate', 'running up'),
			('Aurelien', 'si facile'),
			('Kate', None),
			(None, None),
			('Antoine', 'just the two of us'),
			('Antoine', 'salmon garden'),
			('Aurelien', 'si facile'),
			(None, None),
			('Antoine', None),
			('Citrouille', 'chat'),
			('Antoine', 'salmon garden'),
			('Kate', 'running up'),
			('Aurelien', None),
			('Citrouille', 'chat'),
			('Antoine', 'just the two of us'),
			('Citrouille', 'chat'),
		]

		#sound
		self.sound_manager = SoundManager()
		self.surprise_music_already_played = False #to play Tears For Fears only once

		#sprite groups
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
		data = self.setup() #contains loading the save
		self.state_manager = StateManager(self.player, self.item_loader) #this needs to be after defining player
		self.load_shop_inventory(data)

		self.overlay = Overlay(self.player, self.state_manager)
		self.transition = Transition(self.reset, self.player)

	@property
	def name_npc(self):
		return self.queue[self.day_nb][0]

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

		self.create_npc(save=saved_data)
		self.play_day_music(save=saved_data)

		Generic(
			pos=(0,0),
			surface=pygame.image.load('../graphics/world/ground.png').convert_alpha(),
			groups = [self.all_sprites],
			z = LAYERS['ground']
			)

		return saved_data

	def reset(self):
		self.day_nb +=1
		if self.day_nb>= len(self.queue): self.day_nb = 0
		pygame.mixer.stop()

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

		self.create_npc(save=saved_data)
		self.play_day_music(save=saved_data)

	def write_save(self):
		try:
			with open('../save/save.json', "r") as saving_file:
				data = json.load(saving_file)
		except FileNotFoundError:
			print("Warning: save.json is not found. Starting fresh.")
			data = {}
		except json.JSONDecodeError:
			print("ERROR ! : save.json is invalid, make sure to fix it.")
			data = {}

		# saving npc dialogue state
		for npc in self.npc_sprites:
			if npc.flags.get('next_day', False):
				npc.encounter += 1
				npc.flags['next_day'] = False  # now it concern already the next day so for now it's False again

			# update npc saved values
			entry = data.setdefault(npc.name, {})
			entry['next'] = npc.next[:-6] + '_ldm' if npc.next.endswith('_again') else npc.next
			entry['encounter'] = npc.encounter
			entry.setdefault('flags', {})  # keep existing dict if present
			entry['flags'].update(copy.deepcopy(npc.flags))  # merges npc.flags into existing flags
			npc.flags.update(entry['flags']) # That workaround of updating both to 'merge' make sens only in dev mode during play, save cannot have more flags than the game

		# update player saved values
		player_entry = data.setdefault('PLAYER', {})
		player_entry['flags'] = self.player.flags # will also transfer to data["PLAYER"]
		player_entry['item_inventory'] = self.player.item_inventory
		player_entry['tool_inventory'] = self.player.tools
		player_entry['money'] = self.player.money
		player_entry['seeds'] = self.player.seeds

		# update environment saved values
		env_entry = data.setdefault('Environment', {})
		env_entry['nb_days'] = self.day_nb #this line must come after the update of day_nb
		# self.surprise_music_already_played not saved on purpose, allow to hear it once per session
		# same for sleep_deprived feature, player will not remember he did not get to sleep naturally
		for shop in self.state_manager.states['shop'].shops:
			env_entry[shop.__class__.__name__] = shop.inventory
		env_entry['count_to_unlock_seeds'] = self.state_manager.states['shop'].shops[0].count_to_unlock_seeds

		# save the file
		with open('../save/save.json', "w") as saving_file:
			json.dump(data, saving_file, indent=4)

		return data

	def load_save(self):
		"""Load a save file and put every data in the right attribute
		Except for NPC which depends on the NPC name and are handled outside of this method
		Except for Shops inventories handled in load_shop_inventory
		"""

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
		player_entry = data.get('PLAYER', {})
		self.player.flags = player_entry.get('flags', {})
		self.player.item_inventory = player_entry.get('item_inventory', {})
		self.player.tools = player_entry.get('tool_inventory', ['hand'])
		self.player.selected_tool = self.player.tools[self.player.tool_index] #not very clean sorry...
		self.player.money = player_entry.get('money', 0)
		self.player.seeds = player_entry.get('seeds', ['corn', 'tomato'])
		env_entry = data.get('Environment', {})
		self.day_nb = env_entry.get('nb_days', 0)

		return data

	def load_shop_inventory(self, data):
		env_entry = data.get('Environment', {})
		for shop in self.state_manager.states['shop'].shops:
			shop.inventory = env_entry.get(shop.__class__.__name__, {})
		self.state_manager.states['shop'].shops[0].count_to_unlock_seeds = env_entry.get('count_to_unlock_seeds', 0)

	def play_day_music(self, save):
		music_handled = False
		if self.name_npc == 'Antoine' and not self.surprise_music_already_played:
			save_antoine = save.get('Antoine', {})
			flags_antoine = save_antoine.get('flags', {})
			if flags_antoine.get('beanie', False):
				self.sound_manager.play('everybody wants to rule the world')
				self.surprise_music_already_played = True
				music_handled = True
		if not music_handled:
			if self.queue[self.day_nb][1]: #if None no music except if condition reached above
				self.sound_manager.play(self.queue[self.day_nb][1])

	def create_npc(self, save):

		#Special case : Kate invited in the house and not already with Aurelien
		if self.player.flags.get('invite_kate', False) and not self.player.flags.get('Kate_with_Aurelien'):
			kate_record_file = f'..\\recordings\\Kate\\special_case\\recordingINVITE_200speed_60fps_2025_11_07__13-59-01.txt'
			NPC(
				kate_record_file,
				[self.all_sprites, self.npc_sprites],
				self.collision_sprites,
				name = 'Kate',
				saved_data=save)

		#Special case: Kate and Aurelien are together
		if self.player.flags.get('Kate_with_Aurelien', False) and self.name_npc in ['Kate', 'Aurelien']:
			kate_record_file =  f'..\\recordings\\Kate\\special_case\\recordingWITH_AURELIEN_200speed_60fps_2025_12_13__11-52-38.txt'
			aurelien_record_file = f'..\\recordings\\Aurelien\\special_case\\recordingWITH_KATE_200speed_60fps_2025_12_13__12-23-41.txt'
			record_file = [kate_record_file, aurelien_record_file]
			index = random.randint(0,1)
			NPC(
				record_file[index],
				[self.all_sprites, self.npc_sprites],
				self.collision_sprites,
				name='Kate',
				saved_data=save)
			NPC(
				record_file[(index+1)%2],
				[self.all_sprites, self.npc_sprites],
				self.collision_sprites,
				name='Aurelien',
				saved_data=save)

		#Generic case
		if self.name_npc:
			#First we handle the little tweak if a special case is active
			if self.player.flags.get('invite_kate', False) and self.name_npc == 'Kate':
				pass #if kate invited and is the planned npc, we already have handled her
			if self.player.flags.get('Kate_with_Aurelien', False) and self.name_npc in ['Kate', 'Aurelien']:
				pass

			else :
				record_dir = f'..\\recordings\\{self.name_npc}'
				record_files = [f for f in os.listdir(record_dir) if os.path.isfile(os.path.join(record_dir, f))]
				NPC(
					os.path.join(record_dir, random.choice(record_files)),
					[self.all_sprites, self.npc_sprites],
					self.collision_sprites,
					name = self.name_npc,
					saved_data=save)

	def player_add(self, item):
		self.player.item_inventory.setdefault(item, 0)
		self.player.item_inventory[item] += 1
		self.sound_manager.play(random.choice(['add1','add2','add3']))

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
					if self.state_manager.active_state_name:
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

			#		#analytics
			# 		if sprite in npc_sprites or sprite == player:
			# 			pygame.draw.rect(self.display_surface, 'red', offseted_rect, 5)
			# 			hitbox_rect = sprite.hitbox.copy()
			# 			hitbox_rect.topleft -= self.offset
			# 			pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 2)
			# 			target_pos = offseted_rect.center + PLAYER_TOOL_OFFSET[player.selected_tool][player.status.split("_")[0]]
			# 			pygame.draw.circle(self.display_surface, 'blue', target_pos, 5)
			# for sprite in player.collision_sprites.sprites():
			# 	if hasattr(sprite, 'hitbox'):
			# 		hitbox_rect = sprite.hitbox.copy()
			# 		hitbox_rect.topleft -= self.offset
			# 		pygame.draw.rect(self.display_surface, 'green', hitbox_rect, 2)


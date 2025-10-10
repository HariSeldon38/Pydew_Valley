import pygame
from settings import *
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, npc, tree_sprites, interaction, soil_layer, rain, sound_manager, item_loader): #--------maybe delete rain here , only need control rain from game when dev
        super().__init__(group)

        self.rain = rain #--------------------------------------------------------------------------------same here

        self.import_assets()
        self.status = 'up'
        self.lock_status = False
        self.frame_index = 0
        self.animation_speed = 12

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        self.z = LAYERS['main']

        #movement
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = PLAYER_SPEED
        self.down_offset_hitbox = 23
        self.hitbox = self.rect.copy().inflate((-126,-90))
        self.hitbox.centery += self.down_offset_hitbox
        self.collision_sprites = collision_sprites
        self.record = False #developpement feature to record a path

        #timers
        self.timers = {
            'tool use': Timer(400, self.use_tool),
            'tool switch': Timer(350),
            'seed use': Timer(350, self.use_seed),
            'seed switch': Timer(350),
            'rain switch': Timer(350), #----------------------------------------------------to delete before release
            'record': Timer(500)
        }

        #tools
        self.tools = ['hoe','axe','water','jump']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        #seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        self.item_inventory = {
            'corn' : 1,
            'tomato': 10,
            'corn_seed': 1,
            'tomato_seed': 1,
            'apple': 10,
            'wood': 10,
            'black_beanie': 1,
            'fishing_rod': 1,
            'seewing_needle': 1,
            'white_thread': 1
        }
        self.money = 20000

        #interactions
        self.tree_sprites = tree_sprites
        self.interaction = interaction
        self.sleep = False
        self.soil_layer = soil_layer
        self.npc_sprites = npc
        self.talkable_npcs = set()
        self.talking = False
        self.flags = {} #will contains a dict 'flag_name': boolean to track keypoints in the stories of the npcs, NEED TO BE INSTANCIATE THOUGH LOAD_SAVE

        self.sound_manager = sound_manager
        self.item_loader = item_loader

    def import_assets(self):
        self.animations = {'up': [], 'down': [], 'right': [], 'left': [],
                           'up_idle': [], 'down_idle': [], 'right_idle': [], 'left_idle': [],
                           'up_hoe': [], 'down_hoe': [], 'right_hoe': [], 'left_hoe': [],
                           'up_axe': [], 'down_axe': [], 'right_axe': [], 'left_axe': [],
                           'up_water': [], 'down_water': [], 'right_water': [], 'left_water': [],
                           'up_jump': [], 'down_jump': [], 'right_jump': [], 'left_jump': [],}

        for animation in self.animations.keys():
            full_path = '../graphics/characters/player/' + animation
            self.animations[animation] = import_folder(full_path)

    def use_tool(self):
        if self.selected_tool == 'hoe':
            self.soil_layer.get_hit(self.target_position)
        elif self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_position):
                    tree.damage()
        elif self.selected_tool == 'water':
            self.soil_layer.get_watered(self.target_position)
            self.sound_manager.play('watering')

    def use_seed(self):
        if self.item_inventory.get(self.selected_seed+"_seed", 0) > 0:
            self.soil_layer.plant_seed(self.target_position, self.selected_seed)
            self.item_inventory[self.selected_seed+"_seed"] -= 1

    def get_target_position(self):
        self.target_position = self.rect.center + PLAYER_TOOL_OFFSET[self.selected_tool][self.status.split("_")[0]]

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def trader_nearby(self):
        for sprite in pygame.sprite.spritecollide(self, self.interaction, dokill=False):
            if getattr(sprite, 'name', None) == 'Trader':
                return True
        return False

    def compute_dist_npcs(self):
        """update the distance_with_player attribute of each npc sprite"""
        for sprite in self.npc_sprites.sprites():
            dx = self.hitbox.centerx - sprite.hitbox.centerx
            dy = self.hitbox.centery - sprite.hitbox.centery
            sprite.distance_with_player = (dx**2 + dy**2) ** 0.5

    def npcs_nearby(self, blocking_radius, talkable_radius):
        """update blocked attribute of each npcs
        return the sprite of the npc close enough to talk to them"""
        for sprite in self.npc_sprites.sprites():
            if sprite.distance_with_player < blocking_radius:
                sprite.blocked = True
            else: sprite.blocked = False

            if sprite.distance_with_player < talkable_radius:
                self.talkable_npcs.add(sprite)
            else:
                self.talkable_npcs.discard(sprite)

    def start_record_input(self):
        self.record = True
        self.recorded_inputs = [self.rect.center] #store the starting position

    def stop_record_input(self):
        from datetime import datetime

        self.recorded_inputs.append(self.rect.center) #store the final_position to test drift when replayed
        self.record = False
        timestamp = datetime.now().strftime("%Y_%m_%d__%H-%M-%S")
        filename = f"recording_{PLAYER_SPEED}speed_{FPS}fps_{timestamp}.txt"
        with open(f'../recordings/{filename}', 'w') as file:
            for x, y in self.recorded_inputs:
                file.write(f"{x},{y}\n")
        self.recorded_inputs = []

    def record_input(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)  # Call the original input logic
            if self.record:
                self.recorded_inputs.append((int(self.direction.x), int(self.direction.y)))
            return None
        return wrapper
    @record_input
    def input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_r] and not self.timers['rain switch'].active: #------------------------------------------------------------------to delete before release
            self.timers['rain switch'].activate()
            self.rain.rain_level += 1
            self.rain.update_rain_color(self.rain.rain_level)
        if keys[pygame.K_t] and not self.timers['rain switch'].active:
            self.timers['rain switch'].activate()
            self.rain.rain_level -= 1
            self.rain.update_rain_color(self.rain.rain_level)

        if keys[pygame.K_LSHIFT]:
            self.speed = PLAYER_LOW_SPEED
            self.lock_status = True
        else:
            self.speed = PLAYER_SPEED
            self.lock_status = False

        if not self.timers['tool use'].active and not self.sleep:
            if keys[pygame.K_UP] or keys[pygame.K_z]:
                self.direction.y = -1
                if not self.lock_status:
                    self.status = 'up'
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.direction.y = 1
                if not self.lock_status:
                    self.status = 'down'
            else:
                self.direction.y = 0
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.direction.x = 1
                if not self.lock_status:
                    self.status = 'right'
            elif keys[pygame.K_LEFT] or keys[pygame.K_q]:
                self.direction.x = -1
                if not self.lock_status:
                    self.status = 'left'
            else:
                self.direction.x = 0

            #toggle record feature
            if not self.timers['record'].active and not self.sleep:
                if keys[pygame.K_o]:
                    self.timers['record'].activate()
                    if not self.record:
                        self.start_record_input()
                    else:
                        self.stop_record_input()

            #tools
            if keys[pygame.K_SPACE]:
                self.timers['tool use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0
            if keys[pygame.K_e] and not self.timers['tool switch'].active:
                self.timers['tool switch'].activate()
                if self.tool_index < len(self.tools)-1:
                    self.tool_index += 1
                else: self.tool_index = 0
                self.selected_tool = self.tools[self.tool_index]

            #seeds
            if keys[pygame.K_c]:
                self.timers['seed use'].activate()
                self.direction = pygame.math.Vector2()
                self.frame_index = 0
            if keys[pygame.K_f] and not self.timers['seed switch'].active:
                self.timers['seed switch'].activate()
                if self.seed_index < len(self.seeds)-1:
                    self.seed_index += 1
                else: self.seed_index = 0
                self.selected_seed = self.seeds[self.seed_index]

        # sleep and dialogue
        if keys[pygame.K_RETURN] and not self.sleep:
            collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, dokill=False)
            if collided_interaction_sprite:
                if collided_interaction_sprite[0].name == 'Bed':
                    self.status = 'left_idle'
                    self.sleep = True

    def move(self, dt):
        """due to last line, can't move at lower speed that 1 px/ frame (177 speed)
        because we lose the float advantage the pos vector offers
        also I'm feeling diagonal movement slow, while high speed for dev"""
        if self.direction.magnitude() > 0:
            self.direction = self.direction.normalize()

        self.pos.x += self.direction.x * self.speed * dt #horizontal movement
        self.hitbox.centerx = round(self.pos.x) #need round otherwise it is truncated
        self.collision('horizontal')

        self.pos.y += self.direction.y * self.speed * dt #vertical movement
        self.hitbox.centery = round(self.pos.y) + self.down_offset_hitbox
        self.collision('vertical')

        self.rect.centerx = self.hitbox.centerx
        self.rect.centery = self.hitbox.centery - self.down_offset_hitbox
        self.pos.x,self.pos.y = self.rect.centerx,self.rect.centery

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites() + self.npc_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if sprite in self.npc_sprites.sprites():
                        sprite.blocked = True
                    if direction == 'horizontal':
                        if self.direction.x > 0: #moving right
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0: #moving right
                            self.hitbox.left = sprite.hitbox.right

                    if direction == 'vertical':
                        if self.direction.y > 0: #moving down
                            self.hitbox.bottom = sprite.hitbox.top
                        if self.direction.y < 0: #moving up
                            self.hitbox.top = sprite.hitbox.bottom
                else:
                    if sprite in self.npc_sprites.sprites():
                        sprite.blocked = False

    def get_status(self):
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'

        #tool use
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]

    def update(self, dt):
        self.input()
        self.move(dt)
        self.compute_dist_npcs()
        self.npcs_nearby(blocking_radius=90, talkable_radius=200)
        self.update_timers()
        self.get_target_position() #I'm thinking about running that only in case of using tool, will see if need some optim
        self.get_status()
        self.animate(dt)

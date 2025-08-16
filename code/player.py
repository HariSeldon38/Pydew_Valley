import pygame, sys
from settings import *
from support import *
from timer import Timer

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, tree_sprites, interaction, soil_layer, rain, sound_manager): #--------maybe delete rain here , only need control rain from game when dev
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

        #timers
        self.timers = {
            'tool use': Timer(400, self.use_tool),
            'tool switch': Timer(350),
            'seed use': Timer(350, self.use_seed),
            'seed switch': Timer(350),
            'rain switch': Timer(350), #----------------------------------------------------to delete before release
            'menu toggle': Timer(350),
        }

        #tools
        self.tools = ['hoe','axe','water', 'jump']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        #seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        #inventory
        self.item_inventory = {
            'Bois': 5,
            'Pomme': 6,
            'Maïs': 7,
            'Tomate': 8,
        }
        self.seed_inventory = {
            'Graines de maïs': 3,
            'Graines de tomate': 2,
        }
        self.special_inventory = {
            'Bonnet noir': 0,
            'canne à pêche': 0,
            'Kit de broderie': 0,
            'Fil blanc': 0,
        }
        self.money = 20000

        #interactions
        self.tree_sprites = tree_sprites
        self.interaction = interaction
        self.sleep = False
        self.soil_layer = soil_layer

        self.sound_manager = sound_manager

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
        FR_name = TRANSLATE_EN_FR[self.selected_seed]
        if self.seed_inventory[FR_name] > 0:
            self.soil_layer.plant_seed(self.target_position, self.selected_seed)
            self.seed_inventory[FR_name] -= 1

    def get_target_position(self):
        self.target_position = self.rect.center + PLAYER_TOOL_OFFSET[self.selected_tool][self.status.split("_")[0]]

    def import_assets(self):
        self.animations = {'up': [], 'down': [], 'right': [], 'left': [],
                           'up_idle': [], 'down_idle': [], 'right_idle': [], 'left_idle': [],
                           'up_hoe': [], 'down_hoe': [], 'right_hoe': [], 'left_hoe': [],
                           'up_axe': [], 'down_axe': [], 'right_axe': [], 'left_axe': [],
                           'up_water': [], 'down_water': [], 'right_water': [], 'left_water': [],
                           'up_jump': [], 'down_jump': [], 'right_jump': [], 'left_jump': [],}

        for animation in self.animations.keys():
            full_path = '../graphics/character/' + animation
            self.animations[animation] = import_folder(full_path)

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]

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

        if keys[pygame.K_RETURN] and not self.sleep:
            collided_interaction_sprite = pygame.sprite.spritecollide(self, self.interaction, dokill=False)
            if collided_interaction_sprite:
                if collided_interaction_sprite[0].name == 'Bed':
                    self.status = 'left_idle'
                    self.sleep = True

    def get_status(self):
        if self.direction.magnitude() == 0:
            self.status = self.status.split('_')[0] + '_idle'

        #tool use
        if self.timers['tool use'].active:
            self.status = self.status.split('_')[0] + '_' + self.selected_tool

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def collision(self, direction):
        for sprite in self.collision_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
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

    def trader_nearby(self):
        for sprite in pygame.sprite.spritecollide(self, self.interaction, dokill=False):
            if getattr(sprite, 'name', None) == 'Trader':
                return True
        return False

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

    def update(self, dt):
        self.input()
        self.move(dt)
        self.update_timers()
        self.get_target_position() #I'm thinking about running that only in case of using tool, will see if need some optim
        self.get_status()
        self.animate(dt)

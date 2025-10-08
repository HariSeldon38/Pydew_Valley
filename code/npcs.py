import pygame
import random
import os
import yaml
from menu import Menu
from support import import_folder
from settings import *

"""some of the code is redundant to player class
could be good to generalise but for now WND"""

"""I expect a pb when will implement collision with player
cause already collision collision_sprite vs NPC so NPC cannot be into collision sprite"""

class NPC(pygame.sprite.Sprite):

    def __init__(self,route_file, group, collision_sprites):
        super().__init__(group)
        self.sprite_type = 'npc'

        list_npc = os.listdir('../graphics/characters/npcs')
        self.name = random.choice(list_npc)

        self.import_assets()
        self.status = 'up'
        self.frame_index = 0
        self.animation_speed = 10
        self.image = self.animations[self.status][self.frame_index]
        self.load_route(route_file)
        self.rect = self.image.get_rect(center = self.start_pos)
        self.z = LAYERS['main']

        self.distance_with_player = None

        #movement
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = NPC_SPEED
        self.down_offset_hitbox = 15
        self.hitbox = self.rect.copy().inflate((-14,-30))
        self.hitbox.centery += self.down_offset_hitbox
        self.collision_sprites = collision_sprites
        self.blocked = False

        #dialogue
        with open("../data/dialogues/Euridyce.yaml", "r", encoding="utf-8") as f:
            self.dialogue = yaml.safe_load(f)

    def load_route(self, file_path):
        with open(file_path, 'r') as record:
            self.start_pos = tuple(map(int, record.readline().strip().split(',')))
            self.route = [tuple(map(int, line.strip().split(','))) for line in record]

    def import_assets(self):
        self.animations = {'up': [], 'down': [], 'right': [], 'left': [],
                           'up_idle': [], 'down_idle': [], 'right_idle': [], 'left_idle': [],}

        for animation in self.animations.keys():
            full_path = '../graphics/characters/npcs/' + self.name + '/' + animation
            self.animations[animation] = import_folder(full_path)

    def replay_input(self):
        if len(self.route) > 1:
            if not self.blocked:
                tuple_direction = self.route.pop(0)
                self.direction.x = tuple_direction[0]
                self.direction.y = tuple_direction[1]
            else:
                self.direction.x = 0
                self.direction.y = 0

        elif self.route: #testing drift
            expected_ending_pos = self.route.pop(0)
            ending_pos = self.rect.center
            if ending_pos != expected_ending_pos:
                x_drift = abs(ending_pos[0] - expected_ending_pos[0])
                y_drift = abs(ending_pos[1] - expected_ending_pos[1])
                print(f'Drift detected : {x_drift}px in x-axis, {y_drift}px in y-axis')

    def move(self, dt): #need to implement hitbox like player
        """EXACT SAME AS PLAYER 04/10/25"""
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

    def get_status(self):
        if self.direction.x != 0:
            self.status = 'right' if self.direction.x > 0 else 'left'
        elif self.direction.y != 0:
            self.status = 'down' if self.direction.y > 0 else 'up'
        else:
            self.status = self.status.split('_')[0] + '_idle'

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.animations[self.status]):
            self.frame_index = 0
        self.image = self.animations[self.status][int(self.frame_index)]

    def update(self, dt):
        self.replay_input()
        self.move(dt)
        self.get_status()
        self.animate(dt)

class Dialogue(Menu):

    def __init__(self, player):

        self.player = player

        self.background_surf = pygame.image.load('../graphics/UI/black_long_button_1200x150.png')

        self.text_background_surf1 = pygame.image.load('../graphics/UI/clear_less_box_1020x110.png')
        self.text_background_surf1_selected = pygame.image.load('../graphics/UI/clear_box_1020x110.png')
        self.text_background_surf1_selected.fill((255, 255, 200))

        image = pygame.image.load('../graphics/UI/clear_less_box_1020x45.png')
        image_clear = pygame.image.load('../graphics/UI/clear_box_1020x45.png')
        self.text_background_surf2 = [image_clear, image]

        image = pygame.image.load('../graphics/UI/clear_less_box_1020x30.png')
        image_clear = pygame.image.load('../graphics/UI/clear_box_1020x30.png')
        self.text_background_surf3 = [image_clear, image, image]

        self.frame_surf = pygame.image.load('../graphics/UI/light_edges_upscaled3_140x140.png')
        self.frame_rect = self.frame_surf.get_rect(bottomleft=(45, SCREEN_HEIGHT - 45))

        #movement
        self.index = 0
        self.index_test = 0

    def setUp(self):
        """method that exe when opening the menu, that is not the same as when initialise the menu"""
        self.npc = list(self.player.talkable_npcs)[0] #for now only choosing one npc if several

        self.face = pygame.image.load('../graphics/characters/npcs/' + self.npc.name + '/Faceset.png').convert_alpha()
        self.face = pygame.transform.scale(self.face, (100, 100))
        self.face_rect = self.face.get_rect(bottomleft=(65, SCREEN_HEIGHT - 65))

        self.next = "start" #here something that take into account where we are in the discution for now just start

    def tearDown(self):
        """method that exe when closing the menu"""
        self.player.talking = False

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.index_test += 1
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.index += 1
                elif event.key in [pygame.K_UP, pygame.K_z]:
                    self.index -= 1
                if self.index_test > 2:
                    self.index_test = 0
                if self.index > self.index_test:
                    self.index = 0
                if self.index < 0:
                    self.index = self.index_test

    def update(self):
        """maybe could use that to change the selected surface"""

        pass

    def display_text_background(self, surface, nb_entries):
        if nb_entries == 1:
            surface.blit(self.text_background_surf1, (200, SCREEN_HEIGHT - 170))
        if nb_entries == 2:
            surface.blit(self.text_background_surf2[0+self.index], (200, SCREEN_HEIGHT - 170))
            surface.blit(self.text_background_surf2[(1+self.index)%2], (200, SCREEN_HEIGHT - 105))
        if nb_entries == 3:
            surface.blit(self.text_background_surf3[0+self.index], (200, SCREEN_HEIGHT - 170))
            surface.blit(self.text_background_surf3[(2+self.index)%3], (200, SCREEN_HEIGHT - 130))
            surface.blit(self.text_background_surf3[(1+self.index)%3], (200, SCREEN_HEIGHT - 90))

    def draw(self, surface):
        surface.blit(self.background_surf, (40, SCREEN_HEIGHT - 190))
        self.display_text_background(surface, self.index_test+1)
        surface.blit(self.frame_surf, self.frame_rect)
        surface.blit(self.face, self.face_rect)

import pygame
import random
import os
from support import import_folder
from settings import *

"""some of the code is redundant to player class
could be good to generalise but for now WND"""

"""I expect a pb when will implement collision with player
cause already collision collision_sprite vs NPC so NPC cannot be into collision sprite"""

class NPC(pygame.sprite.Sprite):

    def __init__(self,route_file, group, collision_sprites):
        super().__init__(group)

        list_npc = os.listdir('../graphics/characters/npcs')
        self.npc_id = random.choice(list_npc)

        self.import_assets()
        self.status = 'up'
        self.frame_index = 0
        self.animation_speed = 10
        self.image = self.animations[self.status][self.frame_index]
        self.load_route(route_file)
        self.rect = self.image.get_rect(center = self.start_pos)
        self.z = LAYERS['main']

        #movement
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = NPC_SPEED
        self.down_offset_hitbox = 15
        self.hitbox = self.rect.copy().inflate((-14,-30))
        self.hitbox.centery += self.down_offset_hitbox
        self.collision_sprites = collision_sprites

    def load_route(self, file_path):
        with open(file_path, 'r') as record:
            self.start_pos = tuple(map(int, record.readline().strip().split(',')))
            self.route = [tuple(map(int, line.strip().split(','))) for line in record]

    def import_assets(self):
        self.animations = {'up': [], 'down': [], 'right': [], 'left': [],
                           'up_idle': [], 'down_idle': [], 'right_idle': [], 'left_idle': [],}

        for animation in self.animations.keys():
            full_path = '../graphics/characters/npcs/' + self.npc_id + '/' + animation
            self.animations[animation] = import_folder(full_path)

    def replay_input(self):
        if len(self.route) > 1:
            tuple_direction = self.route.pop(0)
            self.direction.x = tuple_direction[0]
            self.direction.y = tuple_direction[1]

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


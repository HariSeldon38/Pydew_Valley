import pygame
from random import randint, choice
from settings import *
from support import import_folder
from sprites import Generic

class Drop(Generic):
    def __init__(self, surf, pos, moving, rain_level, groups, z):
        super().__init__(pos, surf, groups, z)
        self.lifetime = randint(350, 550)
        self.start_time = pygame.time.get_ticks()

        #moving
        self.moving = moving
        if self.moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2,4)
            self.speed = randint(100+40*rain_level, 160+40*rain_level)

    def update(self, dt):
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = round(self.pos.x), round(self.pos.y)

        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.lifetime:
            self.kill()

class Rain:
    def __init__(self, all_sprites, rain_level):
        self.rain_level = rain_level
        self.all_sprites = all_sprites
        self.rain_drops = import_folder('../graphics/rain/drops')
        self.rain_floor = import_folder('../graphics/rain/floor')
        self.floor_w, self.floor_h = pygame.image.load('../graphics/world/ground.png').get_size() #before release need to hardcode these values

    def random_update_rain_status(self):
        if self.rain_level:
            if randint(1, PROBABILITY_STOP_RAIN) == 1:
                self.rain_level = 0
            if randint(1, PROBABILITY_INCREASE_RAIN) == 1:
                self.rain_level += 1
            if self.rain_level > 1:
                if randint(1, PROBABILITY_DECREASE_RAIN) == 1:
                    self.rain_level -= 1
        if not self.rain_level:
            if randint(1, PROBABILITY_START_RAIN) == 1:
                self.rain_level = 1

    def create_floor(self):
        Drop(
            surf = choice(self.rain_floor),
            pos = (randint(0,self.floor_w),randint(0, self.floor_h)),
            moving = False,
            rain_level = None, #not used if moving is False
            groups = self.all_sprites,
            z = LAYERS['rain floor'])

    def create_drops(self, rain_level):
        if randint(1,3) == 1: #used to mitigate nb of drops on the floor
            Drop(
                surf = choice(self.rain_drops),
                pos = (randint(0,self.floor_w),randint(0, self.floor_h)),
                moving = True,
                rain_level = rain_level,
                groups = self.all_sprites,
                z = LAYERS['rain drops'])

    def update(self):

        if self.rain_level == 1:
            if randint(1,2) == 1: #create drop in sky and ground 1/2 frames
                self.create_floor()
                self.create_drops(self.rain_level)
        else:
            for _ in range(self.rain_level-1): #create 1 drops every frames if rain_level = 2,
                self.create_floor() #              ... 2 drops every frames if = 3
                self.create_drops(self.rain_level) #... and so on
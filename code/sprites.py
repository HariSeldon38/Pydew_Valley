import pygame
from random import randint, choice
from settings import *
from timer import Timer

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surface, groups, z=LAYERS['main']):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.2, -self.rect.height * 0.75)

class Water(Generic):
    def __init__(self, pos, frames, groups):

        #animation setup
        self.frames = frames
        self.frame_index = 0
        #sprite setup
        super().__init__(pos, self.frames[self.frame_index], groups, LAYERS['water'])

    def animate(self, dt):
        self.frame_index += 5 * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self,dt):
        self.animate(dt)

class WildFlower(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20, -self.rect.height * 0.9)

class Tree(Generic):
    def __init__(self, pos, surf, groups, name):
        super().__init__(pos, surf, groups)

        #tree attributes
        self.health = 5
        self.alive = True
        self.stump_surf = pygame.image.load(f'../graphics/stumps/{name.lower()}.png').convert_alpha()
        self.invul_timer = Timer(200)

        #apples
        self.apple_surf = pygame.image.load('../graphics/fruit/apple.png').convert_alpha()
        self.apple_pos = APPLE_POS[name] #name refers to type of tree
        self.apple_sprite = pygame.sprite.Group()
        #self.create_fruit()

    def damage(self):
        self.health -= 1
        if len(self.apple_sprite.sprites()) > 0:
            random_apple = choice(self.apple_sprite.sprites())
            random_apple.kill()

    def check_death(self):
        if self.health <= 0:
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
            self.alive = False

    def create_fruit(self, visible_sprites):
        for pos in self.apple_pos:
            if randint(0,10) < 2:
                x = pos[0] + self.rect.left
                y = pos[1] + self.rect.top
                Generic(
                    pos = (x,y),
                    surface = self.apple_surf,
                    groups = [self.apple_sprite, visible_sprites], #self.groups() return list grp of the tree instance
                    z = 9)

    def update(self, dt):
        if self.alive:
            self.check_death()

class Fence(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-40, -50)
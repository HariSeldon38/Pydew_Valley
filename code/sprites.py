import pygame
from random import randint, choice
from settings import *
from timer import Timer

class Generic(pygame.sprite.Sprite):
    def __init__(self, pos, surface, groups, z=LAYERS['main'], sound_manager=None):
        super().__init__(groups)
        self.image = surface
        self.rect = self.image.get_rect(topleft = pos)
        self.z = z
        self.hitbox = self.rect.copy().inflate(-self.rect.width * 0.35, -self.rect.height * 0.35)
        self.sound_manager = sound_manager

class CollisionShift(Generic):
    def __init__(self, pos, surface, groups, shift, inflate, z=LAYERS['main']):
        super().__init__(pos, surface, groups)
        self.hitbox = self.hitbox.inflate(inflate[0],inflate[1])
        self.hitbox.centery += shift[1]
        self.hitbox.centerx += shift[0]

class Interaction(Generic):
    def __init__(self, pos, size, groups, name):
        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups)
        self.name = name

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
        self.down_offset_hitbox = 15
        self.hitbox.centery += self.down_offset_hitbox

class Particle(Generic):
    def __init__(self, pos, surf, groups, z, duration = 200):
        super().__init__(pos, surf, groups, z)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration

        mask_surf = pygame.mask.from_surface(self.image)
        new_surf = mask_surf.to_surface() #all colored px -> white, all trans -> black
        new_surf.set_colorkey((0,0,0))
        self.image = new_surf

    def update(self, dt):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.duration:
            self.kill()

class Tree(Generic):
    def __init__(self, pos, surf, groups, name, all_sprites, player_add, sound_manager):
        super().__init__(pos, surf, groups, sound_manager=sound_manager)
        self.hitbox = self.hitbox.inflate(0, -20)
        self.down_offset_hitbox = 23
        self.hitbox.centery += self.down_offset_hitbox
        self.all_sprites = all_sprites

        #tree attributes
        self.health = 10
        self.alive = True
        self.stump_surf = pygame.image.load(f'../graphics/stumps/{name.lower()}.png').convert_alpha()

        #apples
        self.apple_surf = pygame.image.load('../graphics/fruit/apple.png').convert_alpha()
        self.apple_pos = APPLE_POS[name] #name refers to type of tree
        self.apple_sprites = pygame.sprite.Group()
        self.create_fruit()

        self.player_add = player_add

    def take_apple(self):
        if len(self.apple_sprites.sprites()) > 0:
            random_apple = choice(self.apple_sprites.sprites())
            Particle(
                pos = random_apple.rect.topleft,
                surf = random_apple.image,
                groups = self.all_sprites,
                z = LAYERS['fruit'],
                duration = 30)
            random_apple.kill()
            self.player_add('apple')

    def damage(self):
        self.health -= 1
        self.sound_manager.play('axe')

    def check_death(self):
        if self.health <= 0:
            Particle(self.rect.topleft, self.image, self.all_sprites, LAYERS['fruit'], duration=120)
            self.image = self.stump_surf
            self.rect = self.image.get_rect(midbottom = self.rect.midbottom)
            self.hitbox = self.rect.copy().inflate(-10, -self.rect.height * 0.6)
            self.alive = False
            self.player_add('wood')

    def create_fruit(self):
        for pos in self.apple_pos:
            if randint(0,10) < 2:
                x = pos[0] + self.rect.left
                y = pos[1] + self.rect.top
                Generic(
                    pos = (x,y),
                    surface = self.apple_surf,
                    groups = [self.apple_sprites , self.all_sprites], #self.groups() return list grp of the tree instance
                    z = 9)

    def update(self, dt):
        if self.alive:
            self.check_death()

class Fence(Generic):
    def __init__(self, pos, surf, groups):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy().inflate(-20, -30)
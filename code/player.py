import pygame, sys
from settings import *
from support import *
from timer import Timer
from debug import debug

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, group, collision_sprites, tree_sprites):
        super().__init__(group)

        self.import_assets()
        self.status = 'up'
        self.lock_status = False
        self.frame_index = 0
        self.animation_speed = 6

        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        self.z = LAYERS['main']

        #movement
        self.direction = pygame.math.Vector2()
        self.pos = pygame.math.Vector2(self.rect.center)
        self.speed = PLAYER_SPEED
        self.hitbox = self.rect.copy().inflate((-126,-70))
        self.collision_sprites = collision_sprites

        #timers
        self.timers = {
            'tool use': Timer(350, self.use_tool),
            'tool switch': Timer(500),
            'seed use': Timer(350, self.use_seed),
            'seed switch': Timer(500)
        }

        #tools
        self.tools = ['hoe','axe','water']
        self.tool_index = 0
        self.selected_tool = self.tools[self.tool_index]

        #seeds
        self.seeds = ['corn', 'tomato']
        self.seed_index = 0
        self.selected_seed = self.seeds[self.seed_index]

        #interactions
        self.tree_sprites = tree_sprites

    def use_tool(self):
        if self.selected_tool == 'hoe':
            pass
        elif self.selected_tool == 'axe':
            for tree in self.tree_sprites.sprites():
                if tree.rect.collidepoint(self.target_position):
                    tree.damage()
        elif self.selected_tool == 'water':
            pass

    def use_seed(self):
        pass

    def get_target_position(self):
        self.target_position = self.rect.center + PLAYER_TOOL_OFFSET[self.selected_tool][self.status.split("_")[0]]

    def import_assets(self):
        self.animations = {'up': [], 'down': [], 'right': [], 'left': [],
                           'up_idle': [], 'down_idle': [], 'right_idle': [], 'left_idle': [],
                           'up_hoe': [], 'down_hoe': [], 'right_hoe': [], 'left_hoe': [],
                           'up_axe': [], 'down_axe': [], 'right_axe': [], 'left_axe': [],
                           'up_water': [], 'down_water': [], 'right_water': [], 'left_water': [],}
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

        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()
        if keys[pygame.K_LSHIFT]:
            self.speed = PLAYER_LOW_SPEED
            self.lock_status = True
        else:
            self.speed = PLAYER_SPEED
            self.lock_status = False

        if not self.timers['tool use'].active:
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
        self.hitbox.centery = round(self.pos.y)
        self.collision('vertical')

        self.rect.center = self.hitbox.center
        self.pos.x,self.pos.y = self.hitbox.centerx,self.hitbox.centery

    def update(self, dt):
        self.input()
        self.move(dt)
        self.update_timers()
        self.get_target_position() #I'm thinking about running that only in case of using tool, will see if need some optim
        self.get_status()
        self.animate(dt)

        debug(self.status)

import pygame
import random
import os
import yaml
from menu import Menu
from support import import_folder, split_text_by_space
from settings import *

"""some of the code is redundant to player class
could be good to generalise but for now WND"""

"""I expect a pb when will implement collision with player
cause already collision collision_sprite vs NPC so NPC cannot be into collision sprite"""

class NPC(pygame.sprite.Sprite):

    def __init__(self, route_file, group, collision_sprites, name, next='start', encounter=0):
        super().__init__(group)
        self.sprite_type = 'npc'
        self.name = name

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
        self.encounter = encounter
        self.next = next
        self.flags = {}
        with open(f"../data/dialogues/{self.name}/{self.name}{self.encounter}.yaml", "r", encoding="utf-8") as f:
            self.dialogue = yaml.safe_load(f)
            print(f'{self.name}{self.encounter}.yaml')

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

    def __init__(self, player, state_manager):

        self.player = player
        self.state_manager = state_manager

        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 30)

        self.background_surf = pygame.image.load('../graphics/UI/black_long_button_1200x150.png')

        self.text_background_surf1 = pygame.image.load('../graphics/UI/clear_less_box_1020x110.png')
        self.text_background_surf1_selected = pygame.image.load('../graphics/UI/clear_box_1020x110.png')

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

    def setUp(self):
        """method that exe when opening the menu, that is not the same as when initialise the menu"""
        self.npc = list(self.player.talkable_npcs)[0] #for now only choosing one npc if several

        self.face = pygame.image.load('../graphics/characters/npcs/' + self.npc.name + '/Faceset.png').convert_alpha()
        self.face = pygame.transform.scale(self.face, (100, 100))
        self.face_rect = self.face.get_rect(bottomleft=(65, SCREEN_HEIGHT - 65))

        self.dialogue = self.npc.dialogue

        self.next = self.npc.next #here something that take into account where we are in the discution for now just start
        self.nb_choices = 0 #all discusion will begin with the npc talking
        self.listen = True

    def tearDown(self):
        """method that exe when closing the menu"""
        self.player.talking = False
        self.npc.next = self.next

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.listen:
                        if 'next' in self.dialogue[self.next]['choices'][self.index]:
                            self.next = self.dialogue[self.next]['choices'][self.index]['next']
                        else: self.state_manager.close_state()

                        if 'trigger' in self.choices[self.index]:
                            if self.choices[self.index]['trigger'] == 'close_dialogue':
                                self.state_manager.close_state()

                        # Handle set_flag from specific choice
                        selected = self.choices[self.index]
                        flag = selected.get('set_flag')
                        if flag:
                            if isinstance(flag, dict):
                                name = flag['name']
                                scope = flag.get('scope', 'npc')  # 'npc' or 'player'
                                if scope == 'player':
                                    self.player.flags[name] = True
                                else:
                                    self.npc.flags[name] = True
                            elif isinstance(flag, str):
                                # treat a simple string as a flag name for the npc.flags dict
                                self.npc.flags[flag] = True

                        unflag = selected.get('unset_flag')
                        if unflag:
                            if isinstance(unflag, dict):
                                name = unflag['name']
                                scope = unflag.get('scope', 'npc')  # 'npc' or 'player'
                                if scope == 'player':
                                    self.player.flags[name] = False
                                else:
                                    self.npc.flags[name] = False
                            elif isinstance(unflag, str):
                                # treat a simple string as a flag name for the npc.flags dict
                                self.npc.flags[unflag] = False

                    elif not self.choices: #mean the dialogue is over after that
                        if 'next' in self.dialogue[self.next]:
                            self.next = self.dialogue[self.next]['next']
                        self.state_manager.close_state()
                    self.listen = not self.listen
                    self.index = 0
                elif event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.index += 1
                elif event.key in [pygame.K_UP, pygame.K_z]:
                    self.index -= 1
                if self.index > self.nb_choices-1:
                    self.index = 0
                if self.index < 0:
                    self.index = self.nb_choices-1

    def update(self):
        """maybe could use that to change the selected surface"""
        current = self.dialogue[self.next]

        # Handle node-level condition
        cond = current.get('condition')
        all_cond = current.get('all_condition')
        if cond:
            name = cond['name'] if isinstance(cond, dict) else cond
            if not self.player.flags.get(name, False):
                self.next = current.get('fallback', 'start')
                current = self.dialogue[self.next]
        elif all_cond:
            if not all(self.player.flags.get(name, False) for name in all_cond):
                self.next = current.get('fallback', 'start')
                current = self.dialogue[self.next]

        self.text = current['text']
        if 'choices' in current:
            self.choices = []
            for choice in current.get('choices', []):
                cond = choice.get('condition')
                if cond:
                    name = cond['name'] if isinstance(cond, dict) else cond
                    if not self.player.flags.get(name, False):
                        continue  # skip this choice

                elif all_cond:
                    if not all(self.player.flags.get(name, False) for name in all_cond):
                        continue  # skip this choice

                self.choices.append(choice)

        else:
            self.choices = []
        if self.listen: self.nb_choices = 0
        else: self.nb_choices = len(self.choices)

        flag = current.get('set_flag')
        if flag:
            if isinstance(flag, dict):
                name = flag['name']
                scope = flag.get('scope', 'npc')  # 'npc' or 'player'
                if scope == 'player':
                    self.player.flags[name] = True
                else:
                    self.npc.flags[name] = True
            elif isinstance(flag, str):
                # treat a simple string as a flag name for the npc.flags dict
                self.npc.flags[flag] = True

        unflag = current.get('unset_flag')
        if unflag:
            if isinstance(unflag, dict):
                name = unflag['name']
                scope = unflag.get('scope', 'npc')  # 'npc' or 'player'
                if scope == 'player':
                    self.player.flags[name] = False
                else:
                    self.npc.flags[name] = False
            elif isinstance(unflag, str):
                # treat a simple string as a flag name for the npc.flags dict
                self.npc.flags[flag] = False

    def display_text_background(self, surface):
        if self.nb_choices == 0:
            surface.blit(self.text_background_surf1, (200, SCREEN_HEIGHT - 170))
        if self.nb_choices == 1:
            surface.blit(self.text_background_surf1_selected, (200, SCREEN_HEIGHT - 170))
        if self.nb_choices == 2:
            surface.blit(self.text_background_surf2[0+self.index], (200, SCREEN_HEIGHT - 170))
            surface.blit(self.text_background_surf2[(1+self.index)%2], (200, SCREEN_HEIGHT - 105))
        if self.nb_choices == 3:
            surface.blit(self.text_background_surf3[0+self.index], (200, SCREEN_HEIGHT - 170))
            surface.blit(self.text_background_surf3[(2+self.index)%3], (200, SCREEN_HEIGHT - 130))
            surface.blit(self.text_background_surf3[(1+self.index)%3], (200, SCREEN_HEIGHT - 90))

    def display_text(self, surface):
        if self.listen: #to avoid render each could just store in self.text_render and flush it when not listening

            # Render and display the main dialogue line
            multi_line_text = split_text_by_space(self.text, max_length=85)
            for idx, line in enumerate(multi_line_text):
                text_render = self.font.render(line, False, 'black')
                surface.blit(text_render, (220, SCREEN_HEIGHT - 160 + 26*idx))  # Adjust position as needed
        else:
            # Render and display all choices
            for i, choice in enumerate(self.choices):
                text = choice['text']
                text_render = self.font.render(text, False, 'black')

                if self.listen:
                    # Render and display the main dialogue line
                    text_render = self.font.render(self.text, False, 'black')
                    surface.blit(text_render, (215, SCREEN_HEIGHT - 160))
                else:
                    for i, choice in enumerate(self.choices):
                        text_render = self.font.render(choice['text'], False, 'black')

                        # Fixed vertical positions based on number of choices
                        if self.nb_choices == 1:
                            y = SCREEN_HEIGHT - 160
                        elif self.nb_choices == 2:
                            y = SCREEN_HEIGHT - 164 if i == 0 else SCREEN_HEIGHT - 99
                        elif self.nb_choices == 3:
                            y_positions = [SCREEN_HEIGHT - 171, SCREEN_HEIGHT - 131, SCREEN_HEIGHT - 91]
                            if i < 3:
                                y = y_positions[i]
                            else:
                                continue  # Ignore extra choices

                        surface.blit(text_render, (215, y))

    def draw(self, surface):
        surface.blit(self.background_surf, (40, SCREEN_HEIGHT - 190))
        surface.blit(self.frame_surf, self.frame_rect)
        surface.blit(self.face, self.face_rect)
        self.display_text_background(surface)
        self.display_text(surface)

import pygame
import random
import os
import yaml
import traceback
from menu import Menu
from support import import_folder, split_text_by_space
from settings import *

"""some of the code is redundant to player class
could be good to generalise but for now WND"""

"""I expect a pb when will implement collision with player
cause already collision collision_sprite vs NPC so NPC cannot be into collision sprite"""

class NPC(pygame.sprite.Sprite):

    def __init__(self, route_file, group, collision_sprites, name, saved_data=None):
        super().__init__(group)
        self.sprite_type = 'npc'
        self.name = name

        #dialogue
        if not saved_data:
            saved_data = {}
        save_npc = saved_data.get(name, {})
        self.encounter = save_npc.get('encounter', 0)
        self.next = save_npc.get('next', "start")
        self.flags = save_npc.get('flags', {})
        with open(f"../data/dialogues/{self.name}/{self.name}{self.encounter}.yaml", "r", encoding="utf-8") as f:
            self.dialogue = yaml.safe_load(f)
            print(f'{self.name}{self.encounter}.yaml')

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

    def load_route(self, file_path):
        with open(file_path, 'r') as record:
            self.start_pos = tuple(map(int, record.readline().strip().split(',')))
            self.route = [tuple(map(int, line.strip().split(','))) for line in record]

    def import_assets(self):
        self.animations = {'up': [], 'down': [], 'right': [], 'left': [],
                           'up_idle': [], 'down_idle': [], 'right_idle': [], 'left_idle': [],}

        if self.name == 'Antoine' and self.flags.get('beanie', False):
            sup_folder = '/with_beanie'
        else: sup_folder = ''

        for animation in self.animations.keys():
            full_path = '../graphics/characters/npcs/' + self.name + sup_folder + '/' + animation
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
        # For faceset animation
        self.frame_index = 0
        self.animation_speed = 7
        self.faceset_animations = [pygame.transform.scale(image, (100, 100)) for image in import_folder('../graphics/characters/player/Faceset')]

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

    def setUp(self, dt):
        """method that exe when opening the menu, that is not the same as when initialise the menu"""

        self.dt = dt
        self.npc = list(self.player.talkable_npcs)[0] #for now only choosing one npc if several

        if self.npc.name == 'Antoine' and self.npc.flags.get('beanie', False):
            sup_folder = '/with_beanie'
        else: sup_folder = ''
        self.npc_face = pygame.image.load('../graphics/characters/npcs/' + self.npc.name + sup_folder + '/Faceset.png').convert_alpha()
        self.npc_face = pygame.transform.scale(self.npc_face, (100, 100))
        self.npc_face_rect = self.npc_face.get_rect(bottomleft=(65, SCREEN_HEIGHT - 65))

        self.dialogue = self.npc.dialogue

        self.next = self.npc.next #here something that take into account where we are in the discution for now just start
        self.nb_choices = 0 #all discusion will begin with the npc talking
        self.listen = True

        # Inventory check
        if 'apple' in self.player.item_inventory:
            self.player.flags["pomme"] = True
        if 'stylised_beanie' in self.player.item_inventory:
            self.player.flags["have_stylised_beanie"] = True

        self.already_triggered = False  # node_level triggers now apply only once and not at each frames

    def tearDown(self):
        """method that exe when closing the menu"""
        self.player.talking = False
        self.npc.next = self.next

        # Clean inventory related flags
        self.player.flags.pop("pomme", None)

    def trigger_action(self, action):
        """called when 'trigger' keyword is found on a dialogue
        execute the instructions linked to the action that follows that 'trigger' keyword"""

        if action == 'close_dialogue':
            self.state_manager.close_state()
        if action == 'give_apple':
            self.player.give('apple')
        if action == 'give_beanie':
            self.player.give('stylised_beanie')
            #make the npc wear it inside dialogue UI
            self.npc_face = pygame.image.load(
                '../graphics/characters/npcs/' + self.npc.name + '/with_beanie' + '/Faceset.png').convert_alpha()
            self.npc_face = pygame.transform.scale(self.npc_face, (100, 100))
            #make the npc wear it in the map
            self.npc.flags["beanie"] = True
            self.npc.import_assets()

        #get_something actions : (ie the player receive something from the npc)
        if action == 'get_flowers':
            self.player.receive('flowers')
        if action == 'get_apples':
            self.player.receive('apple', 10)
        if action == 'get_strawberries':
            self.player.receive('strawberry', 5)
        if action == 'get_peaches':
            self.player.receive('peach', 5)
        if action == 'get_oranges':
            self.player.receive('orange', 5)
        if action == 'get_beanie':
            self.player.receive('black_beanie', 1)
            special_shop = self.state_manager.states['shop'].shops[2]
            special_shop.inventory['seewing_needle'] = 1
            special_shop.inventory['white_thread'] = 1

        print(action)

    def handle_input(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                try:
                    if event.key == pygame.K_SPACE:
                        if not self.listen:
                            self.already_triggered = False  # reset the trigger for node-level triggers, putting the reset at choice level is strange but prevent double triggers
                            visible_choices = []
                            for choice in self.dialogue[self.next]['choices']:
                                if 'condition' not in choice or (
                                        self.player.flags.get(choice['condition'], False)
                                        or self.npc.flags.get(choice['condition'], False)):
                                    if 'not_condition' not in choice or not (
                                            self.player.flags.get(choice['not_condition'], False)
                                            or self.npc.flags.get(choice['not_condition'], False)):
                                        visible_choices.append(choice)

                            if 'next' in visible_choices[self.index]:
                                self.next = visible_choices[self.index]['next']
                            else: self.state_manager.close_state()

                            if 'trigger' in visible_choices[self.index]:
                                self.trigger_action(visible_choices[self.index]['trigger'])

                            # Handle set_flag from specific choice
                            selected = visible_choices[self.index]
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
                except Exception as e:
                    traceback.print_exc()  # prints full traceback to stderr
                    print("Error:", e)  # prints the exception message
                    self.next = "SAFE_GUARD"

    def update(self):
        """maybe could use that to change the selected surface"""
        try:
            current = self.dialogue[self.next]

            # Handle node-level condition
            cond = current.get('condition')
            all_cond = current.get('all_condition')
            if cond:
                name = cond['name'] if isinstance(cond, dict) else cond
                if not (self.player.flags.get(name, False) or self.npc.flags.get(name, False)):
                    self.next = current.get('fallback', 'start')
                    current = self.dialogue[self.next]
            elif all_cond:
                if not all(self.player.flags.get(name, False) for name in all_cond):
                    self.next = current.get('fallback', 'start')
                    current = self.dialogue[self.next]

            # Handle node-level trigger :
            if 'trigger' in current and not self.already_triggered:
                self.already_triggered = True #that is not elegant but too complicated otherwise I think
                self.trigger_action(current['trigger'])

            self.text = current['text']
            if 'choices' in current:
                self.choices = []
                for choice in current.get('choices', []):
                    cond = choice.get('condition')
                    if cond:
                        name = cond['name'] if isinstance(cond, dict) else cond
                        if not (self.player.flags.get(name, False) or self.npc.flags.get(name, False)):
                            continue  # skip this choice
                    not_cond = choice.get('not_condition')
                    if not_cond:
                        name = not_cond['name'] if isinstance(not_cond, dict) else not_cond
                        if (self.player.flags.get(name, False) or self.npc.flags.get(name, False)):
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
        except Exception as e:
            traceback.print_exc()  # prints full traceback to stderr
            print("Error:", e)  # prints the exception message
            self.next = "SAFE_GUARD"

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
            multi_line_text = split_text_by_space(self.text, max_length=82)
            for idx, line in enumerate(multi_line_text):
                text_render = self.font.render(line, False, 'black')
                surface.blit(text_render, (220, SCREEN_HEIGHT - 160 + 26*idx))  # Adjust position as needed
        else:
            # Render and display all choices
            for i, choice in enumerate(self.choices):
                text = choice['text']

                # Fixed vertical positions based on number of choices
                if self.nb_choices == 1:
                    multi_line_text = split_text_by_space(text, max_length=82)
                    for idx, line in enumerate(multi_line_text):
                        text_render = self.font.render(line, False, 'black')
                        surface.blit(text_render, (220, SCREEN_HEIGHT - 160 + 26 * idx))  # Adjust position as needed
                elif self.nb_choices == 2:
                    y = SCREEN_HEIGHT - 164 if i == 0 else SCREEN_HEIGHT - 99
                    text_render = self.font.render(text, False, 'black')
                    surface.blit(text_render, (215, y))
                elif self.nb_choices == 3:
                    y_positions = [SCREEN_HEIGHT - 171, SCREEN_HEIGHT - 131, SCREEN_HEIGHT - 91]
                    if i < 3:
                        y = y_positions[i]
                    else:
                        continue  # Ignore extra choices
                    text_render = self.font.render(text, False, 'black')
                    surface.blit(text_render, (215, y))

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.faceset_animations):
            self.frame_index = 0
        self.faceset_image = self.faceset_animations[int(self.frame_index)]

    def draw(self, surface):
        surface.blit(self.background_surf, (40, SCREEN_HEIGHT - 190))
        surface.blit(self.frame_surf, self.frame_rect)
        if self.listen:
            surface.blit(self.npc_face, self.npc_face_rect)
        else:
            self.animate(self.dt)
            surface.blit(self.faceset_image, self.npc_face_rect)
        self.display_text_background(surface)
        self.display_text(surface)

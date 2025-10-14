import pygame
from settings import *

class Overlay:
    def __init__(self, player, state_manager):
        self.display_surface = pygame.display.get_surface()
        self.player = player
        self.state_manager = state_manager

        #dialogue button
        self.dialogue_button_surf = pygame.image.load('../graphics/UI/clear_box_270x30.png')
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 25)
        self.text_talk_button = self.font.render("Parler ? (Touche Entrée)", False, 'black')

        #imports
        overlay_path = '../graphics/overlay/'
        self.tools_surf = {tool:pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in ['axe', 'jump', 'hoe', 'water', 'fishing', 'hand']}
        self.seeds_surf = {seed:pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha() for seed in player.seeds}

    def display(self):

        if not self.player.talking:
            #seeds
            seed_surf = self.seeds_surf[self.player.selected_seed]
            seed_rect = seed_surf.get_rect(midbottom = OVERLAY_POSITIONS['seed'])
            self.display_surface.blit(seed_surf, seed_rect)

            # tool
            tool_surf = self.tools_surf[self.player.selected_tool]
            tool_rect = tool_surf.get_rect(midbottom=OVERLAY_POSITIONS['tool'])
            self.display_surface.blit(tool_surf, tool_rect)

            # dialogue button
            if self.player.talkable_npcs and not self.state_manager.active_state:
                self.display_surface.blit(self.dialogue_button_surf, (SCREEN_WIDTH//2-135, SCREEN_HEIGHT-40))
                self.display_surface.blit(self.text_talk_button, (SCREEN_WIDTH//2-119, SCREEN_HEIGHT-38))

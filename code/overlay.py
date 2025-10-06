import pygame
from settings import *

class Overlay:
    def __init__(self, player):
        self.display_surface = pygame.display.get_surface()
        self.player = player

        #dialogue button
        self.dialogue_button_surf = pygame.Surface((300,30))
        self.dialogue_button_rect = self.dialogue_button_surf.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT-20))

        #imports
        overlay_path = '../graphics/overlay/'
        self.tools_surf = {tool:pygame.image.load(f'{overlay_path}{tool}.png').convert_alpha() for tool in player.tools}
        self.seeds_surf = {seed:pygame.image.load(f'{overlay_path}{seed}.png').convert_alpha() for seed in player.seeds}

    def display(self):

        #seeds
        seed_surf = self.seeds_surf[self.player.selected_seed]
        seed_rect = seed_surf.get_rect(midbottom = OVERLAY_POSITIONS['seed'])
        self.display_surface.blit(seed_surf, seed_rect)

        # tool
        tool_surf = self.tools_surf[self.player.selected_tool]
        tool_rect = tool_surf.get_rect(midbottom=OVERLAY_POSITIONS['tool'])
        self.display_surface.blit(tool_surf, tool_rect)

        # dialogue button
        if self.player.talkable_npcs:
            self.display_surface.blit(self.dialogue_button_surf, self.dialogue_button_rect)
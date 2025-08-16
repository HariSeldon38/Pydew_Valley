import pygame
#from abc import ABC, abstractmethod
from shop import ShopManager
from transition import Transition
from settings import *

class StateManager:
    """This class allow to open/close all the menus of the game.

    There is at most 4 levels of input handling :

        event based handling :
        main.py : Escape to close the game (will be changed later)
            level.py: open/close menus
                shop.py/TabManager: horizontaly switch tab in a shop menu
                    shop.py.ShopLogic: vertically select item and interact

        beside that there is another way to check inputs in the main state of the game:
        input/timer based handling:
        player.py: movement and environement interaction (except for interaction that triggers a menu)
    """
    def __init__(self, player):
        self.player = player

        self.states = {
            "inventory": InventoryMenu(self.player),
            "shop": ShopManager(self.player),
            "pause": PauseMenu(),
        }
        self.active_state_name = None  # e.g. "shop", "inventory", etc.

    @property
    def active_state(self):
        if self.active_state_name:
            return self.states[self.active_state_name]
        return None

    def open_state(self, name):
        if name in self.states:
            self.active_state_name = name

    def close_state(self):
        self.active_state_name = None

    def handle_input(self, events):
        if self.active_state:
            self.active_state.handle_input(events)

    def update(self):
        if self.active_state:
            self.active_state.update()

    def draw(self, surface):
        if self.active_state:
            self.active_state.draw(surface)

class Menu:

    def handle_input(self, events):
        pass
    def update(self):
        pass
    def draw(self, surface):
        pass

class InventoryMenu(Menu):
    def __init__(self, player):
        self.box = pygame.image.load("../graphics/UI/clear_box_48x48.png").convert_alpha()
        self.player = player
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 30)
        self.title_font = pygame.font.Font('../font/LycheeSoda.ttf', 35)

    def display_grid_box(self, pos, margin, rows, cols, surface, screen):
        """
        :param pos: position of the center of the grid
        :param margin: pixels between each cell
        :param rows: nb rows
        :param cols: nb columns
        :param surface: background image of a cell
        :param screen: surface to draw in
        :return: center position of all the cell in the grid
        """
        cell_size = surface.get_size()
        grid_width = cols*cell_size[0]+(cols-1)*margin
        grid_heigth = rows*cell_size[1]+(rows-1)*margin
        grid_center = (grid_width//2, grid_heigth//2)

        center_cells = []
        for i in range(cols):
            xoffset = i * (cell_size[1] + margin)
            for j in range(rows):
                yoffset = j * (cell_size[0] + margin)
                box_rect = surface.get_rect(topleft=(pos[0]+xoffset-grid_center[0],pos[1]+yoffset-grid_center[1]))
                screen.blit(self.box, box_rect)
                center_cells.append(box_rect.center)

        return center_cells

    def fill_grid_with_items(self, screen, cell_centers):
        """
        Draws item icons from the player's inventory into the grid cells.
        :param screen: Surface to draw on
        :param cell_centers: List of center positions for each cell
        """
        # Load item images once
        item_images = {}
        for item_name, path in ITEM_TOKEN.items():
            item_images[item_name] = pygame.image.load(path).convert_alpha()

        # Flatten inventory into a list of item names (repeated by quantity)
        item_list = []
        for item_name, quantity in self.player.item_inventory.items():
            item_list.extend([item_name] * quantity)
        for item_name, quantity in self.player.seed_inventory.items():
            item_list.extend([item_name] * quantity)
        for item_name, quantity in self.player.special_inventory.items():
            item_list.extend([item_name] * quantity)

        # Draw each item into a cell
        for idx, item_name in enumerate(item_list):
            if idx >= len(cell_centers):
                break  # Avoid overflow if too many items

            icon = item_images.get(item_name)
            if icon:
                icon_rect = icon.get_rect(center=cell_centers[idx])
                screen.blit(icon, icon_rect)

    def display_money(self, screen):
        """same method than in Shop"""
        text_surf = self.font.render(f"{self.player.money}*", False, 'black')
        text_rect = text_surf.get_rect(midbottom = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))
        pygame.draw.rect(screen, 'white', text_rect.inflate(10,10),0,4)
        screen.blit(text_surf, text_rect)

    def draw(self, screen):
        grid = self.display_grid_box((SCREEN_WIDTH//2,SCREEN_HEIGHT//2), 10, 5, 10, self.box, screen)
        self.fill_grid_with_items(screen, grid)
        self.display_money(screen)




class PauseMenu(Menu):

    def draw(self, surface):
        pass
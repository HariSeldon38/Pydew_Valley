import pygame
import time
from state_manager import Menu
from settings import *


class InventoryMenu(Menu):
    def __init__(self, player, item_loader):
        self.box = pygame.image.load("../graphics/UI/clear_box_48x48.png").convert_alpha()
        self.player = player
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 30)
        self.title_font = pygame.font.Font('../font/LycheeSoda.ttf', 35)
        self.loader = item_loader

    def setUp(self):
        #load the icons in the inventory (multi-process/threading has been tested and is not relevant here)
        for item_id in self.player.item_inventory:
            self.loader.get_image(item_id)

    def tearDown(self):
        self.loader.clear_cache()

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

        center_cells = [[] for i in range(rows)]
        for i in range(cols):
            xoffset = i * (cell_size[1] + margin)
            for j in range(rows):
                yoffset = j * (cell_size[0] + margin)
                box_rect = surface.get_rect(topleft=(pos[0]+xoffset-grid_center[0],pos[1]+yoffset-grid_center[1]))
                screen.blit(self.box, box_rect)
                center_cells[j].append(box_rect.center)

        return center_cells

    def fill_grid_with_items(self, screen, cell_centers):
        """
        Draws item icons from the player's inventory into the grid cells.
        :param screen: Surface to draw on
        :param cell_centers: List of center positions for each cell
        """

        # Flatten inventory into a list of item names (repeated by quantity)
        item_list = []
        for item_name, quantity in self.player.item_inventory.items():
            item_list.extend([item_name] * quantity)

        # Draw each item into a cell
        nb_cols = len(cell_centers[0])
        for idx, item_name in enumerate(item_list):
            if idx >= len(cell_centers)*len(cell_centers[0]):
                break  # Avoid overflow if too many items

            icon = self.loader.get_image(item_name)
            if icon:
                icon_rect = icon.get_rect(center=cell_centers[idx//nb_cols][idx%nb_cols])
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


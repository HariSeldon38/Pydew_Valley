import pygame
import pandas as pd
import time
from state_manager import Menu
from settings import *
from support import split_text_by_space

class InventoryMenu(Menu):
    def __init__(self, player, item_loader):
        self.nb_rows = 5
        self.nb_cols = 10
        self.box = pygame.image.load("../graphics/UI/clear_box_48x48.png").convert_alpha()
        self.cursor_box = pygame.image.load("../graphics/UI/clear_less_box_48x48.png").convert_alpha()
        self.box_selected = pygame.image.load("../graphics/UI/clear_box_48x48_selected.png").convert_alpha()
        self.cursor_box_selected = pygame.image.load("../graphics/UI/clear_less_box_48x48_selected.png").convert_alpha()
        self.player = player
        self.mini_font = pygame.font.Font('../font/LycheeSoda.ttf', 20)
        self.little_font = pygame.font.Font('../font/LycheeSoda.ttf', 25)
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 30)
        self.title_font = pygame.font.Font('../font/LycheeSoda.ttf', 35)
        self.loader = item_loader

        self.df_craft = pd.read_csv('../data/crafts.csv', index_col=0, keep_default_na=False, na_values=[])
        self.crafting_button = pygame.image.load('../graphics/UI/clear_box_256x35.png')
        self.crafting_text = self.font.render("Assembler ? (Entrée)", False, 'black')

    def setUp(self):
        # Flatten inventory into a list of item names (repeated by quantity)
        self.item_list = []
        for item_id, quantity in self.player.item_inventory.items():
            self.item_list.extend([item_id] * quantity)

            # Load image for item with non 0 quantity
            if quantity:
                self.loader.get_image(item_id)

        self.cursor = [0,0]
        self.selection1 = None
        self.selection2 = None
        self.last_selected = None

    def tearDown(self):
        self.loader.clear_cache()

    def display_grid_box(self, pos, margin, rows, cols, surface, screen):
        """
        Display the grid, of cells that will contain the item images
        position used for 5x10 cells : topleft = 355,220; bottomright = 925,500
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
                center_cells[j].append(box_rect.center)
                if [i,j] == self.cursor and [i,j] not in [self.selection1, self.selection2]:
                    screen.blit(self.cursor_box, box_rect)
                elif [i,j] == self.cursor and [i,j] in [self.selection1, self.selection2]:
                    screen.blit(self.cursor_box_selected, box_rect)
                elif [i,j] != self.cursor and [i,j] in [self.selection1, self.selection2]:
                    screen.blit(self.box_selected, box_rect)
                else:
                    screen.blit(self.box, box_rect)
        return center_cells

    def display_items(self, screen, cell_centers):
        """
        Draws item icons from the player's inventory into the grid cells.
        :param screen: Surface to draw on
        :param cell_centers: List of center positions for each cell
        """
        for idx, item_name in enumerate(self.item_list):
            if idx >= len(cell_centers)*len(cell_centers[0]):
                break  # Avoid overflow if too many items

            icon = self.loader.get_image(item_name)
            if icon:
                icon_rect = icon.get_rect(center=cell_centers[idx//self.nb_cols][idx%self.nb_cols])
                screen.blit(icon, icon_rect)

    def display_name_selected_item(self, screen, cell_centers, offset=30, x_padding=10):
        idx_inventory = (self.cursor[1])*self.nb_cols + self.cursor[0]
        if idx_inventory <= len(self.item_list)-1:
            name = self.loader.get_name(self.item_list[idx_inventory])
            text_surf = self.mini_font.render(name, False, 'black')

            center = cell_centers[self.cursor[1]][self.cursor[0]]
            position = (center[0],center[1]-offset)
            text_rect = text_surf.get_rect(center=position)

            width = text_rect.size[0] + x_padding
            rect_surf = pygame.Surface((width, 30), pygame.SRCALPHA)
            pygame.draw.rect(rect_surf, (255, 255, 255), rect_surf.get_rect(), border_radius=4)
            rect_pos = rect_surf.get_rect(center=position)
            screen.blit(rect_surf, rect_pos)
            screen.blit(text_surf, text_rect)

    def display_panels(self, screen, width=256, padding=20):
        """
        Display informations right and left to the inventory grid if items are selected.
        How it works: define functions that will be executed twice, the second time with x-axis offset
        """
        def background(display_surf, selection_id):
            if selection_id == 1: offset = 0
            else: offset = 866
            rect_surf = pygame.image.load('../graphics/UI/light_edges_upscaled3_268x288.png')
            rect_pos = (355-width-padding+offset,216)
            display_surf.blit(rect_surf, rect_pos)
        def frame_item(display_surf, selection_id):
            if selection_id == 1: offset = 0
            else: offset = 866
            #rect_surf = pygame.Surface((64,64))
            rect_surf = pygame.image.load('../graphics/UI/black_square_cursor_upscaled2_64x64.png')
            rect_pos = (380-width-padding+offset,241)
            display_surf.blit(rect_surf, rect_pos)
        def big_icon(display_surf, selection_id):
            if selection_id == 1:
                offset = 0
                selection = self.selection1
            else:
                offset = 866
                selection = self.selection2
            idx_inventory = (selection[1])*self.nb_cols + selection[0]
            if idx_inventory <= len(self.item_list) - 1:
                image_surf = self.loader.get_image(self.item_list[idx_inventory])
                bigger_image_surf = pygame.transform.scale(image_surf, (46,46))
                image_rect = bigger_image_surf.get_rect(center=(136+offset,274))
                screen.blit(bigger_image_surf, image_rect)
        def frame_name(display_surf, selection_id):
            if selection_id == 1: offset = 0
            else: offset = 866
            rect_surf = pygame.image.load('../graphics/UI/black_long_button_148x32.png')
            rect_pos = (446-width-padding+offset,256)
            display_surf.blit(rect_surf, rect_pos)
        def big_name(display_surf, selection_id):
            if selection_id == 1:
                offset = 0
                selection = self.selection1
            else:
                offset = 866
                selection = self.selection2
            center = (246+offset,272)
            idx_inventory = (selection[1])*self.nb_cols + selection[0]
            if idx_inventory <= len(self.item_list) - 1:
                name_surf = self.font.render(self.loader.get_name(self.item_list[idx_inventory]), False, 'black')
                text_rect = name_surf.get_rect(center=center)
                if text_rect.size[0] > 144:
                    name_surf = self.mini_font.render(self.loader.get_name(self.item_list[idx_inventory]), False, 'black')
                    text_rect = name_surf.get_rect(center=center)
                screen.blit(name_surf, text_rect)
        def frame_desc(display_surf, selection_id):
            if selection_id == 1: offset = 0
            else: offset = 866
            #rect_surf = pygame.Surface((196+18,152+18))
            #rect_surf.fill((0,255,0))
            rect_surf = pygame.image.load('../graphics/UI/black_long_button_214x170.png')
            rect_pos = (104+offset,309)
            display_surf.blit(rect_surf, rect_pos)
        def description(display_surf, selection_id):
            if selection_id == 1:
                offset = 0
                selection = self.selection1
            else:
                offset = 866
                selection = self.selection2
            idx_inventory = (selection[1])*self.nb_cols + selection[0]
            if idx_inventory <= len(self.item_list) - 1:
                desc_text = self.loader.get_description(self.item_list[idx_inventory])
                desc_text_splitted = split_text_by_space(desc_text, max_length=24)
                for idx, line in enumerate(desc_text_splitted):
                    desc_surf = self.mini_font.render(line, False, 'black')
                    topleft = (115 + offset, 316 + idx*20)
                    text_rect = desc_surf.get_rect(topleft=topleft)
                    screen.blit(desc_surf, text_rect)

        def code_wrapper(id):
            background(screen, selection_id=id)
            big_icon(screen, selection_id=id)
            frame_item(screen, selection_id=id)
            frame_name(screen, selection_id=id)
            big_name(screen, selection_id=id)
            frame_desc(screen, selection_id=id)
            description(screen, selection_id=id)
        if self.selection1: code_wrapper(1) # left_panel
        if self.selection2: code_wrapper(2) # right_panel

        """correct bug select cell with no item"""

    def display_money(self, screen):
        """same method than in Shop"""
        text_surf = self.font.render(f"{self.player.money}*", False, 'black')
        text_rect = text_surf.get_rect(midbottom = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))
        pygame.draw.rect(screen, 'white', text_rect.inflate(10,10),0,4)
        screen.blit(text_surf, text_rect)

    def handle_input(self, events):
        """From here player can navigate through the inventory cells
        and select some item with enter"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_z]:
                    self.cursor[1] = max(0, self.cursor[1] - 1)
                if event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.cursor[1] = min(4, self.cursor[1] + 1)
                if event.key in [pygame.K_RIGHT, pygame.K_d]:
                    self.cursor[0] = min(9, self.cursor[0] + 1)
                if event.key in [pygame.K_LEFT, pygame.K_q]:
                    self.cursor[0] = max(0, self.cursor[0] - 1)
                if event.key == pygame.K_SPACE:
                    c = self.cursor.copy()
                    if not self.selection1 and c != self.selection2:
                        self.selection1 = c
                        self.last_selected = 1
                    elif not self.selection2 and c != self.selection1:
                        self.selection2 = c
                        self.last_selected = 2
                    elif c != self.selection1 and c != self.selection2:
                        if self.last_selected == 1:
                            self.selection2 = c
                            self.last_selected = 2
                        else:
                            self.selection1 = c
                            self.last_selected = 1
                    elif self.cursor == self.selection1:
                        self.selection1 = None
                    else:
                        self.selection2 = None

                if self.selection1 and self.selection2:
                    if event.key == pygame.K_RETURN:
                        self.craft()

    def craft(self):
        idx_invent1 = (self.selection1[1]) * self.nb_cols + self.selection1[0]
        idx_invent2 = (self.selection2[1]) * self.nb_cols + self.selection2[0]
        if idx_invent1 <= len(self.item_list) - 1 and idx_invent2 <= len(self.item_list) - 1: #selection is not empty
            item1 = self.item_list[idx_invent1]
            item2 = self.item_list[idx_invent2]

            crafted_item = self.df_craft[item1][item2]
            if crafted_item:
                self.player.item_inventory.setdefault(crafted_item, 0)
                self.player.item_inventory[crafted_item] += 1  # why not use player add ?
                self.player.item_inventory[item1] -= 1
                self.player.item_inventory[item2] -= 1
                self.setUp()
                self.selection1 = [(len(self.item_list)-1)%10, (len(self.item_list)-1)//10]
                self.last_selected = 1
                self.cursor = list(self.selection1)
                return True
        return False

    def display_crafting_button(self, screen):
        screen.blit(self.crafting_button, (SCREEN_WIDTH//2-124, SCREEN_HEIGHT-190))
        screen.blit(self.crafting_text, (SCREEN_WIDTH//2-116, SCREEN_HEIGHT-189))

    def draw(self, screen):
        grid = self.display_grid_box((SCREEN_WIDTH//2,SCREEN_HEIGHT//2), 10, self.nb_rows, self.nb_cols, self.box, screen)
        self.display_items(screen, grid)
        self.display_panels(screen)
        self.display_name_selected_item(screen, grid)
        self.display_money(screen)
        if self.selection1 and self.selection2:
            self.display_crafting_button(screen)

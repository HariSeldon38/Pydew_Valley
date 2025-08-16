import pygame
from abc import ABC, abstractmethod
from timer import Timer
from settings import *

class ShopManager:
    """my solution involve certain attributes required when creating class (ShopLogic)
    but are not define as abstractmethod property, (except 'transaction') otherwise will be too heavy"""
    def __init__(self, player):
        self.player = player

        #tab management
        self.shops = [
            BuyShop(player),
            SellShop(player),
            SpecialShop(player)
        ]
        self.shop_index = 0

    def handle_input(self, events):
        """From here player can switch between the different tabs/shops"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_RIGHT, pygame.K_d]:
                    self.shop_index -= 1
                elif event.key in [pygame.K_LEFT, pygame.K_q]:
                    self.shop_index += 1
        if self.shop_index < 0:
            self.shop_index = len(self.shops)-1
        if self.shop_index > len(self.shops)-1:
            self.shop_index = 0

        #then we call input method of the current shop that handle item selection (vertical movement)
        self.shops[self.shop_index].handle_input(events)

    def update(self):
        self.shops[self.shop_index].update()

    def draw(self, screen):
        """for now separating update and drawing is not implemented"""
        pass

class ShopLogic(ABC):
    def __init__(self, player):
        self.player = player
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 30)
        self.title_font = pygame.font.Font('../font/LycheeSoda.ttf', 35)

        #options
        self.width = 700
        self.space = 10
        self.padding = 8

        self.setup()

        #movement
        self.index = 0

    def setup(self):
        self.text_surfs = []
        self.total_height = 0
        for item in self.options:
            text_surf = self.font.render(item, False, 'black')
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)
        self.total_height += (len(self.text_surfs) - 1) * self.space
        self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        self.main_rect = pygame.Rect(SCREEN_WIDTH / 2 - self.width / 2, self.menu_top, self.width, self.total_height)

    def display_money(self):
        text_surf = self.font.render(f"{self.player.money}*", False, 'black')
        text_rect = text_surf.get_rect(midbottom = (SCREEN_WIDTH / 2, SCREEN_HEIGHT - 20))
        pygame.draw.rect(self.display_surface, 'white', text_rect.inflate(10,10),0,4)
        self.display_surface.blit(text_surf, text_rect)
    def display_arrow_boxes(self):
        left_arrow = self.font.render(f"<", False, 'black')
        left_rect = left_arrow.get_rect(center=((SCREEN_WIDTH-self.width)/2 - 50, SCREEN_HEIGHT/2))
        right_arrow = self.font.render(f">", False, 'black')
        right_rect = right_arrow.get_rect(center=((SCREEN_WIDTH+self.width)/2 + 50, SCREEN_HEIGHT/2))
        pygame.draw.rect(self.display_surface, 'white', left_rect.inflate(12, 12), 0, 4)
        self.display_surface.blit(left_arrow, left_rect)
        pygame.draw.rect(self.display_surface, 'white', right_rect.inflate(12, 12), 0, 4)
        self.display_surface.blit(right_arrow, right_rect)
    def display_shop_title(self):
        title_text = self.title_font.render(f"{self.title}", False, 'black')
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH/2, self.menu_top - 50))
        pygame.draw.rect(self.display_surface, 'white', title_rect.inflate(20, 15), 0, 4)
        self.display_surface.blit(title_text, title_rect)

    @property
    @abstractmethod
    def action_text(self):
        pass

    @property
    @abstractmethod
    def options(self):
        pass

    @abstractmethod
    def transaction(self):
        pass

    def show_entry(self, text_surf, amount, top, selected):
        #background
        bg_rect = pygame.Rect(self.main_rect.left, top, self.width, text_surf.get_height()+self.padding*2)
        pygame.draw.rect(self.display_surface, 'white', bg_rect,0,4)

        #text
        text_rect = text_surf.get_rect(midleft = (self.main_rect.left+20, bg_rect.centery))
        self.display_surface.blit(text_surf, text_rect)

        #amount
        amount_surf = self.font.render(str(amount), False, 'black')
        amount_rect = amount_surf.get_rect(midright = (self.main_rect.right-20, bg_rect.centery))
        self.display_surface.blit(amount_surf, amount_rect)

        if selected:
            pygame.draw.rect(self.display_surface, 'black', bg_rect,4,4)
            pos_rect = self.action_text.get_rect(center = (self.main_rect.centerx + 42, bg_rect.centery))
            self.display_surface.blit(self.action_text, pos_rect)

    def handle_input(self, events):
        """From here player can switch between the different items in the current shop
        and interact with it (buy or sell)"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_UP, pygame.K_z]:
                    self.index -= 1
                if event.key in [pygame.K_DOWN, pygame.K_s]:
                    self.index += 1
                if event.key == pygame.K_SPACE:
                    self.current_item = self.options[self.index]
                    self.transaction()
        if self.index < 0:
            self.index = len(self.options) - 1
        if self.index > len(self.options) - 1:
            self.index = 0
        self.current_item = self.options[self.index]

    def update(self):
        self.display_money()
        self.display_arrow_boxes()
        self.display_shop_title()
        for text_index, text_surf in enumerate(self.text_surfs):
            top = self.main_rect.top + text_index * (text_surf.get_height() + self.padding*2 + self.space)
            self.show_entry(text_surf, self.inventory[self.options[text_index]], top, self.index==text_index)

class SellShop(ShopLogic):
    def __init__(self, player):
        self.inventory = player.item_inventory
        super().__init__(player)
        self.current_item = self.options[self.index]
        self.title = 'comptoir des récoltes'

    @property
    def action_text(self):
        return self.font.render(f'prix de vente: {SALE_PRICES[self.current_item]}*', False, 'black')
    @property
    def options(self):
        return list(self.inventory.keys())
    def transaction(self):
        if self.inventory[self.current_item] > 0:
            self.inventory[self.current_item] -= 1
            self.player.money += SALE_PRICES[self.current_item]

class BuyShop(ShopLogic):
    def __init__(self, player):
        self.inventory = player.seed_inventory
        super().__init__(player)
        self.current_item = self.options[self.index]
        self.title = 'Marché aux graines'

    @property
    def action_text(self):
        return self.font.render(f"prix d'achat: {PURCHASE_PRICES[self.current_item]}*", False,'black')
    @property
    def options(self):
        return list(self.inventory.keys())
    def transaction(self):
        item_price = PURCHASE_PRICES[self.current_item]
        if self.player.money >= item_price:
            self.inventory.setdefault(self.current_item, 0)
            self.inventory[self.current_item] += 1
            self.player.money -= item_price

class SpecialShop(BuyShop):
    def __init__(self, player):
        super().__init__(player)
        self.inventory = player.special_inventory
        self.title = 'Trésors et reliques'
    @property
    def options(self):
        """cannot use inventory because it would be seed_inventory no matter what I do,
        used before I redefine it in super()init and if super after, will redefine it itself."""
        return list(self.player.special_inventory.keys())


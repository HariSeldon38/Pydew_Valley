import pygame
from abc import ABC, abstractmethod
from settings import *

SALE_PRICES = {
	'Bois': 4,
	'Pomme': 2,
	'Maïs': 10,
	'Tomate': 20
}
PURCHASE_PRICES = {
	'Graines de maïs': 4,
	'Graines de tomate': 5,
	'Bonnet noir': 500,
	'canne à pêche': 500,
	'Kit de broderie': 1000,
	'Fil blanc': 50
}
SELL_SHOP_INVENTORY = {
    'Bois': None,
    'Pomme': None,
    'Maïs': None,
    'Tomate': None,
}
BUY_SHOP_INVENTORY = {
    'Graines de maïs': float('inf'),
    'Graines de tomate': float('inf'),
}
SPECIAL_SHOP_INVENTORY = {
    'Bonnet noir': 1,
    'canne à pêche': 0,
    'Kit de broderie': 0,
    'Fil blanc': 0,
}

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
        for item in self.inventory:
            if self.inventory[item] != 0:
                text_surf = self.font.render(item, False, 'black')
                self.text_surfs.append(text_surf)
                self.total_height += text_surf.get_height() + (self.padding * 2)
        if self.text_surfs:
            self.total_height += (len(self.text_surfs) - 1) * self.space
            self.menu_top = SCREEN_HEIGHT / 2 - self.total_height / 2
        else:
            self.total_height = 46
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

    def transaction(self, mode):
        if self.mode == 'buy':
            item_price = PURCHASE_PRICES[self.current_item]
            if self.player.money >= item_price:
                self.player.item_inventory.setdefault(self.current_item, 0)
                self.player.item_inventory[self.current_item] += 1
                self.player.money -= item_price
                self.inventory[self.current_item] -= 1
                self.setup()
                print(self.inventory)
                print(self.player.item_inventory)
                if self.inventory[self.current_item] < 0:
                    raise ValueError("An item has negative quantities")
        if self.mode == 'sell':
            if self.current_item in self.player.item_inventory.keys() and self.player.item_inventory[self.current_item] > 0:
                self.player.item_inventory[self.current_item] -= 1
                self.player.money += SALE_PRICES[self.current_item]

    @property
    def options(self):
        if all(value==0 for value in self.inventory.values()):
            return [None]
        return [item for item in self.inventory if self.inventory[item]!=0] #items depleted in shop are not an option

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

    def show_empty_shop(self):
        # background
        bg_rect = pygame.Rect(self.main_rect.centerx-300, 337, 600, 46)
        pygame.draw.rect(self.display_surface, 'white', bg_rect, 0, 4)
        
        # text
        text_surf = self.title_font.render("Désolé cet étal est vide pour le moment", False, 'black')
        text_rect = text_surf.get_rect(center=bg_rect.center)
        self.display_surface.blit(text_surf, text_rect)

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
                    if self.current_item: #ie if shop not empty
                        self.transaction(self.mode)
        if self.index < 0:
            self.index = len(self.options) - 1
        if self.index > len(self.options) - 1:
            self.index = 0
        self.current_item = self.options[self.index]

    def update(self):
        self.display_money()
        self.display_arrow_boxes()
        self.display_shop_title()
        if self.text_surfs:
            for text_index, text_surf in enumerate(self.text_surfs):
                top = self.main_rect.top + text_index * (text_surf.get_height() + self.padding*2 + self.space)
                if self.options[text_index] in self.player.item_inventory.keys():
                    amount = self.player.item_inventory[self.options[text_index]]
                else : amount = 0
                self.show_entry(text_surf, amount, top, self.index==text_index)
        else:
            self.show_empty_shop()

class SellShop(ShopLogic):
    def __init__(self, player):
        self.title = 'comptoir des récoltes'
        self.mode = 'sell'
        self.inventory = SELL_SHOP_INVENTORY
        super().__init__(player)
        self.current_item = self.options[self.index]
    @property
    def action_text(self):
        return self.font.render(f'prix de vente: {SALE_PRICES[self.current_item]}*', False, 'black')

class BuyShop(ShopLogic):
    def __init__(self, player):
        self.title = 'Marché aux graines'
        self.mode = 'buy'
        self.inventory = BUY_SHOP_INVENTORY
        super().__init__(player)
        self.current_item = self.options[self.index]
    @property
    def action_text(self):
        return self.font.render(f"prix d'achat: {PURCHASE_PRICES[self.current_item]}*", False,'black')

class SpecialShop(ShopLogic):
    def __init__(self, player):
        self.title = 'Trésors et reliques'
        self.mode = 'buy'
        self.inventory = SPECIAL_SHOP_INVENTORY
        super().__init__(player)
        self.current_item = self.options[self.index]
    @property
    def action_text(self):
        return self.font.render(f"prix d'achat: {PURCHASE_PRICES[self.current_item]}*", False,'black')


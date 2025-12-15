import pygame
from abc import ABC, abstractmethod
from settings import *

SALE_PRICES = {
    'wood': 7,
    'apple': 4,
    'strawberry': 8,
    'peach': 8,
    'orange': 8,
    'pear': 8,
    'grapes': 8,
    'blueberry': 8,
    'anchovy': 7,
    'angelfish': 20,
    'bass': 10,
    'catfish': 15,
    'crab': 40,
    'goldfish': 30,
    'clownfish': 10,
    'pufferfish': 20,
    'rainbow_trout': 10,
    'surgeonfish': 20,
    'can': 1,
    'rock': 1,
    'worm': 1,
    'salmon': 50,
    'baby_salmon': 20,
    'pumkin': 25,
    'eggplant':25,
    'starfruit': 100,
    'corn': 2,
    'tomato': 4,
    'turnip': 5,
    'cabbage': 6,
    'salad': 7,
    'onion': 8,
    'pickle': 10,
    'carrot': 12,
    'radish': 15,
    'blueflower': 0,

}
PURCHASE_PRICES = {
    'worm': 5,
	'fishing_rod': 100,
	'seewing_needle': 1000,
	'white_thread': 50,
    'axe': 200,
    'hoe': 200,
    'water': 300,
    'corn_seed': 1,
    'tomato_seed': 2,
    'turnip_seed': 2,
    'cabbage_seed': 3,
    'salad_seed': 3,
    'onion_seed': 4,
    'pickle_seed': 5,
    'carrot_seed': 6,
    'radish_seed': 8,
    'blueflower_seed': 10,
}
SELL_SHOP_INVENTORY = {
    'wood': None,
    'apple': None,
    'strawberry': None,
    'peach': None,
    'orange': None,
    'pear': None,
    'grapes': None,
    'blueberry': None,
    'corn': None,
    'tomato': None,
    'anchovy': None,
    'angelfish': None,
    'bass': None,
    'catfish': None,
    'crab': None,
    'goldfish': None,
    'clownfish': None,
    'pufferfish': None,
    'rainbow_trout': None,
    'surgeonfish': None,
    'can': None,
    'rock': None,
    'worm': None,
    'salmon': None,
    'baby_salmon': None,
    'pumkin': None,
    'eggplant': None,
    'starfruit': None,
    'blueflower': None,
    'cabbage': None,
    'carrot': None,
    'onion': None,
    'pickle': None,
    'radish': None,
    'salad': None,
    'turnip': None,
}
BUY_SHOP_INVENTORY = {
    'corn_seed': float('inf'),
    'tomato_seed': 0,
    'blueflower_seed': 0,
    'cabbage_seed': 0,
    'carrot_seed': 0,
    'onion_seed': 0,
    'pickle_seed': 0,
    'radish_seed': 0,
    'salad_seed': 0,
    'turnip_seed': 0,
}
SPECIAL_SHOP_INVENTORY = {
    'axe': 1,
    'hoe': 1,
    'water': 1,
    'fishing_rod': 1,
    'worm': 0,
    'seewing_needle': 0,
    'white_thread': 0,
}

class ShopManager:
    """my solution involve certain attributes required when creating class (ShopLogic)
    but are not define as abstractmethod property, (except 'transaction') otherwise will be too heavy"""
    def __init__(self, player, item_loader):
        self.player = player

        #tab management
        self.shops = [
            BuyShop(player, item_loader),
            SellShop(player, item_loader),
            SpecialShop(player, item_loader)
        ]
        self.shop_index = 0
        self.item_loader = item_loader

    def setUp(self):
        """That method is called when opening the menu"""
        for shop in self.shops:
            shop.setup()

    def tearDown(self):
        pass

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
    def __init__(self, player, item_loader):
        self.player = player
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font('../font/LycheeSoda.ttf', 30)
        self.title_font = pygame.font.Font('../font/LycheeSoda.ttf', 35)
        self.item_loader = item_loader

        #movement
        self.index = 0

        #options
        self.width = 700
        self.space = 10
        self.padding = 8

        self.setup()

    def setup(self):
        """That method is used when init the Shop as well as when opening the shop menu"""
        self.text_surfs = []
        self.total_height = 0
        for item in self.options:
            text_surf = self.font.render(self.item_loader.get_name(item), False, 'black')
            self.text_surfs.append(text_surf)
            self.total_height += text_surf.get_height() + (self.padding * 2)
        if self.text_surfs:
            self.total_height += (len(self.text_surfs) - 1) * self.space
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
                #Handling tools separatedly
                if self.current_item == 'fishing_rod':
                    self.inventory['worm'] = float('inf')
                    self.player.tools.append('fishing')
                elif self.current_item in ['hoe', 'water', 'axe']:
                    self.player.tools.append(self.current_item)

                #Handling seed separatedly
                elif self.current_item =='corn_seed':
                    self.player.item_inventory.setdefault(self.current_item, 0)
                    self.player.item_inventory[self.current_item] += 1
                    self.count_to_unlock_seeds += PURCHASE_PRICES['corn_seed']
                    if  10 <= self.count_to_unlock_seeds <= 50:
                        self.inventory['tomato_seed'] = float('inf')
                        if 'tomato' not in self.player.seeds:
                            self.player.seeds.append('tomato')
                elif self.current_item =='tomato_seed':
                    self.player.item_inventory.setdefault(self.current_item, 0)
                    self.player.item_inventory[self.current_item] += 1
                    self.count_to_unlock_seeds += PURCHASE_PRICES['tomato_seed']
                    if 30 <= self.count_to_unlock_seeds <= 60:
                        self.inventory['turnip_seed'] = float('inf')
                        if 'turnip' not in self.player.seeds:
                            self.player.seeds.append('turnip')
                elif self.current_item =='turnip_seed':
                    self.player.item_inventory.setdefault(self.current_item, 0)
                    self.player.item_inventory[self.current_item] += 1
                    self.count_to_unlock_seeds += PURCHASE_PRICES['turnip_seed']
                    if 50 <= self.count_to_unlock_seeds <= 100:
                        self.inventory['cabbage_seed'] = float('inf')
                        if 'cabbage' not in self.player.seeds:
                            self.player.seeds.append('cabbage')
                elif self.current_item =='cabbage_seed':
                    self.player.item_inventory.setdefault(self.current_item, 0)
                    self.player.item_inventory[self.current_item] += 1
                    self.count_to_unlock_seeds += PURCHASE_PRICES['cabbage_seed']
                    if 80 <= self.count_to_unlock_seeds <= 150:
                        self.inventory['salad_seed'] = float('inf')
                        if 'salad' not in self.player.seeds:
                            self.player.seeds.append('salad')
                elif self.current_item =='salad_seed':
                    self.player.item_inventory.setdefault(self.current_item, 0)
                    self.player.item_inventory[self.current_item] += 1
                    self.count_to_unlock_seeds += PURCHASE_PRICES['salad_seed']
                    if 110 <= self.count_to_unlock_seeds <= 200:
                        self.inventory['onion_seed'] = float('inf')
                        if 'onion' not in self.player.seeds:
                            self.player.seeds.append('onion')
                elif self.current_item =='onion_seed':
                    self.player.item_inventory.setdefault(self.current_item, 0)
                    self.player.item_inventory[self.current_item] += 1
                    self.count_to_unlock_seeds += PURCHASE_PRICES['onion_seed']
                    if 150 <= self.count_to_unlock_seeds <= 250:
                        self.inventory['pickle_seed'] = float('inf')
                        if 'pickle' not in self.player.seeds:
                            self.player.seeds.append('pickle')
                elif self.current_item =='pickle_seed':
                    self.player.item_inventory.setdefault(self.current_item, 0)
                    self.player.item_inventory[self.current_item] += 1
                    self.count_to_unlock_seeds += PURCHASE_PRICES['pickle_seed']
                    if 200 <= self.count_to_unlock_seeds <= 300:
                        self.inventory['carrot_seed'] = float('inf')
                        if 'carrot' not in self.player.seeds:
                            self.player.seeds.append('carrot')
                elif self.current_item =='carrot_seed':
                    self.player.item_inventory.setdefault(self.current_item, 0)
                    self.player.item_inventory[self.current_item] += 1
                    self.count_to_unlock_seeds += PURCHASE_PRICES['carrot_seed']
                    if 260 <= self.count_to_unlock_seeds <= 350:
                        self.inventory['radish_seed'] = float('inf')
                        if 'radish' not in self.player.seeds:
                            self.player.seeds.append('radish')
                elif self.current_item =='radish_seed':
                    self.player.item_inventory.setdefault(self.current_item, 0)
                    self.player.item_inventory[self.current_item] += 1
                    self.count_to_unlock_seeds += PURCHASE_PRICES['radish_seed']
                    if 340 <= self.count_to_unlock_seeds <= 400:
                        self.inventory['blueflower_seed'] = float('inf')
                        if 'blueflower' not in self.player.seeds:
                            self.player.seeds.append('blueflower')
                elif self.current_item =='blueflower_seed':
                    self.player.item_inventory.setdefault(self.current_item, 0)
                    self.player.item_inventory[self.current_item] += 1
                    self.count_to_unlock_seeds += PURCHASE_PRICES['blueflower_seed']

                else: #Regular items
                    self.player.item_inventory.setdefault(self.current_item, 0)
                    self.player.item_inventory[self.current_item] += 1 #why not use player add ?

                self.player.money -= item_price
                self.inventory[self.current_item] -= 1
                self.setup()
                if self.inventory[self.current_item] < 0:
                    raise ValueError("An item has negative quantities")
        if self.mode == 'sell':
            if self.current_item in self.player.item_inventory.keys() and self.player.item_inventory[self.current_item] > 0:
                self.player.item_inventory[self.current_item] -= 1
                self.player.money += SALE_PRICES[self.current_item]
                if self.player.item_inventory[self.current_item] <= 0:
                    self.index -= 1
                    if self.index < 0: self.index = 0
                    if self.options:
                        self.current_item = self.options[self.index]
                    self.setup()

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
        if self.mode == 'buy':
            text_surf = self.title_font.render("Désolé cet étal est vide pour le moment", False, 'black')
        else:
            text_surf = self.title_font.render("Tu n'as rien à vendre pour le moment", False, 'black')
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
                    if self.options:
                        self.current_item = self.options[self.index]
                        if self.current_item: #ie if shop not empty
                            self.transaction(self.mode)
        if self.index < 0:
            self.index = len(self.options) - 1
        if self.index > len(self.options) - 1:
            self.index = 0
        if self.options:
            self.current_item = self.options[self.index]

    def update(self):
        self.display_money()
        self.display_arrow_boxes()
        self.display_shop_title()
        if self.text_surfs:
            for text_index, text_surf in enumerate(self.text_surfs):
                item = self.options[text_index]   # guaranteed aligned
                amount = self.player.item_inventory.get(item, 0)
                top = self.main_rect.top + text_index * (text_surf.get_height() + self.padding*2 + self.space)
                self.show_entry(text_surf, amount, top, self.index==text_index)
        else:
            self.show_empty_shop()

class SellShop(ShopLogic):
    def __init__(self, player, item_loader):
        self.title = 'comptoir des récoltes'
        self.mode = 'sell'
        self.inventory = SELL_SHOP_INVENTORY
        super().__init__(player, item_loader)
        if self.options:
            self.current_item = self.options[self.index]

    @property
    def options(self):
        option = [item for item in self.inventory if self.player.item_inventory.get(item, 0)!=0]
        if option and not self.index > len(option) - 1:
            self.current_item = option[self.index]
        return option

    @property
    def action_text(self):
        return self.font.render(f'prix de vente: {SALE_PRICES[self.current_item]}*', False, 'black')

class BuyShop(ShopLogic):
    def __init__(self, player, item_loader):
        self.title = 'Marché aux graines'
        self.mode = 'buy'
        self.inventory = BUY_SHOP_INVENTORY
        super().__init__(player, item_loader)
        if self.options:
            self.current_item = self.options[self.index]
        self.count_to_unlock_seeds = 0
    @property
    def action_text(self):
        return self.font.render(f"prix d'achat: {PURCHASE_PRICES[self.current_item]}*", False,'black')

class SpecialShop(ShopLogic):
    def __init__(self, player, item_loader):
        self.title = 'Trésors et reliques'
        self.mode = 'buy'
        self.inventory = SPECIAL_SHOP_INVENTORY
        super().__init__(player, item_loader)
        if self.options:
            self.current_item = self.options[self.index]
    @property
    def action_text(self):
        return self.font.render(f"prix d'achat: {PURCHASE_PRICES[self.current_item]}*", False,'black')


import pygame
from menu import Menu
from shop import ShopManager
from inventory import InventoryMenu
from settings import *

class StateManager:
    """This class allow to open/close all the menus of the game.

    There is at most 4 levels of input handling :

        event based handling :
        main.py : Escape to close the game (will be changed later)
            level.py: open/close menus
                shop.py/TabManager: horizontally switch tab in a shop menu
                    shop.py.ShopLogic: vertically select item and interact

        beside that there is another way to check inputs in the main state of the game:
        input/timer based handling:
        player.py: movement and environment interaction (except for interaction that triggers a menu)
    """
    def __init__(self, player, item_loader):
        self.player = player

        self.states = {
            "inventory": InventoryMenu(self.player, item_loader=item_loader),
            "shop": ShopManager(self.player, item_loader=item_loader),
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
            self.states[name].setUp()
            self.active_state_name = name

    def close_state(self):
        self.states[self.active_state_name].tearDown()
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

class PauseMenu(Menu):

    def setUp(self):
        pass
    def tearDown(self):
        pass
    def draw(self, surface):
        pass
import pygame
#from abc import ABC, abstractmethod
from shop import Shop
from transition import Transition

class StateManager:
    def __init__(self, player):
        self.player = player

        self.states = {
            "inventory": InventoryMenu(),
            "shop": Shop(self.player),
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
    pass
class PauseMenu(Menu):

    def draw(self, surface):
        pass
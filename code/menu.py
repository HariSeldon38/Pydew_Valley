from abc import ABC, abstractmethod

class Menu(ABC):

    @abstractmethod
    def setUp(self):
        """method that exe when opening the menu, that is not the same as when initialise the menu"""
        pass
    @abstractmethod
    def tearDown(self):
        """method that exe when closing the menu"""
        pass
    def handle_input(self, events):
        pass
    def update(self):
        pass
    def draw(self, surface):
        pass

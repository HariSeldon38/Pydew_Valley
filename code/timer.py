import pygame

class Timer:
    def __init__(self, duration, func=None, loop=False):
        """func : a function that will be ran at the END of the duration of the timer"""
        self.duration = duration
        self.func = func
        self.loop = loop
        self.start_time = 0
        self.active = False
        self.complete = False

    def activate(self):
        self.active = True
        self.start_time = pygame.time.get_ticks()

    def deactivate(self):
        self.active = False
        self.start_time = 0
        self.complete = True

    def update(self):
        if self.active:
            current_time = pygame.time.get_ticks()
            if current_time - self.start_time >= self.duration:
                self.deactivate()
                if self.func:
                    if isinstance(self.func, list):
                        for elt in self.func:
                            elt()
                    else:
                        self.func()
                if self.loop:
                    self.activate()

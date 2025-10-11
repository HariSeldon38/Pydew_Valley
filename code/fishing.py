from os import path
from typing import Callable
import pygame.key
from timer import Timer
from random import randint, choices
from support import import_folder

class Fishing:
    """
    This class is used to handle the fishing activity by the player
    Possible enhancement : choose possible fish from start and random timing based on that
    """

    def __init__(self, player_add: Callable, fishing_status: bool):
        self.display_surface = pygame.display.get_surface()
        self.ripple_frames = import_folder('../graphics/ripple')
        self.frame_index = 0

        # check that you are not making a new object each time
        self.player_add = player_add
        self.fishing_status = fishing_status

        # timer for fish to plop
        self.fishing_timer = Timer(randint(1000, 2000))
        # timer for reeling on time
        self.reel_on_time = Timer(500)
        # extra timer that reels for me
        self.extra_time = Timer(500)

        # water type (for now just y_position threshold to decide wether pond or sea
        self.water_type = None
        self.y_threshold = 350
        self.fishes = {'salted':   {'salmon': 2,
                                    'crab': 8,
                                    'pufferfish': 10,
                                    'surgeonfish': 10,
                                    'clownfish': 20,
                                    'anchovy': 30,
                                    'can': 20},

                       'fresh':    {'baby_salmon': 8,
                                    'angelfish': 12,
                                    'catfish': 15,
                                    'goldfish': 15, #not so rare but worth a lot, hence the name
                                    'rainbow_trout': 20,
                                    'bass': 20,
                                    'rock': 10}
                       }

    def input(self):
        keys = pygame.key.get_pressed()

        # we are already fishing
        if keys[pygame.K_SPACE]:

            # pulled reel on time or not
            if self.fishing_timer.complete and self.reel_on_time.active:
                if not self.worm:
                    fish = choices(
                        population=list(self.fishes[self.water_type].keys()),
                        weights=list(self.fishes[self.water_type].values()),
                        k=1)[0]
                else:
                    fish_dict = self.fishes[self.water_type]
                    # Exclude one key, e.g. "can"
                    filtered_items = [(k, v) for k, v in fish_dict.items() if k != 'can' and k!='rock']
                    population, weights = zip(*filtered_items)
                    fish = choices(population=population, weights=weights, k=1)[0]

                self.player_add(fish)
                # cancel the reel timer and complete it
                self.end_fishing()

            else:
                self.end_fishing()

        if keys[pygame.K_w] or keys[pygame.K_s] or keys[pygame.K_a] or \
                keys[pygame.K_d]:  # to cancel fishing
            self.end_fishing()

    def fishing_start(self, target_position, water_type, worm=False):
        """
        Begins the fishing activity
        :return: None
        """
        self.worm = worm
        self.water_type = water_type
        self.frame_index = 0
        self.target_position = target_position
        self.fishing_timer.activate()
        self.fishing_status = True

    def end_fishing(self):
        """
        Resets all timers for fishing and makes the player exit fishing mode
        """
        self.fishing_timer.complete = False
        self.reel_on_time.complete = False
        self.extra_time.complete = False
        self.fishing_status = False

    def animate_ripple(self, dt):
        self.frame_index += 10 * dt
        if self.frame_index >= len(self.ripple_frames):
            self.frame_index = 0
        frame = self.ripple_frames[int(self.frame_index)]
        rect = frame.get_rect(center=self.target_position)
        self.display_surface.blit(frame, rect)

    def update(self, dt):
        self.fishing_timer.update()
        self.input()
        # if the fishing timer is complete, do check for reeling, otherwise
        # set the status to complete
        if self.fishing_timer.complete:
            self.animate_ripple(dt)
            if self.reel_on_time.active:
                # update timer for reeling
                self.reel_on_time.update()
            elif not self.reel_on_time.complete:
                # reeling timer did not start so start it now
                self.reel_on_time.activate()
            else:
                # Both fishing and on time reeling are done, so start a new
                # timer that reels for the player
                if self.extra_time.active:
                    self.extra_time.update()
                elif not self.extra_time.complete:
                    self.extra_time.activate()  # not complete, activate
                else:
                    self.end_fishing()

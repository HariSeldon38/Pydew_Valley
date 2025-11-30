import pygame

"""
rain noise
thunder

"""

class SoundManager:
    def __init__(self):
        self.sounds = {
            'just the two of us' : (pygame.mixer.Sound('../audio/music/just_the_two_of_us.wav'), 1),
            'everybody wants to rule the world': (pygame.mixer.Sound('../audio/music/everybody_UNFINISHED.wav'), 1),
            'salmon garden': (pygame.mixer.Sound('../audio/music/salmon_garden_UNFINISHED.wav'), 1),
            #'music': (pygame.mixer.Sound('../audio/bg.mp3'), 1.0),
            #'axe': (pygame.mixer.Sound('../audio/axe.mp3'), 0.7),     #when retrieve apple, two sound at same time
            #'hoe': (pygame.mixer.Sound('../audio/hoe.wav'), 0.3),
            #'plant': (pygame.mixer.Sound('../audio/plant.wav'), 0.2), #don't work if too quiet, shitty sound
            #'watering': (pygame.mixer.Sound('../audio/water.mp3'), 1.0),
            #'pickup': (pygame.mixer.Sound('../audio/sound/success.wav'), 0.4),
        }

        self.global_volume = 0.03  # Default volume
        self.muted = False

        # Apply initial volume
        self._apply_volume()

    def _apply_volume(self):
        for sound_tuple in self.sounds.values():
            sound_tuple[0].set_volume(0.0 if self.muted else self.global_volume * sound_tuple[1])

    def play(self, name, loops=0):
        sound_tuple = self.sounds.get(name)
        if sound_tuple and not self.muted:
            sound_tuple[0].play(loops)
            print('ok')

    def set_volume(self, volume):
        """Set volume between 0.0 and 1.0"""
        self.global_volume = max(0.0, min(1.0, volume))
        self._apply_volume()

    def toggle_mute(self):
        self.muted = not self.muted
        self._apply_volume()

    def mute(self):
        self.muted = True
        self._apply_volume()

    def unmute(self):
        self.muted = False
        self._apply_volume()
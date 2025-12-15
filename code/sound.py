import pygame

"""
rain noise
thunder

"""

class SoundManager:
    def __init__(self):
        self.sounds = {
            'just the two of us' : (pygame.mixer.Sound('../audio/music/Juste Le Blanc_up10bpm_master.wav'), 1),
            'everybody wants to rule the world': (pygame.mixer.Sound('../audio/music/Tout les corps_master.wav'), 1),
            'salmon garden': (pygame.mixer.Sound('../audio/music/Salmon_Garden_master.wav'), 0.8),
            'chat': (pygame.mixer.Sound('../audio/music/Chat.wav'), 1),
            'si facile': (pygame.mixer.Sound('../audio/music/Easy_master.wav'), 0.8),
            'running up': (pygame.mixer.Sound('../audio/music/kate_master.wav'), 1),
            'add1': (pygame.mixer.Sound('../audio/sound/add1.wav'), 0.6),
            'add2': (pygame.mixer.Sound('../audio/sound/add2.wav'), 0.6),
            'add3': (pygame.mixer.Sound('../audio/sound/add3.wav'), 0.6),
            'axe1': (pygame.mixer.Sound('../audio/sound/axe1.wav'), 0.4),
            'axe2': (pygame.mixer.Sound('../audio/sound/axe2.wav'), 0.5),
            'axe3': (pygame.mixer.Sound('../audio/sound/axe3.wav'), 0.4),
            'axe4': (pygame.mixer.Sound('../audio/sound/axe4.wav'), 0.5),
            'evening_start': (pygame.mixer.Sound('../audio/sound/evening_start.wav'), 0.5),
            'fishing1': (pygame.mixer.Sound('../audio/sound/fishing1.wav'), 0.8),
            'fishing2': (pygame.mixer.Sound('../audio/sound/fishing2.wav'), 0.8),
            'hoe1': (pygame.mixer.Sound('../audio/sound/hoe1.wav'), 0.5),
            'hoe2': (pygame.mixer.Sound('../audio/sound/hoe2.wav'), 0.5),
            'hoe3': (pygame.mixer.Sound('../audio/sound/hoe3.wav'), 0.5),
            'hoe4': (pygame.mixer.Sound('../audio/sound/hoe4.wav'), 0.5),
            'hoe5': (pygame.mixer.Sound('../audio/sound/hoe5.wav'), 0.5),
            'rain': (pygame.mixer.Sound('../audio/sound/rain.wav'), 0.5),
            'water1': (pygame.mixer.Sound('../audio/sound/water1.wav'), 0.5),
            'water2': (pygame.mixer.Sound('../audio/sound/water2.wav'), 0.5),
            'water3': (pygame.mixer.Sound('../audio/sound/water3.wav'), 0.5),
            'water4': (pygame.mixer.Sound('../audio/sound/water4.wav'), 0.5),


        }

        self.global_volume = 1  # Default volume
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
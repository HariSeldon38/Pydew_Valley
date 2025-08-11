import pygame
from random import randint, choice
from settings import *
from support import import_folder
from sprites import Generic

class Sky:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.full_surf = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))

        #night and day
        self.day_color = [255, 255, 255]
        self.current_color = self.day_color.copy() # for rain filter, need to decrease R and G, but to select color better maybe bind them to input, see that in the end, fine-tuning
        self.night_color = (38,101,189)

        #weather
        self.full_surf_weather = pygame.Surface((SCREEN_WIDTH,SCREEN_HEIGHT))
        self.current_weather_color = [255, 255, 255]
        self.rain_color = []
        self.ongoing_flash = False

    def display_night(self, dt):
        for index, value in enumerate(self.night_color):
            if self.current_color[index] > value:
                self.current_color[index] -= 1 * dt
        self.full_surf.fill(self.current_color)
        self.display_surface.blit(self.full_surf, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    #def increment_color(self, dt, current_color, target_color, speed)

    def display_weather(self, dt, rain_level):
        """could be good to gather in a single function
        increasing/decreasing current_color to reach target"""

        #luminosity change based on rain level
        if not self.ongoing_flash:
            for index, value in enumerate(self.rain_color):
                if self.current_weather_color[index] > value:
                    self.current_weather_color[index] -= 26 * dt
                elif self.current_weather_color[index] < value:
                    self.current_weather_color[index] += 26 * dt
            self.full_surf_weather.fill(self.current_weather_color)
            self.display_surface.blit(self.full_surf_weather, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

        #random lightning effects
        if rain_level >= 4:
            if self.ongoing_flash:
                if self.flash_phase == 0:
                    all_channels_ready = True
                    for index, value in enumerate(self.flash_peak_color):
                        if self.current_weather_color[index] < value:
                            self.current_weather_color[index] += (340-self.random_speed_offset) * dt
                            all_channels_ready = False
                        if all_channels_ready:
                            self.flash_phase = 1
                if self.flash_phase == 1:
                    all_channels_ready = True
                    for index, value in enumerate(self.tmp_save_color[:2]):
                        if self.current_weather_color[index] > value:
                            self.current_weather_color[index] -= (350-self.random_speed_offset) * dt
                            all_channels_ready = False
                        if all_channels_ready:
                            self.ongoing_flash = False

                self.full_surf_weather.fill(self.current_weather_color)
                self.display_surface.blit(self.full_surf_weather, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

            if not self.ongoing_flash:
                if rain_level < 7:
                    probability = (15-2*rain_level)*1000
                else: probability = 2000
                if randint(1,probability) == 1: #pauses the rain lum change and play a flash "animation"
                    self.ongoing_flash = True
                    self.random_shade_offset = randint(7*rain_level,7*rain_level + 40) #this line can crash if rain_level too low/luminosity too high
                    self.random_speed_offset = randint(0,40)
                    self.flash_peak_color = [255-self.random_shade_offset] * 3  #---------------------------------------------------------------------------make it depend on rain level
                    self.tmp_save_color = self.current_weather_color.copy()
                    self.flash_phase = 0 #one phase it increasing luminosity, other phase is return back to normal

class Drop(Generic):
    def __init__(self, surf, pos, moving, rain_level, groups, z):
        super().__init__(pos, surf, groups, z)
        self.lifetime = randint(350, 550)
        self.start_time = pygame.time.get_ticks()

        #moving
        self.moving = moving
        if self.moving:
            self.pos = pygame.math.Vector2(self.rect.topleft)
            self.direction = pygame.math.Vector2(-2,4)
            self.speed = randint(100+40*rain_level, 160+40*rain_level)

    def update(self, dt):
        if self.moving:
            self.pos += self.direction * self.speed * dt
            self.rect.topleft = round(self.pos.x), round(self.pos.y)

        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.lifetime:
            self.kill()

class Rain:
    def __init__(self, all_sprites, rain_level, sky):
        self.sky = sky
        self.rain_level = rain_level
        self.all_sprites = all_sprites
        self.rain_drops = import_folder('../graphics/rain/drops')
        self.rain_floor = import_folder('../graphics/rain/floor')
        self.floor_w, self.floor_h = pygame.image.load('../graphics/world/ground.png').get_size() #before release need to hardcode these values

    def random_update_rain_status(self):
        if self.rain_level:
            if randint(1, PROBABILITY_STOP_RAIN) == 1:
                self.rain_level = 0
                self.update_rain_color(self.rain_level)
            if randint(1, PROBABILITY_INCREASE_RAIN) == 1:
                self.rain_level += 1
                self.update_rain_color(self.rain_level)
            if self.rain_level > 1:
                if randint(1, PROBABILITY_DECREASE_RAIN) == 1:
                    self.rain_level -= 1
                    self.update_rain_color(self.rain_level)
        if not self.rain_level:
            if randint(1, PROBABILITY_START_RAIN) == 1:
                self.rain_level = 1
                self.update_rain_color(self.rain_level)
            if randint(1, PROBABILITY_SUDDEN_DOWNPOUR) == 1:
                self.rain_level = 5
                self.update_rain_color(self.rain_level)

    def update_rain_color(self, rain_level):
        if rain_level == 0:
            self.sky.rain_color = [255, 255, 255]
        elif rain_level <= 7:
            self.sky.rain_color = [255-20*rain_level,255-20*rain_level,255]
        else:
            self.sky.rain_color = [115,115,255]

    def create_floor(self):
        Drop(
            surf = choice(self.rain_floor),
            pos = (randint(0,self.floor_w),randint(0, self.floor_h)),
            moving = False,
            rain_level = None, #not used if moving is False
            groups = self.all_sprites,
            z = LAYERS['rain floor'])

    def create_drops(self, rain_level):
        if randint(1,3) == 1: #used to mitigate nb of drops on the floor
            Drop(
                surf = choice(self.rain_drops),
                pos = (randint(0,self.floor_w),randint(0, self.floor_h)),
                moving = True,
                rain_level = rain_level,
                groups = self.all_sprites,
                z = LAYERS['rain drops'])

    def update(self):

        if self.rain_level == 1:
            if randint(1,2) == 1: #create drop in sky and ground 1/2 frames
                self.create_floor()
                self.create_drops(self.rain_level)
        else:
            for _ in range(self.rain_level-1): #create 1 drops every frames if rain_level = 2,
                self.create_floor() #              ... 2 drops every frames if = 3
                self.create_drops(self.rain_level) #... and so on
from pygame.math import Vector2
# screen
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
TILE_SIZE = 64

PLAYER_SPEED = 500 #can't go below 177 !
PLAYER_LOW_SPEED = 178 #explained in player.move

#environement
PROBABILITY_STOP_RAIN = 7000
PROBABILITY_START_RAIN = 16000
PROBABILITY_INCREASE_RAIN = 2000
PROBABILITY_DECREASE_RAIN = 4000
PROBABILITY_SUDDEN_DOWNPOUR = 48000

# overlay positions 
OVERLAY_POSITIONS = {
	'tool' : (40, SCREEN_HEIGHT - 15), 
	'seed': (70, SCREEN_HEIGHT - 5)}

PLAYER_TOOL_OFFSET = {
	'hoe' : {
		'left': Vector2(-51,37),
		'right': Vector2(51,37),
		'up': Vector2(12,-32),
		'down': Vector2(-12,50)},
	'axe' : {
		'left': Vector2(-56,37),
		'right': Vector2(56,37),
		'up': Vector2(14,-41),
		'down': Vector2(-12,50)},
	'water' : {
		'left': Vector2(-95,25),
		'right': Vector2(95,25),
		'up': Vector2(23,-44),
		'down': Vector2(-23,60)}
}
LAYERS = {
	'water': 0,
	'ground': 1,
	'soil': 2,
	'soil water': 3,
	'rain floor': 4,
	'house bottom': 5,
	'ground plant': 6,
	'main': 7,
	'house top': 8,
	'fruit': 9,
	'rain drops': 10
}
APPLE_POS = {
	'Small': [(18,17), (30,37), (12,50), (30,45), (20,30), (30,10)],
	'Large': [(30,24), (60,65), (50,50), (16,40),(45,50), (42,70)]
}
GROW_SPEED = {
	'Maïs': 1,
	'Tomate': 0.7
}
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
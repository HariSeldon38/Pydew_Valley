import pygame, sys
from settings import *
from level import Level

class Game:
	def __init__(self):
		pygame.mixer.pre_init(44100, -16, 2, 512)
		pygame.init()
		self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
		pygame.display.set_caption('Vallée du Saumon')
		self.clock = pygame.time.Clock()
		self.level = Level()

	def run(self):
		while True:
			events = pygame.event.get()
			for event in events:
				if event.type == pygame.QUIT:  # closing the window
					pygame.quit()
					sys.exit()

			dt = self.clock.tick() / 1000  # delta time
			self.level.run(events, dt)
			pygame.display.update()

if __name__ == '__main__':
	game = Game()
	game.run()


"""
Notes :

maybegood to check the video about delta time
about dt : we need to store position into pos and not inside the rect. 
		because a rect store the pos as an integer and we use dt to 
		move everything in framerate indep way we will have often float so --> error
		so we move the pos vector and then we update the rect based on that

I did duplicate some frame in idle animation in order to have a slower animation for idling
NO a good thing to do I know, need to change that from the code if I find the time

add a zone unreachable, to give player the envy to reach it and when it does there is a big monster guarding something but the ^player does not have attack and he discover that he have a health bar and can die

peut fabriquer un bonnet nlsqps et l'offrir

un jeu n'arrative d'une heure, première choise a faire assez basique histoire à la con mais reviens à la fin et surprend un peu en montrant que c'était pas si con

better animation for destroying trees or no anim to exacerber feeling of hand made

IDk about the reset way for now, strange to reset when we want


change watering sprite generation, need to keep randomness but create more png with different levels of water

growing plants :
	will change that so that during the day the plan can grow but when reset the time passes even more, 
	will figure it out in the end because need to know beforehand what to do with rst
	need also to take into acount nb of time watered : once is ok, twice is best, thrice is slower than once

I changed the player hitbox but now it revealed that the tree hitboxes are not right and I can glitch through corner of the house...
need to recal all the hitboxes of the game in the end, by displaying it
ALso another bug, with that new collision if press enter while moving, continue to move...

Idée de base du jeu:
1ère partie, introduction/tutoriel. Doit durer 1h max
	map de base de clear code, on se balade on peut farm et tout et trade avec le trder pr gg de l'argent
	de temps en temps des png spawn au matin et restent toute la journée, on peut leur parler,
		ils servent à expliquer le jeu, et commencer l'histoire, il y a des interaction entre eux, mais surtout, ils
		tease un endroit plus vaste duquel ils viennent et se plaignent que c'est un peu petit ici.
		on peut leur donner des cadeau et si on trouve le cadeau qu'ils veulent (les kdo s'achètent au trader) ils deviennent nos amis.
		à force, au bout d'un certain nombre d'amis, ils viennent tous en même temps un jour pour nous aider à partir d'ici
		
		un des cadeau est un baton pour controler la pluie (qui marche) mais faut le donner à un pnj en réalité
		
2ème partie, on a le doirt de choisir entre 3 différents maisons:
	on se retrouve dans un monde plus vaste avec tout les pnj du jeux. des magasins plus de sortes de fruit, de graines etc etc

collect, destroy wildflower, need a way like for harvest crops because hitxox too little

BUGS:
- WND animation when tool continuous : WILL NOT DO
- WND lack a little bit of logic for the tiling system, WILL NOT DO
- WND night is over everything, even UI, not very good, WILL NOT DO
- HUC File "C:\work\VsCode\projects\source\Pydew_Valley\code\level.py", line 167, in run
		self.sky.display_weather(dt, self.rain.rain_level)
	 	File "C:\work\VsCode\projects\source\Pydew_Valley\code\sky.py", line 43, in display_weather
		self.full_surf_weather.fill(self.current_weather_color)
		ValueError: invalid color argument  ---BUG HIDDEN UNDER CARPET WITH TRY/EXCEPT


peut aussi utiliser l'effet des éclairs pour créer des feux d'artifices

ajouter pêche
un perso doit avoir un poisson hyper rare, mais en fonction du nombre d'essai, il peut se mettre à pêcher avec toi pour y arriver.

trouver un moyen rapide pr faire comprendre qu'il faut beacoup discuter avec les personnages mais en même temps mettre un cooldown aléatoire
pour éviter d' exploit ça

bug : rain shade can trigger durring menu not paused but rain is
should not call random rain at all during pauses (but day night ok maybe)

add inventory to open
check if correct for planting seeds

nom de la monaie est l'étincelle

next to do with merchant menu : add the item purchased from the special shop.
easiest may be add another tab when initiaize shop if player.special_item not empty with only the non empty fields

better day/ nigh : increase and then descrease

maybe longer cooldown for hoe use

add images in the shop

jump, create the feature properly


close menu with same key that open it

change color apple, mor bright in inventory (TOKEN)
(when adding multi color tomatoes)

more complex meteo, like day whith low proba of rain, and day with high proba

bug apple flying after cut tree

add mention "paused" in inventory

ANKI:
os.walk(path) returns ('path', [subfolders], [file_names])
git log --oneline    : display previous commit and state of master and origin
pour parcourir un group : for sprite in self.collision_sprites.sprites(): pas oublier .sprites() (demander à gpt pk)

important things to do :
	panel with description of object in inventory
	PNJ
	Music

quality of life :
	-buy and sell different colors
	-text decriptif de ce qui se passe en bas de l'écran : 
		inventory += pomme etc... obje obtenus
		add little dialogue box when trying to plant a seed we don't have
	-tomato and apple look too alike
	-hold arrow to navigate faster in inventory

optim:
	check if that could be a good idea to gather all the font in the same place (maybe not an issue)

too complex/ ambitious
	separate shop into multiple stands, unlockable (especially Trésor et reliques)

centering detail :
	in inventory line134:             image_rect = bigger_image_surf.get_rect(center=(126+offset,269))
		# y pos is originally 267 but some items are not well centered so I settled for a middle value

could be dangerous to not be able to purchase an item again, could lose it whatever how, need a way to avoid softlock



create a drwback to be outside with rain to renforcer le comportement de rentrer à l'abri s'occuper de trucs
(mais du coup faut tj avoir un truc à faire à l'intérieur)









IA prompt :
I'm working on a pygame project. The game is a lot inspired by Stardew Valley, it is a farming game.
All the project is following OOP concepts.
Here is are the different files I got for now : 

main.py : Game class with init and run method containing the while True loop. This file is just the entry point, I rarely touch it.

level.py : The "hub" of my code where all the necessary class are imported and declared.
it is composed of a init method, setup method that instanciate all the classes I need, reset method used to start a new day, toggle_shop method that open the shop menu, and run where everything is called.

player.py define all the player character need, it is a Sprite class that contain the following methods : use_tool, use_seed, get_target_position, import_assets, animate, inpu, get_status (direction and action the player is currently doing) update_timers, collision, move, update : the main function to update the sprites.



"""
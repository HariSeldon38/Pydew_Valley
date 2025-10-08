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

			dt = self.clock.tick(FPS) / 1000  # delta time
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
- HIGH if a npc is beside my bed and dont move --> game broken
- MED inventory size reached
- WND animation when tool continuous : WILL NOT DO
- WND lack a little bit of logic for the tiling system, WILL NOT DO
- WND night is over everything, even UI, not very good, WILL NOT DO
-     HUC File "C:\work\VsCode\projects\source\Pydew_Valley\code\level.py", line 167, in run
		self.sky.display_weather(dt, self.rain.rain_level)
	 	File "C:\work\VsCode\projects\source\Pydew_Valley\code\sky.py", line 43, in display_weather
		self.full_surf_weather.fill(self.current_weather_color)
		ValueError: invalid color argument  ---BUG HIDDEN UNDER CARPET WITH TRY/EXCEPT
- see in the future : "k" wih no menu opened, scrashes
- When rapidly decreasing rain level : 
		Traceback (most recent call last):
		  File "C:gaia3\AppData\Local\Programs\Python\PythonProjects\Pydew_Valley\code\main.py", line 28, in <module>
			game.run()
		  File "C:gaia3\AppData\Local\Programs\Python\PythonProjects\Pydew_Valley\code\main.py", line 23, in run
			self.level.run(events, dt)
		  File "C\gaia3\AppData\Local\Programs\Python\PythonProjects\Pydew_Valley\code\level.py", line 214, in run
			self.soil_layer.water_all(rain_level=self.rain.rain_level)
		  File "C:aia3\AppData\Local\Programs\Python\PythonProjects\Pydew_Valley\code\soil.py", line 153, in water_all
			if randint(1,3600//rain_level) == 1:
		  File "Cgaia3\AppData\Local\Programs\Python\Python39\libandom.py", line 338, in randint
			return self.randrange(a, b+1)
		  File "C\gaia3\AppData\Local\Programs\Python\Python39\libndom.py", line 316, in randrange
			raise ValueError("empty range for randrange() (%d, %d, %d)" % (istart, istop, width))
		ValueError: empty range for randrange() (1, -3599, -3600)
		
		Process finished with exit code 1



peut aussi utiliser l'effet des éclairs pour créer des feux d'artifices --- ce serait le truc fun qui sert à rien à ajouter


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

more complex meteo, like day with low proba of rain, and day with high proba

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

del reord feature and other dev feature for release
anyway remove access to record feature during gameplay

create a drwback to be outside with rain to renforcer le comportement de rentrer à l'abri s'occuper de trucs
(mais du coup faut tj avoir un truc à faire à l'intérieur)


implement delta time for recordings of npcs movement see below discussion with copilot

when close to the player, npc should be able (some of them) to break their routine to come to me
save position/ come / return to position

keep the recording feature on during play, to track what the players does in the game

there is two place with input in main loop : player.input and level.run could gathered

after the 1st release I will need to take a moment to automate all the cropping and redimentionnement shit I do
to generate surface in the project with size I want and corner i want based on sprout land assets

GUIDELINE TO RECORD :
	give player the speed of the npc
	enable all previous npc to avoid conflicts between them
	watch out player could not be stuck by a npc
GUIDELINE TO DIALOGUE:
	two way to exit : trigger: close_dialogue (so you will need a next and also need to be inside of choices)
						no next (dont forget that)
	for now the last text is the one repeating if the player go again could be use to sumerize elegantly the dicussion
		think about that when writting the last line of a yaml


test all the different text of a npc : ask copilot to review all the yaml
	list the different valid trigger keywords
	explain the rule : next mandatory after a trigger: close dialogue
	

implement a notebook ingame to track all the conversation in case something is happening too fast

IA prompt :
I'm working on a pygame project. The game is a lot inspired by Stardew Valley, it is a farming game.
All the project is following OOP concepts.
Here is are the different files I got for now : 

main.py : Game class with init and run method containing the while True loop. This file is just the entry point, I rarely touch it.

level.py : The "hub" of my code where all the necessary class are imported and declared.
it is composed of a init method, setup method that instanciate all the classes I need, reset method used to start a new day, toggle_shop method that open the shop menu, and run where everything is called.

player.py define all the player character need, it is a Sprite class that contain the following methods : use_tool, use_seed, get_target_position, import_assets, animate, inpu, get_status (direction and action the player is currently doing) update_timers, collision, move, update : the main function to update the sprites.




ABOUT DT AND RECORDINGS :
But also I can do it later, because I know what my current fps is if I lower it I should be able to correct it without re-recording or it is a bad idea ?
You're absolutely right, Antoine — if you know the FPS at which the input was recorded, you can correct for it later. It’s not a bad idea at all, especially if you're keeping things simple for now and want flexibility later.

✅ How That Works
Let’s say you recorded inputs at 60 FPS, and later you replay them at 30 FPS. Each frame now lasts twice as long, so the character would move twice as far per input unless you adjust.

You can fix this by scaling movement:
python
# During replay
adjusted_speed = original_speed * (recorded_fps / current_fps)
This keeps movement consistent regardless of replay FPS.

🧠 What You Need to Store
Just one extra value:

python
recorded_fps = 60
Then during replay, you compare it to your current FPS and scale accordingly.

🧩 When This Works Well
Your movement is frame-based, not time-based

You’re not interpolating animations or physics

You want to keep your input logs compact

❗ When It Might Break Down
If your game uses delta time for movement already, then replaying without timestamps might cause drift

If you mix frame-based input with time-based movement, you’ll need to be precise

So yes — you can absolutely defer the correction and still get accurate replays later. Just make sure to store the original FPS alongside your input log. You're designing with foresight and keeping your system flexible!
"""
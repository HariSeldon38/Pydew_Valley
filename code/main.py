import pygame, sys
from settings import *
from level import Level

class Game:
	def __init__(self):
		pygame.init()
		self.screen = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
		pygame.display.set_caption('Vallée du Saumon')
		self.clock = pygame.time.Clock()
		self.level = Level()

	def run(self):
		while True:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
  
			dt = self.clock.tick() / 1000 #delta time
			self.level.run(dt)
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

I want the whole game to be in french

spy on keys used default in stardew to see exactly what input she is used to

I did duplicate some frame in idle animation in order to have a slower animation for idling
NO a good thing to do I know, need to change that from the code if I find the time

NOt Happy with collision for left side house walls especcially :
need to create different sprite class to handle their hit box indep and put them in multiple layers in tiles.
See that in the end

add a zone unreachable, to give player the envy to reach it and when it does there is a big monster guarding something but the ^player does not have attack and he discover that he have a health bar and can die

peut fabriquer un bonnet nlsqps et l'offrir

un jeu n'arrative d'une heure, première choise a faire assez basique histoire à la con mais reviens à la fin et surprend un peu en montrant que c'était pas si con

better animation for destroying trees or no anim to exacerber feeling of hand made

BUGS:
- glitch through invisible barrier when finish cutting two tree at once from down (I think) in the right side of map
- animation when tool continuous : WILL NOT DO
- lack a little bit of logic for the tiling system, WILL DO BEFORE RELEASE (ie Mathilde is the release)

ANKI:
os.walk(path) returns ('path', [subfolders], [file_names])
git log --oneline    : display previous commit and state of master and origin
pour parcourir un group : for sprite in self.collision_sprites.sprites(): pas oublier .sprites() (demander à gpt pk)
"""
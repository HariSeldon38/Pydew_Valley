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

spy on Math to see exactly what input she is used to

I did duplicate some frame in idle animation in order to have a slower animation for idling
NO a good thing to do I know, need to change that from the code if I find the time

ANKI:
os.walk(path) returns ('path', [subfolders], [file_names])
git log --oneline    : display previous commit and state of master and origin
"""
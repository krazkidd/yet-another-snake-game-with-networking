#!/usr/bin/python2

import time

import pygame
from pygame.locals import *
import pygcurse

from Snake import *

# these dimension units are in text cells, not pixels
WIN_WIDTH, WIN_HEIGHT = 80, 35

# instantiate players' snakes
snake1 = Snake(15, 15, Dir.Right, 4)
#snake2 = Snake(30, 30, Dir.Right, 4)

pellet = Pellet(WIN_WIDTH - 1, WIN_HEIGHT - 1) 

# initiate pygame and pygcurse
pygame.init()
win = pygcurse.PygcurseWindow(WIN_WIDTH, WIN_HEIGHT, 'Snake')
win.autoupdate = False # turn off autoupdate so window doesn't flicker

# main game loop
while True:
	# clear the screen
	#win.erase() # this would be used instead but for a bug...
	win.fill(' ')

	# draw outside border
#TODO

	# draw game data
	win.putchars("Score: " + str(snake1.length), 0, 0)

	# draw snakes
	win.putchars('O', snake1.headX, snake1.headY, fgcolor = 'red', bgcolor = 'black')

	# draw pellet
	win.putchar('+', pellet.posx, pellet.posy, fgcolor = 'yellow', bgcolor = 'black')

	# actually paint the window
	win.update()

	# pause the screen for just a bit
	time.sleep(0.1)

	# process input queue
#TODO only allow one keypress event per game loop cycle OR fix Snake so it doesn't allow backwards movement
	for event in pygame.event.get():
		if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
			pygame.quit()
		if event.type == KEYDOWN:
			if event.key == K_UP:
				snake1.changeHeading(Dir.Up)
			elif event.key == K_DOWN:
				snake1.changeHeading(Dir.Down)
			elif event.key == K_LEFT:
				snake1.changeHeading(Dir.Left)
			elif event.key == K_RIGHT:
				snake1.changeHeading(Dir.Right)

	# move players' snakes
	snake1.move()
	#Snake.move(snake1) # an alternative way to call a particular object's method
	#snake2.move()	
	
	# check if player's head is on a pellet. If so, consume it and create a new one
	if snake1.headX == pellet.posx and snake1.headY ==  pellet.posy:
		snake1.length += 1
		pellet = Pellet(WIN_WIDTH - 1, WIN_HEIGHT - 1)

#TODO check if player has hit the edge and end the game if so
	#if ...

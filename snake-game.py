#!/usr/bin/python2

import curses
import curses.ascii
import time
from Snake import *

# instantiate players' snakes
snake1 = Snake(15, 15, Dir.Right, 4)
#snake2 = Snake(30, 30, Dir.Right, 4)


# initiate curses
stdscr = curses.initscr() # get window object for whole screen
curses.noecho() # turn off character echo
curses.cbreak() # get input after every keypress
curses.start_color() # for color support
curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK) # define a color for player1's snake
curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK) # define a color for player2's snake
stdscr.keypad(1) # return special keys as single chars
stdscr.nodelay(True)
curses.curs_set(0) # make cursor invisible

# main game loop
while True:
	# clear the screen
	stdscr.erase()

	# draw outside border
	stdscr.border()

	# draw snakes
	stdscr.addch(snake1.headY, snake1.headX, 'O', curses.color_pair(1))
	#stdscr.addch(snake2.headY, snake2.headX, 'O', curses.color_pair(2))

	# actually paint the window
	stdscr.refresh()

	# get user input, if any
	input = stdscr.getch() 

	# change the heading of the snake according to user input
	if input == curses.KEY_UP or input == ord('w'):
		snake1.heading = Dir.Up
	elif input == curses.KEY_DOWN or input == ord('s'):
		snake1.heading = Dir.Down
	elif input == curses.KEY_LEFT or input == ord('a'):
		snake1.heading = Dir.Left
	elif input == curses.KEY_RIGHT or input == ord('d'):
		snake1.heading = Dir.Right
	elif input == curses.ascii.ESC: # quit when Escape is pressed
		break

	# move players' snakes
	snake1.move()
	#Snake.move(snake1) # an alternative way to call a particular object's method
	#snake2.move()

	# pause the screen for just a bit
	time.sleep(0.2)
	
# terminate curses
curses.nocbreak(); stdscr.keypad(0); curses.echo()
curses.endwin()

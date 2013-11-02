#/usr/bin/python2

import curses
from Snake import *

# initiate curses
stdscr = curses.initscr() # get window object for whole screen
curses.noecho() # turn off character echo
curses.cbreak() # get input after every keypress
stdscr.keypad(1) # return special keys as single chars
curses.curs_set(0) # make cursor invisible

# instantiate player's snake
snake = Snake()

#stdscr.addstr("Hello, World!")

# main game loop
while True:
	# clear the screen
	stdscr.erase()

	# draw outside border
	#stdscr.addch(0, 0, curses.ACS_ULCORNER)
	stdscr.border()

	# draw snake
	#stdscr.addstr(snake.headY, snake.headX, "OOOO")
	stdscr.addch(snake.headY, snake.headX, 'O', curses.COLOR_RED)

	stdscr.refresh()

	input = stdscr.getch() # wait for user input
	if input == curses.KEY_UP or input == ord('w'):
		snake.headY -= 1
	elif input == curses.KEY_DOWN or input == ord('s'):
		snake.headY += 1
	elif input == curses.KEY_LEFT or input == ord('a'):
		snake.headX -= 1
	elif input == curses.KEY_RIGHT or input == ord('d'):
		snake.headX += 1
	

# terminate curses
curses.nocbreak(); stdscr.keypad(0); curses.echo()
curses.endwin()

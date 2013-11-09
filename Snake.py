from collections import deque
import random

class Dir:
	"""An enum of the cardinal directions."""
	Up, Down, Left, Right = range(4)

class Snake:

	"""This is the player's (or computer's) avatar in the game.

	For every tick of the game world, the Snake moves. And for every
	pellet it eats, its length grows."""

	def __init__(self, headX = 15, headY = 15, heading = Dir.Right, length = 4):
		# the (X,Y) position of the snake's head
		self.headX = headX
		self.headY = headY
		# the heading of the snake
		self.heading = heading
		# the snake's body length which grows after
		# eating a pellet
		self.length = length
#TODO make deque for body

	def move(self):

		"""Move (update) the snake's body.

		This should be called once for every unit
		of time that passes."""

		# check the heading of the snake and move the
		# head's position accordingly
		if self.heading == Dir.Right:
			self.headX += 1
		elif self.heading == Dir.Left:
			self.headX -= 1
		elif self.heading == Dir.Up:
			self.headY -= 1
		else: # self.heading == Dir.Down
			self.headY += 1

#TODO this still allows going backwards if the player quickly presses two arrow keys before move() is called.
#     this could be fixed by using a flag so that only one direction change can happen per move()
	def changeHeading(self, newHeading):

		"""Tell the Snake the direction the player wants to move in.

		The Snake cannot go backwards."""

		# don't do anything if the new heading is opposite the current heading
		if self.heading == Dir.Up and newHeading == Dir.Down:
			return
		elif self.heading == Dir.Down and newHeading == Dir.Up:
			return
		elif self.heading == Dir.Left and newHeading == Dir.Right:
			return
		elif self.heading == Dir.Right and newHeading == Dir.Left:
			return

		self.heading = newHeading

class Pellet:

	"""This is what the Snake eats.

	For now, this just holds a position. Other attributes could
	be added in the future like power-up abilities."""

	def __init__(self, stdscr_x, stdscr_y):
		
		"""On creation, randomly set a position using the
		given arguments as maximum values."""

		self.posx = random.randint(0, stdscr_x - 1) # subtract 1 because cursor position is zero-based
		self.posy = random.randint(0, stdscr_y - 1)

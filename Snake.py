from collections import deque
import random

class Dir:
	"""An enum of the cardinal directions."""
	Up, Down, Left, Right = range(4)

class Pellet:

	"""This is what the Snake eats.

	For now, this just holds a position. Other attributes could
	be added in the future like power-up abilities."""

	def __init__(self, stdscr_x, stdscr_y):
		
		"""On creation, randomly set a position using the
		given arguments as maximum values."""

		self.posx = random.randint(0, stdscr_x - 1) # subtract 1 because cursor position is zero-based
		self.posy = random.randint(0, stdscr_y - 1)

class Snake:

	"""This is the human player's avatar in the game.

	For every tick of the game world, the Snake moves. And for every
	pellet it eats, its length grows.

	"""

	def __init__(self, headX = 15, headY = 15, heading = Dir.Right, length = 4):
		# the (X,Y) position of the snake's head
		self.headX = headX
		self.headY = headY
		# the heading of the snake
		self.heading = heading
		# the snake's body length which grows after
		# eating a pellet
		self.length = length

	def move(self, p):

		"""Move (update) the snake's body.

		This should be called once for every unit
		of time that passes.

		Arguments:
		p -- a Pellet object

		"""

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

	def changeHeading(self, newHeading):

		"""Tell the Snake the new direction to move in.

		The Snake cannot go backwards, so the only real change that
		can happen is to turn left or right.

		"""

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

class SnakeAI(Snake):

	"""This is the computer's avatar in the game.

	It currently has a very rudimentary AI.

	"""

	def __init__(self, headX = 15, headY = 15, heading = Dir.Right, length = 4):
		# the (X,Y) position of the snake's head
		self.headX = headX
		self.headY = headY
		# the heading of the snake
		self.heading = heading
		# the snake's body length which grows after
		# eating a pellet
		self.length = length

	def move(self, p):

		"""Move (update) the snake's body.

		This should be called once for every unit
		of time that passes.

		"""

		# use changeHeading() instead of manipulating heading directly
		if p.posx > self.headX:
			self.changeHeading(Dir.Right)
		elif p.posx < self.headX:
			self.changeHeading(Dir.Left)
		if p.posy < self.headY:
			self.changeHeading(Dir.Up)
		elif p.posy > self.headY:
			self.changeHeading(Dir.Down)

		# Look! We call the parent class's move() method to do the actual
		# position update. We must use Snake.move(self, ...) instead of
		# self.move(...) to do this.
		Snake.move(self, p);


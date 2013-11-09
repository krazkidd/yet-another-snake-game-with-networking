from collections import deque
import random

class Dir:
	"""An enum of the cardinal directions."""
	Up, Down, Left, Right = range(4)

class Snake:

	"""TODO"""

	# the snake's body length which grows after
	# eating a pellet
	#length = 4

	# the heading of the snake
	#heading = Dir.Right

	# the (X,Y) position of the snake's head
	#headX = 15
	#headY = 15

	def __init__(self, headX = 15, headY = 15, heading = Dir.Right, length = 4):
		self.headX = headX
		self.headY = headY
		self.heading = heading
		self.length = length
#TODO make deque for body

#NOT USED
#	def turnLeft(self):
#		pass
	
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

class Pellet:
	def __init__(self, stdscr_x, stdscr_y):
		self.posx = random.randint(0, stdscr_x - 1)
		self.posy = random.randint(0, stdscr_y - 1)
		

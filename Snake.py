class Dir:
	"""An enum of the cardinal directions."""
	Up, Down, Left, Right = range(4)

class Snake:
	"""TODO"""
	# the snake's body length which grows after
	# eating pellets
	length = 4

	# the heading of the snake
	heading = Dir.Right

	# the (X,Y) position of the snake's head
	headX = 15
	headY = 15

#NOT USED
#	def turnLeft(self):
#		pass
	
	def move(self):
		"""Move the snake's body.

		This should be called once for every unit
		of time that passes."""
		# check the heading of the snake and move the
		# head accordingly
		if self.heading == Dir.Right:
			self.headX += 1
		if self.heading == Dir.Left:
			self.headX -= 1
		if self.heading == Dir.Up:
			self.headY -= 1
		if self.heading == Dir.Down:
			self.headY += 1

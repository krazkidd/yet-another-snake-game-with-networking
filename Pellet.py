class Pellet:

	"""This is what the Snake eats.

	For now, this just holds a position. Other attributes could
	be added in the future like power-up abilities."""

	def __init__(self, stdscr_x, stdscr_y):
		
		"""On creation, randomly set a position using the
		given arguments as maximum values."""

		self.posx = random.randint(0, stdscr_x - 1) # subtract 1 because cursor position is zero-based
		self.posy = random.randint(0, stdscr_y - 1)


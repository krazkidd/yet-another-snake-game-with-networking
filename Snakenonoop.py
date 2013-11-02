class Dir:
	"""An enum of the cardinal directions."""
	Up, Down, Left, Right = range(4)

class SnakeEnum:
	"""An enum of snake data we have to keep track of."""
	Length, Heading, HeadX, HeadY = range(4)

def moveSnake(snake):
	"""Move (update) the snake's body.

	This should be called once for every unit
	of time that passes."""
	# check the heading of the snake and move the
	# head's position accordingly
	if snake[SnakeEnum.Heading] == Dir.Right:
		snake[SnakeEnum.HeadX] += 1
	elif snake[SnakeEnum.Heading] == Dir.Left:
		snake[SnakeEnum.HeadX] -= 1
	elif snake[SnakeEnum.Heading] == Dir.Up:
		snake[SnakeEnum.HeadY] -= 1
	else: # snake[SnakeEnum.Heading] == Dir.Down
		snake[SnakeEnum.HeadY] += 1

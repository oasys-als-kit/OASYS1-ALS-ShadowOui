## @package fast_grid
## @brief Contains 2D Grid containers that supports useful iterators.
## 
# These classes are faster than those provided in fast_grid. They do not support
# slicing, though.
#
# @code
# grid1 = Grid3D(10, 10, 10, 0)
# grid2 = Grid3D(10, 10, 10, 1)
# grid1[0, 0, 0] = grid2[0, 0, 0]
# grid1[0, 0, 2:6:2] = grid2[0, 0, 4:5]
# grid1[0, 0, ...] = grid2[0, 0, ...]
# grid1[0, ..., 0] = grid2[..., 0, 0]
# grid1[..., ..., ...] = grid2[..., ...., ....]
# @endcode
#
# Slicing does not copy elements - an auxiliary window container is created that delegates 
# further operations to the underlying container.
# Note that assignments to slices from the same object might not behave as espected. 
# Parallel assignment also does not always work as expected.
# For example:
#@code
# grid[..., 0], grid[..., 1] = grid[..., 1], grid[..., 0]
#@endcode
# does not correctly swop two rows, but the following does:
#@code
# grid[..., 0], grid[..., 1] = grid[..., 1].clone(), grid[..., 0].clone()
#@endcode
#Strictly speaking, it is necessary only to clone the one object,
#but it is hard to remember which, so it is better to clone both (?).
# 
#@todo Implement a way to use copy containers instead of window containers'

from enhanced_grid import GridWindow2D
from enhanced_grid import GridCol2D
from enhanced_grid import GridRow2D
from enhanced_grid import is_slice

## @brief Makes 2 list of lists.
def make_grid_2d(width, height, initial_item=None):
	grid = [None] * (width * height)

	for i in xrange(width):
		for j in xrange(height):
			grid[i + j * width] = initial_item

	return grid

## @brief Makes 2 list of lists.
def make_grid_2d2(width, height, initial_item=None):
	grid = [None] * width

	for i in xrange(width):
		grid[i] = [None] * height

		for j in xrange(height):
			grid[i][j] = initial_item

	return grid

## @brief Sub-classes of this container can be used directly.
##
## A principle container will do assignment on a 1D point.
## Assignment of larger chunks is delegated to the AuxilaryContainer
## with the right dimensions.
##
## The enherritance is merely for documentation purposes.
class PrincipleContainer:
	pass

##Abstract super class of all grid-like containers.
##These containers are static, that is, once they are created, 
##their dimensions cannot change.
#
# Children of this class must implement
# the attribute __clonetype__, which must 
# hold a callable type that can be constructed
# for clones.
# 
# Children must also implement the iterators
# cell_iter() and index_iter().
class Container:
	##
	##
	# @param dim
	#		The dimensions of this grid
	def __init__(self, dims):
		self.dims = dims

		count = 1

		for dim in dims:
			count *= dim

		self.count = count

	##Test whether two containers have the same dimensions
	##and the same items at equal indices.
	def __eq__(self, other):
		if other == None:
			return False
		if self.dims != other.dims:
			return False

		for cell1, cell2 in zip(self.cell_iter(), other.cell_iter()):
			if cell1 != cell2:
				return False
		return True

	##Equivalent to @code not (self == other) @endcode .
	def __ne__(self, other):
		return not (self == other)

	## Returns the length (1D) or width (nD) of this container.
	#
	# The length of a container is defined such that the length behaves as it would
	# for a list of lists.
	def __len__(self):
		return self.dims[0]

	## @brief Returns the minimum and maximum elements
	## of this grid as a tuple. 
	##
	#This method assumes the grid is filled.
	def min_max(self):		
		cell_iter = self.cell_iter()		
		min = max = cell_iter.next()

		for cell in cell_iter:
			if cell > max:
				max = cell
			elif cell < min:
				min = cell
		return min, max

	def copy_from(self, other):
		for index in self.index_iter():
			self[index] = other[index]

	##Makes a shallow copy of this container.
	#
	#This method constructs an instance of
	#this instance's __clonetype__. In general,
	#if this class is an AuxiliaryContainer,
	#the clone will be a PrincipleContainer
	#of the same dimension.
	def clone(self):
		new_grid = self.__clonetype__(self.dims)		
		new_grid.copy_from(self)

		return new_grid

## Class that implements __str__ and __iter__.
class Container2D (Container):
	def __init__(self, width, height):
		Container.__init__(self, (width, height))
		self.width = width
		self.height = height
		self.__clonetype__ = Grid2D

	def __str__(self):    
		#slow...
		glst = []

		for i in xrange(self.width):
			gcol = []

			for j in xrange(self.height):
				gcol.append(self[i, j])

			glst.append(gcol)

		return glst.__repr__()	

	## @brief Returns an iterator that iterates over columns.
	##
	# This iterator is provided so that a Grid2D better emulates a list of 
	# lists, as in the following example:
	#@code
	# 	for col in grid:
	#		for item in col:
	#			process(item)
	#@endcode
	# Use of this iterator is discouraged - it is slow
	def __iter__(self):
		for i in xrange(self.width):
			yield self[i, ...]
		raise StopIteration

	## @brief Returns an iterator that iterates over all cells in the grid.
	##
	# This allows you to write:
	#@code
	# for cell in cell_iter(grid):
	#   process(cell)
	#@endcode
	def cell_iter(self):
		for i in xrange(self.width):
			for j in xrange(self.height):
				yield self.get_item_i(i, j)
		raise StopIteration

	## @brief Returns an iterator that iterates over a subgrid of this grid.
	##
	# The iterator will iterate over all cells x, y in the grid	
	# such that 
	#@code
	# x0 <= x < x1
	# y0 <= y < y1
	#@endcode
	#	
	def window_index_iter(self, p0, p1):
		x0, y0 = p0
		x1, y1 = p1    
		for i in xrange(max(0, x0), min(x1, self.width)):
			for j in xrange(max(0, y0), min(y1, self.height)):
				yield (i, j)
		raise StopIteration
	## @brief Returns an iterator that iterates over a subgrid of this grid.
	##
	# The iterator will iterate over all cells x, y in the grid	
	# such that 
	#@code
	# x0 <= x < x1
	# y0 <= y < y1
	#@endcode
	#	
	# The iterator wraps over the grid. For example, if x is one unit too high 
	# (it is outside the grid to the right), the iterator will return the index of the 
	# first cell in that row.
	def wrapped_window_index_iter(self, p0, p1):
		x0, y0 = p0
		x1, y1 = p1    
		for i in xrange(x0, x1):
			for j in xrange(y0, y1):
				yield (i % self.width, j % self.height)
		raise StopIteration

	## @brief Returns an iterator that iterates over a subgrid of this grid.
	##
	# The iterator will iterate over all cells x, y in the grid	
	# such that 
	#@code
	# x0 <= x < x1
	# y0 <= y < y1
	#@endcode	
	def window_iter(self, p0, p1):
		x0, y0 = p0
		x1, y1 = p1
		for i in xrange(max(0, x0), min(x1, self.width)):
			for j in xrange(max(0, y0), min(y1, self.height)):
				yield self.get_item_i(i, j)
		raise StopIteration	

	## @brief Returns an iterator that iterates over a subgrid of this grid.
	##
	# The iterator will iterate over all cells x, y in the grid	
	# such that 
	#@code
	# x0 <= x < x1
	# y0 <= y < y1
	#@endcode
	#	
	# The iterator wraps over the grid. For example, if x is one unit too high 
	# (it is outside the grid to the right), the iterator will return first 
	# cell in that row.
	def wrapped_window_iter(self, p0, p1):
		x0, y0 = p0
		x1, y1 = p1
		for i in xrange(x0, x1):
			for j in xrange(y0, y1):
				yield self.get_item_i(i % self.width, j % self.height)
		raise StopIteration	

	## @brief Returns an iterator that iterates over all cells in the square
	## surrounding the given point. 
	##
	#The square is 2*n + 1 units.
	def square_index_iter(self, p, n):
		x, y = p
		return self.window_index_iter((x - n, y - n), (x + n + 1, y + n +1))
	
	## @brief Returns an iterator that iterates over all cells in the square
	## surrounding the given point. 
	##
	#The square is 2*n + 1 units.
	# The iterator wraps over the grid. For example, if x is one unit too high 
	# (it is outside the grid to the right), the iterator will return first 
	# cell in that row.
	def wrapped_square_index_iter(self, p, n):
		x, y = p
		return self.wrapped_window_index_iter((x - n, y - n), (x + n + 1, y + n +1))


	## @brief Returns an iterator that iterates over all cells in the square
	## surrounding the given point. 
	##
	#The square is 2*n + 1 units.
	def square_iter(self, p, n):
		x, y = p
		return self.window_iter((x - n, y - n), (x + n + 1, y + n +1))

	## @brief Returns an iterator that iterates over all cells in the square
	## surrounding the given point. 
	##
	#The square is 2*n + 1 units.
	# The iterator wraps over the grid. For example, if x is one unit too high 
	# (it is outside the grid to the right), the iterator will return first 
	# cell in that row.
	def wrapped_square_iter(self, p, n):
		x, y = p
		return self.wrapped_window_iter((x - n, y - n), (x + n + 1, y + n +1))

	## @brief Returns an iterator that iterates over the indeces of this 
	## grid as tuples.
	##
	# If grid is a 2 by 2 grid, then:
	# @code
	# for p in index_iter(grid):
	# 	print p
	# @endcode
	# will produce 
	# @code
	# 0, 0
	# 0, 1
	# 1, 0
	# 1, 1
	# @endcode
	# This iterator is useful for assigning elements of grids:
	# @code
	# for p in index_iter(grid):
	# 	grid[p] = random()
	# @endcode
	def index_iter(self):
		for i in xrange(self.width):
			for j in xrange(self.height):
				yield i, j
		raise StopIteration	

## Class that represent a 2D grid, with enhanced slicing notation.
class Grid2D (Container2D, PrincipleContainer):
	def __init__(self, dims, initial_item = None):
		(width, height) = dims
		Container2D.__init__(self, width, height)
		self.grid = make_grid_2d(width, height, initial_item)
	## @brief Returns an iterator that iterates over all cells in the grid.
	##
	# This allows you to write:
	#@code
	# for cell in cell_iter(grid):
	#   process(cell)
	#@endcode
	def cell_iter(self):
		for i in xrange(self.width):
			for j in xrange(self.height):
				yield self.get_item_i(i, j)
		raise StopIteration
	
	def get_item_i(self, x, y):
		return self.grid[x + y * self.width]
		#return self.grid[x][y]
	
	def set_item_i(self, x, y, item):
		self.grid[x + y * self.width] = item	
		#self.grid[x][y] = item

	def __getitem__(self, p):
		x, y = p
		return self.grid[x + y * self.width]
		#return self.grid[x][y]
	
	def __setitem__(self, p, item):		
		x, y = p
		self.grid[x + y * self.width] = item	
		#self.grid[x][y] = item

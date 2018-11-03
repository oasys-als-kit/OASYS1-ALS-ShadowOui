## @package random_image 
## This module contains functions that can be used to generate textures.
##
## See:
##   - http://code-spot.co.za/2008/11/07/a-simple-procedural-texture-algorithm/
##   - http://code-spot.co.za/2008/12/15/a-simple-texture-algorithm-faster-code-and-more-results/
##

from __future__ import division 

from random import random
from random import seed

from math import sqrt
from math import sqrt
from math import ceil

from random_distributions import make_distribution_curve
from fast_grid import Grid2D
from gradient import mix_color

from image import greyscale_grid_to_rgb_grid
from image import rgb_image_to_image_grid_channels
from image import channels_to_rgb_grid
from image import grid_to_rgb_image
from image import normalize_grey
from image import mix_grey
from image import tile

# This function generates a grid with random values.
# @param distribution
#        the distribution the values should follow. It should be a response curve generated
#        from the make_distribution_curve function - see the explanation there for details.
# @param dims
#        The dimensions of the grid to return.
# @param period 
#        an integer denoting the size of squares in the grid with the same value. 
#        For instance, if period is set to 2, then the pixels at (0, 0), (0, 1), 
#        (1, 0) and (1, 1) will all have the same value.
def random_grid(distribution, dims, period=1):
	grid = Grid2D(dims)

	width, height = dims

	for i in range(0, width, period):
		for j in range(0, height, period):
			r = random()
			value = distribution(r)

			for index in grid.window_index_iter((i, j), (i + period, j+period)):
				grid[index] = value	

	return grid

## Takes a grid, and returned a slighlty altered version of that grid.
# Each pixel in the new grid is a blend between the corresponding pixel in the old grid
# and another pixel close by. The second pixel is chosen from a square window around the 
# first pixel, with a probability determined by the accumulative probabilities poassed to 
# the function. 
#
# @param grid The grid to process.
#
# @param acc_probs A list of accumulative probabilities. These probabilities are associated 
# with a square. For instance, if list is [0.1, 0.2, 0.3, 0.3, 0.3, 0.4, 0.6, 0.7, 1.0] then 
# the probabilities are:
#
# @code
# 0.1 0.1 0.1
# 0.0 0.0 0.1
# 0.2 0.1 0.3
# @endcode
#
# @param t Is the blend factor.
def corr(grid, acc_probs, t=.9):
	width, height = grid.dims
	n = int(sqrt(len(acc_probs)))
	m = (n - 1) // 2
	new_grid = Grid2D(grid.dims, (0, 0, 0, 1))

	for index in grid.index_iter():	
		r = random()
		k = 0

		while r > acc_probs[k]:
			k += 1
		
		i, j = index
		x = i + k % n - m
		y = j + k // n - m

		if x < 0:
			x += width
		elif x >= width:
			x -= width

		if y < 0:
			y += height
		elif y >= height:
			y -= height

		new_grid[index] = mix_grey(grid[index], grid[int(x), int(y)], t)

	return new_grid

## Returns an altered copy of the given grid.
# This is essentially a blur function, with the proportions of blur
# described by a grid. For example, if the grid is 3 by 3, then 9
# pixels are used in to calculate each new pixel. They are blended
# together in the propertions described in the props grid.
# This value is then blended with the center pixel in the ratio described
# by the parameter t. (This is not necessary - it is to make easier comparissons 
# between this function and the corr function).
# @param grid The grid to process
#
# @param props The proportions to blend pixels.
#
# @param t The blend factor to use with the main pixel.
def corr2(grid, props, t = .9):
	width, height = grid.dims
	n = props.dims[0]
	m = (n - 1) // 2
	new_grid = Grid2D(grid.dims, (0, 0, 0, 1))

	for index in grid.index_iter():
		new_grey = 0
		for window_index, props_index_iter in zip(grid.wrapped_square_index_iter(index, m), props.index_iter()):
			new_grey += grid[window_index] * props[props_index_iter]
		new_grid[index] = mix_grey(grid[index], new_grey, t)

	return new_grid

## This function calculates the average energey in a moving (wrapped) window. 
# This is use to determine some of the statistical properties of the results
# of corr and corr2.
def corr_window(grid, n):
	m = 2*n + 1
	energy_grid = Grid2D((m, m), 0)
	average_coef = 1 / (grid.width * grid.height)

	for index in grid.index_iter():
		for window_cell, energy_index in zip(grid.wrapped_square_iter(index, n), energy_grid.index_iter()):
			energy_grid[energy_index] += abs(window_cell - grid[index]) * average_coef                       

	return energy_grid

## Function that draws a circle at a given point in a grid (no-antialiasing).
#  This function is mainly used as an argument for samples_to_estimation_grid or 
#  samples_to_image.
def add_circle(grid, center, radius, amplitude):
	x, y = center
	width, height = grid.dims
	radius_sqr = radius * radius 
	for yi in xrange(2 * radius + 1):
		yc = radius - yi
		
		yy = int(y + yc)

		if yy < 0 or yy >= height:
			continue
		
		xc = int(ceil(sqrt(radius_sqr - yc*yc)))
		
		for xx in xrange(max(0, x - xc), min(x + xc + 1, width - 1)):
			grid[xx, yy] += amplitude

## Function that draws a "cone" at a given point in a grid (no-antialiasing).
#  The same as add_circle, except that the amplitude falls linearly towards the edges.
#  This function is mainly used as an argument for samples_to_estimation_grid or 
#  samples_to_image.
def add_cone(grid, center, radius, amplitude):
	x, y = center
	radius_sqr = radius * radius 
	for yi in xrange(2 * radius + 1):
		yc = radius - yi
		xc = int(ceil(sqrt(radius_sqr - yc*yc)))
		yy = int(y + yc)
		for xx in xrange(x - xc, x + xc + 1):
			grid[xx, yy] += amplitude * (1 + radius - sqrt(yc*yc + (xx-x)*(xx-x)))/(1 + radius)

## Function that draws a square at a given point in a grid (no-antialiasing).
#  This function is mainly used as an argument for samples_to_estimation_grid or 
#  samples_to_image.
def add_square(grid, center, radius, amplitude):
	x, y = center	
	for yy in xrange(y - radius, y + radius + 1):
		for xx in xrange(x - radius, x + radius + 1):
			grid[xx, yy] += amplitude

## Scales a set of data points (in the range 0..1) to integer values in the range
## 0..scale.
# @param samples A list of tuples, each representing a 2D point.
def scale_lists_to_int(samples, scale):
	new_samples = []
	x_scale, y_scale = scale
	
	for sample in samples:
		x, y = sample
		new_samples.append((int(x * x_scale), int(y * y_scale)))
	
	return new_samples		

## Tries to estimate a distribution from a list of sample points of that distribution.
def samples_to_estimation_grid(samples, image_dims, shape_function=add_circle):
	grid = Grid2D(image_dims, 0)
	samples = scale_lists_to_int(samples, image_dims)
	k = 0
	maxp = -1
	
	for point in samples:
		k += 1
		add_circle(grid, point, 5, 0.5)

	grid = normalize_grey(grid)	

	return grid


## Tries to estimate a distribution from a list of sample points of that distribution, and generates an
# image of that estimation.
def samples_to_image(samples, image_dims, fname, shape_function=add_circle):
	grid = samples_to_estimation_grid(samples, image_dims, shape_function)
	grid = greyscale_grid_to_rgb_grid(grid, (1, 1, 1, 1))	
	grid_to_rgb_image(grid, fname)
## @package random_distributions
## This module provides functionality to generate random numbers with arbitrary 
## distributions. 
##
## See:
##   - http://code-spot.co.za/2008/09/21/generating-random-numbers-with-arbitrary-distributions/ 
##   - http://code-spot.co.za/2009/04/15/generating-random-points-from-arbitrary-distributions-for-2d-and-up/
##   - http://code-spot.co.za/2009/04/15/estimating-a-continuous-distribution-from-a-sample-set/
##
## @author Herman Tulleken (herman.tulleken@gmail.com)
##


from __future__ import division

from math import exp

from random import seed
from random import random

from orangecontrib.shadow.als.util.enhanced_grid import Grid2D

newSampleCount = 1000
THRESHOLD = 0.001

## Linear interpolation, with clamping for inputs outside the range.
# This function can also be used for linear extrapolation.
# Compare with ramp and 
def lerp(value, inputMin, inputMax, outputMin, outputMax):
	if value >= inputMax:
		return outputMax

	return ramp(value, inputMin, inputMax, outputMin, outputMax)

## This function is a "soft" version of lerp.
def sigmoid(value, inputMin, inputMax, outputMin, outputMax):
	w = exp((-2 * value + (inputMax + inputMin))/ (inputMax - inputMin))

	return (outputMax - outputMin) / (1 + w) + outputMin

## The same as lerp, except that the output is extrapolated, not clamped
## when the input is higher than the maximum. 
#  The output is still clamped when the input fals below the inputMin.
def ramp(value, inputMin, inputMax, outputMin, outputMax):
	if value <= inputMin:
		return outputMin

	return line(value, inputMin, inputMax, outputMin, outputMax)

## The same as lerp, except that output is linearly extrapolated when the input 
## falls outside the range on both ends.
def line(value, inputMin, inputMax, outputMin, outputMax):
	return outputMin + ((value - inputMin) * (outputMax - outputMin) / (inputMax - inputMin))


##	Similar to ResponseCurve, but allows sample points to be unevenly spaced.
#
#	This curve is slower than the ordinary ResponseCurve. However, it is useful 
#	for generating the inverse of a monotonic function. For rapid access, this 
#	curve should be sampled into a ordinary ResponseCurve.
class XYResponseCurve:
	##
	#	Construct a new XYResponse curve from input and output samples
	#
	#	@param inputSamples
	#		The input values for this response curve. Must be strictly increasing.
	#	@param outputSamples
	#		The output vlaues for this curve.
	def __init__(self, inputSamples, outputSamples):
		self.count = len(inputSamples)

		if self.count != len(outputSamples):
			raise Exception('Number of input samples does not match number of output samples')

		self.inputSamples = [0] * self.count
		self.outputSamples = [0] * self.count

		for i in range(self.count):
			self.inputSamples[i] = inputSamples[i];
			self.outputSamples[i] = outputSamples[i];


	##	If the input is below the inputMin given in the constructor, 
	#	the output is clamped to the first output sample.

	#	If the input is above the inputMax given in the constructor,
	#	the output is clamped to the last output sample.

	#	Otherwise an index is calculated, and the output is interpolated
	#	between outputSample[index] and outputSample[index + 1].

	#	@param input
	#		The input for which output is sought.	
	def __call__(self, input):
		if input <= self.inputSamples[0]:
			return self.outputSamples[0];


		if input >= self.inputSamples[-1]:
			return self.outputSamples[- 1]

		index = self.findInputIndex(input)


		x1 = self.inputSamples[index + 1]
		x0 = self.inputSamples[index]

		tau = (input - x0) / (x1 - x0)
		y1 = self.outputSamples[index + 1]
		y0 = self.outputSamples[index]

		return (y1 - y0) * tau + y0	

	# @private
	def makeInverse(self):
		tmp = self.inputSamples
		self.inputSamples = self.outputSamples
		self.outputSamples = tmp


	##	@private: only made public for testing! Test which input sample lies to the left of the given input.
	def findInputIndex(self, input):
		min = 0
		max = self.count

		while max > min + 1:		
			mid = (max + min) // 2			

			if input < self.inputSamples[mid]:
				max = mid
			else:
				min = mid

		return min

##This class is described in AI Programming Wisdom 1, 
#"The Beauty of Response Curves", by Bob Alexander.
#Essentailly, this class provides a look-up table with 
#linear interpolation for arbitrary functions.
#@param n 
#	Number of output samples.
#@param T
#	The number type of the input and output, usually float or double.

class ResponseCurve: 

	##	Constructs a new TransferFunction.
	#	
	#	@param inputMin
	#		The minimum value an input can be. 
	#	@param inputMax
	#		The maximum value an input can be.
	#	@param outputSamples
	#		Samples of outputs.

	def __init__(self, inputMin, inputMax, outputSamples):
		self.inputMin = inputMin
		self.inputMax = inputMax
		self.count = len(outputSamples)
		self.period = (inputMax - inputMin) / (self.count - 1)

		self.outputSamples = [0] * self.count

		for i in range(self.count):
			self.outputSamples[i] = outputSamples[i]


	#	If the input is below the inputMin given in the constructor, 
	#	the output is clamped to the first output sample.
	#
	#	If the input is above the inputMax given in the constructor,
	#	the output is clamped to the last output sample.
	#
	#	Otherwise an index is calculated, and the output is interpolated
	#	between outputSample[index] and outputSample[index + 1].
	#
	#	@param input
	#		The input for which output is sought.	
	def __call__ (self, input):
		if input <= self.inputMin:
			return self.outputSamples[0]

		if input >= self.inputMax:
			return self.outputSamples[-1]


		index = int((input - self.inputMin)/(self.period))
		inputSampleMin = self.inputMin + self.period * index

		return lerp(input, inputSampleMin, inputSampleMin + self.period, self.outputSamples[index], self.outputSamples[index + 1])

	def getInputMin(self):
		return self.inputMin

	def getInputMax(self):
		return self.inputMax

class NormalisedInputCurve:
	def __init__ (self, curve):
		self.curve = curve

	## @param input 
	#    is a value between 0 and 1.
	def __call__(self, input): 
		#Step 4. Map random value to the appropriate input value for the response curve
		return self.curve(input*(self.curve.inputMax - self.curve.inputMin) + self.curve.inputMin)

## Makes a distribution curve from input and output samples.
#  The inputSamples denote boundaries, and the outputSamples
#  denote the relative probabilities that a point is between 
#  those boundaries. Let x_0..x_{n-1} denote the inputs, and 
#  y_0..y_{n-1} be the outputs. Then y_i gives the relative 
#  probability that a point will be selected from the range
#  [x_{i-1}, x_i). y_0 should be 0.

def make_distribution_curve(inputSamples, outputSamples):
	newInputMin = outputSamples[0]
	newInputMax = sum(outputSamples)
	newOutputMax = inputSamples[-1]
	newOutputMin = inputSamples[0]	

	oldSampleCount = len(inputSamples)	
	accumulativeOutputSamples = [0] * oldSampleCount

	# Step 1. Calculate accumulative output

	accumulativeOutputSamples[0] = outputSamples[0]

	for i in range(oldSampleCount):
		accumulativeOutputSamples[i] = accumulativeOutputSamples[i - 1] + outputSamples[i]	

	# Step2. Load inverse into XY response curve
	xyCurve = XYResponseCurve(accumulativeOutputSamples, inputSamples)
	#print accumulativeOutputSamples, inputSamples

	newOutputSamples = [0] * newSampleCount

	# Step 3. Gather samples for ordinary reponse curve
	for i in range(newSampleCount):
		input = (i / (newSampleCount - 1)) * (newInputMax - newInputMin) + newInputMin
		newOutputSamples[i] = xyCurve(input)

		#Used for debugging.
		#printf("%f %f\n", input, newOutputSamples[i]);


	# Construct ordinary response curve from samples.
	curve = ResponseCurve(newInputMin, newInputMax, newOutputSamples)

	#Construct a curve that accepts normalised input
	curve = NormalisedInputCurve(curve)

	return curve


## This is a callable class that generates random numbers with an arbitrary distribution.
# The distribution is specified
# with a matrix that denotes relative probabilities of a point 
# being chosen from the cell. For example, the matrix [[1 2][1 1]]
# indicates that twice as many points will be chosen from the one 
# corner cell than any other. 
class Distribution2D():
	
	# The corners specify the actual rectangular range of the distribution.
	# The first row and first column of the matrix must be 0
	# This is to be consistent with the 1D case.
	def __init__(self, prob_matrix, min_corner, max_corner):
		self.min_x, self.min_y = min_corner
		self.max_x, self.max_y = max_corner
		self.width, self.height = prob_matrix.dims

		self.x_curve, self.y_curves = self.make_distribution(prob_matrix)

	def __call__(self, rx, ry):
		x = self.x_curve(rx)		
		xi = int(x * (self.width - 1))
		y = self.y_curves[xi + 1](ry)

		return x, y

	# @private
	def make_distribution(self, matrix):
		x_samples = [0] * self.width
		x_input_samples = [0] * self.width
		delta_x = 1 / (self.width - 1)
		delta_y = 1 / (self.height - 1)
		y_curves = [0] * self.width

		for i in range(self.width):
			x_input_samples[i] = (i) * delta_x
			y_samples = [0] * self.height
			y_input_samples  = [0] * self.height

			for j in range(self.height):
				x_samples[i] += matrix[i,j]
				y_samples[j] = matrix[i,j]

				y_input_samples[j] = (j) * delta_y
				
			y_curves[i] = make_distribution_curve(y_input_samples, y_samples)
		x_curve = make_distribution_curve(x_input_samples, x_samples)
		
		return x_curve, y_curves

# This function computes a distribution matrix from a grid. This is useful for when the distribution
# is specified in a grid, but we want to simplify it. It is, for example, suitable to generate 
# a distribution matrix from an image, or a function.
def distribution_from_grid(grid, x_cells, y_cells):		
	distribution = Grid2D((x_cells, y_cells), 0)
	grid_w, grid_h = grid.dims
	w = grid_w // x_cells
	h = grid_h // y_cells
	
	for index in grid.index_iter():
		i, j = index
		distribution[i // w, j // h] += grid[index]
	
	distribution2 = Grid2D((x_cells + 1, y_cells + 1), 0)
	distribution2[1:, 1:] = distribution	

	return distribution2
		


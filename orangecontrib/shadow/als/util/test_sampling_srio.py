

#
#  srio@esrf.eu: code hacked from http://code-spot.co.za/2009/04/15/generating-random-points-from-arbitrary-distributions-for-2d-and-up/
#


## @package random_distributions_demo
## Demonstrates to generation of numbers from an arbitrary distribution.
##

from __future__ import division
import numpy

from orangecontrib.shadow.als.util.random_distributions import distribution_from_grid, Distribution2D
from orangecontrib.shadow.als.util.enhanced_grid import Grid2D
from random import random
import h5py
from srxraylib.plot.gol import plot_scatter, plot_image
#from random_image import samples_to_image
## Demonstrates to generation of points from a 2D distribution.
# An image is produced that shows an estimate of the distribution
# for a samnple of points generate from the specified distribution.


def loadHDF5Files(filename,do_plot=True):

    # filename="/users/srio/OASYS1.1/OASYS1-ALS-ShadowOui/orangecontrib/shadow/als/widgets/sources/intensity_angular_distribution.h5"
    # filename="/users/srio/Oasys/intensity_angular_distribution.h5"
    f = h5py.File(filename, 'r')
    x_first = f["intensity/axis_x"].value
    z_first = f["intensity/axis_y"].value
    intensity_angular_distribution = f["intensity/image_data"].value.T
    f.close()

    if do_plot:
        plot_image(intensity_angular_distribution,x_first, z_first)

    return intensity_angular_distribution, x_first, z_first


def sample_2d_scattered_points_from_image(image_data,x,y,npoints=10000):


    # grid = Grid2D((4, 4))
    # grid[..., ...] = [[1, 2, 4, 8],
    #         [2, 3, 5, 11],
    #         [4, 5, 7, 11],
    #         [8, 11, 11, 11]]
    #
    # print (type(grid))
    #
    # probs = distribution_from_grid(grid, 4, 4)
    #
    # print (probs)


    # image_data,x,y = loadHDF5Files(filename)

    grid = Grid2D(image_data.shape)

    grid[..., ...] = image_data.tolist()



    # print (grid)

    probs = distribution_from_grid(grid, image_data.shape[0], image_data.shape[1])

    # print (probs)


    d = Distribution2D(probs, (0, 0), (500, 500))

    # samples = []
    #
    # for k in range(npoints):
    #     samples.append(d(random(), random()))
    #
    #
    # samples_x = numpy.zeros( npoints )
    # samples_y = numpy.zeros( npoints )
    # for i,iel in enumerate(samples):
    #     samples_x[i] = ( x[0] + (x[-1]-x[0])*iel[0])
    #     samples_y[i] = ( y[0] + (y[-1]-y[0])*iel[1])

    samples_x = numpy.zeros( npoints )
    samples_y = numpy.zeros( npoints )


    for k in range(npoints):
        samples_x[k],samples_y[k] = (d(random(), random()))

    samples_x = ( x[0] + (x[-1]-x[0])*samples_x)
    samples_y = ( y[0] + (y[-1]-y[0])*samples_y)

    return samples_x,samples_y

#Run any of these to see how they work.
#demo_distribution_1d()
if __name__ == "__main__":
    # filename="/users/srio/Oasys/intensity_angular_distribution.h5"
    # image_data,x,y = loadHDF5Files(filename)
    #
    # samples_x,samples_y = sample_2d_scattered_points_from_image(image_data,x,y,npoints=10000)
    # print(">>>",samples_x.shape,samples_y.shape)
    #
    # plot_scatter(samples_x,samples_y)



    from scipy.ndimage import imread
    image_data = imread("/users/srio/OASYS1.1/OASYS1-ALS-ShadowOui/orangecontrib/shadow/als/util/test1.jpg",flatten=True)
    image_data = numpy.flip(image_data.T,1)
    print(image_data.min(),image_data.max())
    image_data = image_data.max() - image_data
    plot_image(image_data,cmap='binary')

    x = numpy.arange(image_data.shape[0])
    y = numpy.arange(image_data.shape[1])
    print(image_data.shape)

    samples_x,samples_y = sample_2d_scattered_points_from_image(image_data,x,y,npoints=1000000)
    print(">>>",samples_x.shape,samples_y.shape)

    plot_scatter(samples_x,samples_y)
    # import matplotlib.pylab as plt
    # # plt.scatter(samples_y,-samples_x,marker='.',s=0.01)
    # plt.plot(samples_x,samples_y,marker='.',linestyle='',markersize=1)
    # plt.show()


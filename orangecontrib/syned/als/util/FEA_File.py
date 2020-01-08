import numpy

from scipy import interpolate
from scipy import spatial

import matplotlib.pylab as plt
import matplotlib as mpl

from srxraylib.plot.gol import plot_image, set_qt, plot

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

from oasys.util.oasys_util import write_surface_file

def write_generic_h5_surface(s, xx, yy, filename='presurface.hdf5',subgroup_name="surface_file"):
    # import h5py
    # file = h5py.File(filename, 'w')
    # file[subgroup_name + "/X"] = xx
    # file[subgroup_name + "/Y"] = yy
    # file[subgroup_name + "/Z"] = s.T
    # file.close()
    # print("write_h5_surface: File for OASYS " + filename + " written to disk.")
    write_surface_file(s.T, xx, yy, filename, overwrite=True)
    print("write_h5_surface: File for OASYS " + filename + " written to disk.")


class FEA_File():
    def __init__(self,filename=""):
        self.filename = filename
        self.reset()

    def reset(self):
        self.Xundeformed = None  # 1D array
        self.Yundeformed = None  # 1D array
        self.Zundeformed = None  # 1D array

        self.Xdeformation = None  # 1D array
        self.Ydeformation = None  # 1D array
        self.Zdeformation = None  # 1D array

        self.triPi = None
        self.tri = None

        self.x_interpolated = None  # 1D array
        self.y_interpolated = None  # 1D array
        self.Z_INTERPOLATED = None  # 2D array

    @classmethod
    def process_file(cls, filename_in, n_axis_0=301, n_axis_1=51,
                     filename_out="", invert_axes_names=False,
                     detrend=True, reset_height_method=0,
                     replicate_raw_data_flag=0, # 0=None, 1=axis0, 2=axis1, 3=both axis
                     do_plot=False):

        o1 = FEA_File(filename=filename_in)
        o1.load_multicolumn_file()


        o1.replicate_raw_data(replicate_raw_data_flag)



        o1.triangulate()

        if do_plot:
            o1.plot_triangulation()

        o1.interpolate(n_axis_0, n_axis_1)
        if do_plot:
            o1.plot_interpolated()

        if o1.does_interpolated_have_nan():
            o1.remove_borders_in_interpolated_data()

        if do_plot:
            o1.plot_surface_image()

        if detrend:
            o1.detrend()

        # o1.reset_height_to_minimum()

        if reset_height_method == 0:
            pass
        elif reset_height_method == 1:
            o1.reset_height_to_minimum()
        elif reset_height_method == 2:
            o1.reset_height_to_central_value()

        if do_plot:
            o1.plot_surface_image()

        if filename_out != "":
            o1.write_h5_surface(filename=filename_out, invert_axes_names=invert_axes_names)

        return o1

    def set_filename(self,filename):
        self.filename = filename

    def load_multicolumn_file(self,skiprows=0):
        a = numpy.loadtxt(self.filename,skiprows=skiprows )

        node = numpy.round(a, 10)

        # Coordinates

        self.Xundeformed = node[:, 1]  # X=x in m
        self.Yundeformed = node[:, 2]  # Y=z in m
        self.Zundeformed = node[:, 3]  # Z=uy vertical displacement in m

        self.Xdeformation = node[:, 4]  # X=x in m
        self.Ydeformation = node[:, 5]  # Y=z in m
        self.Zdeformation = node[:, 6]  # Z=uy vertical displacement in m

    def Xdeformed(self):
        return self.Xundeformed + self.Xdeformation

    def Ydeformed(self):
        return self.Yundeformed + self.Ydeformation

    def Zdeformed(self):
        return self.Zundeformed + self.Zdeformation


    def get_deformed(self):
        return self.Xdeformed(),self.Ydeformed(),self.Zdeformed()

    def get_undeformed(self):
        return self.Xundeformed,self.Yundeformed,self.Zundeformed

    def get_deformation(self):
        return self.Xdeformation,self.Ydeformation,self.Zdeformation

    def get_limits_undeformed(self):

        print("X undeformed limits: ", self.Xundeformed.min(), self.Xundeformed.max())
        print("Y undeformed limits: ", self.Yundeformed.min(), self.Yundeformed.max())
        print("Z undeformed limits: ", self.Zundeformed.min(), self.Zundeformed.max())

        return self.Xundeformed.min(), self.Xundeformed.max(), \
               self.Yundeformed.min(), self.Yundeformed.max(), \
               self.Zundeformed.min(), self.Zundeformed.max()

    def get_limits_deformation(self):

        print("Xdeformation limits: ", self.Xdeformation.min(), self.Xdeformation.max())
        print("Ydeformation limits: ", self.Ydeformation.min(), self.Ydeformation.max())
        print("Zdeformation limits: ", self.Zdeformation.min(), self.Zdeformation.max())

        return self.Xdeformation.min(), self.Xdeformation.max(), \
               self.Ydeformation.min(), self.Ydeformation.max(), \
               self.Zdeformation.min(), self.Zdeformation.max()

    def get_limits_deformed(self):

        print("X deformed limits: ", self.Xdeformed().min(), self.Xdeformed().max())
        print("Y deformed limits: ", self.Ydeformed().min(), self.Ydeformed().max())
        print("Z deformed limits: ", self.Zdeformed().min(), self.Zdeformed().max())

        return self.Xdeformed().min(), self.Xdeformed().max(), \
               self.Ydeformed().min(), self.Ydeformed().max(), \
               self.Zdeformed().min(), self.Zdeformed().max()


    def replicate_raw_data(self,flag):

        if flag == 0: # nothing
            return
        elif flag == 1: # axis 0
            self.Xundeformed = numpy.concatenate((-self.Xundeformed, self.Xundeformed))
            self.Yundeformed = numpy.concatenate((self.Yundeformed, self.Yundeformed))
            self.Zundeformed = numpy.concatenate((self.Zundeformed, self.Zundeformed))
            self.Xdeformation = numpy.concatenate((-self.Xdeformation, self.Xdeformation))
            self.Ydeformation = numpy.concatenate((self.Ydeformation, self.Ydeformation))
            self.Zdeformation = numpy.concatenate((self.Zdeformation, self.Zdeformation))
        elif flag == 2: # axis 1
            self.Xundeformed = numpy.concatenate((self.Xundeformed, self.Xundeformed))
            self.Yundeformed = numpy.concatenate((-self.Yundeformed, self.Yundeformed))
            self.Zundeformed = numpy.concatenate((self.Zundeformed, self.Zundeformed))
            self.Xdeformation = numpy.concatenate((self.Xdeformation, self.Xdeformation))
            self.Ydeformation = numpy.concatenate((-self.Ydeformation, self.Ydeformation))
            self.Zdeformation = numpy.concatenate((self.Zdeformation, self.Zdeformation))
        elif flag == 3: # both axes
            self.Xundeformed = numpy.concatenate((-self.Xundeformed, self.Xundeformed))
            self.Yundeformed = numpy.concatenate((self.Yundeformed, self.Yundeformed))
            self.Zundeformed = numpy.concatenate((self.Zundeformed, self.Zundeformed))
            self.Xdeformation = numpy.concatenate((-self.Xdeformation, self.Xdeformation))
            self.Ydeformation = numpy.concatenate((self.Ydeformation, self.Ydeformation))
            self.Zdeformation = numpy.concatenate((self.Zdeformation, self.Zdeformation))

            self.Xundeformed = numpy.concatenate((self.Xundeformed, self.Xundeformed))
            self.Yundeformed = numpy.concatenate((-self.Yundeformed, self.Yundeformed))
            self.Zundeformed = numpy.concatenate((self.Zundeformed, self.Zundeformed))
            self.Xdeformation = numpy.concatenate((self.Xdeformation, self.Xdeformation))
            self.Ydeformation = numpy.concatenate((-self.Ydeformation, self.Ydeformation))
            self.Zdeformation = numpy.concatenate((self.Zdeformation, self.Zdeformation))


    def triangulate(self):
        # triangulation
        self.triPi = numpy.array([self.Xdeformed(), self.Ydeformed()]).transpose()
        self.tri = spatial.Delaunay(self.triPi)

    def plot_triangulation(self,show=True):
        fig = plt.figure()
        plt.triplot(self.Xdeformed(), self.Ydeformed() , self.tri.simplices.copy())
        plt.plot(self.Xdeformed(), self.Ydeformed(), "or", label = "Data")
        plt.grid()
        plt.legend()
        plt.title("triangulation")
        plt.xlabel("x")
        plt.ylabel("y")
        if show:
            plt.show()
        return fig

    def get_Xinterpolated_mesh(self):
        return numpy.outer(self.x_interpolated,numpy.ones_like(self.y_interpolated))

    def get_Yinterpolated_mesh(self):
        return numpy.outer(numpy.ones_like(self.x_interpolated),self.y_interpolated)


    def interpolate(self,nx,ny,remove_nan=False):
        if self.tri is None:
            self.triangulate()

        lim = self.get_limits_deformed()
        self.x_interpolated = numpy.linspace(lim[0],lim[1],nx)
        self.y_interpolated = numpy.linspace(lim[2],lim[3],ny)

        X_INTERPOLATED =  self.get_Xinterpolated_mesh()
        Y_INTERPOLATED =  self.get_Yinterpolated_mesh()

        self.P = numpy.array([X_INTERPOLATED.flatten(), Y_INTERPOLATED.flatten() ]).transpose()

        if remove_nan:
            self.Z_INTERPOLATED = interpolate.griddata(self.triPi, self.Zdeformed(), self.P, method = "cubic", fill_value=self.Zdeformed().min() ).reshape([nx,ny])
        else:
            self.Z_INTERPOLATED = interpolate.griddata(self.triPi, self.Zdeformed(), self.P, method="cubic").reshape([nx, ny])


    def plot_interpolated(self, show=True):
        fig = plt.figure()
        plt.contourf(self.get_Xinterpolated_mesh(), self.get_Yinterpolated_mesh(), self.Z_INTERPOLATED, 50, cmap = mpl.cm.jet)
        plt.colorbar()
        plt.contour(self.get_Xinterpolated_mesh(), self.get_Yinterpolated_mesh(), self.Z_INTERPOLATED, 20, colors = "k")
        plt.plot(self.Xdeformed(), self.Ydeformed(), "or", label = "Data")
        plt.legend()
        # plt.title = "Interpolated"  <---- THIS MAKES ERROR IN THE NEXT PLOT!!!!!!!!!!!!!!!!!
        plt.grid()
        if show:
            plt.show()
        return fig



    def plot_surface_image(self,invert_axes_names=False):
        if invert_axes_names:
            plot_image(self.Z_INTERPOLATED,self.x_interpolated,self.y_interpolated ,title="file: %s, axes names INVERTED from ANSYS"%self.filename,
                       xtitle="Y (%d pixels, max:%f)"%(self.x_interpolated.size,self.x_interpolated.max()),
                       ytitle="X (%d pixels, max:%f)"%(self.y_interpolated.size,self.y_interpolated.max()) )
        else:
            plot_image(self.Z_INTERPOLATED,self.x_interpolated,self.y_interpolated,title="file: %s, axes as in ANSYS"%self.filename,
                       xtitle="X (%d pixels, max:%f)"%(self.x_interpolated.size,self.x_interpolated.max()),
                       ytitle="Y (%d pixels, max:%f)"%(self.y_interpolated.size,self.y_interpolated.max()) )


    def does_interpolated_have_nan(self):
        return numpy.isnan(self.Z_INTERPOLATED).sum() > 0

    def remove_borders_in_interpolated_data(self):
        self.x_interpolated = self.x_interpolated[1:-2].copy()
        self.y_interpolated = self.y_interpolated[1:-2].copy()
        self.Z_INTERPOLATED = self.Z_INTERPOLATED[1:-2,1:-2].copy()

    def detrend(self,axis=0):
        if axis == 0:
            xm = self.x_interpolated.copy()
            zm = self.Z_INTERPOLATED[:,self.y_interpolated.size//2]
        elif axis == 1:
            xm = self.y_interpolated.copy()
            zm = self.Z_INTERPOLATED[self.x_interpolated.size // 2, :]

        zm.shape = -1

        icut = numpy.argwhere( xm > -xm[-1])
        xcut = xm[icut]
        zmcut = zm[icut]

        xcut.shape = -1
        zmcut.shape = -1

        print( numpy.argwhere(numpy.isnan(self.Z_INTERPOLATED)) )
        coeff = numpy.polyfit(xcut, zmcut, deg=2)

        zfit = coeff[1] * xm  + coeff[0]

        if axis ==0:
            for i in range(self.Z_INTERPOLATED.shape[1]):
                self.Z_INTERPOLATED[:,i] -= zfit
        elif axis == 1:
            for i in range(self.Z_INTERPOLATED.shape[0]):
                self.Z_INTERPOLATED[i,:] -= zfit

    def reset_height_to_minimum(self):
        self.Z_INTERPOLATED -= self.Z_INTERPOLATED.min()

    def reset_height_to_central_value(self):
        self.Z_INTERPOLATED -= self.Z_INTERPOLATED[self.Z_INTERPOLATED.shape[0]//2,self.Z_INTERPOLATED.shape[1]//2]


    def write_h5_surface(self,filename='presurface.hdf5',invert_axes_names=False):
        if invert_axes_names:
            write_generic_h5_surface(self.Z_INTERPOLATED.T, self.y_interpolated, self.x_interpolated, filename=filename)
        else:
            write_generic_h5_surface(self.Z_INTERPOLATED,self.x_interpolated,self.y_interpolated,filename=filename)\




def surface_plot(xs,ys,zs):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')


    # For each set of style and range settings, plot n random points in the box
    # defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].
    # for m, zlow, zhigh in [('o', -50, -25), ('^', -30, -5)]:
    for m, zlow, zhigh in [('o', zs.min(), zs.max())]:
        ax.scatter(xs, ys, zs, marker=m)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()



if __name__ == "__main__":




    # set_qt()


    # o1 = FEA_File.process_file("/home/manuel/OASYS1.2/alsu-scripts/ANSYS/s4.txt", n_axis_0=301, n_axis_1=51,
    #              filename_out="/home/manuel/Oasys/s4.h5", invert_axes_names=True,
    #              detrend=True, reset_height_method=1, do_plot=False)


    o1 = FEA_File()
    o1.set_filename("/home/manuel/OASYS1.2/alsu-scripts/ANSYS/s4.txt")
    o1.load_multicolumn_file()

    X,Y,Z = o1.get_deformed()
    # X, Y, Z = o1.get_undeformed()
    surface_plot( X,Y,Z)









    # o1.plot_triangulation()
    # o1.plot_interpolated()
    # o1.plot_surface_image()

    # o1 = FEA_File.process_file("73water_side_cooled_notches_best_LH.txt", n_axis_0=1001, n_axis_1=101,
    #              filename_out="/home/manuel/Oasys/water_side_cooled_notches_best_LH.h5", invert_axes_names=True,
    #              detrend=True, reset_height_method=2,
    #              replicate_raw_data_flag=3,do_plot=False)

    # o1 = FEA_File.process_file("73water_side_cooled_notches_best_LV.txt", n_axis_0=1001, n_axis_1=101,
    #              filename_out="/home/manuel/Oasys/water_side_cooled_notches_best_LV.h5", invert_axes_names=True,
    #              detrend=False, reset_height_method=0,
    #              replicate_raw_data_flag=3,do_plot=False)

    #



# class ALSFiniteElementReader(ALSShadowWidget):


from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui

from orangecontrib.shadow.util.shadow_objects import ShadowBeam
from orangecontrib.shadow.util.shadow_util import ShadowCongruence, ShadowPlot
from orangecontrib.shadow.widgets.gui import ow_automatic_element
from orangecontrib.shadow.als.widgets.gui.plots import plot_data1D, plot_data2D

from srxraylib.plot.gol import plot, plot_scatter
import matplotlib.pylab as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

import numpy

from orangecontrib.syned.als.util.FEA_File import FEA_File

from oasys.widgets.widget import OWWidget
from PyQt5.QtCore import QRect, Qt

from srxraylib.plot.gol import plot_image

from silx.gui.plot import Plot2D

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar




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


class ALSFiniteElementReader(OWWidget): #ow_automatic_element.AutomaticElement):

    name = "ALS Finite Element reader"
    description = "Syned: Finite Element reader"
    icon = "icons/hhlo.png"
    maintainer = "APS team"
    maintainer_email = "srio@lbl.gov"
    priority = 1
    category = "Data File Tools"
    keywords = ["data", "file", "load", "read", "FEA", "Finite Elements"]


    # IMAGE_WIDTH = 860
    # IMAGE_HEIGHT = 675
    #
    # want_main_area = 1
    # want_control_area = 1

    want_main_area = 1
    want_control_area = 1

    MAX_WIDTH = 1320
    MAX_HEIGHT = 700

    IMAGE_WIDTH = 860
    IMAGE_HEIGHT = 645

    CONTROL_AREA_WIDTH = 405
    TABS_AREA_HEIGHT = 650

    # "/home/manuel/OASYS1.2/alsu-scripts/ANSYS/s4.txt", n_axis_0 = 301, n_axis_1 = 51,
    # filename_out = "/home/manuel/Oasys/s4.h5", invert_axes_names = True,
    # detrend = True, reset_height_method = 1, do_plot = False

    file_in = Setting("/home/manuel/OASYS1.2/alsu-scripts/ANSYS/s4.txt")
    file_in_type = Setting(0)
    file_in_skiprows = Setting(0)
    replicate_raw_data_flag = Setting(0)  # 0=None, 1=axis0, 2=axis1, 3=both axis
    raw_render_option = Setting(2)

    file_out = Setting("/home/manuel/Oasys/s4.h5")
    n_axis_0 = Setting(301)
    n_axis_1 = Setting(51)
    invert_axes_names = Setting(1)
    detrended = Setting(1)
    reset_height_method = Setting(1)

    fea_file_object = FEA_File()

    def __init__(self, show_automatic_box=False):
        # super().__init__(show_automatic_box=show_automatic_box)
        super().__init__()

        geom = QApplication.desktop().availableGeometry()
        self.setGeometry(QRect(round(geom.width() * 0.05),
                               round(geom.height() * 0.05),
                               round(min(geom.width() * 0.98, self.MAX_WIDTH)),
                               round(min(geom.height() * 0.95, self.MAX_HEIGHT))))

        self.setMaximumHeight(self.geometry().height())
        self.setMaximumWidth(self.geometry().width())

        #
        #
        #
        # general_box = oasysgui.widgetBox(self.general_options_box, "Data file", addSpace=True,
        #                                  orientation="vertical",)


        general_box = oasysgui.widgetBox(self.controlArea, "Data file", addSpace=True,
                                         orientation="vertical",)
                                         # width=self.CONTROL_AREA_WIDTH - 8, height=400)



        figure_box = oasysgui.widgetBox(general_box, "", addSpace=True, orientation="horizontal") #width=550, height=50)
        self.le_beam_file_name = oasysgui.lineEdit(figure_box, self, "file_in", "FEA File:",
                                                    labelWidth=90, valueType=str, orientation="horizontal")
        gui.button(figure_box, self, "...", callback=self.selectFile)
        # gui.separator(general_box, height=20)


        gui.comboBox(general_box, self, "file_in_type", label="File content", labelWidth=220,
                     items=["X Y Z DX DY DZ",],
                     sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(general_box, self, "file_in_skiprows", "Skip rows:", labelWidth=260, valueType=int,
                          orientation="horizontal")


        gui.comboBox(general_box, self, "replicate_raw_data_flag", label="Replicate raw data", labelWidth=220,
                     items=["No","Along axis 0","Along axis 1","Along axes 0 and 1"],
                     sendSelectedValue=False, orientation="horizontal")

        figure_box = oasysgui.widgetBox(general_box, "", addSpace=True, orientation="horizontal")

        gui.comboBox(figure_box, self, "raw_render_option", label="Render", labelWidth=120,
                     items=['Undeformed','Deformation','Deformed'],
                     sendSelectedValue=False, orientation="horizontal")

        gui.button(figure_box, self, "View...", callback=self.plot_raw_data)


        #
        #
        #
        gui.comboBox(self.controlArea, self, "invert_axes_names", label="Invert axes", labelWidth=120,
                     items=['No','Yes'],
                     sendSelectedValue=False, orientation="horizontal")

        gui.button(self.controlArea, self, "Process Raw Data File", callback=self.calculate, height=45)



        # gui.comboBox(general_box, self, "no_lost", label="Rays", labelWidth=220,
        #              items=["All rays", "Good only", "Lost only"],
        #              sendSelectedValue=False, orientation="horizontal")
        #
        # gui.comboBox(general_box, self, "shadow_column", label="Dispersion direction", labelWidth=220,
        #              items=["X (column 1)", "Z (column 3)"],
        #              sendSelectedValue=False, orientation="horizontal")
        #
        # gui.comboBox(general_box, self, "photon_wavelenth_or_energy", label="Photon wavelength/energy",
        #              labelWidth=220,
        #              items=["Wavelength [A]", "Energy [eV]"],
        #              sendSelectedValue=False, orientation="horizontal")
        #
        # oasysgui.lineEdit(general_box, self, "hlim", "Width at percent of max:", labelWidth=260, valueType=int,
        #                   orientation="horizontal")

        gui.separator(self.controlArea, height=200)

        tabs_setting = oasysgui.tabWidget(self.mainArea)
        tabs_setting.setFixedHeight(self.IMAGE_HEIGHT + 5)
        tabs_setting.setFixedWidth(self.IMAGE_WIDTH)

        self.create_tabs_results(tabs_setting)

    def create_tabs_results(self,tabs_setting):

        tmp = oasysgui.createTabPage(tabs_setting, "Result")
        self.result_id = gui.widgetBox(tmp, "", addSpace=True, orientation="vertical")
        self.result_id.setFixedHeight(self.IMAGE_HEIGHT - 30)
        self.result_id.setFixedWidth(self.IMAGE_WIDTH - 20)

        tmp = oasysgui.createTabPage(tabs_setting, "Interpolation")
        self.interpolation_id = gui.widgetBox(tmp, "", addSpace=True, orientation="vertical")
        self.interpolation_id.setFixedHeight(self.IMAGE_HEIGHT - 30)
        self.interpolation_id.setFixedWidth(self.IMAGE_WIDTH - 20)

        tmp = oasysgui.createTabPage(tabs_setting, "Triangulation")
        self.triangulation_id = gui.widgetBox(tmp, "", addSpace=True, orientation="vertical")
        self.triangulation_id.setFixedHeight(self.IMAGE_HEIGHT - 30)
        self.triangulation_id.setFixedWidth(self.IMAGE_WIDTH - 20)

        # tmp = oasysgui.createTabPage(tabs_setting, "Raw Data")
        # self.rawdata_id = gui.widgetBox(tmp, "", addSpace=True, orientation="vertical")
        # self.rawdata_id.setFixedHeight(self.IMAGE_HEIGHT - 30)
        # self.rawdata_id.setFixedWidth(self.IMAGE_WIDTH - 20)
        #
        # tmp = oasysgui.createTabPage(tabs_setting, "Info")
        # self.info_id = oasysgui.textArea(height=self.IMAGE_HEIGHT - 35)
        # info_box = oasysgui.widgetBox(tmp, "", addSpace=True, orientation="horizontal",
        #                               height=self.IMAGE_HEIGHT - 20, width=self.IMAGE_WIDTH - 20)
        # info_box.layout().addWidget(self.info_id)

    def set_input_file(self,filename):
        self.le_beam_file_name.setText(filename)

    def selectFile(self):
        filename = oasysgui.selectFileFromDialog(self,
                previous_file_path=self.file_in, message="Open FEA Raw ASCII File",
                start_directory=".", file_extension_filter="*.*")

        self.le_beam_file_name.setText(filename)

    def load_raw_data(self):
        self.fea_file_object = FEA_File()
        self.fea_file_object.set_filename(self.file_in)
        self.fea_file_object.load_multicolumn_file(skiprows=self.file_in_skiprows)
        self.fea_file_object.replicate_raw_data(self.replicate_raw_data_flag)

    def plot_raw_data(self):
        self.load_raw_data()
        if self.raw_render_option == 0:
            X, Y, Z = self.fea_file_object.get_undeformed()
        elif self.raw_render_option == 1:
            X, Y, Z = self.fea_file_object.get_deformation()
        elif self.raw_render_option == 2:
            X, Y, Z = self.fea_file_object.get_deformed()

        surface_plot(X, Y, Z)

    def calculate(self):
        self.load_raw_data()

        self.fea_file_object.triangulate()

        self.fea_file_object.interpolate(self.n_axis_0, self.n_axis_1)

        if self.fea_file_object.does_interpolated_have_nan():
            self.fea_file_object.remove_borders_in_interpolated_data()


        if self.detrended:
            self.fea_file_object.detrend()

        # o1.reset_height_to_minimum()

        if self.reset_height_method == 0:
            pass
        elif self.reset_height_method == 1:
            self.fea_file_object.reset_height_to_minimum()
        elif self.reset_height_method == 2:
            self.fea_file_object.reset_height_to_central_value()

        self.fea_file_object.write_h5_surface(filename=self.file_out, invert_axes_names=self.invert_axes_names)

        self.plot_results()



        # self.writeStdOut("", initialize=True)
        # beam_to_analize1 = self.get_shadow3_beam1()
        #
        # if beam_to_analize1 is None:
        #     print("No SHADOW Beam")
        #     return
        #
        # if self.shadow_column == 0:
        #     col = 1
        # elif self.shadow_column == 1:
        #     col = 3
        #
        # if self.photon_wavelenth_or_energy == 0:
        #     colE = 19
        # elif self.photon_wavelenth_or_energy == 1:
        #     colE = 11
        #
        # dict = self.respower(beam_to_analize1, colE, col, hlimit=1e-2 * self.hlim, nolost=self.no_lost)
        # for key in dict.keys():
        #     print(key, " = ", dict[key])
        #
        # self.respower_plot(beam_to_analize1, dict, nolost=self.no_lost)
        #
        # self.writeStdOut(dict["info"], initialize=True)

    def writeStdOut(self, text, initialize=True):
        cursor = self.info_id.textCursor()
        if initialize:
            self.info_id.setText(text)
        else:
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertText(text)
            self.info_id.setTextCursor(cursor)
            self.info_id.ensureCursorVisible()


    def plot_results(self):

        #
        # result
        #

        if self.invert_axes_names:
            self.plot_data2D(self.fea_file_object.Z_INTERPOLATED,
                           self.fea_file_object.x_interpolated,
                           self.fea_file_object.y_interpolated,self.result_id,
                       title="file: %s, axes names INVERTED from ANSYS"%self.file_in,
                       xtitle="Y [m] (%d pixels, max:%f)"%(self.fea_file_object.x_interpolated.size,
                                                       self.fea_file_object.x_interpolated.max()),
                       ytitle="X [m] (%d pixels, max:%f)"%(self.fea_file_object.y_interpolated.size,
                                                       self.fea_file_object.y_interpolated.max()) )
        else:
            self.plot_data2D(self.fea_file_object.Z_INTERPOLATED,
                           self.fea_file_object.x_interpolated,
                           self.fea_file_object.y_interpolated,self.result_id,
                       title="file: %s, axes as in ANSYS"%self.file_in,
                       xtitle="X [m] (%d pixels, max:%f)"%(self.fea_file_object.x_interpolated.size,
                                                       self.fea_file_object.x_interpolated.max()),
                       ytitle="Y [m] (%d pixels, max:%f)"%(self.fea_file_object.y_interpolated.size,
                                                       self.fea_file_object.y_interpolated.max()) )


        #
        # interpolation plot
        #
        self.interpolation_id.layout().removeItem(self.interpolation_id.layout().itemAt(1))
        self.interpolation_id.layout().removeItem(self.interpolation_id.layout().itemAt(0))

        f = self.fea_file_object.plot_interpolated(show=0)
        figure_canvas = FigureCanvasQTAgg(f)
        toolbar = NavigationToolbar(figure_canvas, self)

        self.interpolation_id.layout().addWidget(toolbar)
        self.interpolation_id.layout().addWidget(figure_canvas)


        #
        # triangulation plot
        #
        self.triangulation_id.layout().removeItem(self.triangulation_id.layout().itemAt(1))
        self.triangulation_id.layout().removeItem(self.triangulation_id.layout().itemAt(0))

        f = self.fea_file_object.plot_triangulation(show=0)
        figure_canvas = FigureCanvasQTAgg(f)
        toolbar = NavigationToolbar(figure_canvas, self)

        self.triangulation_id.layout().addWidget(toolbar)
        self.triangulation_id.layout().addWidget(figure_canvas)




        #
        # self.fea_file_object.plot_interpolated()

        # self.fea_file_object.plot_surface_image()




    def plot_data2D(self, data2D, dataX, dataY, tabs_canvas_index, title="title", xtitle="X",ytitle="Y"):

        # for i in range(1 + self.tab[tabs_canvas_index].layout().count()):
        #     self.tab[tabs_canvas_index].layout().removeItem(self.tab[tabs_canvas_index].layout().itemAt(i))

        tabs_canvas_index.layout().removeItem(tabs_canvas_index.layout().itemAt(0))

        origin = (dataX[0], dataY[0])
        scale = (dataX[1] - dataX[0], dataY[1] - dataY[0])

        colormap = {"name": "temperature", "normalization": "linear",
                    "autoscale": True, "vmin": 0, "vmax": 0, "colors": 256}

        tmp = Plot2D()
        tmp.resetZoom()
        tmp.setXAxisAutoScale(True)
        tmp.setYAxisAutoScale(True)
        tmp.setGraphGrid(False)
        tmp.setKeepDataAspectRatio(True)
        tmp.yAxisInvertedAction.setVisible(False)
        tmp.setXAxisLogarithmic(False)
        tmp.setYAxisLogarithmic(False)
        tmp.getMaskAction().setVisible(False)
        tmp.getRoiAction().setVisible(False)
        tmp.getColormapAction().setVisible(True)
        tmp.setKeepDataAspectRatio(False)
        tmp.addImage(data2D.T,legend="1",scale=scale,origin=origin,colormap=colormap,replace=True)
        tmp.setActiveImage("1")
        tmp.setGraphXLabel(xtitle)
        tmp.setGraphYLabel(ytitle)
        tmp.setGraphTitle(title)
        tabs_canvas_index.layout().addWidget(tmp)




        # colE = d["colE"]
        # col1 = d["col1"]
        # coeff = d["coeff"]
        # nolost = d["nolost"]
        # coordinates_at_hlimit = d["coordinates_at_hlimit"]
        # orig = d["origin"]
        # title = d["title"]
        # deltax1 = d["deltax1"]
        # deltax2 = d["deltax2"]
        #
        # if colE == 11:
        #     xtitle = "Photon energy [eV]"
        #     unit = "eV"
        # elif colE == 19:
        #     xtitle = "Photon wavelength [A]"
        #     unit = "A"
        #
        # ytitle = "column %i [user units]" % col1
        #
        # energy = beam.getshonecol(colE, nolost=nolost)
        # z = beam.getshonecol(col1, nolost=nolost)
        # yfit = coeff[1] + coeff[0] * energy
        #
        # #
        # # substracted plot
        # #
        # f = plot_scatter(energy, z - (coeff[1] + coeff[0] * energy), xtitle=xtitle, ytitle=ytitle, title=title,
        #                  show=0)
        # f[1].plot(energy, energy * 0 + coordinates_at_hlimit[0])
        # f[1].plot(energy, energy * 0 + coordinates_at_hlimit[1])
        #
        # figure_canvas = FigureCanvasQTAgg(f[0])
        # self.detrended_id.layout().removeItem(self.detrended_id.layout().itemAt(0))
        # self.detrended_id.layout().addWidget(figure_canvas)
        #
        # #
        # # main plot
        # #
        #
        # g = plot_scatter(energy, z, show=0, xtitle=xtitle, ytitle=ytitle,
        #                  title=title + " E/DE=%d, DE=%f %s" % (d["resolvingPower"], d["deltaE"], unit))
        # g[1].plot(energy, yfit)
        # g[1].plot(energy, yfit + coordinates_at_hlimit[0])
        # g[1].plot(energy, yfit + coordinates_at_hlimit[1])
        #
        # g[1].plot(energy, energy * 0)
        # if colE == 19:  # wavelength
        #     g[1].plot(numpy.array((orig + deltax1, orig + deltax1)), numpy.array((-1000, 1000)))
        #     g[1].plot(numpy.array((orig - deltax2, orig - deltax2)), numpy.array((-1000, 1000)))
        # else:  # energy
        #     g[1].plot(numpy.array((orig - deltax1, orig - deltax1)), numpy.array((-1000, 1000)))
        #     g[1].plot(numpy.array((orig + deltax2, orig + deltax2)), numpy.array((-1000, 1000)))
        #
        # figure_canvas = FigureCanvasQTAgg(g[0])
        # self.dispersion_id.layout().removeItem(self.dispersion_id.layout().itemAt(0))
        # self.dispersion_id.layout().addWidget(figure_canvas)

if __name__ == "__main__":
    import sys
    a = QApplication(sys.argv)
    ow = ALSFiniteElementReader()
    ow.show()
    a.exec_()
    ow.saveSettings()


    # from srxraylib.plot.gol import plot_image, set_qt, plot
    # import os
    #
    # set_qt()
    #
    #
    # o1 = FEA_File.process_file("/home/manuel/OASYS1.2/alsu-scripts/ANSYS/s4.txt", n_axis_0=301, n_axis_1=51,
    #              filename_out="/home/manuel/Oasys/s4.h5", invert_axes_names=True,
    #              detrend=True, reset_height_method=1, do_plot=False)
    #
    #

    # o1 = FEA_File.process_file("73water_side_cooled_notches_best_LH.txt", n_axis_0=1001, n_axis_1=101,
    #              filename_out="/home/manuel/Oasys/water_side_cooled_notches_best_LH.h5", invert_axes_names=True,
    #              detrend=True, reset_height_method=2,
    #              replicate_raw_data_flag=3,do_plot=False)

    # o1 = FEA_File.process_file("73water_side_cooled_notches_best_LV.txt", n_axis_0=1001, n_axis_1=101,
    #              filename_out="/home/manuel/Oasys/water_side_cooled_notches_best_LV.h5", invert_axes_names=True,
    #              detrend=False, reset_height_method=0,
    #              replicate_raw_data_flag=3,do_plot=False)

    #
    # o1.plot_triangulation()
    # o1.plot_interpolated()
    # o1.plot_surface_image()
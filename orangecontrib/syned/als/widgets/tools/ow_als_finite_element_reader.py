

# class ALSFiniteElementReader(ALSShadowWidget):

import os
import numpy

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QRect, Qt

from orangewidget import gui
from orangewidget.settings import Setting

from oasys.widgets import gui as oasysgui
from oasys.widgets.widget import OWWidget
from oasys.util.oasys_objects import OasysSurfaceData

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


from orangecontrib.syned.als.util.FEA_File import FEA_File
from silx.gui.plot import Plot2D



class ALSFiniteElementReader(OWWidget): #ow_automatic_element.AutomaticElement):

    name = "ALS Finite Element reader"
    description = "Syned: Finite Element reader"
    icon = "icons/hhlo.png"
    maintainer = "APS team"
    maintainer_email = "srio@lbl.gov"
    priority = 1
    category = "Data File Tools"
    keywords = ["data", "file", "load", "read", "FEA", "Finite Elements"]

    outputs = [{"name": "Surface Data",
                "type": OasysSurfaceData,
                "doc": "Surface Data",
                "id": "Surface Data"},
               {"name": "DABAM 1D Profile",
                "type": numpy.ndarray,
                "doc": "numpy.ndarray",
                "id": "numpy.ndarray"},
               ]

    want_main_area = 1
    want_control_area = 1

    MAX_WIDTH = 1320
    MAX_HEIGHT = 700

    IMAGE_WIDTH = 860
    IMAGE_HEIGHT = 645

    CONTROL_AREA_WIDTH = 405
    TABS_AREA_HEIGHT = 650

    file_in = Setting("/home/manuel/OASYS1.2/alsu-scripts/ANSYS/s4.txt")
    file_in_type = Setting(0)
    file_in_skiprows = Setting(0)
    replicate_raw_data_flag = Setting(0)  # 0=None, 1=axis0, 2=axis1, 3=both axis
    # raw_render_option = Setting(2)

    file_out = Setting("/home/manuel/OASYS1.2/alsu-scripts/ANSYS/s4.h5") # copied from file_in and changed extension to h5
    n_axis_0 = Setting(301)
    n_axis_1 = Setting(51)
    invert_axes_names = Setting(1)
    detrended = Setting(1)
    reset_height_method = Setting(0)
    extract_profile1D = Setting(0)
    coordinate_profile1D = Setting(0.0)

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
        # tabs for results
        #
        self.tabs_setting = oasysgui.tabWidget(self.mainArea)
        self.tabs_setting.setFixedHeight(self.IMAGE_HEIGHT + 5)
        self.tabs_setting.setFixedWidth(self.IMAGE_WIDTH)
        self.create_tabs_results()



        #
        # parameters panel
        #

        gui.button(self.controlArea, self, "Calculate Interpolated File", callback=self.calculate, height=45)

        gui.separator(self.controlArea, height=20)

        #
        #
        data_file_box = oasysgui.widgetBox(self.controlArea, "Data file", addSpace=True,
                                         orientation="vertical",)


        figure_box = oasysgui.widgetBox(data_file_box, "", addSpace=True, orientation="horizontal") #width=550, height=50)
        self.le_beam_file_name = oasysgui.lineEdit(figure_box, self, "file_in", "FEA File:",
                                                    labelWidth=90, valueType=str, orientation="horizontal")
        gui.button(figure_box, self, "...", callback=self.selectFile)


        gui.comboBox(data_file_box, self, "file_in_type", label="File content", labelWidth=220,
                     items=["X Y Z DX DY DZ",],
                     sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(data_file_box, self, "file_in_skiprows", "Skip rows:", labelWidth=260, valueType=int,
                          orientation="horizontal")


        gui.comboBox(data_file_box, self, "replicate_raw_data_flag", label="Replicate raw data", labelWidth=220,
                     items=["No","Along axis 0","Along axis 1","Along axes 0 and 1"],
                     sendSelectedValue=False, orientation="horizontal")

        #
        #
        interpolation_box = oasysgui.widgetBox(self.controlArea, "Interpolation", addSpace=True,
                                         orientation="vertical",)


        oasysgui.lineEdit(interpolation_box, self, "n_axis_0", "Number of interpolated pixels (axis 0))",
                          labelWidth=260, valueType=int, orientation="horizontal")

        oasysgui.lineEdit(interpolation_box, self, "n_axis_1", "Number of interpolated pixels in (axis 1))",
                          labelWidth=260, valueType=int, orientation="horizontal")

        gui.comboBox(interpolation_box, self, "invert_axes_names", label="Invert axes", labelWidth=120,
                     items=['No','Yes'],
                     sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(interpolation_box, self, "detrended", label="Detrend straight line", labelWidth=220,
                     items=["No", "Yes (along axis 0)", "Yes (along axis 1)"],
                     sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(interpolation_box, self, "reset_height_method", label="Reset zero height", labelWidth=220,
                     items=["No", "To height minimum", "To center"],
                     sendSelectedValue=False, orientation="horizontal")

        tmp = oasysgui.lineEdit(interpolation_box, self, "file_out", "Output file name",
                          labelWidth=150, valueType=str, orientation="horizontal")

        tmp.setEnabled(False)

        #
        #
        profile1D_box = oasysgui.widgetBox(self.controlArea, "1D profile", addSpace=True,
                                         orientation="vertical",)
        gui.comboBox(profile1D_box, self, "extract_profile1D", label="Extract and send 1D profile", labelWidth=220,
                     items=["horizontal", "vertical"],
                     sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(profile1D_box, self, "coordinate_profile1D", "At coordinate [m]:", labelWidth=260, valueType=float,
                          orientation="horizontal")


        # self.set_visible()


    def create_tabs_results(self):

        tabs_setting = self.tabs_setting
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

        tmp = oasysgui.createTabPage(tabs_setting, "Raw Data")
        self.rawdata_id = gui.widgetBox(tmp, "", addSpace=True, orientation="vertical")
        self.rawdata_id.setFixedHeight(self.IMAGE_HEIGHT - 30)
        self.rawdata_id.setFixedWidth(self.IMAGE_WIDTH - 20)

        tmp = oasysgui.createTabPage(tabs_setting, "1D profile")
        self.profile1D_id = gui.widgetBox(tmp, "", addSpace=True, orientation="vertical")
        self.profile1D_id.setFixedHeight(self.IMAGE_HEIGHT - 30)
        self.profile1D_id.setFixedWidth(self.IMAGE_WIDTH - 20)
        #
        tmp = oasysgui.createTabPage(tabs_setting, "Output")
        self.info_id = oasysgui.textArea(height=self.IMAGE_HEIGHT - 35)
        info_box = oasysgui.widgetBox(tmp, "", addSpace=True, orientation="horizontal",
                                      height=self.IMAGE_HEIGHT - 20, width=self.IMAGE_WIDTH - 20)
        info_box.layout().addWidget(self.info_id)

    def set_input_file(self,filename):
        self.le_beam_file_name.setText(filename)

    def selectFile(self):
        filename = oasysgui.selectFileFromDialog(self,
                previous_file_path=self.file_in, message="Open FEA Raw ASCII File",
                start_directory=".", file_extension_filter="*.*")

        self.le_beam_file_name.setText(filename)
        self.file_out = os.path.splitext(filename)[0]+'.h5'

    def load_raw_data(self):
        self.fea_file_object = FEA_File()
        self.fea_file_object.set_filename(self.file_in)
        self.fea_file_object.load_multicolumn_file(skiprows=self.file_in_skiprows)
        self.fea_file_object.replicate_raw_data(self.replicate_raw_data_flag)

    def calculate(self):

        self.load_raw_data()

        self.fea_file_object.triangulate()

        # add 3 pixels to match requested pixels after edge removal
        self.fea_file_object.interpolate(self.n_axis_0 + 3, self.n_axis_1 + 3)

        if self.fea_file_object.does_interpolated_have_nan():
            self.fea_file_object.remove_borders_in_interpolated_data()


        if self.detrended == 0:
            pass
        elif self.detrended == 1:
            self.fea_file_object.detrend(axis=0)
        elif self.detrended == 2:
            self.fea_file_object.detrend(axis=1)


        if self.reset_height_method == 0:
            pass
        elif self.reset_height_method == 1:
            self.fea_file_object.reset_height_to_minimum()
        elif self.reset_height_method == 2:
            self.fea_file_object.reset_height_to_central_value()

        self.fea_file_object.write_h5_surface(filename=self.file_out, invert_axes_names=self.invert_axes_names)

        self.plot_and_send_results()


    def write_info(self, text, initialize=True):
        cursor = self.info_id.textCursor()
        if initialize:
            self.info_id.setText(text)
        else:
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertText(text)
            self.info_id.setTextCursor(cursor)
            self.info_id.ensureCursorVisible()


    def plot_and_send_results(self):

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

        self.write_info("File %s written to disk.\n"%self.file_out,initialize=False)
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
        # raw data
        #
        self.rawdata_id.layout().removeItem(self.rawdata_id.layout().itemAt(1))
        self.rawdata_id.layout().removeItem(self.rawdata_id.layout().itemAt(0))


        xs, ys, zs = self.fea_file_object.get_deformed()

        xs *= 1e3
        ys *= 1e3
        zs *= 1e6

        fig = Figure()
        self.axis = fig.add_subplot(111, projection='3d')

        # For each set of style and range settings, plot n random points in the box
        # defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].
        # for m, zlow, zhigh in [('o', -50, -25), ('^', -30, -5)]:
        for m, zlow, zhigh in [('o', zs.min(), zs.max())]:
            self.axis.scatter(xs, ys, zs, marker=m)

        self.axis.set_xlabel('X [mm]')
        self.axis.set_ylabel('Y [mm]')
        self.axis.set_zlabel('Z [um]')


        figure_canvas = FigureCanvasQTAgg(fig)
        toolbar = NavigationToolbar(figure_canvas, self)

        self.rawdata_id.layout().addWidget(toolbar)
        self.rawdata_id.layout().addWidget(figure_canvas)

        self.axis.mouse_init()

        #
        # result
        #

        mesh = self.fea_file_object.Z_INTERPOLATED
        mesh_shape = mesh.shape
        x = self.fea_file_object.x_interpolated
        y = self.fea_file_object.y_interpolated

        if self.extract_profile1D == 0:
            abscissas = x
            perp_abscissas = y
            index0 = numpy.argwhere(perp_abscissas >= self.coordinate_profile1D)
            try:
                index0 = index0[0][0]
            except:
                index0 = -1
            profile1D = mesh[:, index0]
            if self.invert_axes_names:
                title = "profile at X[%d] = %f" % (index0, perp_abscissas[index0])
                xtitle = "Y [m] "
            else:
                title = "profile at Y[%d] = %f" % (index0, perp_abscissas[index0])
                xtitle = "X [m] "
            self.plot_data1D(abscissas, profile1D, self.profile1D_id, title=title, xtitle=xtitle, ytitle="Z [m] ")
        else:
            abscissas = y
            perp_abscissas = x
            index0 = numpy.argwhere(perp_abscissas >= self.coordinate_profile1D)
            try:
                index0 = index0[0][0]
            except:
                index0 = -1
            profile1D = mesh[index0, :]
            if self.invert_axes_names:
                title = "profile at Y[%d] = %f" % (index0, perp_abscissas[index0])
                xtitle = "X [m] "
            else:
                title = "profile at X[%d] = %f" % (index0, perp_abscissas[index0])
                xtitle = "Y [m] "
            self.plot_data1D(abscissas, profile1D, self.profile1D_id, title=title, xtitle=xtitle, ytitle="Z [m] ")


        if self.invert_axes_names:
            self.send("Surface Data",
                      OasysSurfaceData(xx=self.fea_file_object.y_interpolated,
                                       yy=self.fea_file_object.x_interpolated,
                                       zz=self.fea_file_object.Z_INTERPOLATED,
                                       surface_data_file=self.file_out))
        else:
            self.send("Surface Data",
                      OasysSurfaceData(xx=self.fea_file_object.x_interpolated,
                                       yy=self.fea_file_object.y_interpolated,
                                       zz=self.fea_file_object.Z_INTERPOLATED.T,
                                       surface_data_file=self.file_out))

        dabam_profile = numpy.zeros((profile1D.size, 2))
        dabam_profile[:, 0] = abscissas
        dabam_profile[:, 1] = profile1D
        self.send("DABAM 1D Profile", dabam_profile)



    def plot_data2D(self, data2D, dataX, dataY, tabs_canvas_index, title="title", xtitle="X",ytitle="Y"):


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

    def plot_data1D(self, dataX, dataY, tabs_canvas_index, title="", xtitle="", ytitle=""):

        tabs_canvas_index.layout().removeItem(tabs_canvas_index.layout().itemAt(0))

        tmp = oasysgui.plotWindow()
        tmp.addCurve(dataX, dataY)
        tmp.resetZoom()
        tmp.setXAxisAutoScale(True)
        tmp.setYAxisAutoScale(True)
        tmp.setGraphGrid(False)
        tmp.setXAxisLogarithmic(False)
        tmp.setYAxisLogarithmic(False)
        tmp.setGraphXLabel(xtitle)
        tmp.setGraphYLabel(ytitle)
        tmp.setGraphTitle(title)

        tabs_canvas_index.layout().addWidget(tmp)


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
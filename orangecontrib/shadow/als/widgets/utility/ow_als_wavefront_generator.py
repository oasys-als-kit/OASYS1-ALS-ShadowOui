# TODO: exoprt wavefront as wofry generic


from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui

from orangecontrib.shadow.util.shadow_objects import ShadowBeam
from orangecontrib.shadow.util.shadow_util import ShadowCongruence, ShadowPlot
from orangecontrib.shadow.widgets.gui import ow_automatic_element

import numpy as np
import scipy.interpolate as interpolate

from silx.gui.plot import Plot2D

class ALSWavefrontGenerator(ow_automatic_element.AutomaticElement):

    name = "ALS Wavefront Generator"
    description = "Shadow: ALS Wavefront Generator"
    icon = "icons/wavefront_generator.png"
    maintainer = "APS team"
    maintainer_email = "srio@esrf.eu"
    priority = 4
    category = "Data Display Tools"
    keywords = ["data", "file", "load", "read"]

    inputs = [("Input Beam", ShadowBeam, "setBeam")]

    IMAGE_WIDTH = 860
    IMAGE_HEIGHT = 675

    want_main_area=1
    want_control_area = 1

    input_beam=None

    #
    #
    image_plane=Setting(0)
    image_plane_new_position=Setting(10.0)
    image_plane_rel_abs_position=Setting(0)

    mode = Setting(0)
    center_x = Setting(0.0)
    center_z = Setting(0.0)

    x_range=Setting(0)
    x_range_min=Setting(-10.0)
    x_range_max=Setting(10.0)
    x_npoints=Setting(101)


    z_range=Setting(0)
    z_range_min=Setting(-10.0)
    z_range_max=Setting(10.0)
    z_npoints=Setting(101)

    def __init__(self, show_automatic_box=True):
        super().__init__()

        gui.button(self.controlArea, self, "Calculate", callback=self.calculate, height=45)

        general_box = oasysgui.widgetBox(self.controlArea, "General Settings", addSpace=True, orientation="vertical",
                                         width=self.CONTROL_AREA_WIDTH-8, height=320)

        gui.comboBox(general_box, self, "mode", label="Mode", labelWidth=250,
                                    items=["Using slopes",
                                            "Using Optical Path"],
                                    sendSelectedValue=False, orientation="horizontal")


        oasysgui.lineEdit(general_box, self, "x_npoints", "X Points", labelWidth=260, valueType=int, orientation="horizontal")
        gui.comboBox(general_box, self, "x_range", label="X Range",labelWidth=250,
                                     items=["<Default>",
                                            "Set.."],
                                     callback=self.set_XRange, sendSelectedValue=False, orientation="horizontal")

        self.xrange_box = oasysgui.widgetBox(general_box, "", addSpace=False, orientation="vertical", height=100)
        self.xrange_box_empty = oasysgui.widgetBox(general_box, "", addSpace=False, orientation="vertical",  height=100)

        self.le_x_range_min = oasysgui.lineEdit(self.xrange_box, self, "x_range_min", "X min [um]", labelWidth=260, valueType=float, orientation="horizontal")
        self.le_x_range_max = oasysgui.lineEdit(self.xrange_box, self, "x_range_max", "X max [um]", labelWidth=260, valueType=float, orientation="horizontal")

        self.set_XRange()

        oasysgui.lineEdit(general_box, self, "z_npoints", "Z Points", labelWidth=260, valueType=int, orientation="horizontal")

        gui.comboBox(general_box, self, "z_range", label="Z Range",labelWidth=250,
                                     items=["<Default>",
                                            "Set.."],
                                     callback=self.set_ZRange, sendSelectedValue=False, orientation="horizontal")

        self.zrange_box = oasysgui.widgetBox(general_box, "", addSpace=False, orientation="vertical", height=100)
        self.zrange_box_empty = oasysgui.widgetBox(general_box, "", addSpace=False, orientation="vertical",  height=100)

        self.le_z_range_min = oasysgui.lineEdit(self.zrange_box, self, "z_range_min", "Z min [um]", labelWidth=260, valueType=float, orientation="horizontal")
        self.le_z_range_max = oasysgui.lineEdit(self.zrange_box, self, "z_range_max", "Z max [um]", labelWidth=260, valueType=float, orientation="horizontal")

        self.set_ZRange()

        # screen_box = oasysgui.widgetBox(self.controlArea, "Screen Position Settings", addSpace=True, orientation="vertical", height=110)
        #
        # self.image_plane_combo = gui.comboBox(screen_box, self, "image_plane", label="Position of the Image",
        #                                     items=["On Image Plane", "Retraced"], labelWidth=260,
        #                                     callback=self.set_ImagePlane, sendSelectedValue=False, orientation="horizontal")
        #
        # self.image_plane_box = oasysgui.widgetBox(screen_box, "", addSpace=True, orientation="vertical", height=110)
        # self.image_plane_box_empty = oasysgui.widgetBox(screen_box, "", addSpace=True, orientation="vertical", height=110)
        #
        # oasysgui.lineEdit(self.image_plane_box, self, "image_plane_new_position", "Image Plane new Position", labelWidth=220, valueType=float, orientation="horizontal")
        #
        # gui.comboBox(self.image_plane_box, self, "image_plane_rel_abs_position", label="Position Type", labelWidth=250,
        #              items=["Absolute", "Relative"], sendSelectedValue=False, orientation="horizontal")
        #
        # self.set_ImagePlane()

        gui.separator(self.controlArea, height=200)

        tabs_setting = oasysgui.tabWidget(self.mainArea)
        tabs_setting.setFixedHeight(self.IMAGE_HEIGHT+5)
        tabs_setting.setFixedWidth(self.IMAGE_WIDTH)


        tab_scan = oasysgui.createTabPage(tabs_setting, "Wavefront")
        self.image_box = gui.widgetBox(tab_scan, "Scan", addSpace=True, orientation="vertical")
        self.image_box.setFixedHeight(self.IMAGE_HEIGHT-30)
        self.image_box.setFixedWidth(self.IMAGE_WIDTH-20)

        tab_scan_intensity = oasysgui.createTabPage(tabs_setting, "Intensity")
        self.image_box_intensity = gui.widgetBox(tab_scan_intensity, "Scan", addSpace=True, orientation="vertical")
        self.image_box_intensity.setFixedHeight(self.IMAGE_HEIGHT-30)
        self.image_box_intensity.setFixedWidth(self.IMAGE_WIDTH-20)

        tab_info = oasysgui.createTabPage(tabs_setting, "Info")
        self.focnewInfo = oasysgui.textArea(height=self.IMAGE_HEIGHT-35)
        info_box = oasysgui.widgetBox(tab_info, "", addSpace=True, orientation="horizontal", height = self.IMAGE_HEIGHT-20, width = self.IMAGE_WIDTH-20)
        info_box.layout().addWidget(self.focnewInfo)

    def set_XRange(self):
        self.xrange_box.setVisible(self.x_range == 1)
        self.xrange_box_empty.setVisible(self.x_range == 0)

    def set_ZRange(self):
        self.zrange_box.setVisible(self.z_range == 1)
        self.zrange_box_empty.setVisible(self.z_range == 0)

    def set_ImagePlane(self):
        self.image_plane_box.setVisible(self.image_plane==1)
        self.image_plane_box_empty.setVisible(self.image_plane==0)

    def setBeam(self, beam):
        if ShadowCongruence.checkEmptyBeam(beam):
            if ShadowCongruence.checkGoodBeam(beam):
                self.input_beam = beam

                if self.is_automatic_run:
                    self.calculate()
            else:
                QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data not displayable: No good rays or bad content",
                                           QtWidgets.QMessageBox.Ok)
    def get_shadow3_beam(self):
        if ShadowCongruence.checkEmptyBeam(self.input_beam):
            if ShadowCongruence.checkGoodBeam(self.input_beam):

                beam_to_analize = self.input_beam._beam

                # if self.image_plane == 1:
                #     new_shadow_beam = self.input_beam.duplicate(history=False)
                #     dist = 0.0
                #
                #     if self.image_plane_rel_abs_position == 1:  # relative
                #         dist = self.image_plane_new_position
                #     else:  # absolute
                #         historyItem = self.input_beam.getOEHistory(oe_number=self.input_beam._oe_number)
                #
                #         if historyItem is None: image_plane = 0.0
                #         elif self.input_beam._oe_number == 0: image_plane = 0.0
                #         else: image_plane = historyItem._shadow_oe_end._oe.T_IMAGE
                #
                #         dist = self.image_plane_new_position - image_plane
                #
                #     new_shadow_beam._beam.retrace(dist)
                #
                #     beam_to_analize = new_shadow_beam._beam
                #
                return beam_to_analize

    def wavefront_from_slopes(self,_beam,Nx=101,Nz=101,xrange=None,zrange=None,):

        # extract data (position and angles)
        x1 = _beam.getshonecol(1)
        z1 = _beam.getshonecol(3)
        xp = _beam.getshonecol(4)
        zp = _beam.getshonecol(6)

        # from the angles, extract magnitude and direction
        slo = np.sqrt(xp**2+zp**2)
        ang = np.arctan2(zp,xp)

        # interpolare on a linear grid to allow easier processing
        if xrange is None:
            xrange = [np.min(x1), np.max(x1)]
        if zrange is None:
            zrange = [np.min(z1), np.max(z1)]

        x_lin = np.linspace(xrange[0],xrange[1], Nx)
        z_lin = np.linspace(zrange[0],zrange[1], Nz)

        X, Z = np.meshgrid(x_lin,z_lin,indexing='ij')
        slopes = interpolate.griddata((x1,z1),slo,(X,Z),method='linear')
        angles = interpolate.griddata((x1,z1),ang,(X,Z),method='linear')

        # compute the gradients
        grad_x = slopes * np.cos(angles)
        grad_z = slopes * np.sin(angles)

        # integrate the gradients (from the center) to get the wavefront
        zH = Nz//2
        zM = zH + 1
        zr = np.cumsum(-grad_z[:,zM: 0:-1],axis=1)
        zl = np.cumsum( grad_z[:,zH:-1: 1],axis=1)
        zz = np.concatenate((np.flip(zr,axis=1),zl),axis=1)

        xH = Nx//2
        xM = xH + 1
        xr = np.cumsum(-grad_x[xM: 0:-1,:],axis=0)
        xl = np.cumsum( grad_x[xH:-1: 1,:],axis=0)
        xx = np.concatenate((np.flip(xr,axis=0),xl),axis=0)

        # here's the wavefront (the units depend of the backprogation distance)
        wfe_au = (xx+zz)

        wfe_au = np.nan_to_num(wfe_au)

        return wfe_au, x_lin, z_lin

    def wavefront_from_optical_path(self,_beam,Nx=101,Nz=101,xrange=None,zrange=None):

        # get the rays and their optical path
        x1 = _beam.getshonecol(1)
        z1 = _beam.getshonecol(3)
        path1 = _beam.getshonecol(13)

        # interpolare on a linear grid to allow easier processing

        if xrange is None:
            xrange = [np.min(x1), np.max(x1)]
        if zrange is None:
            zrange = [np.min(z1), np.max(z1)]

        x_lin = np.linspace(xrange[0],xrange[1], Nx)
        z_lin = np.linspace(zrange[0],zrange[1], Nz)
        X, Z = np.meshgrid(x_lin,z_lin,indexing='ij')

        wfe1 = interpolate.griddata((x1,z1),path1,(X,Z),method='linear')

        #removal of piston
        wfe_um = (wfe1-np.nanmean(wfe1))*1e6

        wfe_um = np.nan_to_num(wfe_um)
        return wfe_um, x_lin, z_lin

    def wavefront_intensity(self,_beam,Nx=101,Nz=101,xrange=None,zrange=None):

        # get the rays and their optical path
        x1 = _beam.getshonecol(1)
        z1 = _beam.getshonecol(3)

        # interpolare on a linear grid to allow easier processing

        if xrange is None:
            xrange = [np.min(x1), np.max(x1)]
        if zrange is None:
            zrange = [np.min(z1), np.max(z1)]

        ticket = _beam.histo2(1,3,ref=23,nbins_h=Nx,nbins_v=Nz,nolost=1,xrange=xrange,yrange=zrange)

        return ticket['histogram'],ticket['bin_h_center'],ticket['bin_v_center']

    def calculate(self):

        beam_to_analize = self.get_shadow3_beam()

        if beam_to_analize is None:
            print("No SHADOW Beam")
            return

        if beam_to_analize is None:
            return

        if self.x_range == 1:
            if self.x_range_min >= self.x_range_max:
                raise Exception("X range min cannot be greater or than X range max")
            else:
                xrange = [self.x_range_min*1e-6,self.x_range_max*1e-6]
        else:
            xrange = None


        if self.z_range == 1:
            if self.z_range_min >= self.z_range_max:
                raise Exception("Y range min cannot be greater or than Y range max")
            else:
                zrange = [self.z_range_min*1e-6,self.z_range_max*1e-6]
        else:
            zrange = None


        if self.mode ==0:
            im, x, y = self.wavefront_from_slopes(beam_to_analize,Nx=self.x_npoints,Nz=self.z_npoints,
                                                  xrange=xrange,zrange=zrange)
            title="Wavefront phase calculated from slopes"
        elif self.mode == 1:
            im, x, y = self.wavefront_from_optical_path(beam_to_analize,Nx=self.x_npoints,Nz=self.z_npoints,
                                                xrange=xrange,zrange=zrange)
            title="Wavefront phase calculated from optical path"

        h,hx,hy = self.wavefront_intensity(beam_to_analize,Nx=self.x_npoints,Nz=self.z_npoints,
                                                  xrange=xrange,zrange=zrange)

        try:
            print("\nResult arrays (shapes): ", im.shape, x.shape, y.shape )
            self.plot_data2D(self.image_box,
                             im, x*1e6, y*1e6,
                             title=title,xtitle="X [um] (%d pixels)"%x.size,ytitle="Z [um] (%d pixels)"%y.size,)
            self.plot_data2D(self.image_box_intensity,
                             h, hx*1e6, hy*1e6,
                             title="Intensity",
                             xtitle="X [um] (%d pixels)"%x.size,ytitle="Z [um] (%d pixels)"%y.size,)
            self.focnewInfo.setText("This is the info for a new run\n############################\n\n\n")
        except Exception as e:
            raise Exception("Data not plottable: bad content\n" + str(e))


    def plot_data2D(self, image_box, data2D, dataX, dataY, title="", xtitle="", ytitle=""):

        origin = (dataX[0],dataY[0])
        scale = (dataX[1]-dataX[0],dataY[1]-dataY[0])

        colormap = {"name":"temperature", "normalization":"linear", "autoscale":True, "vmin":0, "vmax":0, "colors":256}

        plot_canvas = Plot2D()
        plot_canvas.resetZoom()
        plot_canvas.setXAxisAutoScale(True)
        plot_canvas.setYAxisAutoScale(True)
        plot_canvas.setGraphGrid(False)
        plot_canvas.setKeepDataAspectRatio(True)
        plot_canvas.yAxisInvertedAction.setVisible(False)
        plot_canvas.setXAxisLogarithmic(False)
        plot_canvas.setYAxisLogarithmic(False)
        plot_canvas.getMaskAction().setVisible(False)
        plot_canvas.getRoiAction().setVisible(False)
        plot_canvas.getColormapAction().setVisible(False)
        plot_canvas.setKeepDataAspectRatio(False)
        #
        #
        #
        plot_canvas.addImage(data2D.T,
                                     legend="",
                                     scale=scale,
                                     origin=origin,
                                     colormap=colormap,
                                     replace=True)
        plot_canvas.setActiveImage("")
        plot_canvas.setGraphXLabel(xtitle)
        plot_canvas.setGraphYLabel(ytitle)
        plot_canvas.setGraphTitle(title)
        try:
            image_box.layout().removeItem(image_box.layout().itemAt(0))
        except:
            pass
        image_box.layout().addWidget(plot_canvas)

    def writeStdOut(self, text):
        cursor = self.shadow_output.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.insertText(text)
        self.shadow_output.setTextCursor(cursor)
        self.shadow_output.ensureCursorVisible()


if __name__ == "__main__":
    import sys
    import Shadow

    class MyBeam():
        pass
    beam_to_analize = Shadow.Beam()
    beam_to_analize.load("/Users/srio/Oasys/wfr.01")
    my_beam = MyBeam()
    my_beam._beam = beam_to_analize

    a = QApplication(sys.argv)
    ow = ALSWavefrontGenerator()
    ow.show()
    ow.input_beam = my_beam
    a.exec_()
    ow.saveSettings()

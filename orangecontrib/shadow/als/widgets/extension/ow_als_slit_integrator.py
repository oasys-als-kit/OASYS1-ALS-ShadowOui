from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui

from orangecontrib.shadow.util.shadow_objects import ShadowBeam
from orangecontrib.shadow.util.shadow_util import ShadowCongruence, ShadowPlot
from orangecontrib.shadow.widgets.gui import ow_automatic_element
from orangecontrib.shadow.als.widgets.gui.plots import plot_data1D, plot_data2D

import numpy

class ALSSlitIntegrator(ow_automatic_element.AutomaticElement):

    name = "ALS Slit Integrator"
    description = "Shadow: ALS Slit Integrator"
    icon = "icons/integral.png"
    maintainer = "APS team"
    maintainer_email = "srio@lbl.gov"
    priority = 6
    category = "Data Display Tools"
    keywords = ["data", "file", "load", "read"]

    inputs = [("Input Beam 1", ShadowBeam, "setBeam1"),("Input Beam 2", ShadowBeam, "setBeam2")]

    IMAGE_WIDTH = 860
    IMAGE_HEIGHT = 675

    want_main_area=1
    want_control_area = 1

    input_beam1=None
    input_beam2 = None

    normalize = Setting(0)
    slit_type = Setting(0) # 0=round, 1=square
    npoints_x = Setting(1000) # in X and Z
    no_lost  = Setting(1)



    def __init__(self, show_automatic_box=True):
        super().__init__()

        gui.button(self.controlArea, self, "Calculate", callback=self.calculate, height=45)

        general_box = oasysgui.widgetBox(self.controlArea, "General Settings", addSpace=True, orientation="vertical",
                                         width=self.CONTROL_AREA_WIDTH-8, height=400)


        gui.comboBox(general_box, self, "no_lost", label="Rays",labelWidth=220,
                                     items=["All rays","Good only","Lost only"],
                                     sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(general_box, self, "slit_type", label="Slit type",labelWidth=220,
                                     items=["Round","Square","Rectangular H opening","Rectangular V opening"],
                                     sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(general_box, self, "normalize", label="Normalize results",labelWidth=220,
                                     items=["No","Yes"],
                                     sendSelectedValue=False, orientation="horizontal")


        oasysgui.lineEdit(general_box, self, "npoints_x", "Points", labelWidth=260, valueType=int,orientation="horizontal")

        gui.separator(self.controlArea, height=200)

        tabs_setting = oasysgui.tabWidget(self.mainArea)
        tabs_setting.setFixedHeight(self.IMAGE_HEIGHT+5)
        tabs_setting.setFixedWidth(self.IMAGE_WIDTH)


        tmp = oasysgui.createTabPage(tabs_setting, "Cumulated Intensity")
        self.image_box = gui.widgetBox(tmp, "", addSpace=True, orientation="vertical")
        self.image_box.setFixedHeight(self.IMAGE_HEIGHT-30)
        self.image_box.setFixedWidth(self.IMAGE_WIDTH-20)

        tmp = oasysgui.createTabPage(tabs_setting, "Info")
        self.info_id = oasysgui.textArea(height=self.IMAGE_HEIGHT-35)
        info_box = oasysgui.widgetBox(tmp, "", addSpace=True, orientation="horizontal", height = self.IMAGE_HEIGHT-20, width = self.IMAGE_WIDTH-20)
        info_box.layout().addWidget(self.info_id)


    def setBeam1(self, beam):
        if ShadowCongruence.checkEmptyBeam(beam):
            if ShadowCongruence.checkGoodBeam(beam):
                self.input_beam1 = beam

                if self.is_automatic_run:
                    self.calculate()
            else:
                QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data not displayable: No good rays or bad content",
                                           QtWidgets.QMessageBox.Ok)

    def setBeam2(self, beam):
        if ShadowCongruence.checkEmptyBeam(beam):
            if ShadowCongruence.checkGoodBeam(beam):
                self.input_beam2 = beam

                if self.is_automatic_run:
                    self.calculate()
            else:
                QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data not displayable: No good rays or bad content",
                                           QtWidgets.QMessageBox.Ok)

    def get_shadow3_beam1(self):
        if ShadowCongruence.checkEmptyBeam(self.input_beam1):
            if ShadowCongruence.checkGoodBeam(self.input_beam1):
                beam_to_analize = self.input_beam1._beam
                return beam_to_analize

    def get_shadow3_beam2(self):
        if ShadowCongruence.checkEmptyBeam(self.input_beam2):
            if ShadowCongruence.checkGoodBeam(self.input_beam2):
                beam_to_analize = self.input_beam2._beam
                return beam_to_analize

    def calculate_curve(self,beam_to_analize):
        col = 20
        tkt = beam_to_analize.histo1(col, nbins=self.npoints_x, nolost=self.no_lost, ref=23)
        self.image_box.layout().removeItem(self.image_box.layout().itemAt(0))
        xh = tkt["bin_center"]
        yh = tkt["histogram"].cumsum()
        if self.normalize:
            ymax = beam_to_analize.intensity(nolost=self.no_lost)
            yh /= ymax
            self.writeStdOut("\n\nPlot normalized to intensity value of: %f" % ymax)

        irepeated = numpy.argwhere(yh == yh[-1])
        if len(irepeated) > 1:
            xh = xh[0:(irepeated[1][0])]
            yh = yh[0:(irepeated[1][0])]

        return xh,yh

    def calculate(self):

        self.writeStdOut("",initialize=True)
        beam_to_analize1 = self.get_shadow3_beam1()
        beam_to_analize2 = self.get_shadow3_beam2()

        if beam_to_analize1 is None:
            print("No SHADOW Beam")
            return

        xh,yh = self.calculate_curve(beam_to_analize1)

        if beam_to_analize2 is not None:
            xh2, yh2 = self.calculate_curve(beam_to_analize2)
        else:
            xh2 = None
            yh2 = None

        if self.normalize:
            normalized_text = "normalized"
        else:
            normalized_text = ""
        plot_widget_id = plot_data1D(xh,yh,xh2,yh2,title="",xtitle="Radius",ytitle="Cumulated %s intensity"%normalized_text)
        self.image_box.layout().removeItem(self.image_box.layout().itemAt(0))
        self.image_box.layout().addWidget(plot_widget_id)


    def writeStdOut(self, text, initialize=True):
        cursor = self.info_id.textCursor()
        if initialize:
            self.info_id.setText(text)
        else:
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertText(text)
            self.info_id.setTextCursor(cursor)
            self.info_id.ensureCursorVisible()

if __name__ == "__main__":
    import sys
    import Shadow

    class MyBeam():
        pass
    beam_to_analize = Shadow.Beam()
    beam_to_analize.load("/home/manuel/Oasys/tmp.dat") #star.02")
    my_beam = MyBeam()
    my_beam._beam = beam_to_analize

    a = QApplication(sys.argv)
    ow = ALSSlitIntegrator()
    ow.setBeam1(my_beam)
    ow.show()
    a.exec_()
    ow.saveSettings()

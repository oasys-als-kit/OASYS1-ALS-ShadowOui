import numpy

from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor, QFont
from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence
from orangewidget import widget
from Shadow import ShadowTools as ST
from silx.gui.plot.StackView import StackViewMainWindow


from orangecontrib.shadow.util.shadow_util import ShadowCongruence, ShadowPhysics
from orangecontrib.shadow.util.shadow_objects import ShadowBeam
from orangecontrib.shadow.als.widgets.gui.ow_als_shadow_widget import ALSShadowWidget

class ALSGenericAnalyzer(ALSShadowWidget):

    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    category = "Utility"
    keywords = ["data", "file", "load", "read"]

    inputs = [("Input Beam", ShadowBeam, "setBeam")]

    IMAGE_WIDTH = 860
    IMAGE_HEIGHT = 545

    input_beam = None

    def __init__(self, show_automatic_box=True):
        super().__init__(show_automatic_box=show_automatic_box)

        self.runaction = widget.OWAction("Analyze OE Parameters", self)
        self.runaction.triggered.connect(self.analyze)
        self.addAction(self.runaction)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Analyze OE Parameters", callback=self.analyze)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)

        button = gui.button(button_box, self, "Reset Fields", callback=self.callResetSettings)
        font = QFont(button.font())
        font.setItalic(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Red'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)
        button.setFixedWidth(150)

        gui.separator(self.controlArea)

        ######################################

        self.controlArea.setFixedWidth(self.CONTROL_AREA_WIDTH)

        tabs_setting = oasysgui.tabWidget(self.controlArea)
        tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT)
        tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)

        self.tab_analysis = oasysgui.createTabPage(tabs_setting, "Analysis Setting")


        ######################################

        self.main_tabs = oasysgui.tabWidget(self.mainArea)
        plot_tab = oasysgui.createTabPage(self.main_tabs, "Plots")
        out_tab = oasysgui.createTabPage(self.main_tabs, "Output")

        self.tab = []
        self.tabs = oasysgui.tabWidget(plot_tab)

        self.initializeTabs()

        self.shadow_output = oasysgui.textArea(height=600, width=600)

        out_box = gui.widgetBox(out_tab, "System Output", addSpace=True, orientation="horizontal")
        out_box.layout().addWidget(self.shadow_output)

    def initializeTabs(self):
        current_tab = self.tabs.currentIndex()

        size = len(self.tab)
        indexes = range(0, size)
        for index in indexes:
            self.tabs.removeTab(size-1-index)

        titles = self.getTitles()

        self.tab = [oasysgui.createTabPage(self.tabs, titles[0]),
                    oasysgui.createTabPage(self.tabs, titles[1]),
                    oasysgui.createTabPage(self.tabs, titles[2]),
                    oasysgui.createTabPage(self.tabs, titles[3])
        ]

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)

        self.plot_canvas = [None, None, None, None, None]

        self.tabs.setCurrentIndex(current_tab)


    def setBeam(self, beam):
        self.onReceivingInput()

        if ShadowCongruence.checkEmptyBeam(beam):
            self.input_beam = beam

            if self.is_automatic_run:
                self.analyze()


    def analyze(self):
        # TO ACCESS THE OPTICAL ELEMENT THAT GENERATE THE BEAM AT THIS IMAGE PLANE
        # YOU NEED TO SURF THE HISTORY OF THE BEAM
        oe_number = self.input_beam._oe_number
        history_element = self.input_beam.getOEHistory(oe_number)

        # SHADOWOUI OBJECTS: WRAPPERS OF THE NATIVE SHADOW3 OBJECTS
        shadowOui_input_beam = history_element._input_beam
        shadowOui_OE_before_tracing = history_element._shadow_oe_start
        shadowOui_OE_after_tracing = history_element._shadow_oe_end

        scanned_values = self.create_scanned_values(shadowOui_OE_before_tracing._oe, shadowOui_OE_after_tracing._oe)
        auxiliary_data = self.create_auxiliary_data(shadowOui_OE_before_tracing._oe, shadowOui_OE_after_tracing._oe)

        x_min, x_max, z_min, z_max, nbins = self.get_plot_ranges()

        stack_result = numpy.zeros((len(scanned_values), nbins, nbins))
        fwhms_h =  numpy.zeros(len(scanned_values))
        fwhms_v =  numpy.zeros(len(scanned_values))
        best_focus_positions = numpy.zeros(len(scanned_values))

        for index in range(0, len(scanned_values)):

            # NATIVE SHADOW3 OBJECTS
            # MAKE A DUPLICATE TO BE SURE TO NOT AFFECT THE REST OF SHADOWOUI SIMULATION!
            shadow3_beam = shadowOui_input_beam.duplicate(copy_rays=True, history=False)._beam # KEEP THE ORIGINAL UNTOUCHED
            shadow3_OE_before   = shadowOui_OE_before_tracing.duplicate()._oe                         # KEEP THE ORIGINAL UNTOUCHED

            self.modify_OE(shadow3_OE_before, scanned_values[index], auxiliary_data)

            shadow3_beam.traceOE(shadow3_OE_before, oe_number) #

            # 2D DISTRIBUTION X,Z TO OBTAIN THE FOCAL SPOT DIMENSION
            ticket2D = shadow3_beam.histo2(col_h=1, col_v=3, nbins=nbins, ref=23, xrange=[x_min, x_max], yrange=[z_min, z_max])

            histogram = ticket2D["histogram"]
            fwhms_h[index] = ticket2D["fwhm_h"]
            fwhms_v[index] = ticket2D["fwhm_v"]

            for ix in range(nbins):
                for iz in range(nbins):
                     stack_result[index, ix, iz] = histogram[ix, iz]

            # FOCUS POSITION
            ticketFocus = ST.focnew(shadow3_beam, mode=0, center=[0.0, 0.0])

            best_focus_positions[index] = ticketFocus['z_waist']

        self.plot_data3D(0, stack_result, scanned_values, numpy.linspace(x_min, x_max, nbins)*self.workspace_units_to_m*1e6, numpy.linspace(z_min, z_max, nbins)*self.workspace_units_to_m*1e6,
                                                                                    self.getTitles()[0], self.getXTitles()[0], self.getYTitles()[0])
        self.plot_data1D(1,  scanned_values, fwhms_h*self.workspace_units_to_m*1e6, self.getTitles()[1], self.getXTitles()[1], self.getYTitles()[1])
        self.plot_data1D(2,  scanned_values, fwhms_v*self.workspace_units_to_m*1e6, self.getTitles()[2], self.getXTitles()[2], self.getYTitles()[2])
        self.plot_data1D(3,  scanned_values, best_focus_positions,                  self.getTitles()[3], self.getXTitles()[3], self.getYTitles()[3])

    def get_plot_ranges(self):
        raise NotImplementedError()

    def create_scanned_values(self, shadow_OE_before_tracing, shadow_OE_after_tracing):
        raise NotImplementedError()

    def create_auxiliary_data(self, shadow_OE_before_tracing, shadow_OE_after_tracing):
        raise NotImplementedError()

    def modify_OE(self, shadow_OE, scanned_value, auxiliary_data=None):
        raise NotImplementedError()

    def plot_data1D(self, plot_canvas_index, dataX, dataY, title="", xtitle="", ytitle=""):

        if self.plot_canvas[plot_canvas_index] is None:
            self.plot_canvas[plot_canvas_index] = oasysgui.plotWindow()
            self.tab[plot_canvas_index].layout().addWidget(self.plot_canvas[plot_canvas_index])

        self.plot_canvas[plot_canvas_index].addCurve(dataX, dataY, replace=True)

        self.plot_canvas[plot_canvas_index].resetZoom()
        self.plot_canvas[plot_canvas_index].setXAxisAutoScale(True)
        self.plot_canvas[plot_canvas_index].setYAxisAutoScale(True)
        self.plot_canvas[plot_canvas_index].setGraphGrid(False)

        self.plot_canvas[plot_canvas_index].setXAxisLogarithmic(False)
        self.plot_canvas[plot_canvas_index].setYAxisLogarithmic(False)
        self.plot_canvas[plot_canvas_index].setGraphXLabel(xtitle)
        self.plot_canvas[plot_canvas_index].setGraphYLabel(ytitle)
        self.plot_canvas[plot_canvas_index].setGraphTitle(title)

    def plot_data3D(self, plot_canvas_index, data3D, dataScan, dataX, dataY, title="", xtitle="", ytitle=""):

        if self.plot_canvas[plot_canvas_index] is None:
            self.plot_canvas[plot_canvas_index] = StackViewMainWindow()
            self.tab[plot_canvas_index].layout().addWidget(self.plot_canvas[plot_canvas_index])

        xmin = numpy.min(dataX)
        ymin = numpy.min(dataY)

        stepX = dataX[1]-dataX[0]
        stepY = dataY[1]-dataY[0]
        if len(dataScan) > 1: stepScan = dataScan[1]-dataScan[0]
        else: stepScan = 1.0

        if stepScan == 0.0: stepScan = 1.0
        if stepX == 0.0: stepX = 1.0
        if stepY == 0.0: stepY = 1.0

        dim0_calib = (dataScan[0], stepScan)
        dim1_calib = (ymin, stepY)
        dim2_calib = (xmin, stepX)

        data_to_plot = numpy.swapaxes(data3D,1,2)

        colormap = {"name":"temperature", "normalization":"linear", "autoscale":True, "vmin":0, "vmax":0, "colors":256}

        self.plot_canvas[plot_canvas_index].setGraphTitle(title)
        self.plot_canvas[plot_canvas_index].setLabels(["Scanned Variable", ytitle, xtitle])
        self.plot_canvas[plot_canvas_index].setColormap(colormap=colormap)
        self.plot_canvas[plot_canvas_index].setStack(numpy.array(data_to_plot), calibrations=[dim0_calib, dim1_calib, dim2_calib] )


    def onReceivingInput(self):
        self.initializeTabs()

    def getTitles(self):
        return ["Scanned Variable, X,Z Spot", "Scanned Variable, X Spot Size", "Scanned Variable, Z Spot Size", "Scanned Variable, Focus Distance"]

    def getXTitles(self):
        return [r'X [$\mu$m]', "Scanned Variable", "Scanned Variable", "Scanned Variable"]

    def getYTitles(self):
        return [r'Z [$\mu$m]', "FWHM X [$\mu$m]", "FWHM Z [$\mu$m]", "Focus Distance [" + self.workspace_units_label + "]"]

    def getXUM(self):
        return ["X [" + u"\u03BC" + "m]", "Scanned Variable", "Scanned Variable", "Scanned Variable"]

    def getYUM(self):
        return ["Z [" + u"\u03BC" + "m]", "X [" + u"\u03BC" + "m]", "Z [" + u"\u03BC" + "m]", "Focus Distance [" + self.workspace_units_label + "]"]

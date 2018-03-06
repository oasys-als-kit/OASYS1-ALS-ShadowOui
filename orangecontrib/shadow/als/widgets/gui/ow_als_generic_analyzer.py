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
from silx.gui.plot import Plot2D
from silx.gui.plot.StackView import StackViewMainWindow


from orangecontrib.shadow.util.shadow_util import ShadowCongruence, ShadowPlot
from orangecontrib.shadow.util.shadow_objects import ShadowBeam
from orangecontrib.shadow.als.widgets.gui.ow_als_shadow_widget import ALSShadowWidget

class ALSGenericAnalyzer(ALSShadowWidget):

    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    category = "Utility"
    keywords = ["data", "file", "load", "read"]

    inputs = [("Input Beam", ShadowBeam, "setBeam")]

    IMAGE_WIDTH = 860
    IMAGE_HEIGHT = 540

    input_beam = None
    widget_name = None

    x_min = Setting(-0.005)
    x_max = Setting(0.005)
    z_min = Setting(-0.005)
    z_max = Setting(0.005)
    n_bins = Setting(501)
    
    variable_to_change = Setting(0)
    current_value = ""
    
    v_min = Setting(-0.001)
    v_max = Setting(0.001)
    n_points = Setting(21)

    image_plane=Setting(0)
    image_plane_new_position=Setting(10.0)
    image_plane_rel_abs_position=Setting(0)

    def __init__(self, show_automatic_box=False):
        super().__init__(show_automatic_box=show_automatic_box)

        self.general_options_box.setVisible(False)

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

        self.oe_settings_box = oasysgui.widgetBox(self.tab_analysis, self.get_OE_name() + " Setting", addSpace=False, orientation="vertical")

        self.cb_variable_to_change =  gui.comboBox(self.oe_settings_box, self, "variable_to_change", label="Variable to Change", labelWidth=150,
                                                   items=self.get_variables_to_change_list(), sendSelectedValue=False, orientation="horizontal", callback=self.set_current_value)

        self.le_current_value = oasysgui.lineEdit(self.oe_settings_box, self, "current_value", "Current Value", labelWidth=100, valueType=str, orientation="horizontal")
        self.le_current_value.setReadOnly(True)
        font = QFont(self.le_current_value.font())
        font.setBold(True)
        self.le_current_value.setFont(font)
        palette = QPalette(self.le_current_value.palette())
        palette.setColor(QPalette.Text, QColor('dark blue'))
        palette.setColor(QPalette.Base, QColor(243, 240, 160))
        self.le_current_value.setPalette(palette)
        
        gui.separator(self.oe_settings_box)
        
        oasysgui.lineEdit(self.oe_settings_box, self, "v_min",    "Scanning value min", labelWidth=250, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.oe_settings_box, self, "v_max",    "Scanning value max", labelWidth=250, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.oe_settings_box, self, "n_points", "Nr. Points", labelWidth=250, valueType=float, orientation="horizontal")
        
        left_box_1 = oasysgui.widgetBox(self.tab_analysis, "Plots Setting", addSpace=False, orientation="vertical")

        self.le_x_min = oasysgui.lineEdit(left_box_1, self, "x_min", "X min", labelWidth=250, valueType=float, orientation="horizontal")
        self.le_x_max = oasysgui.lineEdit(left_box_1, self, "x_max", "X max", labelWidth=250, valueType=float, orientation="horizontal")
        self.le_z_min = oasysgui.lineEdit(left_box_1, self, "z_min", "Z min", labelWidth=250, valueType=float, orientation="horizontal")
        self.le_z_max = oasysgui.lineEdit(left_box_1, self, "z_max", "Z max", labelWidth=250, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(left_box_1, self, "n_bins", "Nr. bins", labelWidth=250, valueType=int, orientation="horizontal")

        screen_box = oasysgui.widgetBox(self.tab_analysis, "Screen Position Settings", addSpace=False, orientation="vertical", height=180)

        self.image_plane_combo = gui.comboBox(screen_box, self, "image_plane", label="Position of the Image",
                                            items=["On Image Plane", "Retraced"], labelWidth=260,
                                            callback=self.set_ImagePlane, sendSelectedValue=False, orientation="horizontal")

        self.image_plane_box = oasysgui.widgetBox(screen_box, "", addSpace=True, orientation="vertical", height=80)
        self.image_plane_box_empty = oasysgui.widgetBox(screen_box, "", addSpace=True, orientation="vertical", height=80)

        oasysgui.lineEdit(self.image_plane_box, self, "image_plane_new_position", "Image Plane new Position", labelWidth=220, valueType=float, orientation="horizontal")

        gui.comboBox(self.image_plane_box, self, "image_plane_rel_abs_position", label="Position Type", labelWidth=250,
                     items=["Absolute", "Relative"], sendSelectedValue=False, orientation="horizontal")

        self.set_ImagePlane()

        gui.button(screen_box, self, "Refresh Input Beam", callback=self.refresh_input_beam)


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

    def after_change_workspace_units(self):
        label = self.le_x_min.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [" + self.workspace_units_label + "]")
        label = self.le_x_max.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [" + self.workspace_units_label + "]")
        label = self.le_z_min.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [" + self.workspace_units_label + "]")
        label = self.le_z_max.parent().layout().itemAt(0).widget()
        label.setText(label.text() + " [" + self.workspace_units_label + "]")

    def set_ImagePlane(self):
        self.image_plane_box.setVisible(self.image_plane==1)
        self.image_plane_box_empty.setVisible(self.image_plane==0)

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
                    oasysgui.createTabPage(self.tabs, titles[3]),
                    oasysgui.createTabPage(self.tabs, titles[4]),
                    oasysgui.createTabPage(self.tabs, titles[5])
        ]

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)

        self.plot_canvas = [None, None, None, None, None, None]

        self.tabs.setCurrentIndex(current_tab)


    def setBeam(self, beam):
        try:
            self.onReceivingInput()

            if ShadowCongruence.checkEmptyBeam(beam):
                self.input_beam = beam

                self.refresh_input_beam()
                self.complete_input_form()
                self.set_current_value()

        except Exception as exception:
            QtWidgets.QMessageBox.critical(self, "Error", str(exception), QtWidgets.QMessageBox.Ok)

            self.setStatusMessage("Error!")

    def refresh_input_beam(self):
        beam_to_plot = self.input_beam._beam
        if self.image_plane == 1:
            new_shadow_beam = self.input_beam.duplicate(history=False)

            if self.image_plane_rel_abs_position == 1:  # relative
                dist = self.image_plane_new_position
            else:  # absolute
                historyItem = self.input_beam.getOEHistory(oe_number=self.input_beam._oe_number)

                if historyItem is None:
                    image_plane = 0.0
                elif self.input_beam._oe_number == 0:
                    image_plane = 0.0
                else:
                    image_plane = historyItem._shadow_oe_end._oe.T_IMAGE

                dist = self.image_plane_new_position - image_plane

            new_shadow_beam._beam.retrace(dist)

            beam_to_plot = new_shadow_beam._beam
        ShadowPlot.set_conversion_active(False)
        self.plot_data2D(0, beam_to_plot, 1, 3, 100, self.getTitles()[0], self.getXTitles()[0], self.getYTitles()[0])
        ShadowPlot.set_conversion_active(True)
        self.tabs.setCurrentIndex(0)

    def complete_input_form(self):
        pass

    def check_fields(self):
        congruence.checkNumber(self.x_min, "X min")
        congruence.checkNumber(self.x_max, "X max")
        congruence.checkNumber(self.z_min, "Z min")
        congruence.checkNumber(self.z_max, "Z max")
        congruence.checkGreaterThan(self.x_max, self.x_min, "X max", "X min")
        congruence.checkGreaterThan(self.z_max, self.z_min, "Z max", "Z min")
        congruence.checkStrictlyPositiveNumber(self.n_bins, "Nr. bins")

        congruence.checkGreaterThan(self.v_max, self.v_min, "Scanning value max", "Scanning value min")
        congruence.checkStrictlyPositiveNumber(self.n_points, "Nr. Points")

    def get_shadowOui_objects(self):
        # TO ACCESS THE OPTICAL ELEMENT THAT GENERATE THE BEAM AT THIS IMAGE PLANE
        # YOU NEED TO SURF THE HISTORY OF THE BEAM
        oe_number = self.input_beam._oe_number
        history_element = self.input_beam.getOEHistory(oe_number)

        # SHADOWOUI OBJECTS: WRAPPERS OF THE NATIVE SHADOW3 OBJECTS
        shadowOui_input_beam = history_element._input_beam
        shadowOui_OE_before_tracing = history_element._shadow_oe_start
        shadowOui_OE_after_tracing = history_element._shadow_oe_end
        widget_class_name = history_element._widget_class_name

        return shadowOui_input_beam, oe_number, shadowOui_OE_before_tracing, shadowOui_OE_after_tracing, widget_class_name

    def analyze(self):
        try:
            self.check_fields()

            shadowOui_input_beam, oe_number, shadowOui_OE_before_tracing, shadowOui_OE_after_tracing, widget_class_name = self.get_shadowOui_objects()

            # NEW IMAGE PLANE POSITION
            if self.image_plane == 1:
                if self.image_plane_rel_abs_position == 1:  # relative
                    T_IMAGE = self.image_plane_new_position + shadowOui_OE_after_tracing._oe.T_IMAGE
                else:  # absolute
                    T_IMAGE = self.image_plane_new_position
            else:
                T_IMAGE = shadowOui_OE_after_tracing._oe.T_IMAGE

            scanned_values = self.v_min + numpy.arange(0, self.n_points+1)*numpy.abs((self.v_max-self.v_min)/self.n_points)
            auxiliary_data = self.create_auxiliary_data(shadowOui_OE_before_tracing._oe, shadowOui_OE_after_tracing._oe)

            x_min, x_max, z_min, z_max, n_bins = self.get_plot_ranges()

            stack_result = numpy.zeros((len(scanned_values), n_bins, n_bins))
            fwhms_h =  numpy.zeros(len(scanned_values))
            fwhms_v =  numpy.zeros(len(scanned_values))
            sagittal_focus_positions = numpy.zeros(len(scanned_values))
            tangential_focus_positions = numpy.zeros(len(scanned_values))

            for index in range(0, len(scanned_values)):

                # NATIVE SHADOW3 OBJECTS
                # MAKE A DUPLICATE TO BE SURE TO NOT AFFECT THE REST OF SHADOWOUI SIMULATION!
                shadow3_beam = shadowOui_input_beam.duplicate(copy_rays=True, history=False)._beam # KEEP THE ORIGINAL UNTOUCHED
                shadow3_OE_before   = shadowOui_OE_before_tracing.duplicate()._oe                         # KEEP THE ORIGINAL UNTOUCHED

                self.modify_OE(shadow3_OE_before, scanned_values[index], auxiliary_data)
                shadow3_OE_before.T_IMAGE = T_IMAGE

                shadow3_beam.traceOE(shadow3_OE_before, oe_number) #

                # 2D DISTRIBUTION X,Z TO OBTAIN THE FOCAL SPOT DIMENSION
                self.compute_spatial_distribution(shadow3_beam, stack_result, fwhms_h, fwhms_v, index, n_bins, x_max, x_min, z_max, z_min)

                # FOCUS POSITION
                self.compute_focus_position(shadow3_beam, sagittal_focus_positions, tangential_focus_positions, index)

            factor = self.workspace_units_to_m*1e6

            self.plot_data3D(1,
                             stack_result,
                             scanned_values,
                             numpy.linspace(x_min, x_max, n_bins)*factor,
                             numpy.linspace(z_min, z_max, n_bins)*factor, self.getTitles()[1], self.getXTitles()[1], self.getYTitles()[1])
            self.plot_data1D(2,  scanned_values, fwhms_h*factor,          self.getTitles()[2], self.getXTitles()[2], self.getYTitles()[2])
            self.plot_data1D(3,  scanned_values, fwhms_v*factor,          self.getTitles()[3], self.getXTitles()[3], self.getYTitles()[3])
            self.plot_data1D(4,  scanned_values, sagittal_focus_positions,  self.getTitles()[4], self.getXTitles()[4], self.getYTitles()[4])
            self.plot_data1D(5,  scanned_values, tangential_focus_positions,self.getTitles()[5], self.getXTitles()[5], self.getYTitles()[5])

            self.tabs.setCurrentIndex(1)
        except Exception as exception:
            QtWidgets.QMessageBox.critical(self, "Error", str(exception), QtWidgets.QMessageBox.Ok)

            self.setStatusMessage("Error!")

    def compute_focus_position(self, shadow3_beam, sagittal_focus_positions, tangential_focus_positions, index):
        ticketFocus = ST.focnew(shadow3_beam, mode=0, center=[0.0, 0.0])

        sagittal_focus_positions[index]   = ticketFocus['x_waist']
        tangential_focus_positions[index] = ticketFocus['z_waist']

    def compute_spatial_distribution(self, shadow3_beam, stack_result, fwhms_h, fwhms_v, index, n_bins, x_max, x_min, z_max, z_min):
        ticket2D = shadow3_beam.histo2(1, 3, nbins=n_bins, nolost=1, ref=23, xrange=[x_min, x_max], yrange=[z_min, z_max])

        histogram = ticket2D["histogram"]
        fwhms_h[index] = ticket2D["fwhm_h"]
        fwhms_v[index] = ticket2D["fwhm_v"]

        for x_index in range(0, n_bins):
            for y_index in range(0, n_bins):
                stack_result[index, x_index, y_index] = histogram[y_index][x_index]

    def get_plot_ranges(self):
        return self.x_min, self.x_max, self.z_min, self.z_max, self.n_bins
    
    def get_OE_name(self):
        raise NotImplementedError()
    
    def get_variables_to_change_list(self):
        raise NotImplementedError()
    
    def set_current_value(self):
        if not self.input_beam is None:
            shadowOui_input_beam, oe_number, shadowOui_OE_before_tracing, shadowOui_OE_after_tracing, widget_class_name = self.get_shadowOui_objects()

            self.le_current_value.setText(self.get_current_value(shadowOui_OE_before_tracing._oe, shadowOui_OE_after_tracing._oe))
        else:
            self.le_current_value.setText("")
    
    def get_current_value(self, shadow_OE_before_tracing, shadow_OE_after_tracing):
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
        self.plot_canvas[plot_canvas_index].setGraphGrid(True)

        self.plot_canvas[plot_canvas_index].setXAxisLogarithmic(False)
        self.plot_canvas[plot_canvas_index].setYAxisLogarithmic(False)
        self.plot_canvas[plot_canvas_index].setGraphXLabel(xtitle)
        self.plot_canvas[plot_canvas_index].setGraphYLabel(ytitle)
        self.plot_canvas[plot_canvas_index].setGraphTitle(title)

    def plot_data2D(self, plot_canvas_index, beam_to_plot, var_x, var_y, nbins, title="", xtitle="", ytitle=""):
        if self.plot_canvas[plot_canvas_index] is None:
            self.plot_canvas[plot_canvas_index] = ShadowPlot.DetailedPlotWidget(y_scale_factor=1.14)
            self.tab[plot_canvas_index].layout().addWidget(self.plot_canvas[plot_canvas_index])

        self.plot_canvas[plot_canvas_index].plot_xy(beam_to_plot, var_x, var_y, title, xtitle, ytitle,
                                                    nbins=nbins, conv=self.workspace_units_to_cm, ref=23,
                                                    xum="[" + self.workspace_units_label + "]", yum="[" + self.workspace_units_label + "]")

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

        calibrations=[dim0_calib, dim1_calib, dim2_calib]

        colormap = {"name":"temperature", "normalization":"linear", "autoscale":True, "vmin":0, "vmax":0, "colors":256}

        self.plot_canvas[plot_canvas_index].setGraphTitle(title)
        self.plot_canvas[plot_canvas_index].setLabels(["Scanned Variable", ytitle, xtitle])
        self.plot_canvas[plot_canvas_index].setColormap(colormap=colormap)
        self.plot_canvas[plot_canvas_index].setStack(data3D, calibrations=calibrations)


    def onReceivingInput(self):
        self.initializeTabs()

    def getTitles(self):
        return ["Pristine (X,Z)",
                "(X,Z)",
                "X Spot Size",
                "Z Spot Size",
                "Focus (Sagittal)",
                "Focus (Tangential)"]

    def getXTitles(self):
        return ["X [" + self.workspace_units_label + "]",
                r'X [$\mu$m]',
                "Scanned Variable",
                "Scanned Variable",
                "Scanned Variable",
                "Scanned Variable"]

    def getYTitles(self):
        return ["X [" + self.workspace_units_label + "]",
                r'Z [$\mu$m]',
                "FWHM X [$\mu$m]",
                "FWHM Z [$\mu$m]",
                "Focus Distance [" + self.workspace_units_label + "]",
                "Focus Distance [" + self.workspace_units_label + "]"]

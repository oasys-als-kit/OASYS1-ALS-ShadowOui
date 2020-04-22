__author__ = 'labx'

import numpy

from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QMessageBox
from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui

from orangecontrib.wofry.util.wofry_objects import WofryData
from orangecontrib.wofry.widgets.gui.ow_wofry_widget import WofryWidget


import sys

from orangewidget.widget import OWAction
from oasys.widgets import widget
from oasys.widgets import gui as oasysgui
from oasys.widgets.gui import ConfirmDialog

from orangewidget import gui
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import QMessageBox
from orangewidget.settings import Setting

from oasys.util.oasys_util import TriggerIn, TriggerOut, EmittingStream


from oasys.util.oasys_util import get_fwhm



class OWstepper1D(WofryWidget):

    name = " Generic Wavefront Viewer 1D"
    id = "GenericWavefrontViewer1D"
    description = "Generic Wavefront Viewer 1D"
    icon = "icons/stepper.png"
    priority = 100

    category = "Wofry Tools"
    keywords = ["data", "file", "load", "read"]

    inputs = [("WofryData", WofryData, "set_input"),
              ("Trigger", TriggerIn, "passTrigger")]

    outputs = [{"name":"Trigger",
                "type":TriggerOut,
                "doc":"Trigger",
                "id":"Trigger"}]

    #
    # trigger
    #
    number_of_new_objects = Setting(3)
    current_new_object = 0
    run_loop = True
    suspend_loop = False

    variable_name = Setting("radius")
    variable_display_name = Setting("<variable display name>")
    variable_um = Setting("<u.m.>")

    variable_value_from = Setting(100.0)
    variable_value_to = Setting(1100.0)
    variable_value_step = Setting(100.0)

    list_of_values = Setting([""])
    kind_of_loop = Setting(0)

    current_variable_value = None

    #################################
    process_last = True
    #################################

    #
    # viwer
    #
    wofry_data = None
    accumulated_data = None
    keep_result = Setting(0)
    phase_unwrap = Setting(0)
    titles = ["Wavefront 1D Intensity", "Wavefront 1D Phase",
              "Wavefront Real(Amplitude)","Wavefront Imag(Amplitude)",
              "Scanned peak", "Scanned FWHM"]

    def __init__(self):
        super().__init__(is_automatic=False, show_view_options=True)  #<<<<<<<<<<<<<<<<<<<


        #
        #
        #


        self.controlArea.setFixedWidth(self.CONTROL_AREA_WIDTH)
        tabs_setting = oasysgui.tabWidget(self.controlArea)
        tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT + 50)
        tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)

        #=====================================================================================
        # trigger
        #=====================================================================================

        #
        # trigger
        #
        self.runaction = OWAction("Start", self)
        self.runaction.triggered.connect(self.startLoop)
        self.addAction(self.runaction)

        self.runaction = OWAction("Stop", self)
        self.runaction.triggered.connect(self.stopLoop)
        self.addAction(self.runaction)

        self.runaction = OWAction("Suspend", self)
        self.runaction.triggered.connect(self.suspendLoop)
        self.addAction(self.runaction)

        self.runaction = OWAction("Restart", self)
        self.runaction.triggered.connect(self.restartLoop)
        self.addAction(self.runaction)



        self.tab_trig = oasysgui.createTabPage(tabs_setting, "Stepper/Trigger")


        #
        #

        button_box = oasysgui.widgetBox(self.tab_trig, "", addSpace=True, orientation="horizontal")

        self.start_button = gui.button(button_box, self, "Start", callback=self.startLoop)
        self.start_button.setFixedHeight(35)

        stop_button = gui.button(button_box, self, "Stop", callback=self.stopLoop)
        stop_button.setFixedHeight(35)
        font = QFont(stop_button.font())
        font.setBold(True)
        stop_button.setFont(font)
        palette = QPalette(stop_button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('red'))
        stop_button.setPalette(palette) # assign new palette

        self.stop_button = stop_button

        button_box = oasysgui.widgetBox(self.tab_trig, "", addSpace=True, orientation="horizontal")

        suspend_button = gui.button(button_box, self, "Suspend", callback=self.suspendLoop)
        suspend_button.setFixedHeight(35)
        font = QFont(suspend_button.font())
        font.setBold(True)
        suspend_button.setFont(font)
        palette = QPalette(suspend_button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('orange'))
        suspend_button.setPalette(palette) # assign new palette

        self.re_start_button = gui.button(button_box, self, "Restart", callback=self.restartLoop)
        self.re_start_button.setFixedHeight(35)
        self.re_start_button.setEnabled(False)

        left_box_1 = oasysgui.widgetBox(self.tab_trig, "Loop Management", addSpace=True, orientation="vertical", width=385, height=320)

        oasysgui.lineEdit(left_box_1, self, "variable_name", "Variable Name", labelWidth=100, valueType=str, orientation="horizontal")
        oasysgui.lineEdit(left_box_1, self, "variable_display_name", "Variable Display Name", labelWidth=100, valueType=str, orientation="horizontal")
        oasysgui.lineEdit(left_box_1, self, "variable_um", "Variable Units", labelWidth=250, valueType=str, orientation="horizontal")

        gui.separator(left_box_1)

        gui.comboBox(left_box_1, self, "kind_of_loop", label="Kind of Loop", labelWidth=350,
                     items=["From Range", "From List"],
                     callback=self.set_KindOfLoop, sendSelectedValue=False, orientation="horizontal")

        self.left_box_1_1 = oasysgui.widgetBox(left_box_1, "", addSpace=False, orientation="vertical", width=365, height=100)
        self.left_box_1_2 = oasysgui.widgetBox(left_box_1, "", addSpace=False, orientation="vertical", width=365, height=100)

        oasysgui.lineEdit(self.left_box_1_1, self, "variable_value_from", "Value From", labelWidth=250, valueType=float, orientation="horizontal", callback=self.calculate_step)
        oasysgui.lineEdit(self.left_box_1_1, self, "variable_value_to", "Value to", labelWidth=250, valueType=float, orientation="horizontal", callback=self.calculate_step)
        oasysgui.lineEdit(self.left_box_1_1, self, "number_of_new_objects", "Number of Steps", labelWidth=250, valueType=int, orientation="horizontal", callback=self.calculate_step)

        self.list_of_values_ta = oasysgui.textArea(height=100, width=365, readOnly=False)
        self.list_of_values_ta.textChanged.connect(self.list_of_values_ta_changed)

        text = ""
        for value in self.list_of_values:
            text += value + "\n"

        self.list_of_values_ta.setText(text[:-1])
        self.left_box_1_2.layout().addWidget(self.list_of_values_ta)

        self.le_variable_value_step = oasysgui.lineEdit(self.left_box_1_1, self, "variable_value_step", "Step Value", labelWidth=250, valueType=float, orientation="horizontal")
        self.le_variable_value_step.setReadOnly(True)
        font = QFont(self.le_variable_value_step.font())
        font.setBold(True)
        self.le_variable_value_step.setFont(font)
        palette = QPalette(self.le_variable_value_step.palette()) # make a copy of the palette
        palette.setColor(QPalette.Text, QColor('dark blue'))
        palette.setColor(QPalette.Base, QColor(243, 240, 160))
        self.le_variable_value_step.setPalette(palette)

        self.set_KindOfLoop()

        gui.separator(left_box_1)

        self.le_current_new_object = oasysgui.lineEdit(left_box_1, self, "current_new_object", "Current New " + self.get_object_name(), labelWidth=250, valueType=int, orientation="horizontal")
        self.le_current_new_object.setReadOnly(True)
        font = QFont(self.le_current_new_object.font())
        font.setBold(True)
        self.le_current_new_object.setFont(font)
        palette = QPalette(self.le_current_new_object.palette()) # make a copy of the palette
        palette.setColor(QPalette.Text, QColor('dark blue'))
        palette.setColor(QPalette.Base, QColor(243, 240, 160))
        self.le_current_new_object.setPalette(palette)

        self.le_current_new_object = oasysgui.lineEdit(left_box_1, self, "current_variable_value", "Current Variable Value", labelWidth=250, valueType=float, orientation="horizontal")
        self.le_current_new_object.setReadOnly(True)
        font = QFont(self.le_current_new_object.font())
        font.setBold(True)
        self.le_current_new_object.setFont(font)
        palette = QPalette(self.le_current_new_object.palette()) # make a copy of the palette
        palette.setColor(QPalette.Text, QColor('dark blue'))
        palette.setColor(QPalette.Base, QColor(243, 240, 160))
        self.le_current_new_object.setPalette(palette)






        #=====================================================================================
        # Wavefront
        #=====================================================================================

        self.tab_sou = oasysgui.createTabPage(tabs_setting, "Wavefront Viewer Settings")


        button_box = oasysgui.widgetBox(self.tab_sou, "", addSpace=False, orientation="horizontal")
        button = gui.button(button_box, self, "Refresh", callback=self.refresh)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)


        incremental_box = oasysgui.widgetBox(self.tab_sou, "Incremental Result", addSpace=True, orientation="horizontal", height=80)

        gui.comboBox(incremental_box, self, "keep_result",
                    label="Keep results", addSpace=False,
                    items=['No','Accumulate intensity','Accumulate electric field'],
                    valueType=int, orientation="horizontal", callback=self.refresh)
        # gui.checkBox(incremental_box, self, "keep_result", "Keep Result")
        gui.button(incremental_box, self, "Clear", callback=self.reset_accumumation)

        amplitude_and_phase_box = oasysgui.widgetBox(self.tab_sou, "Amplitude and phase settings",
                                                     addSpace=True, orientation="horizontal", height=80)

        gui.comboBox(amplitude_and_phase_box, self, "phase_unwrap",
                    label="Phase unwrap ", addSpace=False,
                    items=['No','Yes'],
                    valueType=int, orientation="horizontal", callback=self.refresh)

    def initializeTabs(self):
        size = len(self.tab)
        indexes = range(0, size)

        for index in indexes:
            self.tabs.removeTab(size-1-index)

        self.tab = []
        self.plot_canvas = []

        # for index in range(0, len(self.titles)):
        # intensity
        self.tab.append(gui.createTabPage(self.tabs, self.titles[0]))
        self.plot_canvas.append(None)
        # phase
        if self.keep_result != 1:
            self.tab.append(gui.createTabPage(self.tabs, self.titles[1]))
            self.plot_canvas.append(None)
            # real
            self.tab.append(gui.createTabPage(self.tabs, self.titles[2]))
            self.plot_canvas.append(None)
            # imag
            self.tab.append(gui.createTabPage(self.tabs, self.titles[3]))
            self.plot_canvas.append(None)

        # scanned peak
        self.tab.append(gui.createTabPage(self.tabs, self.titles[4]))
        self.plot_canvas.append(None)
        # scanned FWHM
        self.tab.append(gui.createTabPage(self.tabs, self.titles[5]))
        self.plot_canvas.append(None)

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)


    def set_input(self, wofry_data):
        if not wofry_data is None:
            self.wofry_data = wofry_data

            if self.keep_result ==0:
                self.accumulated_data = None

            if self.accumulated_data is None:
                self.accumulated_data = {}
                self.accumulated_data["counter"] = 1
                self.accumulated_data["intensity"] = self.wofry_data.get_wavefront().get_intensity()

                intensities = []
                intensities.append( self.wofry_data.get_wavefront().get_intensity() )
                self.accumulated_data["intensities"] = intensities

                current_variable_values = []
                current_variable_values.append(self.current_variable_value)
                self.accumulated_data["current_variable_values"] = current_variable_values

                self.accumulated_data["complex_amplitude"] = self.wofry_data.get_wavefront().get_complex_amplitude()

                self.accumulated_data["x"] = self.wofry_data.get_wavefront().get_abscissas()

            else:
                self.accumulated_data["counter"] += 1
                self.accumulated_data["intensity"] += self.wofry_data.get_wavefront().get_intensity()

                intensities = self.accumulated_data["intensities"]
                intensities.append( self.wofry_data.get_wavefront().get_intensity() )
                self.accumulated_data["intensities"] = intensities

                current_variable_values = self.accumulated_data["current_variable_values"]
                current_variable_values.append(self.current_variable_value)
                self.accumulated_data["current_variable_values"] = current_variable_values

                self.accumulated_data["complex_amplitude"] += self.wofry_data.get_wavefront().get_complex_amplitude()


            self.refresh()
            #NEWNEWNEW
            self.passTrigger(TriggerIn(new_object=True))

    def refresh(self):
        self.progressBarInit()
        self.wofry_output.setText("")
        sys.stdout = EmittingStream(textWritten=self.writeStdOut)
        try:
            if self.wofry_data is not None:
                if self.view_type != 0:
                    current_index = self.tabs.currentIndex()
                    self.initializeTabs()
                    self.plot_results()
                    self.tabs.setCurrentIndex(current_index)
        except Exception as exception:
            QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)

        self.progressBarFinished()

    def do_plot_results(self, progressBarValue):
        if self.accumulated_data is None:
            return
        else:

            self.progressBarSet(progressBarValue)


            if self.keep_result < 2:
                print(">>>> plotiing intensity")
                self.plot_data1D(x=1e6*self.accumulated_data["x"],
                                 y=self.accumulated_data["intensity"],
                                 progressBarValue=progressBarValue + 5,
                                 tabs_canvas_index=0,
                                 plot_canvas_index=0,
                                 title=self.titles[0],
                                 calculate_fwhm=True,
                                 xtitle="Spatial Coordinate [$\mu$m]",
                                 ytitle="Intensity")
            elif self.keep_result == 2:
                print(">>>> plotiing intensity from accumulated fields")
                self.plot_data1D(x=1e6*self.accumulated_data["x"],
                                 y=numpy.abs(self.accumulated_data["complex_amplitude"])**2,
                                 progressBarValue=progressBarValue + 5,
                                 tabs_canvas_index=0,
                                 plot_canvas_index=0,
                                 title=self.titles[0],
                                 calculate_fwhm=True,
                                 xtitle="Spatial Coordinate [$\mu$m]",
                                 ytitle="Intensity")
            else:
                raise ValueError("Non recognised flag: keep_results")

            if ((self.keep_result == 0) or (self.keep_result == 2)):
                print(">>>> plotiing phase")
                phase = numpy.angle(self.accumulated_data['complex_amplitude'])
                if self.phase_unwrap:
                    phase = numpy.unwrap(phase)
                self.plot_data1D(x=1e6*self.accumulated_data['x'],
                                 y=phase,
                                 progressBarValue=progressBarValue + 5,
                                 tabs_canvas_index=1,
                                 plot_canvas_index=1,
                                 title=self.titles[1],
                                 calculate_fwhm=False,
                                 xtitle="Spatial Coordinate [$\mu$m]",
                                 ytitle="Phase (rad)")

                print(">>>> plotiing real")
                self.plot_data1D(x=1e6*self.accumulated_data['x'],
                                 y=numpy.real(self.accumulated_data['complex_amplitude']),
                                 progressBarValue=progressBarValue + 5,
                                 tabs_canvas_index=2,
                                 plot_canvas_index=2,
                                 title=self.titles[2],
                                 calculate_fwhm=False,
                                 xtitle="Spatial Coordinate [$\mu$m]",
                                 ytitle="Real(Amplitude)")

                print(">>>> plotiing imag")
                self.plot_data1D(x=1e6*self.accumulated_data['x'],
                                 y=numpy.imag(self.accumulated_data['complex_amplitude']),
                                 progressBarValue=progressBarValue + 5,
                                 tabs_canvas_index=3,
                                 plot_canvas_index=3,
                                 title=self.titles[3],
                                 calculate_fwhm=False,
                                 xtitle="Spatial Coordinate [$\mu$m]",
                                 ytitle="Imag(Amplitude)")
            #
            #
            # scan plots

            try:
                nruns = len(self.accumulated_data['intensities'])
                print(">>>>> nruns: ", nruns)

                # try:
                #     x = numpy.array(self.accumulated_data["current_variable_values"]) # numpy.arange(nruns)
                # except:
                if nruns == 1:
                    x = numpy.arange(nruns)
                else:
                    x = numpy.array(self.accumulated_data["current_variable_values"])

                peak = numpy.zeros(nruns)
                fwhm = numpy.zeros(nruns)
                for i in range(nruns):
                    peak[i] = numpy.max(self.accumulated_data['intensities'][i])
                    print(">>>> i peak ", i, peak[i])
                    print(self.accumulated_data['x'].shape, (self.accumulated_data['intensities'][i]).shape)
                    from srxraylib.plot.gol import plot
                    # plot(self.accumulated_data['x'] , self.accumulated_data['intensities'][i])
                    try:
                        fwhm[i], tmp, tmp = get_fwhm(self.accumulated_data['intensities'][i], self.accumulated_data['x'] )
                        print("fwhm: ", i, fwhm[i])
                    except:
                        fwhm[i] = 0.0
                        print("bad fwhm: ",i,fwhm[i])
            except:
                x = numpy.array([-2,-1])
                peak = numpy.array([-1, -1])
                fwhm = numpy.array([-1, -1])

            print(">>> plotting peak")
            self.plot_data1D(x=x,
                             y=peak,
                             progressBarValue=progressBarValue + 5,
                             tabs_canvas_index=4,
                             plot_canvas_index=4,
                             calculate_fwhm=False,
                             title="%s nruns: %s" % (self.titles[4] , self.accumulated_data["counter"]),
                             xtitle="%s [%s]" % (self.variable_display_name, self.variable_um),
                             ytitle="Peak Intensity")
            print(">>> plotting fwhm")
            self.plot_data1D(x=x,
                             y=1e6*fwhm,
                             progressBarValue=progressBarValue + 5,
                             tabs_canvas_index=5,
                             plot_canvas_index=5,
                             calculate_fwhm=False,
                             title="%s nruns: %s" % (self.titles[5] , len(self.accumulated_data["intensities"])),
                             xtitle="%s [%s]" % (self.variable_display_name, self.variable_um),
                             ytitle="FWHM [um]")

            print(">>>>> current value: ",self.current_variable_value)
            print(">>>>> current valueSS: ", self.accumulated_data["current_variable_values"])
            print(">>>>> list of values: ",self.list_of_values)
            print(">>>>> current new object: ",self.current_new_object)
            print(">>>>> self.variable_name = ", self.variable_name)
            print(">>>>> self.variable_display_name = ",self.variable_display_name)
            print(">>>>> self.current_variable_value = ",self.current_variable_value)
            print(">>>>> self.variable_um = ",self.variable_um)




    def reset_accumumation(self):

        self.initializeTabs()
        self.accumulated_data = None
        self.wofry_data = None

    #
    # trigger methods
    #
    def list_of_values_ta_changed(self):
        self.list_of_values = []

        values = self.list_of_values_ta.toPlainText().split("\n")
        for value in values:
            if not value.strip() == "":
                self.list_of_values.append(value)

        self.number_of_new_objects = len(self.list_of_values)

        if len(self.list_of_values) == 0:
            self.list_of_values.append("")

    def set_KindOfLoop(self):
        self.left_box_1_1.setVisible(self.kind_of_loop == 0)
        self.left_box_1_2.setVisible(self.kind_of_loop == 1)

    def calculate_step(self):
        self.variable_value_step = round(
            (self.variable_value_to - self.variable_value_from) / self.number_of_new_objects, 8)

    def startLoop(self):

        self.reset_accumumation()  #NEWNEW

        self.current_new_object = 1

        do_loop = True

        if self.kind_of_loop == 0:
            self.current_variable_value = round(self.variable_value_from, 8)
            self.calculate_step()
        elif len(self.list_of_values) > 0:
            self.current_variable_value = self.list_of_values[self.current_new_object - 1]
        else:
            do_loop = False

        if do_loop:
            self.start_button.setEnabled(False)

            self.setStatusMessage(
                "Running " + self.get_object_name() + " " + str(self.current_new_object) + " of " + str(
                    self.number_of_new_objects))
            self.send("Trigger", TriggerOut(new_object=True, additional_parameters={"variable_name": self.variable_name,
                                                                                    "variable_display_name": self.variable_display_name,
                                                                                    "variable_value": self.current_variable_value,
                                                                                    "variable_um": self.variable_um}))

    def stopLoop(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Interruption of the Loop?"):
            self.run_loop = False
            self.current_variable_value = None
            self.setStatusMessage("Interrupted by user")

    def suspendLoop(self):
        try:
            if ConfirmDialog.confirmed(parent=self, message="Confirm Suspension of the Loop?"):
                self.run_loop = False
                self.suspend_loop = True
                self.stop_button.setEnabled(False)
                self.re_start_button.setEnabled(True)
                self.setStatusMessage("Suspended by user")
        except:
            pass

    def restartLoop(self):
        try:
            self.run_loop = True
            self.suspend_loop = False
            self.stop_button.setEnabled(True)
            self.re_start_button.setEnabled(False)
            self.passTrigger(TriggerIn(new_object=True))
        except:
            pass

    def passTrigger(self, trigger):

        if self.run_loop:
            if trigger:
                if trigger.interrupt:
                    self.current_new_object = 0
                    self.current_variable_value = None
                    self.start_button.setEnabled(True)
                    self.setStatusMessage("")
                    self.send("Trigger", TriggerOut(new_object=False))
                elif trigger.new_object:
                    if self.current_new_object == 0:
                        QMessageBox.critical(self, "Error", "Loop has to be started properly: press the button Start",
                                             QMessageBox.Ok)
                        return

                    if (self.current_new_object < self.number_of_new_objects) or (
                            self.current_new_object == self.number_of_new_objects and self.kind_of_loop == 0):
                        if self.current_variable_value is None:
                            self.current_new_object = 1

                            if self.kind_of_loop == 0:
                                self.current_variable_value = round(self.variable_value_from, 8)
                                self.calculate_step()
                            elif len(self.list_of_values) > 0:
                                self.current_variable_value = self.list_of_values[self.current_new_object - 1]
                        else:
                            self.current_new_object += 1
                            if self.kind_of_loop == 0:
                                self.current_variable_value = round(
                                    self.current_variable_value + self.variable_value_step, 8)
                            elif len(self.list_of_values) > 0:
                                self.current_variable_value = self.list_of_values[self.current_new_object - 1]

                        self.setStatusMessage(
                            "Running " + self.get_object_name() + " " + str(self.current_new_object) + " of " + str(
                                self.number_of_new_objects))
                        self.start_button.setEnabled(False)
                        self.send("Trigger", TriggerOut(new_object=True,
                                                        additional_parameters={"variable_name": self.variable_name,
                                                                               "variable_display_name": self.variable_display_name,
                                                                               "variable_value": self.current_variable_value,
                                                                               "variable_um": self.variable_um}))
                    else:
                        self.current_new_object = 0
                        self.current_variable_value = None
                        self.start_button.setEnabled(True)
                        self.setStatusMessage("")
                        self.send("Trigger", TriggerOut(new_object=False))
        else:
            if not self.suspend_loop:
                self.current_new_object = 0
                self.current_variable_value = None
                self.start_button.setEnabled(True)

            self.send("Trigger", TriggerOut(new_object=False))
            self.setStatusMessage("")
            self.run_loop = True
            self.suspend_loop = False

    def get_object_name(self):
        return "Object"


if __name__ == '__main__':

    from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    ow =OWstepper1D()

    wf = GenericWavefront1D.initialize_wavefront_from_arrays(numpy.linspace(-1e-3,1e-3,300),
                                                             numpy.linspace(-1e-3,1e-3,300)**2 )

    ow.set_input(WofryData(wavefront=wf))
    ow.show()
    app.exec_()
    ow.saveSettings()

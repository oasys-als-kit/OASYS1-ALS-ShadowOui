import numpy
import sys

from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QMessageBox
from orangewidget import gui
from orangewidget import widget
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence
from oasys.util.oasys_util import EmittingStream, TTYGrabber

from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D

from orangecontrib.wofry.widgets.gui.ow_wofry_widget import WofryWidget

import scipy.constants as codata

from orangecontrib.xoppy.util.python_script import PythonScript  # TODO: change import from wofry!!!

from orangecontrib.wofry.util.wofry_objects import WofryData
from orangecontrib.xoppy.util.python_script import PythonScript  # TODO: change import from wofry!!!


class OWGaussianUndulator1D(WofryWidget):

    name = "Undulator Gaussian 1D"
    id = "UndulatorGaussian1D"
    description = "ALS Undulator Gaussian 1D"
    icon = "icons/ugaussian.png"
    priority = 1

    category = "Wofry Wavefront Propagation"
    keywords = ["data", "file", "load", "read"]

    outputs = [{"name":"WofryData",
                "type":WofryData,
                "doc":"WofryData",
                "id":"WofryData"}]

    units = Setting(0)
    energy = Setting(250.0)
    wavelength = Setting(1e-10)
    number_of_points = Setting(1000)
    initialize_from = Setting(0)
    range_from = Setting(-0.00147)
    range_to = Setting(0.00147)
    steps_start = Setting(-0.0005)
    steps_step = Setting(1e-6)
    wavefront_position = Setting(1)
    undulator_distance = Setting(13.73)
    sigma_times = Setting(6.0)
    undulator_length = Setting(3.98)
    add_random_phase = Setting(0)

    wavefront1D = None
    titles = ["Wavefront 1D Intensity", "Wavefront 1D Phase","Wavefront Real(Amplitude)","Wavefront Imag(Amplitude)"]

    def __init__(self):
        super().__init__(is_automatic=False, show_view_options=True)

        #
        # add script tab to tabs panel
        #
        script_tab = oasysgui.createTabPage(self.main_tabs, "Script")
        self.wofry_script = PythonScript()
        self.wofry_script.code_area.setFixedHeight(400)
        script_box = gui.widgetBox(script_tab, "Python script", addSpace=True, orientation="horizontal")
        script_box.layout().addWidget(self.wofry_script)


        #
        # control panel
        #
        self.runaction = widget.OWAction("Generate Wavefront", self)
        self.runaction.triggered.connect(self.generate)
        self.addAction(self.runaction)


        gui.separator(self.controlArea)
        gui.separator(self.controlArea)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Generate", callback=self.generate)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)

        gui.separator(self.controlArea)

        self.controlArea.setFixedWidth(self.CONTROL_AREA_WIDTH)

        tabs_setting = oasysgui.tabWidget(self.controlArea)
        tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT + 50)
        tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)

        self.tab_sou = oasysgui.createTabPage(tabs_setting, "Generic Wavefront 1D Settings")

        box_energy = oasysgui.widgetBox(self.tab_sou, "Energy Settings", addSpace=False, orientation="vertical")

        gui.comboBox(box_energy, self, "units", label="Units in use", labelWidth=350,
                     items=["Electron Volts", "Meters"],
                     callback=self.set_visible,
                     sendSelectedValue=False, orientation="horizontal")

        self.units_box_1 = oasysgui.widgetBox(box_energy, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.units_box_1, self, "energy", "Photon Energy [eV]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.units_box_2 = oasysgui.widgetBox(box_energy, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.units_box_2, self, "wavelength", "Photon Wavelength [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        box_space = oasysgui.widgetBox(self.tab_sou, "Space Settings", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(box_space, self, "number_of_points", "Number of Points",
                          labelWidth=300, valueType=int, orientation="horizontal")

        gui.comboBox(box_space, self, "initialize_from", label="Space Initialization", labelWidth=350,
                     items=["From Range", "From Steps", "From N times sigma"],
                     callback=self.set_visible,
                     sendSelectedValue=False, orientation="horizontal")

        self.initialization_box_1 = oasysgui.widgetBox(box_space, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.initialization_box_1, self, "range_from", "From  [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.initialization_box_1, self, "range_to", "To [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.initialization_box_2 = oasysgui.widgetBox(box_space, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.initialization_box_2, self, "steps_start", "Start [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.initialization_box_2, self, "steps_step", "Step [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.initialization_box_3 = oasysgui.widgetBox(box_space, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.initialization_box_3, self, "sigma_times", "N times sigma",
                          labelWidth=300, valueType=float, orientation="horizontal")


        box_amplitude = oasysgui.widgetBox(self.tab_sou, "Undulator", addSpace=False, orientation="vertical")

        gui.comboBox(box_amplitude, self, "wavefront_position", label="Create wavefront at", labelWidth=350,
                     items=["source position (Gaussian source)", "screen position (spherical wave weighted with Gaussian divergence)"],
                     callback=self.set_visible,
                     sendSelectedValue=False, orientation="horizontal")



        undulator_box = oasysgui.widgetBox(box_amplitude, "", addSpace=False, orientation="vertical")
        oasysgui.lineEdit(undulator_box, self, "undulator_length", "Undulator length [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.undulator_distance_box_id = oasysgui.widgetBox(box_amplitude, "", addSpace=False, orientation="horizontal")
        oasysgui.lineEdit(self.undulator_distance_box_id, self, "undulator_distance", "Undulator-Screen distance [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        gui.checkBox(self.tab_sou, self, "add_random_phase", "Add random phase")

        self.set_visible()

    def set_visible(self):

        self.units_box_1.setVisible(self.units == 0)
        self.units_box_2.setVisible(self.units == 1)

        self.initialization_box_1.setVisible(self.initialize_from == 0)
        self.initialization_box_2.setVisible(self.initialize_from == 1)
        self.initialization_box_3.setVisible(self.initialize_from == 2)

        if self.wavefront_position ==  0:
            self.undulator_distance_box_id.setVisible(False)
        elif self.wavefront_position ==  1:
            self.undulator_distance_box_id.setVisible(True)

    def initializeTabs(self):
        size = len(self.tab)
        indexes = range(0, size)

        for index in indexes:
            self.tabs.removeTab(size-1-index)

        self.tab = []
        self.plot_canvas = []

        for index in range(0, len(self.titles)):
            self.tab.append(gui.createTabPage(self.tabs, self.titles[index]))
            self.plot_canvas.append(None)

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)


    def check_fields(self):

        if self.units == 0:
            self.energy = congruence.checkStrictlyPositiveNumber(self.energy, "Energy")
        else:
            self.wavelength = congruence.checkStrictlyPositiveNumber(self.wavelength, "Wavelength")
        self.number_of_points = congruence.checkStrictlyPositiveNumber(self.number_of_points, "Number of Points")

        if self.initialize_from == 0:
            self.range_from = congruence.checkNumber(self.range_from, "From")
            self.range_to = congruence.checkNumber(self.range_to, "To")
            congruence.checkGreaterThan(self.range_to, self.range_from, "Range To", "Range From")
        elif self.initialize_from == 1:
            self.steps_start = congruence.checkNumber(self.steps_start, "Step start")
            self.steps_step = congruence.checkNumber(self.steps_step, "Step")
        elif self.initialize_from == 2:
            self.sigma_times = congruence.checkPositiveNumber(self.sigma_times, "N times sigma")
        #
        self.undulator_length = congruence.checkPositiveNumber(self.undulator_length, "Undulator length")
        self.undulator_distance = congruence.checkPositiveNumber(self.undulator_distance, "Undulator-Screen distance")


    def generate(self):

        try:
            self.progressBarInit()

            self.wofry_output.setText("")

            sys.stdout = EmittingStream(textWritten=self.writeStdOut)

            self.check_fields()

            if self.units == 0:
                wavelength = codata.h * codata.c / codata.e / self.energy
            else:
                wavelength = self.wavelength


            if self.initialize_from == 0:
                x_min = self.range_from
                x_max = self.range_to
                number_of_points = self.number_of_points
            elif self.initialize_from == 1:
                number_of_points = self.number_of_points
                x_min = self.steps_start
                x_max = x_min + (number_of_points - 1) * self.steps_step

            elif self.initialize_from == 2:
                sigma_r = 2.740 / 4 / numpy.pi * numpy.sqrt(wavelength * self.undulator_length)
                x_min=-0.5 * self.sigma_times * sigma_r
                x_max=+0.5 * self.sigma_times * sigma_r
                number_of_points = self.number_of_points

            self.wavefront1D = self.calculate_wavefront1D(wavelength=wavelength,
                                                        wavefront_position=self.wavefront_position,
                                                        undulator_length=self.undulator_length,
                                                        undulator_distance=self.undulator_distance,
                                                        x_min = x_min,
                                                        x_max = x_max,
                                                        number_of_points = number_of_points,
                                                        add_random_phase=self.add_random_phase,
                                                        )
            #
            # script
            #

            dict_parameters = {"wavelength": wavelength,
                               "wavefront_position": self.wavefront_position,
                               "undulator_length": self.undulator_length,
                               "undulator_distance": self.undulator_distance,
                               "x_min": x_min,
                               "x_max": x_max,
                               "number_of_points": number_of_points,
                               "add_random_phase": self.add_random_phase,
                               }
            script_template = self.script_template()

            # write python script
            self.wofry_script.set_code(script_template.format_map(dict_parameters))


            #
            # plots
            #

            try:
                current_index = self.tabs.currentIndex()
            except:
                current_index = None

            if self.view_type > 0:
                self.initializeTabs()
                self.plot_results()
                if current_index is not None:
                    try:
                        self.tabs.setCurrentIndex(current_index)
                    except:
                        pass

            self.progressBarFinished()

            self.send("WofryData", WofryData(wavefront=self.wavefront1D))


        except Exception as exception:
            QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)

            if self.IS_DEVELOP: raise exception

            self.progressBarFinished()



    def calculate_wavefront1D(self,wavelength=1e-10,
                            undulator_length=1.0,undulator_distance=10.0,
                            x_min=-0.1,x_max=0.1,number_of_points=101,
                            wavefront_position=0,add_random_phase=0):

        sigma_r = 2.740 / 4 / numpy.pi * numpy.sqrt(wavelength * undulator_length)
        sigma_r_prime = 0.69 * numpy.sqrt(wavelength / undulator_length)

        print("Radiation values:")
        print("   intensity sigma': %6.3f urad, FWHM': %6.3f urad" % (sigma_r_prime * 1e6, sigma_r_prime * 2.355e6))
        print("   intensity sigma : %6.3f um, FWHM: %6.3f um\n" % (sigma_r * 1e6, sigma_r * 2.355e6))

        wavefront1D = GenericWavefront1D.initialize_wavefront_from_range(x_min=x_min, x_max=x_max, number_of_points=number_of_points)
        wavefront1D.set_wavelength(wavelength)

        if wavefront_position == 0: # Gaussian source
            wavefront1D.set_gaussian(sigma_x=sigma_r, amplitude=1.0, shift=0.0)
        elif wavefront_position == 1: # Spherical source, Gaussian intensity
            wavefront1D.set_spherical_wave(radius=undulator_distance, center=0.0, complex_amplitude=complex(1,0))
            # weight with Gaussian
            X = wavefront1D.get_abscissas()
            A = wavefront1D.get_complex_amplitude()
            sigma = undulator_distance * sigma_r_prime
            sigma_amplitude = sigma * numpy.sqrt(2)
            Gx = numpy.exp(-X * X / 2 / sigma_amplitude ** 2)
            wavefront1D.set_complex_amplitude(A * Gx)

            print("intensity sigma at %3.1f m : %6.3f um, FWHM: %6.3f um"%\
                  (undulator_distance,sigma*1e6,sigma*2.35e6))
            print("amplitude sigma at %3.1f m : %6.3f um, FWHM: %6.3f um\n"%\
                  (undulator_distance,sigma_amplitude*1e6,sigma_amplitude*2.35e6))

        if add_random_phase:
            wavefront1D.add_phase_shifts(2*numpy.pi*numpy.random.random(wavefront1D.size()))

        return wavefront1D

    def script_template(self):
        return \
"""
import numpy

def calculate_wavefront1D(wavelength=1e-10,
                        undulator_length=1.0,undulator_distance=10.0,
                        x_min=-0.1,x_max=0.1,number_of_points=101,
                        wavefront_position=0,add_random_phase=0):
    
    from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D

    sigma_r = 2.740 / 4 / numpy.pi * numpy.sqrt(wavelength * undulator_length)
    sigma_r_prime = 0.69 * numpy.sqrt(wavelength / undulator_length)

    wavefront1D = GenericWavefront1D.initialize_wavefront_from_range(x_min=x_min, x_max=x_max, number_of_points=number_of_points)
    wavefront1D.set_wavelength(wavelength)

    if wavefront_position == 0: # Gaussian source
        wavefront1D.set_gaussian(sigma_x=sigma_r, amplitude=1.0, shift=0.0)
    elif wavefront_position == 1: # Spherical source, Gaussian intensity
        wavefront1D.set_spherical_wave(radius=undulator_distance, center=0.0, complex_amplitude=complex(1,0))
        # weight with Gaussian
        X = wavefront1D.get_abscissas()
        A = wavefront1D.get_complex_amplitude()
        sigma = undulator_distance * sigma_r_prime
        sigma_amplitude = sigma * numpy.sqrt(2)
        Gx = numpy.exp(-X * X / 2 / sigma_amplitude ** 2)
        wavefront1D.set_complex_amplitude(A * Gx)

    if add_random_phase:
        wavefront1D.add_phase_shifts(2*numpy.pi*numpy.random.random(wavefront1D.size()))

    return wavefront1D



output_wavefront = calculate_wavefront1D(wavelength={wavelength},
                                                    wavefront_position={wavefront_position},
                                                    undulator_length={undulator_length},
                                                    undulator_distance={undulator_distance},
                                                    x_min={x_min},
                                                    x_max={x_max},
                                                    number_of_points = {number_of_points},
                                                    add_random_phase={add_random_phase})
from srxraylib.plot.gol import plot
plot(output_wavefront.get_abscissas(),output_wavefront.get_intensity())
"""


    def do_plot_results(self, progressBarValue=80):
        if not self.wavefront1D is None:

            self.progressBarSet(progressBarValue)


            self.plot_data1D(x=1e6*self.wavefront1D.get_abscissas(),
                             y=self.wavefront1D.get_intensity(),
                             progressBarValue=progressBarValue,
                             tabs_canvas_index=0,
                             plot_canvas_index=0,
                             calculate_fwhm=True,
                             title=self.titles[0],
                             xtitle="Spatial Coordinate [$\mu$m]",
                             ytitle="Intensity")

            self.plot_data1D(x=1e6*self.wavefront1D.get_abscissas(),
                             y=self.wavefront1D.get_phase(from_minimum_intensity=0.1,unwrap=1),
                             progressBarValue=progressBarValue + 10,
                             tabs_canvas_index=1,
                             plot_canvas_index=1,
                             calculate_fwhm=False,
                             title=self.titles[1],
                             xtitle="Spatial Coordinate [$\mu$m]",
                             ytitle="Phase [unwrapped, for intensity > 10% of peak] (rad)")

            self.plot_data1D(x=1e6*self.wavefront1D.get_abscissas(),
                             y=numpy.real(self.wavefront1D.get_complex_amplitude()),
                             progressBarValue=progressBarValue + 10,
                             tabs_canvas_index=2,
                             plot_canvas_index=2,
                             calculate_fwhm=False,
                             title=self.titles[2],
                             xtitle="Spatial Coordinate [$\mu$m]",
                             ytitle="Real(Amplitude)")

            self.plot_data1D(x=1e6*self.wavefront1D.get_abscissas(),
                             y=numpy.imag(self.wavefront1D.get_complex_amplitude()),
                             progressBarValue=progressBarValue + 10,
                             tabs_canvas_index=3,
                             plot_canvas_index=3,
                             calculate_fwhm=False,
                             title=self.titles[3],
                             xtitle="Spatial Coordinate [$\mu$m]",
                             ytitle="Imag(Amplitude)")


            self.plot_canvas[0].resetZoom()

            self.progressBarFinished()

if __name__ == '__main__':

    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    ow = OWGaussianUndulator1D()
    ow.show()
    app.exec_()
    ow.saveSettings()

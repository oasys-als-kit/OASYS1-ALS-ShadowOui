import numpy

from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QMessageBox
from orangewidget import gui
from orangewidget import widget
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D

from orangecontrib.wofry.widgets.gui.ow_wofry_widget import WofryWidget

import scipy.constants as codata

from orangecontrib.xoppy.util.python_script import PythonScript  # TODO: change import from wofry!!!

class OWGaussianUndulator1D(WofryWidget):

    name = "Wofry Undulator Gaussian 1D"
    id = "UndulatorGaussian1D"
    description = "Undulator Gaussian 1D"
    icon = "icons/ugaussian.png"
    priority = 1

    category = "Wofry Wavefront Propagation"
    keywords = ["data", "file", "load", "read"]

    outputs = [{"name":"GenericWavefront1D",
                "type":GenericWavefront1D,
                "doc":"GenericWavefront1D",
                "id":"GenericWavefront1D"}]

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
        super().__init__(is_automatic=False, show_view_options=False)

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
            self.wofry_output.setText("")

            self.progressBarInit()

            self.check_fields()

            if self.units == 0:
                wavelength = codata.h * codata.c / codata.e / self.energy
            else:
                wavelength = self.wavelength

            sigma_r = 2.740 / 4 / numpy.pi * numpy.sqrt(wavelength * self.undulator_length)
            sigma_r_prime = 0.69 * numpy.sqrt(wavelength / self.undulator_length)

            if self.wavefront_position == 0: # Gaussian source

                if self.initialize_from == 0:
                    self.wavefront1D = GenericWavefront1D.initialize_wavefront_from_range(x_min=self.range_from, x_max=self.range_to, number_of_points=self.number_of_points)
                elif self.initialize_from == 1:
                    self.wavefront1D = GenericWavefront1D.initialize_wavefront_from_steps(x_start=self.steps_start, x_step=self.steps_step, number_of_points=self.number_of_points)
                elif self.initialize_from == 2:
                    self.wavefront1D = GenericWavefront1D.initialize_wavefront_from_range(x_min=-0.5*self.sigma_times*sigma_r,
                                                                                          x_max=+0.5*self.sigma_times*sigma_r,
                                                                                          number_of_points=self.number_of_points)

                if self.units == 0:
                    self.wavefront1D.set_photon_energy(self.energy)
                else:
                    self.wavefront1D.set_wavelength(self.wavelength)

                self.wavefront1D.set_gaussian(sigma_x=sigma_r, amplitude=1.0, shift=0.0)

            elif self.wavefront_position == 1: # Spherical source, Gaussian intensity

                if self.initialize_from == 0:
                    self.wavefront1D = GenericWavefront1D.initialize_wavefront_from_range(x_min=self.range_from, x_max=self.range_to, number_of_points=self.number_of_points)
                elif self.initialize_from == 1:
                    self.wavefront1D = GenericWavefront1D.initialize_wavefront_from_steps(x_start=self.steps_start, x_step=self.steps_step, number_of_points=self.number_of_points)
                elif self.initialize_from == 2:
                    self.wavefront1D = GenericWavefront1D.initialize_wavefront_from_range(x_min=-0.5*self.sigma_times*sigma_r_prime*self.undulator_distance,
                                                                                          x_max=+0.5*self.sigma_times*sigma_r_prime*self.undulator_distance,
                                                                                          number_of_points=self.number_of_points)

                if self.units == 0:
                    self.wavefront1D.set_photon_energy(self.energy)
                else:
                    self.wavefront1D.set_wavelength(self.wavelength)


                self.wavefront1D.set_spherical_wave(radius=self.undulator_distance, center=0.0, complex_amplitude=complex(1,0))

                # weight with Gaussian
                X = self.wavefront1D.get_abscissas()
                A = self.wavefront1D.get_complex_amplitude()
                sigma = self.undulator_distance * sigma_r_prime
                sigma_amplitude = sigma * numpy.sqrt(2)
                Gx = numpy.exp(-X * X / 2 / sigma_amplitude ** 2)
                self.wavefront1D.set_complex_amplitude(A * Gx)


            # if self.units == 0:
            #     self.wavefront1D.set_photon_energy(self.energy)
            # else:
            #     self.wavefront1D.set_wavelength(self.wavelength)

            if self.add_random_phase:
                self.wavefront1D.add_phase_shifts(2*numpy.pi*numpy.random.random(self.wavefront1D.size()))

            try:
                current_index = self.tabs.currentIndex()
            except:
                current_index = None
            self.initializeTabs()
            self.plot_results()
            if current_index is not None:
                try:
                    self.tabs.setCurrentIndex(current_index)
                except:
                    pass

            try:
                python_code = self.generate_python_code()
                self.writeStdOut(python_code)
            except:
                pass

            self.send("GenericWavefront1D", self.wavefront1D)

        except Exception as exception:
            QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)

            #raise exception

            self.progressBarFinished()

    def generate_python_code(self):

        txt = ""
        #
        # txt += "\n\n#"
        # txt += "\n# create input_wavefront\n#"
        # txt += "\n#"
        # txt += "\nfrom wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D"

        # if self.initialize_from == 0:
        #     txt += "\ninput_wavefront = GenericWavefront1D.initialize_wavefront_from_range(x_min=%g,x_max=%g,number_of_points=%d)"%\
        #     (self.range_from,self.range_to,self.number_of_points)
        #
        # if self.initialize_from == 1:
        #     txt += "\ninput_wavefront = GenericWavefront1D.initialize_wavefront_from_steps(x_start=%g, x_step=%g,number_of_points=%d)"%\
        #            (self.steps_start,self.steps_step,self.number_of_points)
        # elif self.initialize_from == 2:
        #     txt += ""
        #
        # if self.units == 0:
        #     txt += "\ninput_wavefront.set_photon_energy(%g)"%(self.energy)
        # else:
        #     txt += "\ninput_wavefront.set_wavelength(%g)"%(self.wavelength)
        #
        #
        #
        # if self.kind_of_wave == 0: #plane
        #     if self.initialize_amplitude == 0:
        #         txt += "\ninput_wavefront.set_plane_wave_from_complex_amplitude(complex_amplitude=complex(%g,%g),inclination=%g)"%\
        #                (self.complex_amplitude_re,self.complex_amplitude_im,self.inclination)
        #     else:
        #         txt += "\ninput_wavefront.set_plane_wave_from_amplitude_and_phase(amplitude=%g,phase=%g,inclination=%g)"%(self.amplitude,self.phase,self.inclination)
        # elif self.kind_of_wave == 1: # spheric
        #     txt += "\ninput_wavefront.set_spherical_wave(radius=%g,center=%g,complex_amplitude=complex(%g, %g))"%\
        #            (self.radius,self.center,self.complex_amplitude_re,self.complex_amplitude_im)
        # elif self.kind_of_wave == 2: # gaussian
        #     txt += "\ninput_wavefront.set_gaussian(sigma_x=%f, amplitude=%f,shift=%f)"%\
        #            (self.gaussian_sigma,self.gaussian_amplitude,self.gaussian_shift)
        # elif self.kind_of_wave == 3: # g.s.m.
        #     txt += "\ninput_wavefront.set_gaussian_hermite_mode(sigma_x=%g,amplitude=%g,mode_x=%d,shift=%f,beta=%g)"%\
        #            (self.gaussian_sigma,self.gaussian_amplitude,self.gaussian_mode,self.gaussian_shift,self.gaussian_beta)
        #
        #     #
        #     # if self.add_random_phase:
        #     #     self.wavefront1D.add_phase_shifts(2*numpy.pi*numpy.random.random(self.wavefront1D.size()))
        # if self.add_random_phase:
        #     txt += "\ninput_wavefront.add_phase_shifts(2*numpy.pi*numpy.random.random(input_wavefront.size()))"
        #
        # txt += "\n\n\nfrom srxraylib.plot.gol import plot"
        # txt += "\nplot(input_wavefront.get_abscissas(),input_wavefront.get_intensity())"

        return txt


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

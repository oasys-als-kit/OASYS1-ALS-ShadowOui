import numpy
import sys
from scipy import interpolate


from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QMessageBox

from orangewidget import gui
from orangewidget.settings import Setting

from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence
from oasys.util.oasys_util import TriggerIn, EmittingStream

from orangecontrib.wofry.util.wofry_objects import WofryData
from orangecontrib.wofry.widgets.gui.ow_wofry_widget import WofryWidget
from orangecontrib.xoppy.util.python_script import PythonScript  # TODO: change import from wofry!!!

from syned.widget.widget_decorator import WidgetDecorator

from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D

from numba import jit, prange


@jit(nopython=True, parallel=True)
def goFromToSequential(field1, x1, y1, x2, y2, wavelength=1e-10, normalize_intensities=False):
    field2 = x2 * 0j
    wavenumber = numpy.pi * 2 / wavelength

    for i in prange(field2.size):
        r = numpy.sqrt(numpy.power(x1 - x2[i], 2) + numpy.power(y1 - y2[i], 2))
        field2[i] = (field1 * numpy.exp(1.j * wavenumber * r)).sum()

    if normalize_intensities:
        field2 *= numpy.sqrt((numpy.abs(field1) ** 2).sum() / (numpy.abs(field2) ** 2).sum())
    return field2

class OWGrating1D(WofryWidget):

    name = "Grating 1D"
    id = "WofryGrating1D"
    description = "ALS Grating 1D"
    icon = "icons/grating1D.png"
    priority = 4

    category = "Wofry Wavefront Propagation"
    keywords = ["data", "file", "load", "read", "grazing"]

    # outputs = [{"name":"GenericWavefront1D",
    #             "type":GenericWavefront1D,
    #             "doc":"GenericWavefront1D",
    #             "id":"GenericWavefront1D"}]
    #
    # inputs = [("GenericWavefront1D", GenericWavefront1D, "set_input"),
    #           ("DABAM 1D Profile", numpy.ndarray, "receive_dabam_profile")]

    outputs = [{"name":"WofryData",
                "type":WofryData,
                "doc":"WofryData",
                "id":"WofryData"},
               {"name":"Trigger",
                "type": TriggerIn,
                "doc":"Feedback signal to start a new beam simulation",
                "id":"Trigger"}]

    inputs = [("WofryData", WofryData, "set_input"),
              ("GenericWavefront1D", GenericWavefront1D, "set_input"),
              ("DABAM 1D Profile", numpy.ndarray, "receive_dabam_profile"),
              WidgetDecorator.syned_input_data()[0]]

    # Grating
    angle_in_deg = Setting(87.239145)
    angle_out_deg = Setting(85.829039)


    grating_flag = Setting(0) # 0-3 = calculated, 4=from file


    # radius = Setting(1000.0)  # TODO: delete?
    # shape = Setting(1)


    g_0 = Setting(300000.0)
    g_1 = Setting(269816.234363)
    g_2 = Setting(87748.010405)
    g_3 = Setting(27876.983114)
    grating_amplitude = Setting(20e-9)
    grating_length = Setting(150e-3)
    points_per_period = Setting(9.0)

    grating_file = Setting("<none>")
    write_profile = Setting(0)

    # Propagator
    p_distance = Setting(1.0)
    q_distance = Setting(1.0)
    zoom_factor = Setting(1.0)


    write_input_wavefront = Setting(0)

    input_data = None
    titles = ["Wavefront 1D Intensity", "Wavefront 1D Phase","Wavefront Real(Amplitude)","Wavefront Imag(Amplitude)","O.E. Profile"]

    def __init__(self):
        super().__init__(is_automatic=True, show_view_options=True)

        #
        # add script tab to tabs panel
        #
        script_tab = oasysgui.createTabPage(self.main_tabs, "Script")
        self.wofry_script = PythonScript()
        self.wofry_script.code_area.setFixedHeight(400)
        script_box = gui.widgetBox(script_tab, "Python script", addSpace=True, orientation="horizontal")
        script_box.layout().addWidget(self.wofry_script)


        #
        # build control panel
        #

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Propagate Wavefront", callback=self.propagate_wavefront)
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

        self.tab_sou = oasysgui.createTabPage(tabs_setting, "Grating 1D Settings")


        box_grating = oasysgui.widgetBox(self.tab_sou, "Grating", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(box_grating, self, "angle_in_deg", "Incidence angle [deg]",
                          labelWidth=200, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(box_grating, self, "angle_out_deg", "Reflection angle [deg]",
                          labelWidth=200, valueType=float, orientation="horizontal")


        gui.comboBox(box_grating, self, "grating_flag", label="Grating profile",
                     items=["Calculated (sin)",
                            "Calculated (cos)",
                            "Calculated (square)",
                            "Calculated (VLS)",
                            "Fom file"],
                     callback=self.set_visible,
                     sendSelectedValue=False, orientation="horizontal")

        self.grating_flag0_box_id = oasysgui.widgetBox(box_grating, "", addSpace=True, orientation="vertical")

        oasysgui.lineEdit(self.grating_flag0_box_id, self, "grating_amplitude", "grating amplitude [m]",
                          labelWidth=200, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.grating_flag0_box_id, self, "points_per_period", "points per period",
                          labelWidth=200, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.grating_flag0_box_id, self, "g_0", "g0 (lines/m)",
                          labelWidth=200, valueType=float, orientation="horizontal")

        self.grating_flag0vls_box_id = oasysgui.widgetBox(box_grating, "", addSpace=True, orientation="vertical")

        oasysgui.lineEdit(self.grating_flag0vls_box_id, self, "g_1", "g1 (m^-2)",
                          labelWidth=200, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.grating_flag0vls_box_id, self, "g_2", "g2 (m^-3)",
                          labelWidth=200, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.grating_flag0vls_box_id, self, "g_3", "g3 (m^-4)",
                          labelWidth=200, valueType=float, orientation="horizontal")

        self.grating_flag1_box_id = oasysgui.widgetBox(box_grating, "", addSpace=True, orientation="horizontal")
        self.grating_file_id = oasysgui.lineEdit(self.grating_flag1_box_id, self, "grating_file", "Grating file X[m] Y[m]",
                                                 labelWidth=120, valueType=str, orientation="horizontal")
        gui.button(self.grating_flag1_box_id, self, "...", callback=self.set_grating_file)


        self.grating_file_write_id = oasysgui.widgetBox(box_grating, "", addSpace=True, orientation="vertical")
        oasysgui.lineEdit(self.grating_file_write_id, self, "grating_length", "Grating length [m]",
                          labelWidth=200, valueType=float, orientation="horizontal")
        tmp_id = oasysgui.widgetBox(self.grating_file_write_id, "", addSpace=True, orientation="horizontal")
        gui.comboBox(tmp_id, self, "write_profile", label="Dump profile to file",
                     items=["No","Yes [grating_profile1D.dat]"], sendSelectedValue=False, orientation="horizontal")



        box_propagator = oasysgui.widgetBox(self.tab_sou, "Propagator", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(box_propagator, self, "p_distance", "Entrance arm [m]",
                          valueType=float, orientation="horizontal")


        oasysgui.lineEdit(box_propagator, self, "q_distance", "Exit arm [m]",
                          valueType=float, orientation="horizontal")

        oasysgui.lineEdit(box_propagator, self, "zoom_factor", "Zoom factor",
                          valueType=float, orientation="horizontal")

        gui.comboBox(box_propagator, self, "write_input_wavefront", label="Input wf to file (for script)",
                     items=["No","Yes [wavefront_input.h5]"], sendSelectedValue=False, orientation="horizontal")

        self.set_visible()

    def set_visible(self):
        if self.grating_flag ==4: # file
            self.grating_flag0_box_id.setVisible(False)
            self.grating_flag0vls_box_id.setVisible(False)
            self.grating_flag1_box_id.setVisible(True)
            self.grating_file_write_id.setVisible(False)
        else:
            self.grating_flag0_box_id.setVisible(True)
            self.grating_file_write_id.setVisible(True)
            if self.grating_flag == 3:
                self.grating_flag0vls_box_id.setVisible(True)
            else:
                self.grating_flag0vls_box_id.setVisible(False)
            self.grating_flag1_box_id.setVisible(False)


    def set_grating_file(self):
        self.grating_file_id.setText(oasysgui.selectFileFromDialog(self, self.grating_file, "Open file with profile error"))

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
        self.angle_in_deg = congruence.checkStrictlyPositiveNumber(self.angle_in_deg, "Grazing incidence angle")
        self.angle_out_deg = congruence.checkStrictlyPositiveNumber(self.angle_out_deg, "Grazing reflection angle")
        self.p_distance = congruence.checkNumber(self.p_distance, "Entrance arm")
        self.q_distance = congruence.checkNumber(self.q_distance, "Exit arm")
        self.zoom_factor = congruence.checkStrictlyPositiveNumber(self.zoom_factor, "Zoom factor")
        # self.radius = congruence.checkNumber(self.radius, "Radius")
        self.grating_file = congruence.checkFileName(self.grating_file)

    def receive_syned_data(self):
        raise Exception(NotImplementedError)

    def set_input(self, wofry_data):
        if not wofry_data is None:
            if isinstance(wofry_data, WofryData):
                self.input_data = wofry_data
            else:
                self.input_data = WofryData(wavefront=wofry_data)

            if self.is_automatic_execution:
                self.propagate_wavefront()

    def receive_dabam_profile(self, dabam_profile):
        if not dabam_profile is None:
            try:
                file_name = "dabam_profile_" + str(id(self)) + ".dat"

                file = open(file_name, "w")

                for element in dabam_profile:
                    file.write(str(element[0]) + " " + str(element[1]) + "\n")

                file.flush()
                file.close()

                self.grating_flag = 4 # file
                self.grating_file = file_name
                self.set_visible()

            except Exception as exception:
                QMessageBox.critical(self, "Error", exception.args[0], QMessageBox.Ok)

                if self.IS_DEVELOP: raise exception

    def propagate_wavefront(self):
        self.progressBarInit()

        self.wofry_output.setText("")
        sys.stdout = EmittingStream(textWritten=self.writeStdOut)

        self.check_fields()

        if self.input_data is None: raise Exception("No Input Wavefront")

        if self.grating_flag == 4:
            grating_file = self.grating_file
        else:
            grating_file = ""

        output_wavefront, abscissas_on_mirror, height = self.calculate_output_wavefront_after_grating1D(
            self.input_data.get_wavefront(),
            angle_in=self.angle_in_deg,
            angle_out=self.angle_out_deg,
            grating_flag=self.grating_flag,
            grating_amplitude=self.grating_amplitude,
            points_per_period=self.points_per_period,
            g_0=self.g_0,
            g_1=self.g_1,
            g_2=self.g_2,
            g_3=self.g_3,
            grating_file=grating_file,
            p_distance=self.p_distance,
            q_distance=self.q_distance,
            zoom_factor=self.zoom_factor,
            write_profile=self.write_profile)

        if self.write_input_wavefront:
            self.input_data.get_wavefront().save_h5_file("wavefront_input.h5",subgroupname="wfr",intensity=True,phase=True,overwrite=True,verbose=True)

        # script

        # input_wavefront,
        # angle_in = {angle_in},
        # angle_out = {angle_out},
        # grating_flag = {grating_flag},
        # grating_amplitude = {grating_amplitude},
        # points_per_period = {points_per_period},
        # g_0 = {g_0},
        # g_1 = {g_1},
        # g_2 = {g_2},
        # g_3 = {g_3},
        # grating_file = {grating_file},
        # p_distance = {p_distance},
        # q_distance = {q_distance},
        # zoom_factor = {zoom_factor},
        # write_profile = {write_profile}


        dict_parameters = {"angle_in": self.angle_in_deg,
                            "angle_out": self.angle_out_deg,
                            "grating_flag": self.grating_flag,
                            "grating_amplitude": self.grating_amplitude,
                            "points_per_period": self.points_per_period,
                            "g_0": self.g_0,
                            "g_1": self.g_1,
                            "g_2": self.g_2,
                            "g_3": self.g_3,
                            "grating_file": "'"+grating_file+"'",
                            "p_distance": self.p_distance,
                            "q_distance": self.q_distance,
                            "zoom_factor": self.zoom_factor,
                            "write_profile":self.write_profile}

        script_template = self.script_template_output_wavefront()
        self.wofry_script.set_code(script_template.format_map(dict_parameters))


        if self.view_type > 0:
            self.do_plot_wavefront(output_wavefront, abscissas_on_mirror, height)

        self.progressBarFinished()

        beamline = self.input_data.get_beamline().duplicate() # TODO add element here
        self.send("WofryData", WofryData(beamline=beamline, wavefront=output_wavefront))
        self.send("Trigger", TriggerIn(new_object=True))

    @classmethod
    def propagator1D_offaxis(cls, input_wavefront, x2_oe, y2_oe, p, q, theta_grazing_in, theta_grazing_out=None,
                             zoom_factor=1.0, normalize_intensities=False):

        from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D

        if theta_grazing_out is None:
            theta_grazing_out = theta_grazing_in

        x1 = input_wavefront.get_abscissas()
        field1 = input_wavefront.get_complex_amplitude()
        wavelength = input_wavefront.get_wavelength()

        x1_oe = -p * numpy.cos(theta_grazing_in) + x1 * numpy.sin(theta_grazing_in)
        y1_oe = p * numpy.sin(theta_grazing_in) + x1 * numpy.cos(theta_grazing_in)

        # field2 is the electric field in the mirror
        field2 = goFromToSequential(field1, x1_oe, y1_oe, x2_oe, y2_oe,
                                    wavelength=wavelength, normalize_intensities=normalize_intensities)

        x3 = x1 * zoom_factor

        x3_oe = q * numpy.cos(theta_grazing_out) + x3 * numpy.sin(theta_grazing_out)
        y3_oe = q * numpy.sin(theta_grazing_out) + x3 * numpy.cos(theta_grazing_out)

        # field2 is the electric field in the image plane
        field3 = goFromToSequential(field2, x2_oe, y2_oe, x3_oe, y3_oe,
                                    wavelength=wavelength, normalize_intensities=normalize_intensities)

        output_wavefront = GenericWavefront1D.initialize_wavefront_from_arrays(x3, field3, wavelength=wavelength)

        return output_wavefront



    @classmethod
    def create_grating(cls, grating_length=0.150,
                       points_per_period=9,
                       grating_flag=0,
                       g_0=300000.0,
                       g_1=0.0,
                       g_2=0.0,
                       g_3=0.0):

        lines_per_m = g_0
        period = 1. / lines_per_m
        number_of_periods = grating_length / period
        print("Number of periods: ", number_of_periods)
        print("Period: %f um" % (1e6 * period))

        x = numpy.linspace(-grating_length / 2, grating_length / 2, int(points_per_period * number_of_periods))
        if grating_flag == 0:  # sin
            y = (numpy.sin(2 * numpy.pi * x / period) + 1) / 2
        elif grating_flag == 1:  # cos
            y = (numpy.cos(2 * numpy.pi * x / period) + 1) / 2
        elif grating_flag == 2:  # square
            from scipy.signal import square
            y = (square(2 * numpy.pi * x / period, duty=0.5) + 1) / 2
        elif grating_flag == 3:  # vls
            from scipy.signal import sweep_poly
            p = numpy.poly1d([g_3, g_2, g_1, g_0])
            y = numpy.ceil(sweep_poly(x, p))
        return x, y



    @classmethod
    def calculate_output_wavefront_after_grating1D(cls,input_wavefront,
                                                   angle_in=88.0,
                                                   angle_out=87.0,
                                                   grating_flag=3,
                                                   grating_amplitude=20e-9,
                                                   grating_length=150e-3,
                                                   points_per_period=5,
                                                   g_0=300000.0,
                                                   g_1=0.0,
                                                   g_2=0.0,
                                                   g_3=0.0,
                                                   grating_file="",
                                                   p_distance=1.0,
                                                   q_distance=1.0,
                                                   zoom_factor=1.0,
                                                   write_profile=0):

        grazing_angle_in = (90 - angle_in) * numpy.pi / 180
        grazing_angle_out = (90 - numpy.abs(angle_out)) * numpy.pi / 180

        x1 = input_wavefront.get_abscissas()
        field1 = input_wavefront.get_complex_amplitude()

        if grating_flag == 4: # grating profile from file
            a = numpy.loadtxt(grating_file)
            x2_oe = a[:, 0]
            y2_oe = a[:, 1]
        else:
            x2_oe,y2_oe = cls.create_grating(
                           grating_length=grating_length,
                           points_per_period=points_per_period,
                           grating_flag=grating_flag,
                           g_0=g_0, g_1=g_1, g_2=g_2, g_3=g_3)
            y2_oe -= y2_oe.min()
            y2_oe /= y2_oe.max()
            y2_oe *= grating_amplitude

        output_wavefront = cls.propagator1D_offaxis(input_wavefront, x2_oe, y2_oe,
                                                     p_distance,q_distance,
                                                     grazing_angle_in, grazing_angle_out,
                                                     zoom_factor=zoom_factor,normalize_intensities=True)

        # output files
        if write_profile:
            f = open("grating_profile1D.dat","w")
            for i in range(x2_oe.size):
                f.write("%g %g\n"%(x2_oe[i],y2_oe[i]))
            f.close()
            print("File grating_profile1D.dat written to disk.")

        return output_wavefront, x2_oe, y2_oe


    # warning: pay attention to the double backslash in \\n
    def script_template_output_wavefront(self):
        return \
"""

import numpy
from numba import jit, prange

@jit(nopython=True, parallel=True)
def goFromToSequential(field1, x1, y1, x2, y2, wavelength=1e-10, normalize_intensities=False):
    field2 = x2 * 0j
    wavenumber = numpy.pi * 2 / wavelength

    for i in prange(field2.size):
        r = numpy.sqrt(numpy.power(x1 - x2[i], 2) + numpy.power(y1 - y2[i], 2))
        field2[i] = (field1 * numpy.exp(1.j * wavenumber * r)).sum()

    if normalize_intensities:
        field2 *= numpy.sqrt((numpy.abs(field1) ** 2).sum() / (numpy.abs(field2) ** 2).sum())
    return field2


def propagator1D_offaxis(input_wavefront, x2_oe, y2_oe, p, q, theta_grazing_in, theta_grazing_out=None,
                         zoom_factor=1.0, normalize_intensities=False):

    from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D

    if theta_grazing_out is None:
        theta_grazing_out = theta_grazing_in

    x1 = input_wavefront.get_abscissas()
    field1 = input_wavefront.get_complex_amplitude()
    wavelength = input_wavefront.get_wavelength()

    x1_oe = -p * numpy.cos(theta_grazing_in) + x1 * numpy.sin(theta_grazing_in)
    y1_oe = p * numpy.sin(theta_grazing_in) + x1 * numpy.cos(theta_grazing_in)

    # field2 is the electric field in the mirror
    field2 = goFromToSequential(field1, x1_oe, y1_oe, x2_oe, y2_oe,
                                wavelength=wavelength, normalize_intensities=normalize_intensities)

    x3 = x1 * zoom_factor

    x3_oe = q * numpy.cos(theta_grazing_out) + x3 * numpy.sin(theta_grazing_out)
    y3_oe = q * numpy.sin(theta_grazing_out) + x3 * numpy.cos(theta_grazing_out)

    # field2 is the electric field in the image plane
    field3 = goFromToSequential(field2, x2_oe, y2_oe, x3_oe, y3_oe,
                                wavelength=wavelength, normalize_intensities=normalize_intensities)

    output_wavefront = GenericWavefront1D.initialize_wavefront_from_arrays(x3, field3, wavelength=wavelength)

    return output_wavefront

def create_grating(grating_length=0.150,
                   points_per_period=9,
                   grating_flag=0,
                   g_0=300000.0,
                   g_1=0.0,
                   g_2=0.0,
                   g_3=0.0):

    lines_per_m = g_0
    period = 1. / lines_per_m
    number_of_periods = grating_length / period
    print("Number of periods: ", number_of_periods)
    print("Period: %f um" % (1e6 * period))

    x = numpy.linspace(-grating_length / 2, grating_length / 2, int(points_per_period * number_of_periods))
    if grating_flag == 0:  # sin
        y = (numpy.sin(2 * numpy.pi * x / period) + 1) / 2
    elif grating_flag == 1:  # cos
        y = (numpy.cos(2 * numpy.pi * x / period) + 1) / 2
    elif grating_flag == 2:  # square
        from scipy.signal import square
        y = (square(2 * numpy.pi * x / period, duty=0.5) + 1) / 2
    elif grating_flag == 3:  # vls
        from scipy.signal import sweep_poly
        p = numpy.poly1d([g_3, g_2, g_1, g_0])
        y = numpy.ceil(sweep_poly(x, p))
    return x, y


def calculate_output_wavefront_after_grating1D(input_wavefront,
                                               angle_in=88.0,
                                               angle_out=87.0,
                                               grating_flag=3,
                                               grating_amplitude=20e-9,
                                               grating_length=150e-3,
                                               points_per_period=5,
                                               g_0=300000.0,
                                               g_1=0.0,
                                               g_2=0.0,
                                               g_3=0.0,
                                               grating_file="",
                                               p_distance=1.0,
                                               q_distance=1.0,
                                               zoom_factor=1.0,
                                               write_profile=0):

    grazing_angle_in = (90 - angle_in) * numpy.pi / 180
    grazing_angle_out = (90 - numpy.abs(angle_out)) * numpy.pi / 180

    x1 = input_wavefront.get_abscissas()
    field1 = input_wavefront.get_complex_amplitude()

    if grating_flag == 4: # grating profile from file
        a = numpy.loadtxt(grating_file)
        x2_oe = a[:, 0]
        y2_oe = a[:, 1]
    else:
        x2_oe,y2_oe = create_grating(
                       grating_length=grating_length,
                       points_per_period=points_per_period,
                       grating_flag=grating_flag,
                       g_0=g_0, g_1=g_1, g_2=g_2, g_3=g_3)
        y2_oe -= y2_oe.min()
        y2_oe /= y2_oe.max()
        y2_oe *= grating_amplitude

    output_wavefront = propagator1D_offaxis(input_wavefront, x2_oe, y2_oe,
                                                 p_distance,q_distance,
                                                 grazing_angle_in, grazing_angle_out,
                                                 zoom_factor=zoom_factor,normalize_intensities=True)

    # output files
    if write_profile:
        f = open("grating_profile1D.dat","w")
        for i in range(x2_oe.size):
            f.write("%g %g\\n"%(x2_oe[i],y2_oe[i]))
        f.close()
        print("File grating_profile1D.dat written to disk.")

    return output_wavefront, x2_oe, y2_oe
        
#
# main
#
from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D
input_wavefront = GenericWavefront1D.load_h5_file("wavefront_input.h5","wfr")


                                        
output_wavefront, abscissas_on_mirror, height = calculate_output_wavefront_after_grating1D(
            input_wavefront,
            angle_in={angle_in},
            angle_out={angle_out},
            grating_flag={grating_flag},
            grating_amplitude={grating_amplitude},
            points_per_period={points_per_period},
            g_0={g_0},
            g_1={g_1},
            g_2={g_2},
            g_3={g_3},
            grating_file={grating_file},
            p_distance={p_distance},
            q_distance={q_distance},
            zoom_factor={zoom_factor},
            write_profile={write_profile})
            
from srxraylib.plot.gol import plot
plot(output_wavefront.get_abscissas(),output_wavefront.get_intensity())
"""

    def do_plot_results(self, progressBarValue): # required by parent
        pass

    def do_plot_wavefront(self, wavefront1D, abscissas_on_mirror, height, progressBarValue=80):
        if not self.input_data is None:

            self.progressBarSet(progressBarValue)


            self.plot_data1D(x=1e6*wavefront1D.get_abscissas(),
                             y=wavefront1D.get_intensity(),
                             progressBarValue=progressBarValue,
                             tabs_canvas_index=0,
                             plot_canvas_index=0,
                             calculate_fwhm=True,
                             title=self.titles[0],
                             xtitle="Spatial Coordinate [$\mu$m]",
                             ytitle="Intensity")

            self.plot_data1D(x=1e6*wavefront1D.get_abscissas(),
                             y=wavefront1D.get_phase(from_minimum_intensity=0.1,unwrap=1),
                             progressBarValue=progressBarValue + 10,
                             tabs_canvas_index=1,
                             plot_canvas_index=1,
                             calculate_fwhm=False,
                             title=self.titles[1],
                             xtitle="Spatial Coordinate [$\mu$m]",
                             ytitle="Phase [unwrapped, for intensity > 10% of peak] (rad)")

            self.plot_data1D(x=1e6*wavefront1D.get_abscissas(),
                             y=numpy.real(wavefront1D.get_complex_amplitude()),
                             progressBarValue=progressBarValue + 10,
                             tabs_canvas_index=2,
                             plot_canvas_index=2,
                             calculate_fwhm=False,
                             title=self.titles[2],
                             xtitle="Spatial Coordinate [$\mu$m]",
                             ytitle="Real(Amplitude)")

            self.plot_data1D(x=1e6*wavefront1D.get_abscissas(),
                             y=numpy.imag(wavefront1D.get_complex_amplitude()),
                             progressBarValue=progressBarValue + 10,
                             tabs_canvas_index=3,
                             plot_canvas_index=3,
                             calculate_fwhm=False,
                             title=self.titles[3],
                             xtitle="Spatial Coordinate [$\mu$m]",
                             ytitle="Imag(Amplitude)")

            self.plot_data1D(x=abscissas_on_mirror,
                             y=1e6*height,
                             progressBarValue=progressBarValue + 10,
                             tabs_canvas_index=4,
                             plot_canvas_index=4,
                             calculate_fwhm=False,
                             title=self.titles[4],
                             xtitle="Spatial Coordinate along o.e. [m]",
                             ytitle="Profile Height [$\mu$m]")

            self.plot_canvas[0].resetZoom()

if __name__ == '__main__':

    from PyQt5.QtWidgets import QApplication


    def create_wavefront():
        #
        # create input_wavefront
        #
        from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D
        input_wavefront = GenericWavefront1D.initialize_wavefront_from_range(x_min=-0.00147, x_max=0.00147,
                                                                             number_of_points=1000)
        input_wavefront.set_photon_energy(250)
        input_wavefront.set_spherical_wave(radius=13.73, center=0, complex_amplitude=complex(1, 0))
        return input_wavefront

    app = QApplication([])
    ow = OWGrating1D()
    ow.set_input(create_wavefront())

    # ow.receive_dabam_profile(numpy.array([[1,2],[3,4]]))
    ow.propagate_wavefront()

    ow.show()
    app.exec_()
    ow.saveSettings()

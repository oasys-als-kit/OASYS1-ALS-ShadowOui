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

from syned.widget.widget_decorator import WidgetDecorator

from orangecontrib.wofry.util.wofry_objects import WofryData
from orangecontrib.wofry.widgets.gui.ow_wofry_widget import WofryWidget
from orangecontrib.xoppy.util.python_script import PythonScript  # TODO: change import from wofry!!!

from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D


class OWReflector1D(WofryWidget):

    name = "Wofry Reflector 1D"
    id = "WofryReflector1D"
    description = "Wofry Reflector 1D"
    icon = "icons/reflector1D.png"
    priority = 3

    category = "Wofry Wavefront Propagation"
    keywords = ["data", "file", "load", "read"]

    outputs = [{"name":"WofryData",
                "type":WofryData,
                "doc":"WofryData",
                "id":"WofryData"},
               {"name":"Trigger",
                "type": TriggerIn,
                "doc":"Feedback signal to start a new beam simulation",
                "id":"Trigger"}]

    inputs = [("WofryData", WofryData, "set_input"),
              ("GenericWavefront2D", GenericWavefront1D, "set_input"),
              WidgetDecorator.syned_input_data()[0]]


    grazing_angle = Setting(1.5e-3)
    shape = Setting(1)
    radius = Setting(1000.0)
    error_flag = Setting(0)
    error_file = Setting("<none>")
    error_edge_management = Setting(0)
    write_profile = Setting(0)
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

        self.tab_sou = oasysgui.createTabPage(tabs_setting, "Generic Reflector 1D Settings")

        box_reflector = oasysgui.widgetBox(self.tab_sou, "Reflector", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(box_reflector, self, "grazing_angle", "Grazing angle [rad]",
                          labelWidth=300, valueType=float, orientation="horizontal")



        gui.comboBox(box_reflector, self, "shape", label="Reflector shape", labelWidth=350,
                     items=["Flat","Curved"], sendSelectedValue=False, orientation="horizontal",callback=self.set_visible)


        self.box_radius_id = oasysgui.widgetBox(box_reflector, "", addSpace=True, orientation="horizontal")
        oasysgui.lineEdit(self.box_radius_id, self, "radius", "Radius of curvature [m] (R<0 if convex)",
                          labelWidth=300, valueType=float, orientation="horizontal")


        gui.comboBox(box_reflector, self, "error_flag", label="Add profile deformation",
                     items=["No","Yes (from file)"],
                     callback=self.set_visible,
                     sendSelectedValue=False, orientation="horizontal")

        self.error_profile = oasysgui.widgetBox(box_reflector, "", addSpace=True, orientation="vertical")
        file_box_id = oasysgui.widgetBox(self.error_profile, "", addSpace=True, orientation="horizontal")

        self.error_file_id = oasysgui.lineEdit(file_box_id, self, "error_file", "Error file X[m] Y[m]",
                                                    labelWidth=100, valueType=str, orientation="horizontal")
        gui.button(file_box_id, self, "...", callback=self.set_error_file)

        gui.comboBox(self.error_profile, self, "error_edge_management", label="Manage edges",
                     items=["Extrapolate deformation profile","Crop beam to deformation profile dimension"],
                     callback=self.set_visible,
                     sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(box_reflector, self, "write_profile", label="Dump profile to file",
                     items=["No","Yes [reflector_profile1D.dat]"], sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(box_reflector, self, "write_input_wavefront", label="Input wf to file (for script)",
                     items=["No","Yes [wavefront_input.h5]"], sendSelectedValue=False, orientation="horizontal")



        self.set_visible()

    def set_visible(self):
        self.error_profile.setVisible(self.error_flag)
        self.box_radius_id.setVisible(self.shape)

    def set_error_file(self):
        self.error_file_id.setText(oasysgui.selectFileFromDialog(self, self.error_file, "Open file with profile error"))

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
        self.grazing_angle = congruence.checkStrictlyPositiveNumber(self.grazing_angle, "Grazing angle")
        self.radius = congruence.checkNumber(self.radius, "Radius")
        self.error_file = congruence.checkFileName(self.error_file)

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

                self.error_flag = 1
                self.error_file = file_name
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

        if self.error_flag == 0:
            error_file = ""
        else:
            error_file = self.error_file

        output_wavefront, abscissas_on_mirror, height = self.calculate_output_wavefront_after_reflector1D(self.input_data.get_wavefront(),
                                                                       shape=self.shape,
                                                                       radius=self.radius,
                                                                       grazing_angle=self.grazing_angle,
                                                                       error_flag=self.error_flag,
                                                                       error_file=error_file,
                                                                       error_edge_management=self.error_edge_management,
                                                                       write_profile=self.write_profile)

        if self.write_input_wavefront:
            self.input_data.get_wavefront().save_h5_file("wavefront_input.h5",subgroupname="wfr",intensity=True,phase=True,overwrite=True,verbose=True)

        # script
        dict_parameters = {"grazing_angle": self.grazing_angle,
                           "shape": self.shape,
                           "radius": self.radius,
                           "error_flag":self.error_flag,
                           "error_file":error_file,
                           "error_edge_management": self.error_edge_management,
                           "write_profile":self.write_profile}

        script_template = self.script_template_output_wavefront_from_radius()
        self.wofry_script.set_code(script_template.format_map(dict_parameters))


        self.do_plot_wavefront(output_wavefront, abscissas_on_mirror, height)

        beamline = self.input_data.get_beamline().duplicate()
        # self.send("GenericWavefront1D", output_wavefront)
        self.send("WofryData", WofryData(beamline=beamline, wavefront=output_wavefront))
        self.send("Trigger", TriggerIn(new_object=True))

    @classmethod
    def calculate_output_wavefront_after_reflector1D(cls,input_wavefront,shape=1,radius=10000.0,grazing_angle=1.5e-3,
                                               error_flag=0, error_file="", error_edge_management=0, write_profile=0):

        output_wavefront = input_wavefront.duplicate()
        abscissas = output_wavefront.get_abscissas()
        abscissas_on_mirror = abscissas / numpy.sin(grazing_angle)

        if shape == 0:
            height = numpy.zeros_like(abscissas_on_mirror)
        elif shape == 1:
            if radius >= 0:
                height = radius - numpy.sqrt(radius ** 2 - abscissas_on_mirror ** 2)
            else:
                height = radius + numpy.sqrt(radius ** 2 - abscissas_on_mirror ** 2)
        else:
            raise Exception("Wrong shape")


        if error_flag:
            a = numpy.loadtxt(error_file) # extrapolation
            if error_edge_management == 0:
                finterpolate = interpolate.interp1d(a[:, 0], a[:, 1], fill_value="extrapolate")  # fill_value=(0,0),bounds_error=False)
            elif error_edge_management == 1:
                finterpolate = interpolate.interp1d(a[:,0], a[:,1],fill_value=(0,0),bounds_error=False)
            else: # crop
                raise Exception("Bad value of error_edge_management")
            height_interpolated = finterpolate( abscissas_on_mirror)
            height += height_interpolated

        phi = -2 * output_wavefront.get_wavenumber() * height * numpy.sin(grazing_angle)

        output_wavefront.add_phase_shifts(phi)

        if error_flag:
            profile_limits = a[-1, 0] - a[0, 0]
            profile_limits_projected = (a[-1,0] - a[0,0]) * numpy.sin(grazing_angle)
            wavefront_dimension = output_wavefront.get_abscissas()[-1] - output_wavefront.get_abscissas()[0]
            print("profile deformation dimension: %f m"%(profile_limits))
            print("profile deformation projected perpendicular to optical axis: %f um"%(1e6 * profile_limits_projected))
            print("wavefront window dimension: %f um" % (1e6 * wavefront_dimension))

            if wavefront_dimension <= profile_limits_projected:
                print("\nWavefront window inside error profile domain: no action needed")
            else:
                if error_edge_management == 0:
                    print("\nProfile deformation extrapolated to fit wavefront dimensions")
                else:
                    output_wavefront.clip(a[0,0] * numpy.sin(grazing_angle),a[-1,0] * numpy.sin(grazing_angle))
                    print("\nWavefront clipped to projected limits of profile deformation")

        # output files
        if write_profile:
            f = open("reflector_profile1D.dat","w")
            for i in range(height.size):
                f.write("%g %g\n"%(abscissas_on_mirror[i],height[i]))
            f.close()
            print("File reflector_profile1D.dat written to disk.")


        return output_wavefront, abscissas_on_mirror, height

    # warning: pay attention to the double backslash in \\n
    def script_template_output_wavefront_from_radius(self):
        return \
"""

def calculate_output_wavefront_after_reflector1D(input_wavefront,shape=1,radius=10000.0,grazing_angle=1.5e-3,error_flag=0, error_file="", error_edge_management=0, write_profile=0):
    import numpy
    from scipy import interpolate
    
    output_wavefront = input_wavefront.duplicate()
    abscissas = output_wavefront.get_abscissas()
    abscissas_on_mirror = abscissas / numpy.sin(grazing_angle)

    if shape == 0:
        height = numpy.zeros_like(abscissas_on_mirror)
    elif shape == 1:
        if radius >= 0:
            height = radius - numpy.sqrt(radius ** 2 - abscissas_on_mirror ** 2)
        else:
            height = radius + numpy.sqrt(radius ** 2 - abscissas_on_mirror ** 2)
    else:
        raise Exception("Wrong shape")


    if error_flag:
        a = numpy.loadtxt(error_file) # extrapolation
        if error_edge_management == 0:
            finterpolate = interpolate.interp1d(a[:, 0], a[:, 1], fill_value="extrapolate")  # fill_value=(0,0),bounds_error=False)
        elif error_edge_management == 1:
            finterpolate = interpolate.interp1d(a[:,0], a[:,1],fill_value=(0,0),bounds_error=False)
        else: # crop
            raise Exception("Bad value of error_edge_management")
        height_interpolated = finterpolate( abscissas_on_mirror)
        height += height_interpolated

    phi = -2 * output_wavefront.get_wavenumber() * height * numpy.sin(grazing_angle)

    output_wavefront.add_phase_shifts(phi)

    if error_flag:
        profile_limits = a[-1, 0] - a[0, 0]
        profile_limits_projected = (a[-1,0] - a[0,0]) * numpy.sin(grazing_angle)
        wavefront_dimension = output_wavefront.get_abscissas()[-1] - output_wavefront.get_abscissas()[0]
        print("profile deformation dimension: %f m"%(profile_limits))
        print("profile deformation projected perpendicular to optical axis: %f um"%(1e6 * profile_limits_projected))
        print("wavefront window dimension: %f um" % (1e6 * wavefront_dimension))

        if wavefront_dimension <= profile_limits_projected:
            print("\\nWavefront window inside error profile domain: no action needed")
        else:
            if error_edge_management == 0:
                print("\\nProfile deformation extrapolated to fit wavefront dimensions")
            else:
                output_wavefront.clip(a[0,0] * numpy.sin(grazing_angle),a[-1,0] * numpy.sin(grazing_angle))
                print("\\nWavefront clipped to projected limits of profile deformation")


    # output files
    if write_profile:
        f = open("reflector_profile1D.dat","w")
        for i in range(height.size):
            f.write("%g %g\\n"%(abscissas_on_mirror[i],height[i]))
        f.close()
        print("File reflector_profile1D.dat written to disk.")


    return output_wavefront, abscissas_on_mirror, height
        

#
# main
#
from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D
input_wavefront = GenericWavefront1D.load_h5_file("wavefront_input.h5","wfr")
output_wavefront, abscissas_on_mirror, height = calculate_output_wavefront_after_reflector1D(input_wavefront,shape={shape},radius={radius},grazing_angle={grazing_angle},error_flag={error_flag},error_file="{error_file}",error_edge_management={error_edge_management},write_profile={write_profile})

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

            self.progressBarFinished()

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
    ow = OWReflector1D()
    ow.set_input(create_wavefront())

    ow.receive_dabam_profile(numpy.array([[-1.50,0],[1.50,0]]))
    ow.propagate_wavefront()

    ow.show()
    app.exec_()
    ow.saveSettings()

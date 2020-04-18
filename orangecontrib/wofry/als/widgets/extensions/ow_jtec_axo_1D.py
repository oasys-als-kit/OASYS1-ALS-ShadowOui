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


class OWJtecAxo1D(WofryWidget):

    name = "Wofry JtecAxo1D"
    id = "JtecAxo1D"
    description = "Wofry JtecAxo1D"
    icon = "icons/jtec.png"
    priority = 3

    category = "Wofry Wavefront Propagation"
    keywords = ["data", "file", "load", "read", "AXO", "JTEC"]

    outputs = [{"name": "DABAM 1D Profile",
                "type": numpy.ndarray,
                "doc": "numpy.ndarray",
                "id": "numpy.ndarray"},]

    inputs = [("DABAM 1D Profile", numpy.ndarray, "receive_profile")]


    # grazing_angle = Setting(1.5e-3)
    # shape = Setting(1)
    # radius = Setting(1000.0)
    # error_flag = Setting(0)
    file_influence = Setting("C:/Users/Manuel/OASYS1.2/alsu-scripts/LEA/aps_axo_influence_functions2019.dat")
    file_orthonormal = Setting("C:/Users/Manuel/OASYS1.2/alsu-scripts/LEA/aps_axo_orthonormal_functions2019.dat")
    profile_from = Setting(0)
    file_profile = Setting("<none>")

    # error_edge_management = Setting(0)
    # write_profile = Setting(0)
    # write_input_wavefront = Setting(0)


    input_data = None
    titles = ["Input O.E. profile", "Output O.E. profile","Coefficients"]

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

        button = gui.button(button_box, self, "Calculate Coefficients", callback=self.calculate_coefficients)
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

        self.tab_sou = oasysgui.createTabPage(tabs_setting, "JTEC AXO Settings")

        #
        # basis
        #
        box_basis = oasysgui.widgetBox(self.tab_sou, "Basis", addSpace=False, orientation="vertical")

        #
        file_influence_box_id = oasysgui.widgetBox(box_basis, "", addSpace=True, orientation="horizontal")
        self.file_influence_id = oasysgui.lineEdit(file_influence_box_id, self, "file_influence", "Influence functions",
                                                   labelWidth=100, valueType=str, orientation="horizontal")
        gui.button(file_influence_box_id, self, "...", callback=self.set_file_influence)


        # orthonormal bases
        file_orthonormal_box_id = oasysgui.widgetBox(box_basis, "", addSpace=True, orientation="horizontal")
        self.file_orthonormal_id = oasysgui.lineEdit(file_orthonormal_box_id, self, "file_orthonormal", "Orthonormal functions",
                                                   labelWidth=100, valueType=str, orientation="horizontal")
        gui.button(file_orthonormal_box_id, self, "...", callback=self.set_file_orthonormal)
        gui.button(file_orthonormal_box_id, self, "Create", callback=self.create_orthonormal)

        #
        # profile
        #
        box_profile = oasysgui.widgetBox(self.tab_sou, "Profile", addSpace=False, orientation="vertical")

        gui.comboBox(box_profile, self, "profile_from", label="Profile",
                     items=["Flat","From Oasys wire","From file"],
                     # callback=self.set_visible,
                     sendSelectedValue=False, orientation="horizontal")

        #
        file_profile_box_id = oasysgui.widgetBox(box_profile, "", addSpace=True, orientation="horizontal")
        self.file_profile_id = oasysgui.lineEdit(file_profile_box_id, self, "file_profile", "File with profile",
                                                   labelWidth=100, valueType=str, orientation="horizontal")
        gui.button(file_profile_box_id, self, "...", callback=self.set_file_profile)
        self.show_at("self.profile_from == 2", file_profile_box_id)

        #
        # gui.comboBox(box_reflector, self, "write_profile", label="Dump profile to file",
        #              items=["No","Yes [reflector_profile1D.dat]"], sendSelectedValue=False, orientation="horizontal")
        #
        # gui.comboBox(box_reflector, self, "write_input_wavefront", label="Input wf to file (for script)",
        #              items=["No","Yes [wavefront_input.h5]"], sendSelectedValue=False, orientation="horizontal")

        # gui.rubber(self.mainArea)

    #     self.set_visible()
    #
    # def set_visible(self):
    #     self.file_profile_id.setVisible(self.profile_from == 2)
    #     # self.box_radius_id.setVisible(self.shape)

        # gui.button(file_orthonormal_box_id, self, "...", callback=self.set_file_orthonormal)
        # gui.button(file_orthonormal_box_id, self, "Create", callback=self.create_orthonormal)

    def set_file_influence(self):
        self.file_influence_id.setText(oasysgui.selectFileFromDialog(self, self.file_influence, "Open file influence basis"))

    def set_file_orthonormal(self):
        self.file_orthonormal_id.setText(oasysgui.selectFileFromDialog(self, self.file_influence, "Open file with orthonormal basis"))

    def set_file_profile(self):
        self.file_orthonormal_id.setText(
            oasysgui.selectFileFromDialog(self, self.file_profile, "Open file with profile"))

    def create_orthonormal(self):
        pass

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
        pass
        # self.grazing_angle = congruence.checkStrictlyPositiveNumber(self.grazing_angle, "Grazing angle")
        # self.radius = congruence.checkNumber(self.radius, "Radius")
        # self.error_file = congruence.checkFileName(self.error_file)

    # def receive_syned_data(self):
    #     raise Exception(NotImplementedError)


    def receive_profile(self, dabam_profile):
        pass
        if not dabam_profile is None:
            try:
                file_name = "profile_" + str(id(self)) + ".dat"

                file = open(file_name, "w")

                for element in dabam_profile:
                    file.write(str(element[0]) + " " + str(element[1]) + "\n")

                file.flush()
                file.close()

                self.error_flag = 1
                self.file_profile = file_name
                # self.set_visible()

            except Exception as exception:
                QMessageBox.critical(self, "Error", exception.args[0], QMessageBox.Ok)

                if self.IS_DEVELOP: raise exception

    def calculate_coefficients(self):
        self.progressBarInit()

        self.wofry_output.setText("")
        sys.stdout = EmittingStream(textWritten=self.writeStdOut)

        self.check_fields()
        print(">>>>>callig do_plot_results...")
        self.do_plot_results(20.0)

        # if self.input_data is None: raise Exception("No Input Wavefront")
        #
        # if self.error_flag == 0:
        #     error_file = ""
        # else:
        #     error_file = self.error_file
        #
        # output_wavefront, abscissas_on_mirror, height = self.calculate_output_wavefront_after_reflector1D(self.input_data.get_wavefront(),
        #                                                                shape=self.shape,
        #                                                                radius=self.radius,
        #                                                                grazing_angle=self.grazing_angle,
        #                                                                error_flag=self.error_flag,
        #                                                                error_file=error_file,
        #                                                                error_edge_management=self.error_edge_management,
        #                                                                write_profile=self.write_profile)
        #
        # if self.write_input_wavefront:
        #     self.input_data.get_wavefront().save_h5_file("wavefront_input.h5",subgroupname="wfr",intensity=True,phase=True,overwrite=True,verbose=True)
        #
        # # script
        # dict_parameters = {"grazing_angle": self.grazing_angle,
        #                    "shape": self.shape,
        #                    "radius": self.radius,
        #                    "error_flag":self.error_flag,
        #                    "error_file":error_file,
        #                    "error_edge_management": self.error_edge_management,
        #                    "write_profile":self.write_profile}
        #
        # script_template = self.script_template_output_wavefront_from_radius()
        # self.wofry_script.set_code(script_template.format_map(dict_parameters))
        #
        #
        # self.do_plot_wavefront(output_wavefront, abscissas_on_mirror, height)
        #
        # beamline = self.input_data.get_beamline().duplicate()
        # self.send("GenericWavefront1D", output_wavefront)
        # self.send("WofryData", WofryData(beamline=beamline, wavefront=output_wavefront))
        # self.send("Trigger", TriggerIn(new_object=True))


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

        self.progressBarSet(progressBarValue)
        print(">>>>>>> plotting file: %s" % self.file_profile)
        try:
            a = numpy.loadtxt(self.file_profile)
        except:
            return

        print(">>>>>",a.shape)
        self.plot_data1D(x=a[:,0],
                         y=a[:,1],
                         progressBarValue=progressBarValue,
                         tabs_canvas_index=0,
                         plot_canvas_index=0,
                         calculate_fwhm=True,
                         title=self.titles[0],
                         xtitle="X [m]",
                         ytitle="Y [m]")


    # def do_plot_wavefront(self, wavefront1D, abscissas_on_mirror, height, progressBarValue=80):
    #     if not self.input_data is None:
    #
    #         self.progressBarSet(progressBarValue)
    #
    #
    #         self.plot_data1D(x=1e6*wavefront1D.get_abscissas(),
    #                          y=wavefront1D.get_intensity(),
    #                          progressBarValue=progressBarValue,
    #                          tabs_canvas_index=0,
    #                          plot_canvas_index=0,
    #                          calculate_fwhm=True,
    #                          title=self.titles[0],
    #                          xtitle="Spatial Coordinate [$\mu$m]",
    #                          ytitle="Intensity")
    #
    #         self.plot_data1D(x=1e6*wavefront1D.get_abscissas(),
    #                          y=wavefront1D.get_phase(from_minimum_intensity=0.1,unwrap=1),
    #                          progressBarValue=progressBarValue + 10,
    #                          tabs_canvas_index=1,
    #                          plot_canvas_index=1,
    #                          calculate_fwhm=False,
    #                          title=self.titles[1],
    #                          xtitle="Spatial Coordinate [$\mu$m]",
    #                          ytitle="Phase [unwrapped, for intensity > 10% of peak] (rad)")
    #
    #         self.plot_data1D(x=1e6*wavefront1D.get_abscissas(),
    #                          y=numpy.real(wavefront1D.get_complex_amplitude()),
    #                          progressBarValue=progressBarValue + 10,
    #                          tabs_canvas_index=2,
    #                          plot_canvas_index=2,
    #                          calculate_fwhm=False,
    #                          title=self.titles[2],
    #                          xtitle="Spatial Coordinate [$\mu$m]",
    #                          ytitle="Real(Amplitude)")
    #
    #         self.plot_data1D(x=1e6*wavefront1D.get_abscissas(),
    #                          y=numpy.imag(wavefront1D.get_complex_amplitude()),
    #                          progressBarValue=progressBarValue + 10,
    #                          tabs_canvas_index=3,
    #                          plot_canvas_index=3,
    #                          calculate_fwhm=False,
    #                          title=self.titles[3],
    #                          xtitle="Spatial Coordinate [$\mu$m]",
    #                          ytitle="Imag(Amplitude)")
    #
    #         self.plot_data1D(x=abscissas_on_mirror,
    #                          y=1e6*height,
    #                          progressBarValue=progressBarValue + 10,
    #                          tabs_canvas_index=4,
    #                          plot_canvas_index=4,
    #                          calculate_fwhm=False,
    #                          title=self.titles[4],
    #                          xtitle="Spatial Coordinate along o.e. [m]",
    #                          ytitle="Profile Height [$\mu$m]")
    #
    #         self.plot_canvas[0].resetZoom()
    #
    #         self.progressBarFinished()

if __name__ == '__main__':

    from PyQt5.QtWidgets import QApplication



    app = QApplication([])
    ow = OWJtecAxo1D()
    # ow.set_input(create_wavefront())

    # ow.receive_profile(numpy.array([[-1.50,0],[1.50,0]]))
    ow.file_profile = "C:/Users/Manuel/OASYS1.2/ML_Optics/oasys_scripts/correction.dat"
    # ow.propagate_wavefront()

    ow.show()
    app.exec_()
    ow.saveSettings()

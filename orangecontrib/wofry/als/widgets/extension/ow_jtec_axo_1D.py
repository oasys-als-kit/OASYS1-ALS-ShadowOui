import numpy
import sys, os



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

import orangecanvas.resources as resources

from orangecontrib.wofry.als.util.axo_fit_profile import axo_fit_profile, calculate_orthonormal_basis

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
# from matplotlib.figure import Figure
import matplotlib.pyplot as plt

class OWJtecAxo1D(WofryWidget):

    name = "JtecAxo1D"
    id = "JtecAxo1D"
    description = "ALS JtecAxo1D"
    icon = "icons/jtec.png"
    priority = 7

    category = "Wofry Wavefront Propagation"
    keywords = ["data", "file", "load", "read", "AXO", "JTEC"]

    outputs = [{"name": "DABAM 1D Profile",
                "type": numpy.ndarray,
                "doc": "numpy.ndarray",
                "id": "numpy.ndarray"},]

    inputs = [("DABAM 1D Profile", numpy.ndarray, "receive_profile")]

    file_influence =   Setting(os.path.join(resources.package_dirname("orangecontrib.wofry.als.util"), "data", "aps_axo_influence_functions2019.dat"))
    file_orthonormal = Setting(os.path.join(resources.package_dirname("orangecontrib.wofry.als.util"), "data", "aps_axo_orthonormal_functions2019.dat"))
    file_profile = Setting("<none>")
    file_profile_out_flag = Setting(0)
    file_profile_out = Setting("jtec_profile1D.dat")


    input_data = None
    titles = ["Input O.E. profile", "Output O.E. profile","Compare profiles","Coefficients"]

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
        gui.button(file_influence_box_id, self, "...", width=25, callback=self.set_file_influence)


        # orthonormal bases
        file_orthonormal_box_id = oasysgui.widgetBox(box_basis, "", addSpace=True, orientation="horizontal")
        self.file_orthonormal_id = oasysgui.lineEdit(file_orthonormal_box_id, self, "file_orthonormal", "Orthonormal functions",
                                                   labelWidth=100, valueType=str, orientation="horizontal")
        gui.button(file_orthonormal_box_id, self, "...", width=25, callback=self.set_file_orthonormal)
        gui.button(file_orthonormal_box_id, self, "Create", width=45, callback=self.create_orthonormal)

        #
        # profile
        #
        box_profile = oasysgui.widgetBox(self.tab_sou, "Profile", addSpace=False, orientation="vertical")

        #
        file_profile_box_id = oasysgui.widgetBox(box_profile, "", addSpace=True, orientation="horizontal")
        self.file_profile_id = oasysgui.lineEdit(file_profile_box_id, self, "file_profile", "File with profile",
                                                   labelWidth=100, valueType=str, orientation="horizontal")
        gui.button(file_profile_box_id, self, "...", width=25, callback=self.set_file_profile)

        gui.comboBox(box_profile, self, "file_profile_out_flag", label="Write fitted profile to file",
                     items=["No","Yes",],
                     sendSelectedValue=False, orientation="horizontal",
                     callback=self.set_visible)
        #
        self.box_file_out = oasysgui.widgetBox(box_profile, "", addSpace=False, orientation="vertical")
        oasysgui.lineEdit(self.box_file_out, self, "file_profile_out", "Fitted profile file",
                            labelWidth=200, valueType=str, orientation="horizontal")

        self.set_visible()

    def set_visible(self):
        self.box_file_out.setVisible(self.file_profile_out_flag == 1)
    # self.show_at("s", t)

    def set_file_influence(self):
        self.file_influence_id.setText(oasysgui.selectFileFromDialog(self, self.file_influence, "Open file influence basis"))

    def set_file_orthonormal(self):
        self.file_orthonormal_id.setText(oasysgui.selectFileFromDialog(self, self.file_influence, "Open file with orthonormal basis"))

    def set_file_profile(self):
        self.file_orthonormal_id.setText(
            oasysgui.selectFileFromDialog(self, self.file_profile, "Open file with profile"))

    def create_orthonormal(self):
        file_orthonormal_functions = "aps_axo_orthonormal_functions2019"
        calculate_orthonormal_basis(file_influence_functions=self.file_influence,
                                    file_orthonormal_functions=file_orthonormal_functions,
                                    mask=None,
                                    do_plot=False, )
        self.file_orthonormal = file_orthonormal_functions

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

                if self.is_automatic_execution:
                    self.calculate_coefficients()

            except Exception as exception:
                QMessageBox.critical(self, "Error", exception.args[0], QMessageBox.Ok)

                if self.IS_DEVELOP: raise exception

    def calculate_coefficients(self):
        self.progressBarInit()

        self.wofry_output.setText("")
        sys.stdout = EmittingStream(textWritten=self.writeStdOut)

        self.check_fields()

        #
        # calculations
        #
        if self.file_profile_out_flag == 0:
            fileout = ""
        else:
            fileout = self.file_profile_out

        v, abscissas, u, y = axo_fit_profile(self.file_profile,
                                         fileout=fileout,
                                         file_influence_functions=self.file_influence,
                                         file_orthonormal_functions=self.file_orthonormal,
                                         calculate=False)

        print("\n\nCoefficients of the orthonormal basis: ")
        v_labels = []
        for i in range(v.size):
            v_labels.append("[%d]" % i)
            print("v[%d] = %5.2f nm" % (i, 1e9 * v[i]))

        self.progressBarSet(80)

        if self.view_type > 0:
            #
            # plots
            #
            print("\n\nPlotting file with input profile: %s" % self.file_profile)
            try:
                a = numpy.loadtxt(self.file_profile)
            except:
                return

            self.plot_data1D(x=a[:,0],
                             y=a[:,1],
                             progressBarValue=30,
                             tabs_canvas_index=0,
                             plot_canvas_index=0,
                             calculate_fwhm=False,
                             title=self.titles[0],
                             xtitle="X [m]",
                             ytitle="Y [m]")

            self.plot_data1D(x=abscissas*1e-3,
                             y=y,
                             progressBarValue=30,
                             tabs_canvas_index=1,
                             plot_canvas_index=0,
                             calculate_fwhm=False,
                             title=self.titles[0],
                             xtitle="X [m]",
                             ytitle="Y [m]")

            self.plot_data1D(x=abscissas*1e-3,
                             y=y,
                             progressBarValue=30,
                             tabs_canvas_index=2,
                             plot_canvas_index=0,
                             calculate_fwhm=False,
                             title="Fitted profile",
                             xtitle="X [m]",
                             ytitle="Y [m]",
                             color='green')


            self.plot_canvas[0].addCurve(a[:,0], a[:,1],
                                             "Input profile",
                                             xlabel="X [m]", ylabel="Y [m]",
                                             symbol='', color='red')

            # self.plot_canvas[0].setActiveCurve("Click on curve to highlight it")
            self.plot_canvas[0].getLegendsDockWidget().setFixedHeight(150)
            self.plot_canvas[0].getLegendsDockWidget().setVisible(True)

            # plot coeffs
            print(self.plot_canvas)
            self.tab[3].layout().removeItem(self.tab[3].layout().itemAt(1))
            self.tab[3].layout().removeItem(self.tab[3].layout().itemAt(0))

            f = plt.figure()

            y_pos = numpy.arange(v.size)
            plt.bar(y_pos, v, align='center', alpha=0.5)
            plt.xticks(y_pos, v_labels)
            plt.xlabel('Coefficient')
            plt.title('Coefficients')

            figure_canvas = FigureCanvasQTAgg(f)
            toolbar = NavigationToolbar(figure_canvas, self)

            self.tab[3].layout().addWidget(toolbar)
            self.tab[3].layout().addWidget(figure_canvas)

        self.progressBarFinished()
        #
        # send fit_profile
        #

        dabam_profile = numpy.zeros((abscissas.size, 2))
        dabam_profile[:, 0] = abscissas * 1e-3
        dabam_profile[:, 1] = y
        self.send("DABAM 1D Profile", dabam_profile)

        #
        # script
        #
        dict_parameters = {"fileout": fileout,
                           "file_profile": self.file_profile.replace("\\","/"),
                           "file_influence": self.file_influence.replace("\\","/"),
                           "file_orthonormal": self.file_orthonormal.replace("\\","/")}

        script_template = self.script_template_jtec_axo_1D()
        self.wofry_script.set_code(script_template.format_map(dict_parameters))


    def script_template_jtec_axo_1D(self):
        return \
"""#
# main
#
from orangecontrib.wofry.als.util.axo_fit_profile import axo_fit_profile

coeffs, abscissas, interpolated, fitted = axo_fit_profile("{file_profile}",
                                 fileout="{fileout}",
                                 file_influence_functions="{file_influence}",
                                 file_orthonormal_functions="{file_orthonormal}",
                                 calculate=False)
                                 
# plot
from srxraylib.plot.gol import plot, set_qt
set_qt()
plot(abscissas, interpolated, abscissas, fitted, legend=["interpolated","fitted"], xtitle="X [m]", ytitle="Y [m]")
"""

    def do_plot_results(self, progressBarValue): # required by parent
        pass


if __name__ == '__main__':

    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    ow = OWJtecAxo1D()
    ow.file_profile = "C:/Users/Manuel/OASYS1.2/ML_Optics/oasys_scripts/correction.dat"

    ow.show()
    app.exec_()
    ow.saveSettings()

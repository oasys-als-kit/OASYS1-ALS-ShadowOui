import sys, os, platform
import numpy
from PyQt5.QtWidgets import QApplication, QMessageBox, QSizePolicy
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5 import QtGui, QtWidgets

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui, congruence
from oasys.widgets.exchange import DataExchangeObject
from orangecontrib.xoppy.util.xoppy_xraylib_util import xpower_calc

from oasys.widgets.exchange import DataExchangeObject
from orangecontrib.xoppy.widgets.gui.ow_xoppy_widget import XoppyWidget


import scipy.constants as codata
import orangecanvas.resources as resources


from oasys.util.oasys_util import EmittingStream, TTYGrabber

#
# TO DO: uncomment import and delete class when moving to xoppy
#
# from orangecontrib.xoppy.util.xoppy_util import locations
class locations:
    @classmethod
    def home_bin(cls):
        if platform.system() == "Windows":
            return resources.package_dirname("orangecontrib.xoppy.als.util") + "\\bin\windows\\"
        else:
            return resources.package_dirname("orangecontrib.xoppy.als.util") + "/bin/" + str(sys.platform) + "/"

    @classmethod
    def home_doc(cls):
        if platform.system() == "Windows":
            return resources.package_dirname("orangecontrib.xoppy.als.util") + "\doc_txt/"
        else:
            return resources.package_dirname("orangecontrib.xoppy.als.util") + "/doc_txt/"

    @classmethod
    def home_data(cls):
        if platform.system() == "Windows":
            return resources.package_dirname("orangecontrib.xoppy.als.util") + "\data/"
        else:
            return resources.package_dirname("orangecontrib.xoppy.als.util") + "/data/"

    @classmethod
    def home_bin_run(cls):
        return os.getcwd()


class OWsrcalc(XoppyWidget):
    name = "SRCALC"
    id = "orange.widgets.srcalc"
    description = "Power Absorbed and Transmitted by Optical Elements"
    icon = "icons/xoppy_xpower.png"
    priority = 80
    category = ""
    keywords = ["srcalc", "power"]

    # inputs = [("ExchangeData", DataExchangeObject, "acceptExchangeData")]


    RING_ENERGY = Setting(2.0)
    RING_CURRENT = Setting(0.5)
    KY = Setting(3.07)
    KX = Setting(0.0)
    NUMBER_OF_PERIODS = Setting(137)
    PERIOD_LENGTH = Setting(0.0288)
    NUMBER_OF_HARMONICS = Setting(-49)
    SOURCE_SCREEN_DISTANCE = Setting(13.73)
    HORIZONTAL_ACCEPTANCE = Setting(30.0)
    VERTICAL_ACCEPTANCE = Setting(15.0)
    NUMBER_OF_POINTS_H = Setting(31)
    NUMBER_OF_POINTS_V = Setting(21)
    ELECTRON_SIGMAS = Setting(4)
    SIGMAX = Setting(12.1e-3)
    SIGMAXP = Setting(5.7e-3)
    SIGMAY = Setting(14.7e-3)
    SIGMAYP = Setting(4.7e-3)
    NELEMENTS = Setting(2)

    EL0_SHAPE = Setting(2)
    EL0_P = Setting(0.0)
    EL0_Q = Setting(0.0)
    EL0_ANG = Setting(88.75)
    EL0_THICKNESS = Setting(1000)
    EL0_RELATIVE_TO_PREVIOUS = Setting(0)
    EL0_COATING = Setting(1)

    EL1_SHAPE = Setting(2)
    EL1_P = Setting(0.0)
    EL1_Q = Setting(0.0)
    EL1_ANG = Setting(90.0 - 2.5e-3 * 180 / numpy.pi )
    EL1_THICKNESS = Setting(1000)
    EL1_RELATIVE_TO_PREVIOUS = Setting(0)
    EL1_COATING = Setting(9)

    EL2_SHAPE = Setting(2)
    EL2_P = Setting(0.0)
    EL2_Q = Setting(0.0)
    EL2_ANG = Setting(90.0 - 2.5e-3 * 180 / numpy.pi )
    EL2_THICKNESS = Setting(1000)
    EL2_RELATIVE_TO_PREVIOUS = Setting(0)
    EL2_COATING = Setting(9)

    EL3_SHAPE = Setting(2)
    EL3_P = Setting(0.0)
    EL3_Q = Setting(0.0)
    EL3_ANG = Setting(90.0 - 2.5e-3 * 180 / numpy.pi )
    EL3_THICKNESS = Setting(1000)
    EL3_RELATIVE_TO_PREVIOUS = Setting(0)
    EL3_COATING = Setting(9)

    EL4_SHAPE = Setting(2)
    EL4_P = Setting(0.0)
    EL4_Q = Setting(0.0)
    EL4_ANG = Setting(90.0 - 2.5e-3 * 180 / numpy.pi )
    EL4_THICKNESS = Setting(1000)
    EL4_RELATIVE_TO_PREVIOUS = Setting(0)
    EL4_COATING = Setting(9)

    EL5_SHAPE = Setting(2)
    EL5_P = Setting(0.0)
    EL5_Q = Setting(0.0)
    EL5_ANG = Setting(90.0 - 2.5e-3 * 180 / numpy.pi )
    EL5_THICKNESS = Setting(1000)
    EL5_RELATIVE_TO_PREVIOUS = Setting(0)
    EL5_COATING = Setting(9)


    FILE_DUMP = 0

    def __init__(self):
        super().__init__()

        info_tab = oasysgui.createTabPage(self.main_tabs, "Info")
        self.info_output = QtWidgets.QTextEdit()
        self.info_output.setReadOnly(True)
        info_tab.layout().addWidget(self.info_output)


    def resetSettings(self):
        pass

    def build_gui(self):



        self.leftWidgetPart.setSizePolicy(QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding))
        self.leftWidgetPart.setMaximumWidth(self.CONTROL_AREA_WIDTH + 20)
        self.leftWidgetPart.updateGeometry()

        # box0 = oasysgui.widgetBox(self.controlArea, self.name + " Input Parameters",
        #                           orientation="vertical", width=self.CONTROL_AREA_WIDTH-10)

        # tab1 = oasysgui.tabWidget(self.controlArea)
        self.controls_tabs = oasysgui.tabWidget(self.controlArea)
        box = oasysgui.createTabPage(self.controls_tabs, "Light Source")


        idx = -1 

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        oasysgui.lineEdit(box1, self, "RING_ENERGY",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        oasysgui.lineEdit(box1, self, "RING_CURRENT",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        oasysgui.lineEdit(box1, self, "KY",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        oasysgui.lineEdit(box1, self, "KX",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        oasysgui.lineEdit(box1, self, "NUMBER_OF_PERIODS",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        oasysgui.lineEdit(box1, self, "PERIOD_LENGTH",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        oasysgui.lineEdit(box1, self, "SIGMAX",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        oasysgui.lineEdit(box1, self, "SIGMAXP",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        oasysgui.lineEdit(box1, self, "SIGMAY",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        oasysgui.lineEdit(box1, self, "SIGMAYP",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)





        ##########################
        box = oasysgui.createTabPage(self.controls_tabs, "Calculation")
        ##########################



        ########
        idx += 1
        box1 = gui.widgetBox(box)
        oasysgui.lineEdit(box1, self, "NUMBER_OF_HARMONICS",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        oasysgui.lineEdit(box1, self, "SOURCE_SCREEN_DISTANCE",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        oasysgui.lineEdit(box1, self, "HORIZONTAL_ACCEPTANCE",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        oasysgui.lineEdit(box1, self, "VERTICAL_ACCEPTANCE",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)


        ########
        idx += 1
        box1 = gui.widgetBox(box)
        oasysgui.lineEdit(box1, self, "NUMBER_OF_POINTS_H",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        oasysgui.lineEdit(box1, self, "NUMBER_OF_POINTS_V",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        oasysgui.lineEdit(box1, self, "ELECTRON_SIGMAS",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)




        ##########################
        box = oasysgui.createTabPage(self.controls_tabs, "Beamline")
        ##########################


        #widget index 10
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.comboBox(box1, self, "NELEMENTS",
                     label=self.unitLabels()[idx], addSpace=False,
                    items=['0', '1', '2', '3', '4', '5'],
                    valueType=int, orientation="horizontal", callback=self.set_NELEMENTS,
                    labelWidth=330)
        self.show_at(self.unitFlags()[idx], box1)



        #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

        self.shape_list = [
            "Toroidal mirror",
            "Spherical mirror",
            "Plane mirror",
            "MerCyl mirror",
            "SagCyl mirror",
            "Ellipsoidal mirror",
            "MerEll mirror",
            "SagEllip mirror",
            "Filter",
            "Crystal"]

        self.coating_list = ["Al","Au","cr","Dia","Gra","InSb","MGF2","Ni","pd","Rh","SiC","Test","Al2O3","be","Cu.txt","Fe","Ice","Ir","Mo","Os","Pt","Si","SiO2","WW"]


        tabs_elements = oasysgui.tabWidget(box)
        self.tab_el = []
        self.tab_el.append( oasysgui.createTabPage(tabs_elements, "o.e. 1") )
        self.tab_el.append( oasysgui.createTabPage(tabs_elements, "o.e. 2") )
        self.tab_el.append( oasysgui.createTabPage(tabs_elements, "o.e. 3") )
        self.tab_el.append( oasysgui.createTabPage(tabs_elements, "o.e. 4") )
        self.tab_el.append( oasysgui.createTabPage(tabs_elements, "o.e. 5") )
        self.tab_el.append( oasysgui.createTabPage(tabs_elements, "o.e. 6") )


        for element_index in range(6):

            #widget index xx
            idx += 1
            box1 = gui.widgetBox(self.tab_el[element_index])
            gui.comboBox(box1, self, "EL%d_SHAPE"%element_index,
                         label=self.unitLabels()[idx], addSpace=False,
                        items=self.shape_list,
                        valueType=int, orientation="horizontal", callback=self.set_EL_FLAG, labelWidth=250)
            self.show_at(self.unitFlags()[idx], box1)

            #widget index xx
            idx += 1
            box1 = gui.widgetBox(self.tab_el[element_index])
            oasysgui.lineEdit(box1, self, "EL%d_P"%element_index,
                         label=self.unitLabels()[idx], addSpace=False,
                        valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
            self.show_at(self.unitFlags()[idx], box1)

            #widget index xx
            idx += 1
            box1 = gui.widgetBox(self.tab_el[element_index])
            oasysgui.lineEdit(box1, self, "EL%d_Q"%element_index,
                         label=self.unitLabels()[idx], addSpace=False,
                        valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
            self.show_at(self.unitFlags()[idx], box1)

            #widget index xx
            idx += 1
            box1 = gui.widgetBox(self.tab_el[element_index])
            oasysgui.lineEdit(box1, self, "EL%d_ANG"%element_index,
                         label=self.unitLabels()[idx], addSpace=False,
                        valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
            self.show_at(self.unitFlags()[idx], box1)


            #widget index xx
            idx += 1
            box1 = gui.widgetBox(self.tab_el[element_index])
            gui.comboBox(box1, self, "EL%d_RELATIVE_TO_PREVIOUS"%element_index,
                         label=self.unitLabels()[idx], addSpace=False,
                        items=['Left','Right','Up','Down'],
                        valueType=int, orientation="horizontal", callback=self.set_EL_FLAG, labelWidth=250)
            self.show_at(self.unitFlags()[idx], box1)

            #widget index xx
            idx += 1
            box1 = gui.widgetBox(self.tab_el[element_index])
            gui.comboBox(box1, self, "EL%d_COATING"%element_index,
                         label=self.unitLabels()[idx], addSpace=False,
                        items=self.coating_list,
                        valueType=int, orientation="horizontal", callback=self.set_EL_FLAG, labelWidth=250)
            self.show_at(self.unitFlags()[idx], box1)



        #widget index 42
        idx += 1
        box1 = gui.widgetBox(box)
        gui.separator(box1, height=7)

        gui.comboBox(box1, self, "FILE_DUMP",
                     label=self.unitLabels()[idx], addSpace=False,
                    items=['No', 'Yes (srcalc.h5) [NOT YET WORKING]'],
                    valueType=int, orientation="horizontal", labelWidth=250)

        self.show_at(self.unitFlags()[idx], box1)

        self.mirror_tabs_visibility()

    def set_NELEMENTS(self):
        self.initializeTabs()
        self.mirror_tabs_visibility()

    def mirror_tabs_visibility(self):

        for i in range(6):
            if (i+1) <= self.NELEMENTS:
                self.tab_el[i].setEnabled(True)
            else:
                self.tab_el[i].setEnabled(False)

    def set_EL_FLAG(self):
        self.initializeTabs()

    def unitLabels(self):
         labels =  ["Ring energy [eV]","Ring current [A]","Ky","Kx",
                 "Number of Periods","Period Length [m]",
                 "Sigma H [mm]", "Sigma Prime H [mrad]", "Sigma V [mm]", "Sigma Prime V [mrad]",
                 "Number of harmonics",
                 "Source to screen distance [m]","Horizontal acceptance [mm]","Vertical acceptance [mm]",
                 "Number of intervals in half H screen","Number of intervals in half V screen","Electron sigmas",
                 'Number of optical elements:']

         for i in range(6):
            labels = labels + [
                'Type',
                'Ent. Arm [mm]',
                'Exit Arm [mm]',
                'Inc. Angle [deg]',
                'Reflecting (relative to previous)',
                'Coating',
                ]

         labels = labels + ["Dump file"]
         return labels


    def unitFlags(self):
         return ["True","True","True","True",
                 "True", "True",
                 "True", "True", "True", "True",
                 "True",
                 "True", "True", "True",
                 "True", "True","True",
                 'True',
                 "True", "True", "True", "True", "True", "True",  # OE fields
                 "True", "True", "True", "True", "True", "True",  # OE fields
                 "True", "True", "True", "True", "True", "True",  # OE fields
                 "True", "True", "True", "True", "True", "True",  # OE fields
                 "True", "True", "True", "True", "True", "True",  # OE fields
                 "True", "True", "True", "True", "True", "True",  # OE fields
                 'True']

    def get_help_name(self):
        return 'srcalc'

    def selectFile(self):
        self.le_source_file.setText(oasysgui.selectFileFromDialog(self, self.SOURCE_FILE, "Open Source File", file_extension_filter="*.*"))


    def check_fields(self):
        pass

        # if self.SOURCE == 1:
        #     self.ENER_MIN = congruence.checkPositiveNumber(self.ENER_MIN, "Energy from")
        #     self.ENER_MAX = congruence.checkStrictlyPositiveNumber(self.ENER_MAX, "Energy to")
        #     congruence.checkLessThan(self.ENER_MIN, self.ENER_MAX, "Energy from", "Energy to")
        #     self.NPOINTS = congruence.checkStrictlyPositiveNumber(self.ENER_N, "Energy Points")
        # elif self.SOURCE == 2:
        #     congruence.checkFile(self.SOURCE_FILE)

        # if self.NELEMENTS >= 1:
        #     self.EL1_FOR = congruence.checkEmptyString(self.EL1_FOR, "1st oe formula")
        #
        #     if self.EL1_FLAG == 0: # filter
        #         self.EL1_THI = congruence.checkStrictlyPositiveNumber(self.EL1_THI, "1st oe filter thickness")
        #     elif self.EL1_FLAG == 1: # mirror
        #         self.EL1_ANG = congruence.checkStrictlyPositiveNumber(self.EL1_ANG, "1st oe mirror angle")
        #         self.EL1_ROU = congruence.checkPositiveNumber(self.EL1_ROU, "1st oe mirror roughness")
        #
        #     if not self.EL1_DEN.strip() == "?":
        #         self.EL1_DEN = str(congruence.checkStrictlyPositiveNumber(float(congruence.checkNumber(self.EL1_DEN, "1st oe density")), "1st oe density"))


    def do_xoppy_calculation(self):
        return self.xoppy_calc_srcalc()

    def extract_data_from_xoppy_output(self, calculation_output):
        return calculation_output

    def plot_results(self, calculated_data, progressBarValue=80):


        if not self.view_type == 0:
            if not calculated_data is None:
                # current_index = self.tabs.currentIndex()

                # try:
                if True:
                    for index in range(self.NELEMENTS+1):
                        totPower = calculated_data["Zlist"][index].sum() * \
                                   (calculated_data["X"][1] - calculated_data["X"][0]) * \
                                   (calculated_data["Y"][1] - calculated_data["Y"][0])
                        if index == 0:
                            title = 'Power density [W/mm2] at %4.1f m, Integrated Power: %6.1f W'%(self.SOURCE_SCREEN_DISTANCE,totPower)
                        else:
                            title = 'Power density [W/mm2] transmitted after element %d Integrated Power: %6.1f W'%(index, totPower)

                        self.plot_data2D(calculated_data["Zlist"][index], calculated_data["X"], calculated_data["Y"], index, 0,
                                         xtitle='X [mm] (%d pixels)'%(calculated_data["X"].size),
                                         ytitle='Y [mm] (%d pixels)'%(calculated_data["Y"].size),
                                         title=title)
                # except:
                #     pass

            else:
                raise Exception("Empty Data")


    def get_data_exchange_widget_name(self):
        return "SRCALC"


    def getTitles(self):
        titles = []

        # titles.append("[oe 0] Source screen")

        for oe_n in range(self.NELEMENTS+1):
            titles.append("[oe %d ]"%oe_n)

        return titles


    def xoppy_calc_srcalc(self):

        # odd way to clean output window
        view_type_old = self.view_type
        self.view_type = 0
        self.set_ViewType()
        self.view_type = view_type_old
        self.set_ViewType()

        run_flag = True

        self.progressBarSet(0)


        sys.stdout = EmittingStream(textWritten=self.writeStdOut)

        if True:  # self.trace_shadow:
            grabber = TTYGrabber()
            grabber.start()


        if run_flag:
            for file in ["IDPower.TXT","O_IDPower.TXT","D_IDPower.TXT"]:
                try:
                    os.remove(os.path.join(locations.home_bin_run(),file))
                except:
                    pass


            f = open("IDPower.TXT","w")

            f.write( "%s\n"% (os.path.join(locations.home_data(), "reflect" + os.sep))    )
            f.write("%f\n" % self.KY)               #   READ(1,*) ky
            f.write("%f\n" % self.RING_ENERGY)      # 	READ(1,*) energy
            f.write("%f\n" % self.RING_CURRENT)     # 	READ(1,*) cur
            f.write("%f\n" % self.SIGMAX)       # 	READ(1,*) sigmx
            f.write("%f\n" % self.SIGMAY)       # 	READ(1,*) sigy
            f.write("%f\n" % self.SIGMAXP)      # 	READ(1,*) sigx1
            f.write("%f\n" % self.SIGMAYP)      # 	READ(1,*) sigy1
            f.write("%d\n" % self.NUMBER_OF_PERIODS)     # 	READ(1,*) n
            f.write("%f\n" % self.PERIOD_LENGTH)         # 	READ(1,*) period

            f.write("%f\n" % self.SOURCE_SCREEN_DISTANCE)          # 	READ(1,*) d            p M1
            f.write("%d\n" % self.NELEMENTS)     # 	READ(1,*) nMir

            #
            # BEAMLINE
            #
            f.write("%f\n" % self.EL0_ANG)  # READ(1,*) anM(1)           # incidence angle
            f.write("%d\n" % self.EL0_SHAPE)  # READ(1,*) miType(1)        # type
            f.write("%d\n" % self.EL0_THICKNESS)  # READ(1,*) thic(1)
            f.write("'%s'\n" % self.coating_list[self.EL0_SHAPE])  # READ(1,*) com(1)           # coating
            f.write("'%s'\n" % 'p')

            f.write("%f\n" %                   self.EL1_ANG)        #  READ(1,*) anM(1)           # incidence angle
            f.write("%d\n" %                   self.EL1_SHAPE)      # 	READ(1,*) miType(1)        # type
            f.write("%d\n" %                   self.EL1_THICKNESS)  # 	READ(1,*) thic(1)
            f.write("'%s'\n" % self.coating_list[self.EL1_SHAPE])     # 	READ(1,*) com(1)           # coating
            f.write("'%s'\n" % 'p')                                 # 	READ(1,*) iPom(1)          # ! Polarization or filter

            f.write("%f\n" %                   self.EL2_ANG)        #  READ(1,*) anM(1)           # incidence angle
            f.write("%d\n" %                   self.EL2_SHAPE)      # 	READ(1,*) miType(1)        # type
            f.write("%d\n" %                   self.EL2_THICKNESS)  # 	READ(1,*) thic(1)
            f.write("'%s'\n" % self.coating_list[self.EL2_SHAPE])     # 	READ(1,*) com(1)           # coating
            f.write("'%s'\n" % 'p')                                 # 	READ(1,*) iPom(1)          # ! Polarization or filter

            f.write("%f\n" %                   self.EL3_ANG)        #  READ(1,*) anM(1)           # incidence angle
            f.write("%d\n" %                   self.EL3_SHAPE)      # 	READ(1,*) miType(1)        # type
            f.write("%d\n" %                   self.EL3_THICKNESS)  # 	READ(1,*) thic(1)
            f.write("'%s'\n" % self.coating_list[self.EL3_SHAPE])     # 	READ(1,*) com(1)           # coating
            f.write("'%s'\n" % 'p')                                 # 	READ(1,*) iPom(1)          # ! Polarization or filter

            f.write("%f\n" %                   self.EL4_ANG)        #  READ(1,*) anM(1)           # incidence angle
            f.write("%d\n" %                   self.EL4_SHAPE)      # 	READ(1,*) miType(1)        # type
            f.write("%d\n" %                   self.EL4_THICKNESS)  # 	READ(1,*) thic(1)
            f.write("'%s'\n" % self.coating_list[self.EL4_SHAPE])     # 	READ(1,*) com(1)           # coating
            f.write("'%s'\n" % 'p')                                 # 	READ(1,*) iPom(1)          # ! Polarization or filter

            f.write("%f\n" %                   self.EL5_ANG)        #  READ(1,*) anM(1)           # incidence angle
            f.write("%d\n" %                   self.EL5_SHAPE)      # 	READ(1,*) miType(1)        # type
            f.write("%d\n" %                   self.EL5_THICKNESS)  # 	READ(1,*) thic(1)
            f.write("'%s'\n" % self.coating_list[self.EL5_SHAPE])     # 	READ(1,*) com(1)           # coating
            f.write("'%s'\n" % 'p')                                 # 	READ(1,*) iPom(1)          # ! Polarization or filter


            #
            # Calculation
            #

            f.write("%f\n" % self.HORIZONTAL_ACCEPTANCE)     # 	READ(1,*) xps
            f.write("%f\n" % self.VERTICAL_ACCEPTANCE)     # 	READ(1,*) yps

            f.write("%d\n" % self.NUMBER_OF_POINTS_H)     # 	READ(1,*) nxp
            f.write("%d\n" % self.NUMBER_OF_POINTS_V)     # 	READ(1,*) nyp
            f.write("%d\n" % -6)     # 	READ(1,*) mode
            f.write("%d\n" % self.NUMBER_OF_HARMONICS)   # 	READ(1,*) iharm
            f.write("%d\n" % 1)     # 	READ(1,*) icalc
            f.write("%d\n" % 1)     # 	READ(1,*) itype
            f.write("%d\n" % self.ELECTRON_SIGMAS)     # 	READ(1,*) nSig
            f.write("%d\n" % 20)     # 	READ(1,*) nPhi
            f.write("%d\n" % 20)     # 	READ(1,*) nAlpha
            f.write("%f\n" % 0.000000)     # 	READ(1,*) dAlpha
            f.write("%d\n" % 0)            # 	READ(1,*) nOmega
            f.write("%f\n" % 0.000000)     # 	READ(1,*) dOmega
            f.write("%f\n" % 0.000000)     # 	READ(1,*) xpc
            f.write("%f\n" % 0.000000)     # 	READ(1,*) ypc
            f.write("%d\n" % 0)            # 	READ(1,*) ne
            f.write("%f\n" % 0.000000)     # 	READ(1,*) emin
            f.write("%f\n" % 0.000000)     # 	READ(1,*) emax
            f.write("%f\n" % self.KX)      # 	READ(1,*) kx
            f.write("%f\n" % 0.000000)     # 	READ(1,*) phase

            f.close()

            self.progressBarSet(5)

            if platform.system() == "Windows":
                command = os.path.join(locations.home_bin(),'srcalc') + "'"
            else:
                command = "'" + os.path.join(locations.home_bin(), 'srcalc') + "'"
            print("Running command '%s' in directory: %s "%(command, locations.home_bin_run()))
            print("\n--------------------------------------------------------\n")
            os.system(command)
            print("\n--------------------------------------------------------\n")


        if True:  # self.trace_shadow:
            grabber.stop()

            for row in grabber.ttyData:
                self.writeStdOut(row)

        self.progressBarSet(99)



        f = open("O_IDPower.TXT",'r')
        txt = f.read()
        f.close()
        self.info_output.setText(txt)

        out_dictionary = load_srcalc_output_file(filename="D_IDPower.TXT")

        return out_dictionary

#
# auxiliar functions
#

def load_srcalc_output_file(filename="D_IDPower.TXT",skiprows=5,four_quadrants=True,do_plot=False):
    from srxraylib.plot.gol import plot_image

    a = numpy.loadtxt(filename,skiprows=skiprows)
    f = open(filename,'r')
    line = f.readlines()
    f.close()


    npx = int(line[0])
    xps = float(line[1])
    npy = int(line[2])
    yps = float(line[3])
    nMirr = int(line[4])


    if nMirr == 0:
        a.shape = (a.size,1)

    SOURCE = numpy.zeros((nMirr+1,npx,npy))

    ii = -1
    for ix in range(npx):
        for iy in range(npy):
            ii += 1
            for icol in range(nMirr+1):
                SOURCE[icol,ix,iy] = a[ii,icol]

    # plot_image(SOURCE,title="Source nx: %d, ny: %d"%(npx,npy),show=True)

    hh = numpy.linspace(0,0.5 * xps,npx)
    vv = numpy.linspace(0,0.5 * yps,npy)
    hhh = numpy.concatenate((-hh[::-1], hh[1:]))
    vvv = numpy.concatenate((-vv[::-1], vv[1:]))

    int_mesh1 = []
    int_mesh2 = []

    for i in range(nMirr+1):
        int_mesh = SOURCE[i,:,:].copy()
        int_mesh1.append(int_mesh)
        tmp = numpy.concatenate((int_mesh[::-1, :], int_mesh[1:, :]), axis=0)
        int_mesh2.append( numpy.concatenate((tmp[:, ::-1], tmp[:, 1:]), axis=1) )

        if do_plot:
            if four_quadrants:
                totPower = int_mesh2[i].sum() * (hhh[1] - hhh[0]) * (vvv[1] - vvv[0])
                plot_image(int_mesh2[i],hhh,vvv,title=">>%d<< Source Tot Power %f, pow density: %f"%(i,totPower,int_mesh2[i].max()),show=True)
            else:
                totPower = int_mesh1[i].sum() * (hh[1] - hh[0]) * (vv[1] - vv[0])
                plot_image(int_mesh1[i], hh, vv,
                           title=">>%d<< Source Tot Power %f, pow density: %f" % (i, totPower, int_mesh2[i].max()),
                           show=True)

    if four_quadrants:
        out_dictionary = {"Zlist": int_mesh2, "X": hhh, "Y": vvv, "RAWDATA": a, "NELEMENTS": nMirr}
    else:
        out_dictionary = {"Zlist": int_mesh1, "X": hh, "Y": vv, "RAWDATA": a, "NELEMENTS": nMirr}

    return out_dictionary

def 2d_interpolation(x,y,power_density):
    return X,Y,P


def ray_tracing(
        out_dictionary,
        SOURCE_SCREEN_DISTANCE=13.73,
        oe_parameters=  {
            "EL0_SHAPE":2,"EL0_P":0.0,"EL0_Q":0.0,"EL0_ANG":88.75,"EL0_THICKNESS":1000,"EL0_RELATIVE_TO_PREVIOUS":0,
                        } ):

    import shadow4
    from shadow4.beam.beam import Beam
    from shadow4.compatibility.beam3 import Beam3

    from shadow4.optical_surfaces.conic import Conic


    for key in out_dictionary.keys():
        print(">>>> ",key)

    vx = out_dictionary["X"] / ( 1e3 * SOURCE_SCREEN_DISTANCE )
    vz = out_dictionary["Y"] / ( 1e3 * SOURCE_SCREEN_DISTANCE )

    VX = numpy.outer(vx,numpy.ones_like(vz))
    VZ = numpy.outer(numpy.ones_like(vx),vz)
    VY = numpy.sqrt( 1.0 - VX**2 + VZ**2)

    # print(VY)
    beam = Beam.initialize_as_pencil(N=VX.size)
    beam.set_column(4, VX.flatten())
    beam.set_column(5, VY.flatten())
    beam.set_column(6, VZ.flatten())

    Beam3.initialize_from_shadow4_beam(beam).write('/home/manuel/Oasys/begin.dat')
    # beam3 = Beam3.initialize_from_shadow4_beam(beam)
    # beam3.write('/home/manuel/Oasys/begin.dat')



    oe_index = 0

    if   oe_parameters["EL%d_SHAPE"%oe_index] == 0:     # "Toroidal mirror",
        raise Exception("Not implemented")
    elif oe_parameters["EL%d_SHAPE"%oe_index] == 1:     # "Spherical mirror",
        raise Exception("Not implemented")
    elif oe_parameters["EL%d_SHAPE"%oe_index] == 2:     # "Plane mirror",
        ccc = Conic.initialize_as_plane()
        is_conic = True
        alpha = 0
        theta_grazing = 0
        p = SOURCE_SCREEN_DISTANCE
        q = 0

    elif oe_parameters["EL%d_SHAPE"%oe_index] == 3:     # "MerCyl mirror",
        raise Exception("Not implemented")
    elif oe_parameters["EL%d_SHAPE"%oe_index] == 4:     # "SagCyl mirror",
        raise Exception("Not implemented")
    elif oe_parameters["EL%d_SHAPE"%oe_index] == 5:     # "Ellipsoidal mirror",
        raise Exception("Not implemented")
    elif oe_parameters["EL%d_SHAPE"%oe_index] == 6:     # "MerEll mirror",
        raise Exception("Not implemented")
    elif oe_parameters["EL%d_SHAPE"%oe_index] == 7:     # "SagEllip mirror",
        raise Exception("Not implemented")
    elif oe_parameters["EL%d_SHAPE"%oe_index] == 8:     # "Filter",
        raise Exception("Not implemented")
    elif oe_parameters["EL%d_SHAPE"%oe_index] == 9:     # "Crystal"
        raise Exception("Not implemented")



    theta_grazing = (90.0 - oe_parameters["EL0_ANG"]) * numpy.pi / 180
    newbeam = beam.duplicate()
    if oe_parameters["EL0_RELATIVE_TO_PREVIOUS"] == 0:
        alpha = 90.0 * numpy.pi / 180
    elif oe_parameters["EL0_RELATIVE_TO_PREVIOUS"] == 1:
        alpha = 270.0 * numpy.pi / 180
    elif oe_parameters["EL0_RELATIVE_TO_PREVIOUS"] == 2:
        alpha = 0.0
    elif oe_parameters["EL0_RELATIVE_TO_PREVIOUS"] == 3:
        alpha = 180.0 * numpy.pi / 180


    # p = oe_parameters["EL0_P"]
    # q = oe_parameters["EL0_Q"]

    if is_conic:
        #
        # put beam in mirror reference system
        #
        # TODO: calculate rotation matrices? Invert them for putting back to the lab system?

        newbeam.rotate(alpha, axis=2)
        newbeam.rotate(theta_grazing, axis=1)
        newbeam.translation([0.0, -p * numpy.cos(theta_grazing), p * numpy.sin(theta_grazing)])

        #
        # reflect beam in the mirror surface and dump mirr.01
        #
        newbeam = ccc.apply_specular_reflection_on_beam(newbeam)
        Beam3.initialize_from_shadow4_beam(newbeam).write('/home/manuel/Oasys/minimirr.01')

        #
        # put beam in lab frame and compute image
        #
        newbeam.rotate(theta_grazing, axis=1)
        # TODO what about alpha?
        newbeam.retrace(q, resetY=True)
        Beam3.initialize_from_shadow4_beam(newbeam).write('/home/manuel/Oasys/ministar.01')


    # shape_vx = VX.shape
    #
    # VXf = VX.flatten()
    # VXff = VXf.copy()
    # VXff.shape = shape_vx
    # print(">>>>",shape_vx,VXf.shape,VXff.shape,numpy.min(VXff - VX),numpy.max(VXff - VX) )

    # print(">>>>",out_dictionary["RAWDATA"].shape,vx.shape,vz.shape)


if __name__ == "__main__":

    test = 2  # 0= widget, 1=load D_IDPower.TXT, 2 =ray tracing
    if test == 0:
        app = QApplication(sys.argv)
        w = OWsrcalc()
        w.show()
        app.exec()
        w.saveSettings()
    elif test == 1:
        dict1 = load_srcalc_output_file(filename="D_IDPower.TXT", skiprows=5, do_plot=1)
    elif test == 2:
        dict1 = load_srcalc_output_file(filename="D_IDPower.TXT", skiprows=5, do_plot=0)
        out = ray_tracing(dict1)
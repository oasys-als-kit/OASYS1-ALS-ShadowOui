import sys, os, platform
import numpy
from PyQt5.QtWidgets import QApplication, QMessageBox, QSizePolicy
from PyQt5.QtGui import QIntValidator, QDoubleValidator

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui, congruence
from oasys.widgets.exchange import DataExchangeObject
from orangecontrib.xoppy.util.xoppy_xraylib_util import xpower_calc

from oasys.widgets.exchange import DataExchangeObject
from orangecontrib.xoppy.widgets.gui.ow_xoppy_widget import XoppyWidget


import scipy.constants as codata
import orangecanvas.resources as resources



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


    RING_ENERGY = Setting(6.0)
    RING_CURRENT = Setting(0.2)
    KY = Setting(2.0)
    KX = Setting(0.0)
    NUMBER_OF_PERIODS = Setting(50)
    PERIOD_LENGTH = Setting(0.03)
    NUMBER_OF_HARMONICS = Setting(-49)
    SOURCE_SCREEN_DISTANCE = Setting(20.0)
    HORIZONTAL_ACCEPTANCE = Setting(2)
    VERTICAL_ACCEPTANCE = Setting(2)
    NUMBER_OF_POINTS_H = Setting(41)
    NUMBER_OF_POINTS_V = Setting(41)
    ELECTRON_SIGMAS = Setting(4)
    SIGMAX = Setting(0.149)
    SIGMAXP = Setting(0.003)
    SIGMAY = Setting(0.0037)
    SIGMAYP = Setting(0.0015)
    NELEMENTS = Setting(2)

    EL0_P = Setting(0.0)
    EL0_Q = Setting(0.0)
    EL0_ANG = Setting(90.0 - 2.5e-3 * 180 / numpy.pi )
    EL0_THICKNESS = Setting(1000)
    EL0_RELATIVE_TO_PREVIOUS = Setting(0)
    EL0_COATING = Setting(9)
    EL0_SHAPE = Setting(2)

    EL1_P = Setting(0.0)
    EL1_Q = Setting(0.0)
    EL1_ANG = Setting(90.0 - 2.5e-3 * 180 / numpy.pi )
    EL1_THICKNESS = Setting(1000)
    EL1_RELATIVE_TO_PREVIOUS = Setting(0)
    EL1_COATING = Setting(9)
    EL1_SHAPE = Setting(2)

    EL2_P = Setting(0.0)
    EL2_Q = Setting(0.0)
    EL2_ANG = Setting(90.0 - 2.5e-3 * 180 / numpy.pi )
    EL2_THICKNESS = Setting(1000)
    EL2_RELATIVE_TO_PREVIOUS = Setting(0)
    EL2_COATING = Setting(9)
    EL2_SHAPE = Setting(2)

    EL3_P = Setting(0.0)
    EL3_Q = Setting(0.0)
    EL3_ANG = Setting(90.0 - 2.5e-3 * 180 / numpy.pi )
    EL3_THICKNESS = Setting(1000)
    EL3_RELATIVE_TO_PREVIOUS = Setting(0)
    EL3_COATING = Setting(9)
    EL3_SHAPE = Setting(2)

    EL4_P = Setting(0.0)
    EL4_Q = Setting(0.0)
    EL4_ANG = Setting(90.0 - 2.5e-3 * 180 / numpy.pi )
    EL4_THICKNESS = Setting(1000)
    EL4_RELATIVE_TO_PREVIOUS = Setting(0)
    EL4_COATING = Setting(9)
    EL4_SHAPE = Setting(2)

    EL5_P = Setting(0.0)
    EL5_Q = Setting(0.0)
    EL5_ANG = Setting(90.0 - 2.5e-3 * 180 / numpy.pi )
    EL5_THICKNESS = Setting(1000)
    EL5_RELATIVE_TO_PREVIOUS = Setting(0)
    EL5_COATING = Setting(9)
    EL5_SHAPE = Setting(2)

    FILE_DUMP = 0

    def __init__(self):
        super().__init__()

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

        self.shape_list = ["Toroid","Spherical","Plane","MerCyl","SagCyl",
                      "Ellipsoidal","MerEll","SagEllip","Filter","Crystal"]

        self.coating_list = ["Al","Au","cr","Dia","Gra","InSb","MGF2","Ni","pd","Rh","SiC","Test","Al2O3","be","Cu.txt","Fe","Ice","Ir","Mo","Os","Pt","Si","SiO2","WW"]


        tabs_elements = oasysgui.tabWidget(box)
        self.tab_el = []
        self.tab_el.append( oasysgui.createTabPage(tabs_elements, "Mirror 1") )
        self.tab_el.append( oasysgui.createTabPage(tabs_elements, "Mirror 2") )
        self.tab_el.append( oasysgui.createTabPage(tabs_elements, "Mirror 3") )
        self.tab_el.append( oasysgui.createTabPage(tabs_elements, "Mirror 4") )
        self.tab_el.append( oasysgui.createTabPage(tabs_elements, "Mirror 5") )
        self.tab_el.append( oasysgui.createTabPage(tabs_elements, "Mirror 6") )


        for element_index in range(6):
            #widget index 13
            idx += 1
            box1 = gui.widgetBox(self.tab_el[element_index])
            oasysgui.lineEdit(box1, self, "EL%d_P"%element_index,
                         label=self.unitLabels()[idx], addSpace=False,
                        valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
            self.show_at(self.unitFlags()[idx], box1)

            #widget index 13
            idx += 1
            box1 = gui.widgetBox(self.tab_el[element_index])
            oasysgui.lineEdit(box1, self, "EL%d_Q"%element_index,
                         label=self.unitLabels()[idx], addSpace=False,
                        valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
            self.show_at(self.unitFlags()[idx], box1)

            #widget index 13
            idx += 1
            box1 = gui.widgetBox(self.tab_el[element_index])
            oasysgui.lineEdit(box1, self, "EL%d_ANG"%element_index,
                         label=self.unitLabels()[idx], addSpace=False,
                        valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
            self.show_at(self.unitFlags()[idx], box1)


            #widget index 12
            idx += 1
            box1 = gui.widgetBox(self.tab_el[element_index])
            gui.comboBox(box1, self, "EL%d_RELATIVE_TO_PREVIOUS"%element_index,
                         label=self.unitLabels()[idx], addSpace=False,
                        items=['Left','Right','Up','Down'],
                        valueType=int, orientation="horizontal", callback=self.set_EL_FLAG, labelWidth=250)
            self.show_at(self.unitFlags()[idx], box1)

            #widget index 12
            idx += 1
            box1 = gui.widgetBox(self.tab_el[element_index])
            gui.comboBox(box1, self, "EL%d_COATING"%element_index,
                         label=self.unitLabels()[idx], addSpace=False,
                        items=self.coating_list,
                        valueType=int, orientation="horizontal", callback=self.set_EL_FLAG, labelWidth=250)
            self.show_at(self.unitFlags()[idx], box1)


            #widget index 12
            idx += 1
            box1 = gui.widgetBox(self.tab_el[element_index])
            gui.comboBox(box1, self, "EL%d_SHAPE"%element_index,
                         label=self.unitLabels()[idx], addSpace=False,
                        items=self.shape_list,
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
                 "Number of points in H","Number of points in V","Electron sigmas",
                 'Number of elements:']

         for i in range(6):
            labels = labels + ['Ent. Arm [mm]',
                'Exit Arm [mm]',
                'Inc. Angle [deg]',
                'Reflecting (relative to previous)',
                'Coating',
                'Shape']

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

                try:
                # if True:
                    for index in range(self.NELEMENTS+1):
                        totPower = calculated_data["Zlist"][index].sum() * \
                                   (calculated_data["X"][1] - calculated_data["X"][0]) * \
                                   (calculated_data["Y"][1] - calculated_data["Y"][0])
                        if index == 0:
                            title = 'Power density [W/mm2] at %4.1f m, Integrated Power: %6.1f W'%(self.SOURCE_SCREEN_DISTANCE,totPower)
                        else:
                            title = 'Power density [W/mm2] transmitted after element %d Integrated Power: %6.1f W'%(index, totPower)

                        self.plot_data2D(calculated_data["Zlist"][index], calculated_data["X"], calculated_data["Y"], index, 0,
                                         xtitle='X [mm]',
                                         ytitle='Y [mm]',
                                         title=title)
                except:
                    pass

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

                           # 	READ(1,*) iPom(1)          # ! Polarization or filter

            if True:

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

            else:

                f.write("%f\n" % self.EL0_ANG)  # READ(1,*) anM(1)           # incidence angle
                f.write("%d\n" % self.EL0_SHAPE)  # READ(1,*) miType(1)        # type
                f.write("%d\n" % self.EL0_THICKNESS)  # READ(1,*) thic(1)
                f.write("'%s'\n" % self.coating_list[self.EL0_SHAPE])  # READ(1,*) com(1)           # coating
                f.write("'%s'\n" % 'p')

                f.write("%f\n" % 85.500000)  # 	READ(1,*) anM(2)
                f.write("%d\n" % 2)          # 	READ(1,*) miType(2)
                f.write("%d\n" % 21000)      # 	READ(1,*) thic(2)
                f.write("'%s'\n" % 'Au')     # 	READ(1,*) com(2)
                f.write("'%s'\n" % 'p')      # 	READ(1,*) iPom(2)

                f.write("%f\n" % 78.000000)  # 	READ(1,*) anM(3)
                f.write("%d\n" % 1)          # 	READ(1,*) miType(3)
                f.write("%d\n" % 1000)       # 	READ(1,*) thic(3)
                f.write("'%s'\n" % 'Si')     # 	READ(1,*) com(3)
                f.write("'%s'\n" % 's')      # 	READ(1,*) iPom(3)

                f.write("%f\n" % 78.000000)  # 	READ(1,*) anM(4)
                f.write("%d\n" % 2)          # 	READ(1,*) miType(4)
                f.write("%d\n" % 1000)       # 	READ(1,*) thic(4)
                f.write("'%s'\n" % 'Mo')     # 	READ(1,*) com(4)
                f.write("'%s'\n" % 's')      # 	READ(1,*) iPom(4)

                f.write("%f\n" % 86.000000)   # 	READ(1,*) anM(5)
                f.write("%d\n" % 0)           # 	READ(1,*) miType(5)
                f.write("%d\n" % 1000)        # 	READ(1,*) thic(5)
                f.write("'%s'\n" % 'Dia')     # 	READ(1,*) com(5)
                f.write("'%s'\n" % 's')       # 	READ(1,*) iPom(5)

                f.write("%f\n" % 86.000000)     # 	READ(1,*) anM(6)
                f.write("%d\n" % 0)         # 	READ(1,*) miType(6)
                f.write("%d\n" % 1000)     # 	READ(1,*) thic(6)
                f.write("'%s'\n" % 'Dia')     # 	READ(1,*) com(6)
                f.write("'%s'\n" % 's')       # 	READ(1,*) iPom(6)

            f.write("%f\n" % self.HORIZONTAL_ACCEPTANCE)     # 	READ(1,*) xps
            f.write("%f\n" % self.VERTICAL_ACCEPTANCE)     # 	READ(1,*) yps

            f.write("%d\n" % self.NUMBER_OF_POINTS_H)     # 	READ(1,*) nxp
            f.write("%d\n" % self.NUMBER_OF_POINTS_V)     # 	READ(1,*) nyp
            f.write("%d\n" % -6)     # 	READ(1,*) mode
            f.write("%d\n" % -274)   # 	READ(1,*) iharm
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


            if platform.system() == "Windows":
                command = os.path.join(locations.home_bin(),'srcalc') + "'"
            else:
                command = "'" + os.path.join(locations.home_bin(), 'srcalc') + "'"
            print("Running command '%s' in directory: %s "%(command, locations.home_bin_run()))
            print("\n--------------------------------------------------------\n")
            os.system(command)
            print("\n--------------------------------------------------------\n")


        f = open("O_IDPower.TXT",'r')
        txt = f.read()
        f.close()
        self.xoppy_output.setText(txt)

        out_dictionary = load_srcalc_output_file(filename="D_IDPower.TXT")

        return out_dictionary


# def load_srcalc_output_file(filename="O_IDPower.TXT",skiprows=5):
#     # from srxraylib.plot.gol import plot_image
#
#     a = numpy.loadtxt(filename,skiprows=skiprows)
#     f = open(filename,'r')
#     line = f.readlines()
#     f.close()
#
#
#     npx = int(line[0])
#     xps = float(line[1])
#     npy = int(line[2])
#     yps = float(line[3])
#     nMirr = int(line[4])
#
#     SOURCE = numpy.zeros((npx,npy))
#     MIRROR1 = numpy.zeros((npx,npy)) # TODO: repeat for all mirrors
#
#     ii = -1
#     for ix in range(npx):
#         for iy in range(npy):
#             ii += 1
#             SOURCE[ix,iy] = a[ii,0]
#             MIRROR1[ix, iy] = a[ii, 1]
#
#     # plot_image(SOURCE,title="Source nx: %d, ny: %d"%(npx,npy),show=True)
#
#     hh = numpy.linspace(0,xps,npx)
#     vv = numpy.linspace(0,yps,npy)
#     int_mesh = SOURCE
#
#     hhh = numpy.concatenate((-hh[::-1], hh[1:]))
#     vvv = numpy.concatenate((-vv[::-1], vv[1:]))
#
#     tmp = numpy.concatenate((int_mesh[::-1, :], int_mesh[1:, :]), axis=0)
#     int_mesh2 = numpy.concatenate((tmp[:, ::-1], tmp[:, 1:]), axis=1)
#
#     totPower = int_mesh2.sum() * (hhh[1] - hhh[0]) * (vvv[1] - vvv[0])
#     # plot_image(int_mesh2,hhh,vvv,title="Source Tot Power %f, pow density: %f"%(totPower,int_mesh2.max()),show=True)
#
#     out_dictionary = {"Z": int_mesh2, "X": hhh, "Y": vvv}
#
#     return out_dictionary


def load_srcalc_output_file(filename="D_IDPower.TXT",skiprows=5,do_plot=False):
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
    # MIRROR1 = numpy.zeros((npx,npy)) # TODO: repeat for all mirrors

    ii = -1
    for ix in range(npx):
        for iy in range(npy):
            ii += 1
            for icol in range(nMirr+1):
                SOURCE[icol,ix,iy] = a[ii,icol]

    # plot_image(SOURCE,title="Source nx: %d, ny: %d"%(npx,npy),show=True)

    hh = numpy.linspace(0,xps,npx)
    vv = numpy.linspace(0,yps,npy)
    hhh = numpy.concatenate((-hh[::-1], hh[1:]))
    vvv = numpy.concatenate((-vv[::-1], vv[1:]))

    int_mesh2 = []

    for i in range(nMirr+1):
        int_mesh = SOURCE[i,:,:].copy()
        tmp = numpy.concatenate((int_mesh[::-1, :], int_mesh[1:, :]), axis=0)
        int_mesh2.append( numpy.concatenate((tmp[:, ::-1], tmp[:, 1:]), axis=1) )

        if do_plot:
            totPower = int_mesh2[i].sum() * (hhh[1] - hhh[0]) * (vvv[1] - vvv[0])
            plot_image(int_mesh2[i],hhh,vvv,title=">>%d<< Source Tot Power %f, pow density: %f"%(i,totPower,int_mesh2[i].max()),show=True)

    out_dictionary = {"Zlist": int_mesh2, "X": hhh, "Y": vvv, "RAWDATA":a, "NELEMENRS":nMirr}

    return out_dictionary

if __name__ == "__main__":


    from oasys.widgets.exchange import DataExchangeObject


    app = QApplication(sys.argv)
    w = OWsrcalc()

    w.show()


    app.exec()
    w.saveSettings()

    # dict1 = load_srcalc_output_file(filename="D_IDPower.TXT", skiprows=5)

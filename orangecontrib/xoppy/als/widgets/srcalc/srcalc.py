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
from orangecontrib.xoppy.util.xoppy_util import locations

import scipy.constants as codata

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
    HORIZONTAL_ACCEPTANCE = Setting(2)
    VERTICAL_ACCEPTANCE = Setting(2)
    NUMBER_OF_POINTS_H = Setting(41)
    NUMBER_OF_POINTS_V = Setting(41)
    ELECTRON_SIGMAS = Setting(4)
    SIGMAX = Setting(0.149)
    SIGMAXP = Setting(0.003)
    SIGMAY = Setting(0.0037)
    SIGMAYP = Setting(0.0015)
    NELEMENTS = Setting(1)

    EL0_P = Setting(10.0)
    EL0_Q = Setting(0.0)
    EL0_ANG = Setting(0.0)
    EL0_THICKNESS = Setting(1000)
    EL0_RELATIVE_TO_PREVIOUS = Setting(0)
    EL0_COATING = Setting(0)
    EL0_SHAPE = Setting(0)

    EL1_P = Setting(0.0)
    EL1_Q = Setting(0.0)
    EL1_ANG = Setting(89.88)
    EL1_THICKNESS = Setting(1000)
    EL1_RELATIVE_TO_PREVIOUS = Setting(0)
    EL1_COATING = Setting(0)
    EL1_SHAPE = Setting(0)

    EL2_P = Setting(0.0)
    EL2_Q = Setting(0.0)
    EL2_ANG = Setting(0.0)
    EL2_THICKNESS = Setting(1000)
    EL2_RELATIVE_TO_PREVIOUS = Setting(0)
    EL2_COATING = Setting(0)
    EL2_SHAPE = Setting(0)

    EL3_P = Setting(0.0)
    EL3_Q = Setting(0.0)
    EL3_ANG = Setting(0.0)
    EL3_THICKNESS = Setting(1000)
    EL3_RELATIVE_TO_PREVIOUS = Setting(0)
    EL3_COATING = Setting(0)
    EL3_SHAPE = Setting(0)

    EL4_P = Setting(0.0)
    EL4_Q = Setting(0.0)
    EL4_ANG = Setting(0.0)
    EL4_THICKNESS = Setting(1000)
    EL4_RELATIVE_TO_PREVIOUS = Setting(0)
    EL4_COATING = Setting(0)
    EL4_SHAPE = Setting(0)

    EL5_P = Setting(0.0)
    EL5_Q = Setting(0.0)
    EL5_ANG = Setting(0.0)
    EL5_THICKNESS = Setting(1000)
    EL5_RELATIVE_TO_PREVIOUS = Setting(0)
    EL5_COATING = Setting(0)
    EL5_SHAPE = Setting(0)

    FILE_DUMP = 0

    def __init__(self):
        super().__init__()

        # plot_tab = oasysgui.createTabPage(self.main_tabs, "Results111")

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
                    items=['1', '2', '3', '4', '5'],
                    valueType=int, orientation="horizontal", callback=self.set_NELEMENTS,
                    labelWidth=330)
        self.show_at(self.unitFlags()[idx], box1)



        #$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$

        shape_list = ["Toroid","Spherical","Plane","MerCyl","SagCyl",
                      "Ellipsoidal","MerEll","SagEllip","Filter","Crystal"]

        coating_list = ["Si","Ge"] #TODO


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
                        items=coating_list,
                        valueType=int, orientation="horizontal", callback=self.set_EL_FLAG, labelWidth=250)
            self.show_at(self.unitFlags()[idx], box1)


            #widget index 12
            idx += 1
            box1 = gui.widgetBox(self.tab_el[element_index])
            gui.comboBox(box1, self, "EL%d_SHAPE"%element_index,
                         label=self.unitLabels()[idx], addSpace=False,
                        items=shape_list,
                        valueType=int, orientation="horizontal", callback=self.set_EL_FLAG, labelWidth=250)
            self.show_at(self.unitFlags()[idx], box1)



        #widget index 42
        idx += 1
        box1 = gui.widgetBox(box)
        gui.separator(box1, height=7)

        gui.comboBox(box1, self, "FILE_DUMP",
                     label=self.unitLabels()[idx], addSpace=False,
                    items=['No', 'Yes (power.spec)'],
                    valueType=int, orientation="horizontal", labelWidth=250)

        self.show_at(self.unitFlags()[idx], box1)

        self.mirror_tabs_visibility()



    def set_NELEMENTS(self):
        self.initializeTabs()
        self.mirror_tabs_visibility()

    def mirror_tabs_visibility(self):
        for i in range(6):
            if i <= self.NELEMENTS:
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
                 "Horizontal acceptance [mm]","Vertical acceptance [mm]",
                 "Number of points in H","Number of points in V","Electron sigmas",
                 'Number of elements:']

         for i in range(6):
            labels = labels + ['Ent. Arm [mm]',
                'Exit Arm [mm]',
                'Inc. Angle [deg]',
                'Relative to previous',
                'Coating',
                'Shape']

         labels = labels + ["Dump file"]
         return labels


    def unitFlags(self):
         return ["True","True","True","True",
                 "True", "True",
                 "True", "True", "True", "True",
                 "True",
                 "True", "True",
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


    def get_data_exchange_widget_name(self):
        return "POWER"

    def getKind(self, oe_n):
        if oe_n == 1:
            return self.EL1_FLAG
        # elif oe_n == 2:
        #     return self.EL2_FLAG
        # elif oe_n == 3:
        #     return self.EL3_FLAG
        # elif oe_n == 4:
        #     return self.EL4_FLAG
        # elif oe_n == 5:
        #     return self.EL5_FLAG

    # def do_plot_local(self):
    #     out = False
    #     if self.PLOT_SETS == 0: out = True
    #     if self.PLOT_SETS == 2: out = True
    #     return out

    # def do_plot_intensity(self):
    #     out = False
    #     if self.PLOT_SETS == 1: out = True
    #     if self.PLOT_SETS == 2: out = True
    #     return out


    def getTitles(self):
        titles = []

        # if self.do_plot_intensity(): titles.append("Input beam")

        for oe_n in range(1, self.NELEMENTS+2):


            titles.append("[oe " + str(oe_n) + "] Absorption")
            titles.append("[oe " + str(oe_n) + "] Transmitivity")


        return titles

    def getXTitles(self):

        xtitles = []

        if self.do_plot_intensity(): xtitles.append("Photon Energy [eV]")

        for oe_n in range(1, self.NELEMENTS+2):
            kind = self.getKind(oe_n)

            if kind == 0: # FILTER
                if self.do_plot_local(): xtitles.append("Photon Energy [eV]")
                if self.do_plot_local(): xtitles.append("Photon Energy [eV]")
                if self.do_plot_local(): xtitles.append("Photon Energy [eV]")
                if self.do_plot_local(): xtitles.append("Photon Energy [eV]")
                if self.do_plot_intensity(): xtitles.append("Photon Energy [eV]")
            else: # MIRROR
                if self.do_plot_local(): xtitles.append("Photon Energy [eV]")
                if self.do_plot_local(): xtitles.append("Photon Energy [eV]")
                if self.do_plot_local(): xtitles.append("Photon Energy [eV]")
                if self.do_plot_local(): xtitles.append("Photon Energy [eV]")
                if self.do_plot_local(): xtitles.append("Photon Energy [eV]")
                if self.do_plot_intensity(): xtitles.append("Photon Energy [eV]")

        return xtitles

    def getYTitles(self):
        ytitles = []

        if self.do_plot_intensity(): ytitles.append("Source")

        for oe_n in range(1, self.NELEMENTS+2):
            kind = self.getKind(oe_n)

            if kind == 0: # FILTER
                if self.do_plot_local(): ytitles.append("[oe " + str(oe_n) + "] Total CS cm2/g")
                if self.do_plot_local(): ytitles.append("[oe " + str(oe_n) + "] Mu cm^-1")
                if self.do_plot_local(): ytitles.append("[oe " + str(oe_n) + "] Transmitivity")
                if self.do_plot_local(): ytitles.append("[oe " + str(oe_n) + "] Absorption")
                if self.do_plot_intensity(): ytitles.append("Intensity after oe " + str(oe_n))
            else: # MIRROR
                if self.do_plot_local(): ytitles.append("[oe " + str(oe_n) + "] 1-Re[n]=delta")
                if self.do_plot_local(): ytitles.append("[oe " + str(oe_n) + "] Im[n]=beta")
                if self.do_plot_local(): ytitles.append("[oe " + str(oe_n) + "] delta/beta")
                if self.do_plot_local(): ytitles.append("[oe " + str(oe_n) + "] Reflectivity-s")
                if self.do_plot_local(): ytitles.append("[oe " + str(oe_n) + "] Transmitivity")
                if self.do_plot_intensity(): ytitles.append("Intensity after oe " + str(oe_n))

        return ytitles

    def getVariablesToPlot(self):
        variables = []

        if self.do_plot_intensity(): variables.append((0, 1)) # start plotting the source
        shift = 0

        for oe_n in range(1, self.NELEMENTS+2):
            kind = self.getKind(oe_n)

            if oe_n == 1:
                shift = 0
            else:
                kind_previous = self.getKind(oe_n-1)

                if kind_previous == 0: # FILTER
                    shift += 5
                else:
                    shift += 6

            if kind == 0: # FILTER
                if self.do_plot_local(): variables.append((0, 2+shift))
                if self.do_plot_local(): variables.append((0, 3+shift))
                if self.do_plot_local(): variables.append((0, 4+shift))
                if self.do_plot_local(): variables.append((0, 5+shift))
                if self.do_plot_intensity(): variables.append((0, 6+shift))
            else:
                if self.do_plot_local(): variables.append((0, 2+shift))
                if self.do_plot_local(): variables.append((0, 3+shift))
                if self.do_plot_local(): variables.append((0, 4+shift))
                if self.do_plot_local(): variables.append((0, 5+shift))
                if self.do_plot_local(): variables.append((0, 6+shift))
                if self.do_plot_intensity(): variables.append((0, 7+shift))

        return variables

    def getLogPlot(self):


        logplot = []

        if self.do_plot_intensity(): logplot.append((False,False))

        for oe_n in range(1, self.NELEMENTS+2):
            kind = self.getKind(oe_n)

            if kind == 0: # FILTER
                if self.do_plot_local(): logplot.append((False, True))
                if self.do_plot_local(): logplot.append((False, True))
                if self.do_plot_local(): logplot.append((False, False))
                if self.do_plot_local(): logplot.append((False, False))
                if self.do_plot_intensity(): logplot.append((False, False))
            else: # MIRROR
                if self.do_plot_local(): logplot.append((False, True))
                if self.do_plot_local(): logplot.append((False, True))
                if self.do_plot_local(): logplot.append((False, False))
                if self.do_plot_local(): logplot.append((False, False))
                if self.do_plot_local(): logplot.append((False, False))
                if self.do_plot_intensity(): logplot.append((False, False))

        return logplot

    def xoppy_calc_srcalc(self):
        print(">>>>>>xoppy_calc_srcalc")
        os.system("rm IDPower.TXT O_IDPower.TXT")
        f = open("IDPower.TXT","w")
     #
        f.write("%f\n" % self.KY)               #   READ(1,*) ky
        f.write("%f\n" % self.RING_ENERGY)      # 	READ(1,*) energy
        f.write("%f\n" % self.RING_CURRENT)     # 	READ(1,*) cur
        f.write("%f\n" % self.SIGMAX)       # 	READ(1,*) sigmx
        f.write("%f\n" % self.SIGMAY)       # 	READ(1,*) sigy
        f.write("%f\n" % self.SIGMAXP)      # 	READ(1,*) sigx1
        f.write("%f\n" % self.SIGMAYP)      # 	READ(1,*) sigy1
        f.write("%d\n" % self.NUMBER_OF_PERIODS)     # 	READ(1,*) n
        f.write("%f\n" % self.PERIOD_LENGTH)         # 	READ(1,*) period

        f.write("%f\n" % 20.000000)          # 	READ(1,*) d            p M1
        f.write("%d\n" % self.NELEMENTS)     # 	READ(1,*) nMir

        f.write("%f\n" % 50.000000)  # 	READ(1,*) anM(1)           # incidence angle
        f.write("%d\n" % 9)          # 	READ(1,*) miType(1)        # type
        f.write("%d\n" % 1000)       # 	READ(1,*) thic(1)
        f.write("'%s'\n" % 'Si')     # 	READ(1,*) com(1)           # coating
        f.write("'%s'\n" % 'p')      # 	READ(1,*) iPom(1)          # shape??

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

        directory = "./" # locations.home_bin()
        if platform.system() == "Windows":
            command = os.path.join(directory,'srcalc')
        else:
            command = "'" + os.path.join(directory, 'srcalc') + "'"
        print("Running command '%s' in directory: %s "%(command, locations.home_bin_run()))
        print("\n--------------------------------------------------------\n")
        os.system(command)
        os.system("cat O_IDPower.TXT")
        print("\n--------------------------------------------------------\n")

        f = open("O_IDPower.TXT",'r')
        txt = f.read()
        f.close()
        self.xoppy_output.setText(txt)

        # #
        # # prepare input for xpower_calc
        # # Note that the input for xpower_calc accepts any number of elements.
        # #
        #
        # substance = [self.EL1_FOR,self.EL2_FOR,self.EL3_FOR,self.EL4_FOR,self.EL5_FOR]
        # thick     = numpy.array( (self.EL1_THI,self.EL2_THI,self.EL3_THI,self.EL4_THI,self.EL5_THI))
        # angle     = numpy.array( (self.EL1_ANG,self.EL2_ANG,self.EL3_ANG,self.EL4_ANG,self.EL5_ANG))
        # dens      = [self.EL1_DEN,self.EL2_DEN,self.EL3_DEN,self.EL4_DEN,self.EL5_DEN]
        # roughness = numpy.array( (self.EL1_ROU,self.EL2_ROU,self.EL3_ROU,self.EL4_ROU,self.EL5_ROU))
        # flags     = numpy.array( (self.EL1_FLAG,self.EL2_FLAG,self.EL3_FLAG,self.EL4_FLAG,self.EL5_FLAG))
        #
        # substance = substance[0:self.NELEMENTS+1]
        # thick = thick[0:self.NELEMENTS+1]
        # angle = angle[0:self.NELEMENTS+1]
        # dens = dens[0:self.NELEMENTS+1]
        # roughness = roughness[0:self.NELEMENTS+1]
        # flags = flags[0:self.NELEMENTS+1]
        #
        #
        # if self.SOURCE == 0:
        #     # energies = numpy.arange(0,500)
        #     # elefactor = numpy.log10(10000.0 / 30.0) / 300.0
        #     # energies = 10.0 * 10**(energies * elefactor)
        #     # source = numpy.ones(energies.size)
        #     # tmp = numpy.vstack( (energies,source))
        #     if self.input_spectrum is None:
        #         raise Exception("No input beam")
        #     else:
        #         energies = self.input_spectrum[0,:].copy()
        #         source = self.input_spectrum[1,:].copy()
        # elif self.SOURCE == 1:
        #     energies = numpy.linspace(self.ENER_MIN,self.ENER_MAX,self.ENER_N)
        #     source = numpy.ones(energies.size)
        #     tmp = numpy.vstack( (energies,source))
        #     self.input_spectrum = source
        # elif self.SOURCE == 2:
        #     if self.SOURCE == 2: source_file = self.SOURCE_FILE
        #     # if self.SOURCE == 3: source_file = "SRCOMPE"
        #     # if self.SOURCE == 4: source_file = "SRCOMPF"
        #     try:
        #         tmp = numpy.loadtxt(source_file)
        #         energies = tmp[:,0]
        #         source = tmp[:,1]
        #         self.input_spectrum = source
        #     except:
        #         print("Error loading file %s "%(source_file))
        #         raise
        #
        # if self.FILE_DUMP == 0:
        #     output_file = None
        # else:
        #     output_file = "power.spec"
        # out_dictionary = xpower_calc(energies=energies,source=source,substance=substance,
        #                              flags=flags,dens=dens,thick=thick,angle=angle,roughness=roughness,output_file=output_file)
        #
        #
        # try:
        #     print(out_dictionary["info"])
        # except:
        #     pass
        # #send exchange
        calculated_data = DataExchangeObject("XOPPY", self.get_data_exchange_widget_name())
        #
        # try:
        #     calculated_data.add_content("xoppy_data", out_dictionary["data"].T)
        #     calculated_data.add_content("plot_x_col",0)
        #     calculated_data.add_content("plot_y_col",-1)
        # except:
        #     pass
        # try:
        #     # print(out_dictionary["labels"])
        #     calculated_data.add_content("labels", out_dictionary["labels"])
        # except:
        #     pass
        # try:
        #     calculated_data.add_content("info",out_dictionary["info"])
        # except:
        #     pass
        #
        return calculated_data


if __name__ == "__main__":


    from oasys.widgets.exchange import DataExchangeObject


    app = QApplication(sys.argv)
    w = OWsrcalc()

    w.show()


    app.exec()
    w.saveSettings()

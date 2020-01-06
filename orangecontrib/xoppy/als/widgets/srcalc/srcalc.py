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

# from srxraylib.plot.gol import plot_scatter

import syned.beamline.beamline as synedb
import syned.storage_ring.magnetic_structures.insertion_device as synedid

from syned.widget.widget_decorator import WidgetDecorator

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


class OWsrcalc(XoppyWidget, WidgetDecorator):
    name = "SRCALC"
    id = "orange.widgets.srcalc"
    description = "Power Absorbed and Transmitted by Optical Elements"
    icon = "icons/srcalc.png"
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
    NELEMENTS = Setting(1)

    EL0_SHAPE = Setting(2)
    EL0_POSITION = Setting(13.73)  # this is then copied from  SOURCE_SCREEN_DISTANCE
    EL0_P = Setting(10.0)
    EL0_Q = Setting(10.0)
    EL0_ANG = Setting(88.75)
    EL0_THICKNESS = Setting(1000)
    EL0_RELATIVE_TO_PREVIOUS = Setting(0)
    EL0_COATING = Setting(9)

    EL1_SHAPE = Setting(2)
    EL1_POSITION = Setting(10.0)
    EL1_P = Setting(10.0)
    EL1_Q = Setting(10.0)
    EL1_ANG = Setting(88.75)
    EL1_THICKNESS = Setting(1000)
    EL1_RELATIVE_TO_PREVIOUS = Setting(2)
    EL1_COATING = Setting(9)

    EL2_SHAPE = Setting(2)
    EL2_POSITION = Setting(10.0)
    EL2_P = Setting(10.0)
    EL2_Q = Setting(10.0)
    EL2_ANG = Setting(88.75)
    EL2_THICKNESS = Setting(1000)
    EL2_RELATIVE_TO_PREVIOUS = Setting(0)
    EL2_COATING = Setting(9)

    EL3_SHAPE = Setting(2)
    EL3_POSITION = Setting(10.0)
    EL3_P = Setting(10.0)
    EL3_Q = Setting(10.0)
    EL3_ANG = Setting(88.75)
    EL3_THICKNESS = Setting(1000)
    EL3_RELATIVE_TO_PREVIOUS = Setting(0)
    EL3_COATING = Setting(9)

    EL4_SHAPE = Setting(2)
    EL4_POSITION = Setting(10.0)
    EL4_P = Setting(10.0)
    EL4_Q = Setting(10.0)
    EL4_ANG = Setting(88.75)
    EL4_THICKNESS = Setting(1000)
    EL4_RELATIVE_TO_PREVIOUS = Setting(0)
    EL4_COATING = Setting(9)

    EL5_SHAPE = Setting(2)
    EL5_POSITION = Setting(10.0)
    EL5_P = Setting(10.0)
    EL5_Q = Setting(10.0)
    EL5_ANG = Setting(88.75)
    EL5_THICKNESS = Setting(1000)
    EL5_RELATIVE_TO_PREVIOUS = Setting(0)
    EL5_COATING = Setting(9)

    DO_PLOT_GRID = Setting(0)
    DUMP_SHADOW_FILES = Setting(0)

    inputs = WidgetDecorator.syned_input_data()

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
        self.id_RING_ENERGY = oasysgui.lineEdit(box1, self, "RING_ENERGY",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        self.id_RING_CURRENT = oasysgui.lineEdit(box1, self, "RING_CURRENT",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        self.id_KY = oasysgui.lineEdit(box1, self, "KY",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        self.id_KX = oasysgui.lineEdit(box1, self, "KX",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        self.id_NUMBER_OF_PERIODS = oasysgui.lineEdit(box1, self, "NUMBER_OF_PERIODS",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        self.id_PERIOD_LENGTH = oasysgui.lineEdit(box1, self, "PERIOD_LENGTH",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        self.id_SIGMAX = oasysgui.lineEdit(box1, self, "SIGMAX",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        self.id_SIGMAXP = oasysgui.lineEdit(box1, self, "SIGMAXP",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        self.id_SIGMAY = oasysgui.lineEdit(box1, self, "SIGMAY",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
        self.show_at(self.unitFlags()[idx], box1)

        ########
        idx += 1
        box1 = gui.widgetBox(box)
        self.id_SIGMAYP = oasysgui.lineEdit(box1, self, "SIGMAYP",
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
                    valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250,
                          callback=self.setdistance)
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
            oasysgui.lineEdit(box1, self, "EL%d_POSITION"%element_index,
                         label=self.unitLabels()[idx], addSpace=False,
                        valueType=float, validator=QDoubleValidator(), orientation="horizontal", labelWidth=250)
            self.show_at(self.unitFlags()[idx], box1)

            # first element distance is the same as urgent screen position
            if element_index == 0:
                box1.setEnabled(False)

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




        #widget index xx
        idx += 1
        box1 = gui.widgetBox(box)
        gui.separator(box1, height=7)

        gui.comboBox(box1, self, "DO_PLOT_GRID",
                    label=self.unitLabels()[idx], addSpace=False,
                    items=['No', 'Yes'],
                    valueType=int, orientation="horizontal", labelWidth=250)

        self.show_at(self.unitFlags()[idx], box1)

        #widget index xx
        idx += 1
        box1 = gui.widgetBox(box)
        gui.separator(box1, height=7)

        gui.comboBox(box1, self, "DUMP_SHADOW_FILES",
                     label=self.unitLabels()[idx], addSpace=False,
                    items=['No', 'Yes (begin.dat mirr.xx star.xx'],
                    valueType=int, orientation="horizontal", labelWidth=250)

        self.show_at(self.unitFlags()[idx], box1)

        #
        #
        #
        self.mirror_tabs_visibility()

    def setdistance(self):
        self.EL0_POSITION = self.SOURCE_SCREEN_DISTANCE

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
         labels =  ["Ring energy [GeV]","Ring current [A]","Ky","Kx",
                 "Number of Periods","Period Length [m]",
                 "Sigma H [mm]", "Sigma Prime H [mrad]", "Sigma V [mm]", "Sigma Prime V [mrad]",
                 "Number of harmonics",
                 "Source to screen distance [m]","Horizontal acceptance [mm]","Vertical acceptance [mm]",
                 "Number of intervals in half H screen","Number of intervals in half V screen","Electron sigmas",
                 'Number of optical elements:']

         for i in range(6):
            labels = labels + [
                'Type',
                'Distance from previous oe [m]',
                'Focus Ent. Arm [m]',
                'Focus Exit Arm [m]',
                'Inc. Angle to normal [deg]',
                'Orientation (relative to previous)',
                'Coating',
                ]

         labels = labels + ["Plot ray-traced grid","Dump SHADOW files"]

         return labels


    def unitFlags(self):
         return ["True","True","True","True",
                 "True", "True",
                 "True", "True", "True", "True",
                 "True",
                 "True", "True", "True",
                 "True", "True","True",
                 'True',
                 "True", "True", "self.EL0_SHAPE not in (2,8,9)", "self.EL0_SHAPE not in (2,8,9)", "True", "True", "True",  # OE fields
                 "True", "True", "self.EL1_SHAPE not in (2,8,9)", "self.EL1_SHAPE not in (2,8,9)", "True", "True", "True",  # OE fields
                 "True", "True", "self.EL2_SHAPE not in (2,8,9)", "self.EL2_SHAPE not in (2,8,9)", "True", "True", "True",  # OE fields
                 "True", "True", "self.EL3_SHAPE not in (2,8,9)", "self.EL3_SHAPE not in (2,8,9)", "True", "True", "True",  # OE fields
                 "True", "True", "self.EL4_SHAPE not in (2,8,9)", "self.EL4_SHAPE not in (2,8,9)", "True", "True", "True",  # OE fields
                 "True", "True", "self.EL5_SHAPE not in (2,8,9)", "self.EL5_SHAPE not in (2,8,9)", "True", "True", "True",  # OE fields
                 'True','True']

    def get_help_name(self):
        return 'srcalc'

    def selectFile(self):
        self.le_source_file.setText(oasysgui.selectFileFromDialog(self, self.SOURCE_FILE, "Open Source File", file_extension_filter="*.*"))


    def check_fields(self):

        self.RING_ENERGY       = congruence.checkPositiveNumber(self.RING_ENERGY      , "RING_ENERGY      ")
        self.RING_CURRENT      = congruence.checkPositiveNumber(self.RING_CURRENT     , "RING_CURRENT     ")
        self.KY                = congruence.checkPositiveNumber(self.KY               , "KY               ")
        self.KX                = congruence.checkPositiveNumber(self.KX               , "KX               ")
        self.NUMBER_OF_PERIODS = congruence.checkPositiveNumber(self.NUMBER_OF_PERIODS, "NUMBER_OF_PERIODS")
        self.PERIOD_LENGTH     = congruence.checkPositiveNumber(self.PERIOD_LENGTH    , "PERIOD_LENGTH    ")

        self.NUMBER_OF_HARMONICS = congruence.checkNumber(self.NUMBER_OF_HARMONICS, "NUMBER_OF_HARMONICS")

        self.SOURCE_SCREEN_DISTANCE = congruence.checkPositiveNumber(self.SOURCE_SCREEN_DISTANCE, "SOURCE_SCREEN_DISTANCE")
        self.HORIZONTAL_ACCEPTANCE  = congruence.checkPositiveNumber(self.HORIZONTAL_ACCEPTANCE , "HORIZONTAL_ACCEPTANCE ")
        self.VERTICAL_ACCEPTANCE    = congruence.checkPositiveNumber(self.VERTICAL_ACCEPTANCE   , "VERTICAL_ACCEPTANCE   ")
        self.NUMBER_OF_POINTS_H     = congruence.checkPositiveNumber(self.NUMBER_OF_POINTS_H    , "NUMBER_OF_POINTS_H    ")
        self.NUMBER_OF_POINTS_V     = congruence.checkPositiveNumber(self.NUMBER_OF_POINTS_V    , "NUMBER_OF_POINTS_V    ")
        self.ELECTRON_SIGMAS        = congruence.checkPositiveNumber(self.ELECTRON_SIGMAS       , "ELECTRON_SIGMAS       ")
        self.SIGMAX                 = congruence.checkPositiveNumber(self.SIGMAX                , "SIGMAX                ")
        self.SIGMAXP                = congruence.checkPositiveNumber(self.SIGMAXP               , "SIGMAXP               ")
        self.SIGMAY                 = congruence.checkPositiveNumber(self.SIGMAY                , "SIGMAY                ")
        self.SIGMAYP                = congruence.checkPositiveNumber(self.SIGMAYP               , "SIGMAYP               ")

        if self.NELEMENTS >=6:
            self.EL5_POSITION  = congruence.checkPositiveNumber(self.EL5_POSITION,  "EL5_POSITION")
            self.EL5_P         = congruence.checkPositiveNumber(self.EL5_P,         "EL5_P")
            self.EL5_Q         = congruence.checkPositiveNumber(self.EL5_Q,         "EL5_Q")
            self.EL5_ANG       = congruence.checkPositiveNumber(self.EL5_ANG,       "EL5_ANG")
            self.EL5_THICKNESS = congruence.checkPositiveNumber(self.EL5_THICKNESS, "EL5_THICKNESS")

        if self.NELEMENTS >=5:
            self.EL4_POSITION  = congruence.checkPositiveNumber(self.EL4_POSITION,  "EL4_POSITION")
            self.EL4_P         = congruence.checkPositiveNumber(self.EL4_P,         "EL4_P")
            self.EL4_Q         = congruence.checkPositiveNumber(self.EL4_Q,         "EL4_Q")
            self.EL4_ANG       = congruence.checkPositiveNumber(self.EL4_ANG,       "EL4_ANG")
            self.EL4_THICKNESS = congruence.checkPositiveNumber(self.EL4_THICKNESS, "EL4_THICKNESS")

        if self.NELEMENTS >=4:
            self.EL3_POSITION  = congruence.checkPositiveNumber(self.EL3_POSITION,  "EL3_POSITION")
            self.EL3_P         = congruence.checkPositiveNumber(self.EL3_P,         "EL3_P")
            self.EL3_Q         = congruence.checkPositiveNumber(self.EL3_Q,         "EL3_Q")
            self.EL3_ANG       = congruence.checkPositiveNumber(self.EL3_ANG,       "EL3_ANG")
            self.EL3_THICKNESS = congruence.checkPositiveNumber(self.EL3_THICKNESS, "EL3_THICKNESS")

        if self.NELEMENTS >=3:
            self.EL2_POSITION  = congruence.checkPositiveNumber(self.EL2_POSITION,  "EL2_POSITION")
            self.EL2_P         = congruence.checkPositiveNumber(self.EL2_P,         "EL2_P")
            self.EL2_Q         = congruence.checkPositiveNumber(self.EL2_Q,         "EL2_Q")
            self.EL2_ANG       = congruence.checkPositiveNumber(self.EL2_ANG,       "EL2_ANG")
            self.EL2_THICKNESS = congruence.checkPositiveNumber(self.EL2_THICKNESS, "EL2_THICKNESS")

        if self.NELEMENTS >=2:
            self.EL1_POSITION  = congruence.checkPositiveNumber(self.EL1_POSITION,  "EL1_POSITION")
            self.EL1_P         = congruence.checkPositiveNumber(self.EL1_P,         "EL1_P")
            self.EL1_Q         = congruence.checkPositiveNumber(self.EL1_Q,         "EL1_Q")
            self.EL1_ANG       = congruence.checkPositiveNumber(self.EL1_ANG,       "EL1_ANG")
            self.EL1_THICKNESS = congruence.checkPositiveNumber(self.EL1_THICKNESS, "EL1_THICKNESS")

        if self.NELEMENTS >=1:
            self.EL0_POSITION  = congruence.checkPositiveNumber(self.EL0_POSITION,  "EL0_POSITION")
            self.EL0_P         = congruence.checkPositiveNumber(self.EL0_P,         "EL0_P")
            self.EL0_Q         = congruence.checkPositiveNumber(self.EL0_Q,         "EL0_Q")
            self.EL0_ANG       = congruence.checkPositiveNumber(self.EL0_ANG,       "EL0_ANG")
            self.EL0_THICKNESS = congruence.checkPositiveNumber(self.EL0_THICKNESS, "EL0_THICKNESS")

    def receive_syned_data(self, data):

        if isinstance(data, synedb.Beamline):
            if not data._light_source is None and isinstance(data._light_source._magnetic_structure, synedid.InsertionDevice):
                light_source = data._light_source

                # RING_ENERGY = Setting(2.0)
                # RING_CURRENT = Setting(0.5)
                # KY = Setting(3.07)
                # KX = Setting(0.0)
                # NUMBER_OF_PERIODS = Setting(137)
                # PERIOD_LENGTH = Setting(0.0288)
                # NUMBER_OF_HARMONICS = Setting(-49)
                # ELECTRON_SIGMAS = Setting(4)
                # SIGMAX = Setting(12.1e-3)
                # SIGMAXP = Setting(5.7e-3)
                # SIGMAY = Setting(14.7e-3)
                # SIGMAYP = Setting(4.7e-3)
                # NELEMENTS = Setting(2)


                self.RING_ENERGY = light_source._electron_beam._energy_in_GeV
                self.RING_CURRENT = light_source._electron_beam._current

                x, xp, y, yp = light_source._electron_beam.get_sigmas_all()

                self.SIGMAX = x * 1e3
                self.SIGMAY = y * 1e3
                self.SIGMAXP = xp * 1e3
                self.SIGMAYP = yp * 1e3
                self.PERIOD_LENGTH = light_source._magnetic_structure._period_length
                self.NUMBER_OF_PERIODS = int(light_source._magnetic_structure._number_of_periods)
                self.KY = light_source._magnetic_structure._K_vertical
                self.KX = light_source._magnetic_structure._K_horizontal

                self.set_enabled(False)

            else:
                self.set_enabled(True)
                # raise ValueError("Syned data not correct")
        else:
            self.set_enabled(True)
            # raise ValueError("Syned data not correct")

    def set_enabled(self,value):
        if value == True:
                self.id_RING_ENERGY.setEnabled(True)
                self.id_SIGMAX.setEnabled(True)
                self.id_SIGMAY.setEnabled(True)
                self.id_SIGMAXP.setEnabled(True)
                self.id_SIGMAYP.setEnabled(True)
                self.id_RING_CURRENT.setEnabled(True)
                self.id_PERIOD_LENGTH.setEnabled(True)
                self.id_NUMBER_OF_PERIODS.setEnabled(True)
                self.id_KX.setEnabled(True)
                self.id_KY.setEnabled(True)
        else:
                self.id_RING_ENERGY.setEnabled(False)
                self.id_SIGMAX.setEnabled(False)
                self.id_SIGMAY.setEnabled(False)
                self.id_SIGMAXP.setEnabled(False)
                self.id_SIGMAYP.setEnabled(False)
                self.id_RING_CURRENT.setEnabled(False)
                self.id_PERIOD_LENGTH.setEnabled(False)
                self.id_NUMBER_OF_PERIODS.setEnabled(False)
                self.id_KX.setEnabled(False)
                self.id_KY.setEnabled(False)


    def do_xoppy_calculation(self):
        return self.xoppy_calc_srcalc()

    def extract_data_from_xoppy_output(self, calculation_output):
        return calculation_output

    def plot_results(self, calculated_data, progressBarValue=80):

        if not self.view_type == 0:
            if not calculated_data is None:
                # current_index = self.tabs.currentIndex()

                # try:
                index = -1
                if True:
                    for oe_n in range(self.NELEMENTS+1):
                        totPower = calculated_data["Zlist"][oe_n].sum() * \
                                   (calculated_data["X"][1] - calculated_data["X"][0]) * \
                                   (calculated_data["Y"][1] - calculated_data["Y"][0])

                        #
                        # urgent results
                        #
                        if oe_n == 0:
                            title = 'Power density [W/mm2] at %4.1f m, Integrated Power: %6.1f W'%(self.SOURCE_SCREEN_DISTANCE,totPower)
                            xtitle = 'H (urgent) [mm] (%d pixels)' % (calculated_data["X"].size)
                            ytitle = 'V (urgent) [mm] (%d pixels)' % (calculated_data["Y"].size)
                            x = calculated_data["X"]
                            y = calculated_data["Y"]
                        else:
                            title = 'Power density [W/mm2] transmitted after element %d Integrated Power: %6.1f W'%(oe_n, totPower)
                            xtitle = 'H [pixels]'
                            ytitle = 'V [pixels]'
                            x = numpy.arange(calculated_data["X"].size)
                            y = numpy.arange(calculated_data["Y"].size)
                        index += 1
                        self.plot_data2D(calculated_data["Zlist"][oe_n], x, y,  index, 0,
                                         xtitle=xtitle, ytitle=ytitle, title=title)
                        #
                        # ray tracing results
                        #
                        if oe_n > 0:
                            if self.DO_PLOT_GRID:
                                # mirror grid
                                index += 1
                                dataX = calculated_data["OE_FOOTPRINT"][oe_n-1][0, :]
                                dataY = calculated_data["OE_FOOTPRINT"][oe_n-1][1, :]
                                self.plot_data1D(1e3*dataX, 1e3*dataY, index, 0, title="footprint oe %d"%oe_n, xtitle="Y (shadow col 2) [mm]",ytitle="X (shadow col 1) [mm]")
                                # image grid
                                index += 1
                                dataX = calculated_data["OE_IMAGE"][oe_n-1][0, :]
                                dataY = calculated_data["OE_IMAGE"][oe_n-1][1, :]
                                self.plot_data1D(1e3*dataX, 1e3*dataY, index, 0, title="image just after oe %d perp to beam"%oe_n, xtitle="X (shadow col 1) [mm]",ytitle="Z (shadow col 2) [mm]")
                            # mirror power density
                            index += 1
                            data2D = calculated_data["POWER_DENSITY_FOOTPRINT"][oe_n - 1]
                            H = 1e3 * calculated_data["POWER_DENSITY_FOOTPRINT_H"][oe_n - 1]
                            V = 1e3 * calculated_data["POWER_DENSITY_FOOTPRINT_V"][oe_n - 1]
                            tmp = data2D.shape
                            self.plot_data2D(data2D,H[:,0],V[0,:],
                                             index, 0,
                                             xtitle='Y (shadow col 2) [mm]',
                                             ytitle='X (shadow col 1) [mm]')
                            # image power density
                            index += 1
                            data2D = calculated_data["POWER_DENSITY_IMAGE"][oe_n-1]
                            H = 1e3 * calculated_data["POWER_DENSITY_IMAGE_H"][oe_n - 1]
                            V = 1e3 * calculated_data["POWER_DENSITY_IMAGE_V"][oe_n - 1]
                            self.plot_data2D(data2D,H[:,0],V[0,:],
                                             index, 0,
                                             xtitle='X (shadow col 1) [mm]',
                                             ytitle='Z (shadow col 3) [mm]')

                # except:
                #     pass

            else:
                raise Exception("Empty Data")


    def get_data_exchange_widget_name(self):
        return "SRCALC"

    def getTitles(self):
        titles = []
        for oe_n in range(self.NELEMENTS+1):
            titles.append("[oe %d (urgent)]"%oe_n)
            if oe_n > 0:
                if self.DO_PLOT_GRID:
                    titles.append("[oe %d (ray-traced mirror grid)]" % oe_n)
                    titles.append("[oe %d (ray-traced image grid)]" % oe_n)
                titles.append("[oe %d (ray tracing mirror power)]" % oe_n)
                titles.append("[oe %d (ray tracing image power)]" % oe_n)
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
                command = os.path.join(locations.home_bin(),'srcalc')
            else:
                command = "'" + os.path.join(locations.home_bin(), 'srcalc') + "'"
            print("Running command '%s' in directory: %s "%(command, locations.home_bin_run()))
            print("\n--------------------------------------------------------\n")
            os.system(command)
            print("\n--------------------------------------------------------\n")



        grabber.stop()

        for row in grabber.ttyData:
            self.writeStdOut(row)

        self.progressBarSet(99)

        #
        # read urgent file
        #
        f = open("O_IDPower.TXT",'r')
        txt = f.read()
        f.close()
        self.info_output.setText(txt)

        out_dictionary = load_srcalc_output_file(filename="D_IDPower.TXT")

        #
        # do additional calculations (ray-tracing and power density maps)
        # Note that the results of these two calculations are added to out_dictionary

        #
        # do the ray tracing
        #
        oe_parameters = {
            "EL0_SHAPE":                self.EL0_SHAPE               ,
            "EL0_POSITION":             self.EL0_POSITION            ,
            "EL0_P":                    self.EL0_P                   ,
            "EL0_Q":                    self.EL0_Q                   ,
            "EL0_ANG":                  self.EL0_ANG                 ,
            "EL0_THICKNESS":            self.EL0_THICKNESS           ,
            "EL0_RELATIVE_TO_PREVIOUS": self.EL0_RELATIVE_TO_PREVIOUS,
            "EL1_SHAPE":                self.EL1_SHAPE               ,
            "EL1_POSITION":             self.EL1_POSITION            ,
            "EL1_P":                    self.EL1_P                   ,
            "EL1_Q":                    self.EL1_Q                   ,
            "EL1_ANG":                  self.EL1_ANG                 ,
            "EL1_THICKNESS":            self.EL1_THICKNESS           ,
            "EL1_RELATIVE_TO_PREVIOUS": self.EL1_RELATIVE_TO_PREVIOUS,
            "EL2_SHAPE":                self.EL2_SHAPE               ,
            "EL2_POSITION":             self.EL2_POSITION            ,
            "EL2_P":                    self.EL2_P                   ,
            "EL2_Q":                    self.EL2_Q                   ,
            "EL2_ANG":                  self.EL2_ANG                 ,
            "EL2_THICKNESS":            self.EL2_THICKNESS           ,
            "EL2_RELATIVE_TO_PREVIOUS": self.EL2_RELATIVE_TO_PREVIOUS,
            "EL3_SHAPE":                self.EL3_SHAPE               ,
            "EL3_POSITION":             self.EL3_POSITION            ,
            "EL3_P":                    self.EL3_P                   ,
            "EL3_Q":                    self.EL3_Q                   ,
            "EL3_ANG":                  self.EL3_ANG                 ,
            "EL3_THICKNESS":            self.EL3_THICKNESS           ,
            "EL3_RELATIVE_TO_PREVIOUS": self.EL3_RELATIVE_TO_PREVIOUS,
            "EL4_SHAPE":                self.EL4_SHAPE               ,
            "EL4_POSITION":             self.EL4_POSITION            ,
            "EL4_P":                    self.EL4_P                   ,
            "EL4_Q":                    self.EL4_Q                   ,
            "EL4_ANG":                  self.EL4_ANG                 ,
            "EL4_THICKNESS":            self.EL4_THICKNESS           ,
            "EL4_RELATIVE_TO_PREVIOUS": self.EL4_RELATIVE_TO_PREVIOUS,
            "EL5_SHAPE":                self.EL5_SHAPE               ,
            "EL5_POSITION":             self.EL5_POSITION            ,
            "EL5_P":                    self.EL5_P                   ,
            "EL5_Q":                    self.EL5_Q                   ,
            "EL5_ANG":                  self.EL5_ANG                 ,
            "EL5_THICKNESS":            self.EL5_THICKNESS           ,
            "EL5_RELATIVE_TO_PREVIOUS": self.EL5_RELATIVE_TO_PREVIOUS,

        }

        out_dictionary_with_ray_tracing = ray_tracing(out_dictionary,
                                             SOURCE_SCREEN_DISTANCE=self.SOURCE_SCREEN_DISTANCE,
                                             number_of_elements=self.NELEMENTS,
                                             oe_parameters=oe_parameters,
                                             )
        #
        # calculate power density maps
        #
        out_dictionary_with_power_density = compute_power_density_on_optical_elements(out_dictionary_with_ray_tracing)

        return out_dictionary_with_power_density

    #
    # overwritten methods
    #
    def plot_data1D(self, dataX, dataY, tabs_canvas_index, plot_canvas_index, title="", xtitle="", ytitle=""):

        self.tab[tabs_canvas_index].layout().removeItem(self.tab[tabs_canvas_index].layout().itemAt(0))

        self.plot_canvas[plot_canvas_index] = oasysgui.plotWindow()

        self.plot_canvas[plot_canvas_index].addCurve(dataX, dataY, symbol=',', linestyle=' ')

        self.plot_canvas[plot_canvas_index].resetZoom()
        self.plot_canvas[plot_canvas_index].setXAxisAutoScale(True)
        self.plot_canvas[plot_canvas_index].setYAxisAutoScale(True)
        self.plot_canvas[plot_canvas_index].setGraphGrid(False)

        self.plot_canvas[plot_canvas_index].setXAxisLogarithmic(False)
        self.plot_canvas[plot_canvas_index].setYAxisLogarithmic(False)
        self.plot_canvas[plot_canvas_index].setGraphXLabel(xtitle)
        self.plot_canvas[plot_canvas_index].setGraphYLabel(ytitle)
        self.plot_canvas[plot_canvas_index].setGraphTitle(title)

        self.tab[tabs_canvas_index].layout().addWidget(self.plot_canvas[plot_canvas_index])


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


def ray_tracing(
        out_dictionary,
        SOURCE_SCREEN_DISTANCE=13.73,
        number_of_elements=1,
        oe_parameters=  {
            "EL0_SHAPE":2,"EL0_POSITION":13.73,"EL0_P":0.0,"EL0_Q":0.0,"EL0_ANG":88.75,"EL0_THICKNESS":1000,"EL0_RELATIVE_TO_PREVIOUS":2,
                        },
        dump_shadow_files=True):

    import shadow4
    from shadow4.beam.beam import Beam
    from shadow4.compatibility.beam3 import Beam3

    from shadow4.optical_surfaces.conic import Conic
    from shadow4.optical_surfaces.toroid import Toroid

    #
    # compute shadow beam from urgent results
    #
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

    if dump_shadow_files:
        Beam3.initialize_from_shadow4_beam(beam).write('begin.dat')

    OE_FOOTPRINT = []
    OE_IMAGE = []

    for oe_index in range(number_of_elements):

        p = oe_parameters["EL%d_POSITION" % oe_index]
        q = 0

        theta_grazing = (90.0 - oe_parameters["EL0_ANG"]) * numpy.pi / 180

        if oe_parameters["EL%d_RELATIVE_TO_PREVIOUS"%oe_index] == 0:
            alpha = 90.0 * numpy.pi / 180
        elif oe_parameters["EL%d_RELATIVE_TO_PREVIOUS"%oe_index] == 1:
            alpha = 270.0 * numpy.pi / 180
        elif oe_parameters["EL%d_RELATIVE_TO_PREVIOUS"%oe_index] == 2:
            alpha = 0.0
        elif oe_parameters["EL%d_RELATIVE_TO_PREVIOUS"%oe_index] == 3:
            alpha = 180.0 * numpy.pi / 180


        if oe_parameters["EL%d_SHAPE"%oe_index] == 0:     # "Toroidal mirror",
            is_conic = False
            toroid = Toroid()
            toroid.set_from_focal_distances(
                oe_parameters["EL%d_P" % oe_index],
                oe_parameters["EL%d_Q" % oe_index],
                theta_grazing)
        elif oe_parameters["EL%d_SHAPE"%oe_index] == 1:     # "Spherical mirror",
            is_conic = True
            ccc = Conic.initialize_as_sphere_from_focal_distances(
                oe_parameters["EL%d_P" % oe_index],
                oe_parameters["EL%d_Q" % oe_index],
                theta_grazing,cylindrical=0,cylangle=0,switch_convexity=0)
        elif oe_parameters["EL%d_SHAPE"%oe_index] == 2:     # "Plane mirror",
            is_conic = True
            ccc = Conic.initialize_as_plane()
        elif oe_parameters["EL%d_SHAPE"%oe_index] == 3:     # "MerCyl mirror",
            is_conic = True
            ccc = Conic.initialize_as_sphere_from_focal_distances(
                oe_parameters["EL%d_P" % oe_index],
                oe_parameters["EL%d_Q" % oe_index],
                theta_grazing,cylindrical=1,cylangle=0,switch_convexity=0)
        elif oe_parameters["EL%d_SHAPE"%oe_index] == 4:     # "SagCyl mirror",
            raise Exception("Not implemented")
        elif oe_parameters["EL%d_SHAPE"%oe_index] == 5:     # "Ellipsoidal mirror",
            is_conic = True
            ccc = Conic.initialize_as_ellipsoid_from_focal_distances(
                oe_parameters["EL%d_P" % oe_index],
                oe_parameters["EL%d_Q" % oe_index],
                theta_grazing,cylindrical=0,cylangle=0,switch_convexity=0)
        elif oe_parameters["EL%d_SHAPE"%oe_index] == 6:     # "MerEll mirror",
            is_conic = True
            ccc = Conic.initialize_as_ellipsoid_from_focal_distances(
                oe_parameters["EL%d_P" % oe_index],
                oe_parameters["EL%d_Q" % oe_index],
                theta_grazing,cylindrical=1,cylangle=0,switch_convexity=0)
        elif oe_parameters["EL%d_SHAPE"%oe_index] == 7:     # "SagEllip mirror",
            raise Exception("Not implemented")
        elif oe_parameters["EL%d_SHAPE"%oe_index] == 8:     # "Filter",
            is_conic = True
            ccc = Conic.initialize_as_plane()
        elif oe_parameters["EL%d_SHAPE"%oe_index] == 9:     # "Crystal"
            is_conic = True
            ccc = Conic.initialize_as_plane()



        newbeam = beam.duplicate()


        #
        # put beam in mirror reference system
        #

        newbeam.rotate(alpha, axis=2)
        newbeam.rotate(theta_grazing, axis=1)
        newbeam.translation([0.0, -p * numpy.cos(theta_grazing), p * numpy.sin(theta_grazing)])

        #
        # reflect beam in the mirror surface and dump mirr.01
        #
        if is_conic:
            print("Element index %d is CONIC :" % oe_index, ccc.info())
            newbeam = ccc.apply_specular_reflection_on_beam(newbeam)
        else:
            print("Element index %d is TOROIDAL :" % oe_index, toroid.info())
            newbeam = toroid.apply_specular_reflection_on_beam(newbeam)

        if dump_shadow_files:
            Beam3.initialize_from_shadow4_beam(newbeam).write('mirr.%02d'%(oe_index+1))
        OE_FOOTPRINT.append( newbeam.get_columns((2, 1)) )

        #
        # put beam in lab frame and compute image
        #
        newbeam.rotate(theta_grazing, axis=1)
        newbeam.rotate(-alpha, axis=2) # TODO ckeck alpha
        newbeam.retrace(q, resetY=True)
        if dump_shadow_files:
            Beam3.initialize_from_shadow4_beam(newbeam).write('star.%02d'%(oe_index+1))
        OE_IMAGE.append(newbeam.get_columns((1, 3)))


    # add ray tracing results to output
    out_dictionary["OE_FOOTPRINT"] = OE_FOOTPRINT
    out_dictionary["OE_IMAGE"] = OE_IMAGE

    return out_dictionary

def calculate_pixel_areas(X,Y,suppress_last_row_and_column=True):
    u1 = numpy.roll(X, -1, axis=0) - X
    u2 = numpy.roll(Y, -1, axis=0) - Y
    v1 = numpy.roll(X, -1, axis=1) - X
    v2 = numpy.roll(Y, -1, axis=1) - Y

    if suppress_last_row_and_column:
        u1 = u1[0:-1, 0:-1].copy()
        u2 = u2[0:-1, 0:-1].copy()
        v1 = v1[0:-1, 0:-1].copy()
        v2 = v2[0:-1, 0:-1].copy()
        XX = X[0:-1, 0:-1].copy()
        YY = Y[0:-1, 0:-1].copy()
    else:
        XX = X.copy()
        YY = Y.copy()
    return u1 * v2 - u2 * v1, XX, YY


def compute_power_density_on_optical_elements(dict1,do_interpolation=True):

    # first compute the area of the pixels at the screen used by usrgent

    x = 1e-3 * dict1["X"]
    y = 1e-3 * dict1["Y"]
    X = numpy.outer(x, numpy.ones_like(y))
    Y = numpy.outer(numpy.ones_like(x), y)

    shapeXY = X.shape

    AREA0,X0,Y0 = calculate_pixel_areas(X, Y)
    # plot_scatter(X.flatten(), Y.flatten(), title="SCREEN")
    shapeXYbis = AREA0.shape

    # now build maps for optical elements

    try:
        OE_FOOTPRINT = dict1["OE_FOOTPRINT"]
        OE_IMAGE = dict1["OE_IMAGE"]
        number_of_elements_traced = len(OE_FOOTPRINT)
    except:
        number_of_elements_traced = 0

    print("Number of raytraced elements: %d"%number_of_elements_traced)

    POWER_DENSITY_FOOTPRINT = []
    POWER_DENSITY_FOOTPRINT_H = []
    POWER_DENSITY_FOOTPRINT_V = []

    POWER_DENSITY_IMAGE = []
    POWER_DENSITY_IMAGE_H = []
    POWER_DENSITY_IMAGE_V = []

    for element_index in range(number_of_elements_traced):
        FOOTPRINT_H = OE_FOOTPRINT[element_index][0, :].copy().reshape(shapeXY)
        FOOTPRINT_V = OE_FOOTPRINT[element_index][1, :].copy().reshape(shapeXY)
        AREA_FOOTPRINT,XX_FOOTPRINT,YY_FOOTPRINT = calculate_pixel_areas(FOOTPRINT_H, FOOTPRINT_V)
        areas_factor_footprint = numpy.abs(AREA0 / AREA_FOOTPRINT)
        power_density_footprint = areas_factor_footprint * (dict1["Zlist"][element_index] - dict1["Zlist"][element_index+1])[0:(shapeXYbis[0]),0:(shapeXYbis[1])]

        # plot_scatter(footprint_h.flatten(), AREA0.flatten() , title="OE %d" % (1 + element_index))

        IMAGE_H = OE_IMAGE[element_index][0, :].copy().reshape(shapeXY)
        IMAGE_V = OE_IMAGE[element_index][1, :].copy().reshape(shapeXY)
        AREA_IMAGE,XX_IMAGE,YY_IMAGE = calculate_pixel_areas(IMAGE_H, IMAGE_V)
        areas_factor_image = numpy.abs(AREA0 / AREA_IMAGE)
        power_density_image = areas_factor_image * (dict1["Zlist"][element_index + 1])[0:(shapeXYbis[0]),0:(shapeXYbis[1])]

        from scipy import interpolate
        if do_interpolation:

            XX_FOOTPRINT_old = XX_FOOTPRINT.copy()
            YY_FOOTPRINT_old = YY_FOOTPRINT.copy()
            xx_footprint = numpy.linspace(XX_FOOTPRINT_old.min(), XX_FOOTPRINT_old.max(), XX_FOOTPRINT_old.shape[0])
            yy_footprint = numpy.linspace(YY_FOOTPRINT_old.min(), YY_FOOTPRINT_old.max(), YY_FOOTPRINT_old.shape[1])

            XX_FOOTPRINT = numpy.outer(xx_footprint,numpy.ones_like(yy_footprint))
            YY_FOOTPRINT = numpy.outer(numpy.ones_like(xx_footprint), yy_footprint)

            power_density_footprint = interpolate.griddata(
                (XX_FOOTPRINT_old.flatten(), YY_FOOTPRINT_old.flatten()),
                power_density_footprint.flatten(),
                (XX_FOOTPRINT, YY_FOOTPRINT), method='cubic',fill_value=0.0)

            # print(">>>>> before: ", XX_FOOTPRINT_old.shape, YY_FOOTPRINT_old.shape, power_density_footprint.shape)
            # print(">>>>> after: ", XX_FOOTPRINT.shape, YY_FOOTPRINT.shape, power_density_footprint.shape)

            XX_IMAGE_old = XX_IMAGE.copy()
            YY_IMAGE_old = YY_IMAGE.copy()
            xx_image = numpy.linspace(XX_IMAGE_old.min(), XX_IMAGE_old.max(), XX_IMAGE_old.shape[0])
            yy_image = numpy.linspace(YY_IMAGE_old.min(), YY_IMAGE_old.max(), YY_IMAGE_old.shape[1])

            XX_IMAGE = numpy.outer(xx_image,numpy.ones_like(yy_image))
            YY_IMAGE = numpy.outer(numpy.ones_like(xx_image), yy_image)

            power_density_image = interpolate.griddata(
                (XX_IMAGE_old.flatten(), YY_IMAGE_old.flatten()),
                power_density_image.flatten(),
                (XX_IMAGE, YY_IMAGE), method='cubic',fill_value=0.0)


        POWER_DENSITY_FOOTPRINT.append( power_density_footprint )
        POWER_DENSITY_FOOTPRINT_H.append(XX_FOOTPRINT)
        POWER_DENSITY_FOOTPRINT_V.append(YY_FOOTPRINT)
        POWER_DENSITY_IMAGE.append(  power_density_image )
        POWER_DENSITY_IMAGE_H.append(XX_IMAGE)
        POWER_DENSITY_IMAGE_V.append(YY_IMAGE)

    dict1["POWER_DENSITY_FOOTPRINT"] = POWER_DENSITY_FOOTPRINT
    dict1["POWER_DENSITY_FOOTPRINT_H"] = POWER_DENSITY_FOOTPRINT_H
    dict1["POWER_DENSITY_FOOTPRINT_V"] = POWER_DENSITY_FOOTPRINT_V
    dict1["POWER_DENSITY_IMAGE"] = POWER_DENSITY_IMAGE
    dict1["POWER_DENSITY_IMAGE_H"] = POWER_DENSITY_IMAGE_H
    dict1["POWER_DENSITY_IMAGE_V"] = POWER_DENSITY_IMAGE_V

    return dict1


if __name__ == "__main__":



    test = 0  # 0= widget, 1=load D_IDPower.TXT, 2 =ray tracing
    if test == 0:
        app = QApplication(sys.argv)
        w = OWsrcalc()
        w.show()
        app.exec()
        w.saveSettings()
    elif test == 1:
        dict1 = load_srcalc_output_file(filename="D_IDPower.TXT", skiprows=5, do_plot=0)
        dict2 = ray_tracing(dict1)
        dict3 = compute_power_density_on_optical_elements(dict2)


    elif test == 2:
        dict1 = load_srcalc_output_file(filename="D_IDPower.TXT", skiprows=5, do_plot=0)
        dict2 = ray_tracing(dict1)
        OE_FOOTPRINT = dict2["OE_FOOTPRINT"]
        OE_IMAGE = dict2["OE_IMAGE"]
        print(OE_FOOTPRINT[0].shape)
        plot_scatter(OE_FOOTPRINT[0][0,:],OE_FOOTPRINT[0][1,:],plot_histograms=False,title="Footprint",show=False)
        plot_scatter(OE_IMAGE[0][0, :], OE_IMAGE[0][1, :], plot_histograms=False,title="Image")

import os, sys
import numpy

from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QWidget, QLabel, QSizePolicy
from PyQt5.QtGui import QTextCursor,QFont, QPalette, QColor, QPainter, QBrush, QPen, QPixmap

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import orangecanvas.resources as resources

from orangewidget import gui, widget
from orangewidget.settings import Setting

from oasys.widgets.widget import OWWidget
from oasys.widgets import gui as oasysgui

from srxraylib.metrology.dabam import dabam, autocorrelationfunction


from orangecontrib.shadow.util.shadow_objects import ShadowPreProcessorData

from copy import copy
import re
from urllib.request import urlopen

class OWpre_dabam(OWWidget):
    name = "DABAM Prepare Profile"
    id = "dabam_prepare_profile"
    description = "Import 1D surface error profile into DABAM"
    icon = "icons/pre_dabam.png"
    author = "M Sanchez del Rio"
    maintainer_email = "srio@lbl.gov; lrebuffi@anl.gov"
    priority = 7
    category = ""
    keywords = ["dabam_prepare_profile"]

    outputs = [{"name": "DABAM 1D Profile",
         "type": numpy.ndarray,
         "doc": "DABAM 1D Profile",
         "id": "DABAM 1D Profile"}]


    want_main_area = 1
    want_control_area = 1

    MAX_WIDTH = 1320
    MAX_HEIGHT = 700

    IMAGE_WIDTH = 860
    IMAGE_HEIGHT = 645

    CONTROL_AREA_WIDTH = 405
    TABS_AREA_HEIGHT = 618

    heigth_profile_file_name = Setting('dabam-XXX')
    raw_actions = Setting(0)

    column_index_abscissas = Setting(0)
    column_index_ordinates = Setting(1)
    skiprows = Setting(0)
    useHeightsOrSlopes = Setting(1)
    to_SI_abscissas = Setting(1e-3)
    to_SI_ordinates = Setting(1.0)
    detrending_option = Setting(0)

    YEAR_FABRICATION        =  Setting("")
    SURFACE_SHAPE           =  Setting(0)
    SURFACE_SHAPE_LIST = ["undefined","plane","spherical","cylindrical",
                          "elliptical","elliptical(unbent)","elliptical(detrended)",
                          "toroidal","toroidal(unbent)","toroidal(detrended)",
                          "parabolic","parabolic(unbent)"]
    # Undefined plane spherical cylindrical elliptical parabolic toroidal + (unbent,detrended)
                                            # Plane Spherical Elliptical Parabolic Toroidal Other [WEB]
                                            # All Plane Cylindrical Elliptical Toroidal Spherical [OASYS DABAM]
                                            # plane spherical elliptical toroidal cylindrical  elliptical(unbent) toroid(unbent) elliptical(detrended)
    FUNCTION                =  Setting(0)  # 0=Undefined 1=White Beam Mirror 2=Collimating Mirror 3=Focusing Mirror 4=Substrate for grating 5=substrate for multilayer
    FUNCTION_LIST = ["undefined","white beam mirror","collimating mirror","focusing mirror","substrate for grating","substrate for multilayer"]
    LENGTH                  =  Setting("")  #
    WIDTH                   =  Setting("")
    THICK                   =  Setting("")
    LENGTH_OPTICAL          =  Setting("")
    SUBSTRATE               =  Setting("")
    COATING                 =  Setting("")
    FACILITY                =  Setting("")
    INSTRUMENT              =  Setting("")
    POLISHING               =  Setting("")
    ENVIRONMENT             =  Setting(0)  # Other - Clamped - Gravity Direction - Cooling system -
    ENVIRONMENT_LIST = ["unknown","Clamped","gravity direction","cooling system"]
    SCAN_DATE               =  Setting("")
    CALC_HEIGHT_RMS         =  Setting("")
    CALC_HEIGHT_RMS_FACTOR  =  Setting("")
    CALC_SLOPE_RMS          =  Setting("")
    CALC_SLOPE_RMS_FACTOR   =  Setting("")
    USER_EXAMPLE            =  Setting("")
    USER_REFERENCE          =  Setting("")
    USER_ADDED_BY           =  Setting("")


    workspace_units_label = "m"
    si_to_user_units = 1.0
    undo_text_buffer = ""
    tab=[]

    usage_path = os.path.join(resources.package_dirname("orangecontrib.shadow.widgets.gui"), "misc", "dabam_height_profile_usage.png")

    def __init__(self):
        super().__init__()

        geom = QApplication.desktop().availableGeometry()
        self.setGeometry(QRect(round(geom.width() * 0.05),
                               round(geom.height() * 0.05),
                               round(min(geom.width() * 0.98, self.MAX_WIDTH)),
                               round(min(geom.height() * 0.95, self.MAX_HEIGHT))))

        self.setMaximumHeight(self.geometry().height())
        self.setMaximumWidth(self.geometry().width())

        gui.separator(self.controlArea)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        tabs_setting = oasysgui.tabWidget(self.controlArea)
        tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT)
        tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)

        tab_input = oasysgui.createTabPage(tabs_setting, "Import")
        tab_calc = oasysgui.createTabPage(tabs_setting, "Calculate")
        tab_gener = oasysgui.createTabPage(tabs_setting, "Export")
        tab_out = oasysgui.createTabPage(tabs_setting, "Output")
        tab_usa = oasysgui.createTabPage(tabs_setting, "Use of the Widget")

        #
        #-------------------- Import
        #

        out_box = oasysgui.widgetBox(tab_input, "Raw data", addSpace=True, orientation="horizontal", height=600)
        self.raw_textarea = oasysgui.textArea(height=500,width=None,readOnly=False,noWrap=True)
        out_box.layout().addWidget(self.raw_textarea)
        gui.comboBox(tab_input, self, "raw_actions", label="Modify:", labelWidth=300,
                     items=["Select action: ",
                            "Load from file",
                            "Remove comment lines",
                            "Remove commas",
                            "Remove quotes",
                            "Clear",
                            "Undo last action",
                            "Load example",
                            ], sendSelectedValue=False, orientation="horizontal",
                     callback=self.raw_edit)

        gui.separator(out_box)

        #
        #-------------------- calculate
        #

        button = gui.button(tab_calc, self, "Calculate", callback=self.calculate)

        out_calc = oasysgui.widgetBox(tab_calc, "Calculation Parameters", addSpace=True, orientation="vertical", height=500)


        gui.comboBox(out_calc, self, "useHeightsOrSlopes", label="data is", labelWidth=300,
                     items=["heights",
                            "slopes",
                            ], sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(out_calc, self, "skiprows", "Number of rows to skip",
                           labelWidth=300, valueType=int, orientation="horizontal")
        oasysgui.lineEdit(out_calc, self, "column_index_abscissas", "Index of column with abscissas",
                           labelWidth=300, valueType=int, orientation="horizontal")
        oasysgui.lineEdit(out_calc, self, "column_index_ordinates", "Index of column with ordinates",
                           labelWidth=300, valueType=int, orientation="horizontal")

        oasysgui.lineEdit(out_calc, self, "to_SI_abscissas", "Factor to convert abscissas into SI",
                           labelWidth=300, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(out_calc, self, "to_SI_ordinates", "Factor to convert ordinates into SI",
                           labelWidth=300, valueType=float, orientation="horizontal")

        gui.comboBox(out_calc, self, "detrending_option", label="detrending", labelWidth=300,
                     items=["None",
                            "Fisrt degree polynomial",
                            "Ellipse",
                            ], sendSelectedValue=False, orientation="horizontal")


        gui.separator(out_calc)

        #
        #-------------------- Export
        #

        button = gui.button(tab_gener, self, "Create DABAM files", callback=self.export)


        export_box = oasysgui.widgetBox(tab_gener, "Export DABAM file", addSpace=True, orientation="vertical", height=520)

        label_width = 250

        tmp = oasysgui.widgetBox(tab_gener, "", addSpace=True, orientation="horizontal")
        button = gui.button(tmp, self, "Clear Info", callback=self.clear)

        oasysgui.lineEdit(export_box, self, "YEAR_FABRICATION", "Year of fabrication", labelWidth=label_width, valueType=str, orientation="horizontal")

        gui.comboBox(export_box, self, "SURFACE_SHAPE", label="Surface shape", labelWidth=label_width,
                     items=self.SURFACE_SHAPE_LIST, sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(export_box, self, "FUNCTION", label="Function", labelWidth=label_width,
                     items=self.FUNCTION_LIST, sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(export_box, self, "LENGTH", "Length in SI units [m]", labelWidth=label_width, valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(export_box, self, "WIDTH", "Width in SI units [m]", labelWidth=label_width, valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(export_box, self, "THICK", "Thickness in SI units [m]", labelWidth=label_width, valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(export_box, self, "LENGTH_OPTICAL", "Optical length in SI units [m]", labelWidth=label_width, valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(export_box, self, "SUBSTRATE", "Substrate (e.g. Si)", labelWidth=label_width, valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(export_box, self, "COATING", "Coating (e.g. Pt)", labelWidth=label_width, valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(export_box, self, "FACILITY", "Facility (e.g. ESRF)", labelWidth=label_width, valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(export_box, self, "INSTRUMENT", "Instrument type used", labelWidth=label_width, valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(export_box, self, "POLISHING", "Polishing method", labelWidth=label_width, valueType=str,
                          orientation="horizontal")

        gui.comboBox(export_box, self, "ENVIRONMENT", label="Environment", labelWidth=300,
                     items=self.ENVIRONMENT_LIST, sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(export_box, self, "SCAN_DATE", "Date of measurement YYYMMDD", labelWidth=label_width, valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(export_box, self, "USER_EXAMPLE", "User example", labelWidth=label_width, valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(export_box, self, "USER_REFERENCE", "User comment", labelWidth=label_width, valueType=str,
                          orientation="horizontal")

        oasysgui.lineEdit(export_box, self, "USER_ADDED_BY", "User name", labelWidth=label_width, valueType=str,
                          orientation="horizontal")

        gui.separator(tab_gener)

        select_file_box = oasysgui.widgetBox(tab_gener, "", addSpace=True, orientation="horizontal")

        self.le_heigth_profile_file_name = oasysgui.lineEdit(select_file_box, self, "heigth_profile_file_name", "Output File Root",
                                                        labelWidth=120, valueType=str, orientation="horizontal")



        #
        #-------------------- Output
        #
        out_box = oasysgui.widgetBox(tab_out, "System Output", addSpace=True, orientation="horizontal", height=600)
        self.output_textarea = oasysgui.textArea(height=500,readOnly=False)
        out_box.layout().addWidget(self.output_textarea)

        #
        #-------------------- Use
        #

        tab_usa.setStyleSheet("background-color: white;")

        usage_box = oasysgui.widgetBox(tab_usa, "", addSpace=True, orientation="horizontal")

        label = QLabel("")
        label.setAlignment(Qt.AlignCenter)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        label.setPixmap(QPixmap(self.usage_path))

        usage_box.layout().addWidget(label)

        #
        #
        #

        gui.rubber(self.controlArea)

        self.initializeTabs()

        gui.rubber(self.mainArea)

        # self.overlay_search.raise_()

    def clear(self):
        # plane spherical elliptical toroidal cylindrical  elliptical(unbent) toroid(unbent) elliptical(detrended)
        self.YEAR_FABRICATION = ""
        self.SURFACE_SHAPE = 0
        self.FUNCTION = 0
        self.LENGTH = ""
        self.WIDTH = ""
        self.THICK = ""
        self.LENGTH_OPTICAL = ""
        self.SUBSTRATE = ""
        self.COATING = ""
        self.FACILITY = ""
        self.INSTRUMENT = ""
        self.POLISHING = ""
        self.ENVIRONMENT = 0
        self.SCAN_DATE = ""
        self.CALC_HEIGHT_RMS = ""
        self.CALC_HEIGHT_RMS_FACTOR = ""
        self.CALC_SLOPE_RMS = ""
        self.CALC_SLOPE_RMS_FACTOR = ""
        self.USER_EXAMPLE = ""
        self.USER_REFERENCE = ""
        self.USER_ADDED_BY = ""



    def export(self):
        self.calculate()
        try:

            self.server.metadata_set_info( YEAR_FABRICATION=self.YEAR_FABRICATION,
                                  SURFACE_SHAPE=self.SURFACE_SHAPE,
                                  FUNCTION=self.FUNCTION,
                                  LENGTH=self.LENGTH,
                                  WIDTH=self.WIDTH,
                                  THICK=self.THICK,
                                  LENGTH_OPTICAL=self.LENGTH_OPTICAL,
                                  SUBSTRATE=self.SUBSTRATE,
                                  COATING=self.COATING,
                                  FACILITY=self.FACILITY,
                                  INSTRUMENT=self.INSTRUMENT,
                                  POLISHING=self.POLISHING,
                                  ENVIRONMENT=self.ENVIRONMENT,
                                  SCAN_DATE=self.SCAN_DATE,
                                  # CALC_HEIGHT_RMS        = CALC_HEIGHT_RMS       ,
                                  # CALC_HEIGHT_RMS_FACTOR = CALC_HEIGHT_RMS_FACTOR,
                                  # CALC_SLOPE_RMS         = CALC_SLOPE_RMS        ,
                                  # CALC_SLOPE_RMS_FACTOR  = CALC_SLOPE_RMS_FACTOR ,
                                  USER_EXAMPLE=self.USER_EXAMPLE,
                                  USER_REFERENCE=self.USER_REFERENCE,
                                  USER_ADDED_BY=self.USER_ADDED_BY)



            self.server.write_output_dabam_files(filename_root=self.heigth_profile_file_name,
                                                 loaded_from_file=self.raw_textarea.toPlainText())
            QMessageBox.information(self, "OK",
                                    "Files %s.dat and %s.txt written to disk"%(self.heigth_profile_file_name,self.heigth_profile_file_name),
                                    QMessageBox.Ok)
            self.output_textarea.append(
                ">>>>Export files %s and %s" % (self.heigth_profile_file_name, self.heigth_profile_file_name))
        except:
            self.output_textarea.append(
                ">>>>Export **ERROR* writing files %s and %s" % (self.heigth_profile_file_name, self.heigth_profile_file_name))
            QMessageBox.information(self, "Error",
                                    "Failed to write files %s.dat and %s.txt"%(self.heigth_profile_file_name,self.heigth_profile_file_name),
                                    QMessageBox.Ok)

    def raw_edit(self):

        if self.raw_actions != 6: # save buffer for undo, always except when undo is requested.
            self.undo_text_buffer = copy(self.raw_textarea.toPlainText())

        if self.raw_actions == 0:  # title
            pass
        elif self.raw_actions == 1: # load from file
            filename = oasysgui.selectFileFromDialog(self, "","Read File with Raw Data")
            if filename != "":
                f = open(filename, "r")
                txt = f.read()
                f.close()
                self.raw_textarea.setText(txt)
        elif self.raw_actions == 2: # remove comments
            txt = self.raw_textarea.toPlainText()
            txt = txt.split("\n")
            txt1 = ""
            for line in txt:
                if len(line.strip()) > 0:
                    if (line.strip()[0].isdigit()) or (line.strip()[0] == "-"):
                        txt1 += line+"\n"

            self.raw_textarea.setText(txt1)



        elif self.raw_actions == 3: # remove commas
            txt = self.raw_textarea.toPlainText()
            txt = txt.replace(","," ")
            self.raw_textarea.setText(txt)
        elif self.raw_actions == 4: # remove quotes
            txt = self.raw_textarea.toPlainText()
            txt = txt.replace('"', " ")
            txt = txt.replace("'", " ")
            self.raw_textarea.setText(txt)
        elif self.raw_actions == 5: # clear
            self.raw_textarea.setText("")
        elif self.raw_actions == 6: # undo
            self.raw_textarea.setText(self.undo_text_buffer)
        elif self.raw_actions == 7: # example
            myfileurl = "http://ftp.esrf.eu/pub/scisoft/dabam/data/dabam-001.dat"
            self.to_SI_ordinates = 1e-6
            self.to_SI_abscissas = 1e-3
            self.useHeightsOrSlopes = 1
            self.detrending_option = 1
            self.skiprows = 4
            try:
                u = urlopen(myfileurl)
                ur = u.read()
                txt = ur.decode(encoding='UTF-8')
                # txt = txt.split("\n")
                self.raw_textarea.setText(txt)
            except:
                self.raw_textarea.setText("Failed to load %s"%myfileurl)
        else:
            pass

        self.raw_actions = 0

    def calculate(self):

        self.check_fields()

        txt = self.raw_textarea.toPlainText()

        txt = txt.split("\n")


        if self.detrending_option == 0:
            detrending_flag = 0
        elif self.detrending_option == 1:
            detrending_flag = 1
        else:
            detrending_flag = -2

        # print(type(txt))
        #
        #
        # for ii in range(5):
        #     print(">>>>",txt[ii])

        # a = numpy.loadtxt(txt, skiprows=1)
        # print(a.shape)


        dm = dabam.initialize_from_external_data(txt,
                                                 column_index_abscissas=self.column_index_abscissas,
                                                 column_index_ordinates=self.column_index_ordinates,
                                                 skiprows=self.skiprows,
                                                 useHeightsOrSlopes=self.useHeightsOrSlopes,
                                                 to_SI_abscissas=self.to_SI_abscissas,
                                                 to_SI_ordinates=self.to_SI_ordinates,
                                                 detrending_flag=detrending_flag)

        self.server = dm
        self.retrieve_profile()

        self.output_textarea.setText(">>>>calculate")

        self.send_profile()

    def send_profile(self):
        try:
            if self.server.y is None: raise Exception("No Profile Selected")

            dabam_y = self.server.y
            dabam_profile = numpy.zeros((len(dabam_y), 2))
            dabam_profile[:, 0] = dabam_y
            dabam_profile[:, 1] = self.server.zHeights

            self.send("DABAM 1D Profile", dabam_profile)
        except Exception as exception:
            QMessageBox.critical(self, "Error",
                                 exception.args[0],
                                 QMessageBox.Ok)


    def retrieve_profile(self):
        try:
            self.profileInfo.setText(self.server.info_profiles())
            self.plot_canvas[0].setGraphTitle(
                "Heights Profile. St.Dev.=%.3f nm" % (self.server.stdev_profile_heights() * 1e9))
            self.plot_canvas[1].setGraphTitle(
                "Slopes Profile. St.Dev.=%.3f $\mu$rad" % (self.server.stdev_profile_slopes() * 1e6))
            if self.detrending_option > 0: #use_undetrended == 0:
                self.plot_dabam_graph(0, "heights_profile", self.si_to_user_units * self.server.y,
                                      1e9 * self.server.zHeights, "Y [" + self.workspace_units_label + "]", "Z [nm]")
                self.plot_dabam_graph(1, "slopes_profile", self.si_to_user_units * self.server.y, 1e6 * self.server.zSlopes,
                                      "Y [" + self.workspace_units_label + "]", "Zp [$\mu$rad]")
            else:
                self.plot_dabam_graph(0, "heights_profile", self.si_to_user_units * self.server.y,
                                      1e9 * self.server.zHeightsUndetrended, "Y [" + self.workspace_units_label + "]",
                                      "Z [nm]")
                self.plot_dabam_graph(1, "slopes_profile", self.si_to_user_units * self.server.y,
                                      1e6 * self.server.zSlopesUndetrended, "Y [" + self.workspace_units_label + "]",
                                      "Zp [$\mu$rad]")
            y = self.server.f ** (self.server.powerlaw["hgt_pendent"]) * 10 ** self.server.powerlaw["hgt_shift"]
            i0 = self.server.powerlaw["index_from"]
            i1 = self.server.powerlaw["index_to"]
            beta = -self.server.powerlaw["hgt_pendent"]
            self.plot_canvas[2].setGraphTitle(
                "Power Spectral Density of Heights Profile (beta=%.2f,Df=%.2f)" % (beta, (5 - beta) / 2))
            self.plot_dabam_graph(2, "psd_heights_2", self.server.f, self.server.psdHeights, "f [m^-1]", "PSD [m^3]")
            self.plot_dabam_graph(2, "psd_heights_1", self.server.f, y, "f [m^-1]", "PSD [m^3]", color='green',
                                  replace=False)
            self.plot_dabam_graph(2, "psd_heights_3", self.server.f[i0:i1], y[i0:i1], "f [m^-1]", "PSD [m^3]", color='red',
                                  replace=False)
            self.plot_dabam_graph(3, "csd", self.server.f, self.server.csd_heights(), "f [m^-1]", "CSD [m^3]")
            c1, c2, c3 = autocorrelationfunction(self.server.y, self.server.zHeights)
            self.plot_canvas[4].setGraphTitle(
                "Autocovariance Function of Heights Profile.\nAutocorrelation Length (ACF=0.5)=%.3f m" % (c3))
            self.plot_dabam_graph(4, "acf", c1[0:-1], c2, "Length [m]", "Heights Autocovariance")

            if (self.tabs.currentIndex()==6): self.tabs.setCurrentIndex(1)

        except Exception as exception:
            QMessageBox.critical(self, "Error",
                                 exception.args[0],
                                 QMessageBox.Ok)


    def plot_dabam_graph(self, plot_canvas_index, curve_name, x_values, y_values, xtitle, ytitle, color='blue', replace=True):
        self.plot_canvas[plot_canvas_index].addCurve(x_values, y_values, curve_name, symbol='', color=color, replace=replace) #'+', '^', ','
        self.plot_canvas[plot_canvas_index].setGraphXLabel(xtitle)
        self.plot_canvas[plot_canvas_index].setGraphYLabel(ytitle)
        self.plot_canvas[plot_canvas_index].replot()

    def initializeTabs(self):
        self.tabs = oasysgui.tabWidget(self.mainArea)

        self.tab = [oasysgui.createTabPage(self.tabs, "Info"),
                    oasysgui.createTabPage(self.tabs, "Heights Profile"),
                    oasysgui.createTabPage(self.tabs, "Slopes Profile"),
                    oasysgui.createTabPage(self.tabs, "PSD Heights"),
                    oasysgui.createTabPage(self.tabs, "CSD Heights"),
                    oasysgui.createTabPage(self.tabs, "ACF"),
        ]

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)

        self.plot_canvas = [None, None, None, None, None, None]

        self.plot_canvas[0] = oasysgui.plotWindow(roi=False, control=False, position=True)
        self.plot_canvas[0].setDefaultPlotLines(True)
        self.plot_canvas[0].setActiveCurveColor(color='blue')
        self.plot_canvas[0].setGraphYLabel("Z [nm]")
        self.plot_canvas[0].setGraphTitle("Heights Profile")
        self.plot_canvas[0].setInteractiveMode(mode='zoom')

        self.plot_canvas[1] = oasysgui.plotWindow(roi=False, control=False, position=True)
        self.plot_canvas[1].setDefaultPlotLines(True)
        self.plot_canvas[1].setActiveCurveColor(color='blue')
        self.plot_canvas[1].setGraphYLabel("Zp [$\mu$rad]")
        self.plot_canvas[1].setGraphTitle("Slopes Profile")
        self.plot_canvas[1].setInteractiveMode(mode='zoom')

        self.plot_canvas[2] = oasysgui.plotWindow(roi=False, control=False, position=True)
        self.plot_canvas[2].setDefaultPlotLines(True)
        self.plot_canvas[2].setActiveCurveColor(color='blue')
        self.plot_canvas[2].setGraphXLabel("f [m^-1]")
        self.plot_canvas[2].setGraphYLabel("PSD [m^3]")
        self.plot_canvas[2].setGraphTitle("Power Spectral Density of Heights Profile")
        self.plot_canvas[2].setInteractiveMode(mode='zoom')
        self.plot_canvas[2].setXAxisLogarithmic(True)
        self.plot_canvas[2].setYAxisLogarithmic(True)

        self.plot_canvas[3] = oasysgui.plotWindow(roi=False, control=False, position=True)
        self.plot_canvas[3].setDefaultPlotLines(True)
        self.plot_canvas[3].setActiveCurveColor(color='blue')
        self.plot_canvas[3].setGraphXLabel("f [m^-1]")
        self.plot_canvas[3].setGraphYLabel("CSD [m^3]")
        self.plot_canvas[3].setGraphTitle("Cumulative Spectral Density of Heights Profile")
        self.plot_canvas[3].setInteractiveMode(mode='zoom')
        self.plot_canvas[3].setXAxisLogarithmic(True)

        self.plot_canvas[4] = oasysgui.plotWindow(roi=False, control=False, position=True)
        self.plot_canvas[4].setDefaultPlotLines(True)
        self.plot_canvas[4].setActiveCurveColor(color='blue')
        self.plot_canvas[4].setGraphXLabel("Length [m]")
        self.plot_canvas[4].setGraphYLabel("ACF")
        self.plot_canvas[4].setGraphTitle("Autocovariance Function of Heights Profile")
        self.plot_canvas[4].setInteractiveMode(mode='zoom')

        self.figure = Figure(figsize=(self.IMAGE_HEIGHT, self.IMAGE_HEIGHT)) # QUADRATA!
        self.figure.patch.set_facecolor('white')

        self.axis = self.figure.add_subplot(111, projection='3d')
        self.axis.set_zlabel("Z [nm]")

        self.plot_canvas[5] = FigureCanvasQTAgg(self.figure)

        self.profileInfo = oasysgui.textArea(height=self.IMAGE_HEIGHT-5, width=400)

        profile_box = oasysgui.widgetBox(self.tab[0], "", addSpace=True, orientation="horizontal", height = self.IMAGE_HEIGHT, width=410)
        profile_box.layout().addWidget(self.profileInfo)

        for index in range(0, 5):
            self.tab[index+1].layout().addWidget(self.plot_canvas[index])

        self.tabs.setCurrentIndex(1)

    def check_fields(self):
        pass
        # self.dimension_x = congruence.checkStrictlyPositiveNumber(self.dimension_x, "Dimension X")
        # self.step_x = congruence.checkStrictlyPositiveNumber(self.step_x, "Step X")
        #
        # congruence.checkLessOrEqualThan(self.step_x, self.dimension_x/2, "Step Width", "Width/2")
        #
        # if self.modify_y == 1 or self.modify_y == 2:
        #     self.new_length = congruence.checkStrictlyPositiveNumber(self.new_length, "New Length")
        #
        # if self.renormalize_y == 1:
        #     self.rms_y = congruence.checkPositiveNumber(self.rms_y, "Rms Y")
        #
        # congruence.checkDir(self.heigth_profile_file_name)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OWpre_dabam()
    w.show()
    app.exec()
    w.saveSettings()

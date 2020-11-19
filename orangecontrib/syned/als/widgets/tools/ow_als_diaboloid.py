import os, sys
import numpy

from PyQt5.QtCore import QRect, Qt
from PyQt5.QtWidgets import QApplication, QMessageBox, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QWidget, QLabel, QSizePolicy
from PyQt5.QtGui import QTextCursor,QFont, QPalette, QColor, QPainter, QBrush, QPen, QPixmap
from PyQt5.QtWidgets import QLabel, QSizePolicy
from PyQt5.QtWidgets import QApplication

import orangecanvas.resources as resources

from orangewidget import gui, widget
from orangewidget.settings import Setting

from oasys.widgets.widget import OWWidget
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from oasys.util.oasys_objects import OasysSurfaceData
from oasys.util.oasys_util import write_surface_file

from silx.gui.plot import Plot2D

from oasys.util.oasys_util import EmittingStream
from PyQt5 import QtGui

from orangecontrib.syned.als.util.fqs import single_quartic
from orangecontrib.syned.als.util.fqs import quartic_roots
# from orangecontrib.syned.als.util.FEA_File import FEA_File

class OWALSDiaboloid(OWWidget):
    name = "Diaboloid"
    id = "diaboloid"
    description = "Diaboloid surface generator"
    icon = "icons/devil.png"
    author = "M Sanchez del Rio"
    maintainer_email = "srio@lbl.gov"
    priority = 5
    category = ""
    keywords = ["preprocessor", "surface", "diaboloid", "diabloid"]

    outputs = [{"name": "Surface Data",
                "type": OasysSurfaceData,
                "doc": "Surface Data",
                "id": "Surface Data"},
               ]


    want_main_area = 1
    want_control_area = 1

    MAX_WIDTH = 1320
    MAX_HEIGHT = 700

    IMAGE_WIDTH = 860
    IMAGE_HEIGHT = 645

    CONTROL_AREA_WIDTH = 405
    TABS_AREA_HEIGHT = 650 #18

    #
    # variable list
    #

    configuration = Setting(3)
    source_diaboloid = Setting(19.54)
    diaboloid_image = Setting(9.77)
    theta = Setting(4.5) # mrad
    ny = Setting(1001)
    nx = Setting(101)
    semilength_x = Setting(0.015)
    semilength_y = Setting(0.25)
    detrend = Setting(1)  # not used anymore
    detrend_toroid = Setting(0)
    filename_h5 = Setting("diaboloid.h5")

    cylindrize = Setting(0)

    #
    #
    #

    tab=[]
    usage_path = os.path.join(resources.package_dirname("orangecontrib.syned.als.widgets.tools") , "misc", "diaboloid_usage.png")

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

        # button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        tabs_setting = oasysgui.tabWidget(self.controlArea)
        tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT)
        tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)


        tab_calc = oasysgui.createTabPage(tabs_setting, "Calculate")
        tab_usa = oasysgui.createTabPage(tabs_setting, "Use of the Widget")


        #
        #-------------------- calculate
        #

        button = gui.button(tab_calc, self, "Calculate", callback=self.calculate)

        out_calc = oasysgui.widgetBox(tab_calc, "Diaboloid Parameters", addSpace=True, orientation="vertical")

        # configiration = Setting(1)
        gui.comboBox(out_calc, self, "configuration", label="Focusing configuration", labelWidth=300,
                     items=["Diaboloid: Point-to-segment K (approx)", "Diaboloid: Segment-to-point K (approx)",
                            "Diaboloid: Point-to-segment V (exact)", "Diaboloid: Segment-to-point V (exact)",
                            "Toroid: point-to-segment","Toroid: segment-to-point",
                            "Parabolic-Cone: point-to-segment V","Parabolic-Cone: segment-to-point V",
                            "Parabolic-Cone(linearized): point-to-segment V",
                            "Parabolic-Cone(linearized): segment-to-point V"],
                     sendSelectedValue=False, orientation="horizontal")

        # source_diaboloid = Setting(18.8)
        oasysgui.lineEdit(out_calc, self, "source_diaboloid", "distance source to mirror [m]",
                           labelWidth=300, valueType=float, orientation="horizontal")
        # diaboloid_image = Setting(26.875 - 18.8)
        oasysgui.lineEdit(out_calc, self, "diaboloid_image", "distance mirror to image [m]",
                           labelWidth=300, valueType=float, orientation="horizontal")
        # theta = Setting(2)  # mrad
        oasysgui.lineEdit(out_calc, self, "theta", "grazing angle [mrad]",
                           labelWidth=300, valueType=float, orientation="horizontal")


        # detrend_toroid = Setting(0)
        gui.comboBox(out_calc, self, "detrend_toroid", label="substract surface", labelWidth=300,
                     items=["No [default]", "Yes (toroid)", "Yes (diaboloid)"], sendSelectedValue=False, orientation="horizontal")
        #
        # --------------- MESH
        #
        out_calc = oasysgui.widgetBox(tab_calc, "Mesh Parameters", addSpace=True, orientation="vertical")

        # ny = Setting(1001)
        oasysgui.lineEdit(out_calc, self, "ny", "Points in Y (tangential)",
                           labelWidth=300, valueType=int, orientation="horizontal")
        # nx = Setting(101)
        oasysgui.lineEdit(out_calc, self, "nx", "Points in X (sagittal)",
                           labelWidth=300, valueType=int, orientation="horizontal")
        # semilength_y = 0.4
        oasysgui.lineEdit(out_calc, self, "semilength_y", "Half length Y [m]",
                           labelWidth=300, valueType=float, orientation="horizontal")
        # semilength_x = 0.015
        oasysgui.lineEdit(out_calc, self, "semilength_x", "Half length X [m]",
                           labelWidth=300, valueType=float, orientation="horizontal")

        #
        gui.comboBox(out_calc, self, "cylindrize", label="Replicate central sagittal profile", labelWidth=300,
                     items=["No [default]", "Yes"], sendSelectedValue=False,
                     orientation="horizontal")

        gui.separator(out_calc)
        #
        # --------------- FILE
        #
        out_file = oasysgui.widgetBox(tab_calc, "Output hdf5 file", addSpace=True, orientation="vertical")

        oasysgui.lineEdit(out_file , self, "filename_h5", "Output filename *.h5",
                           labelWidth=150, valueType=str, orientation="horizontal")

        gui.separator(out_file)

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

    def initializeTabs(self):
        self.tabs = oasysgui.tabWidget(self.mainArea)

        self.tab = [oasysgui.createTabPage(self.tabs, "Results"),
                    oasysgui.createTabPage(self.tabs, "Output"),
        ]

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)

        self.plot_canvas = [None] * len(self.tab)

        # tab index 0
        # self.figure = Figure(figsize=(self.IMAGE_HEIGHT, self.IMAGE_HEIGHT)) # QUADRATA!
        # self.figure.patch.set_facecolor('white')
        # self.axis = self.figure.add_subplot(111) #, projection='3d')
        # # self.axis.set_zlabel("Z [nm]")
        # self.plot_canvas[0] = FigureCanvasQTAgg(self.figure)
        # self.plot_canvas[0] = Plot2D()


        # tab index 1
        self.profileInfo = oasysgui.textArea()
        profile_box = oasysgui.widgetBox(self.tab[1], "", addSpace=True, orientation="horizontal")
        profile_box.layout().addWidget(self.profileInfo)


        # self.plot_canvas[0] = oasysgui.plotWindow(roi=False, control=False, position=True)
        # self.plot_canvas[0].setDefaultPlotLines(True)
        # self.plot_canvas[0].setActiveCurveColor(color='blue')
        # self.plot_canvas[0].setGraphYLabel("Z [nm]")
        # self.plot_canvas[0].setGraphTitle("Heights Profile")
        # self.plot_canvas[0].setInteractiveMode(mode='zoom')

        for index in range(len(self.tab)):
            try:
                self.tab[index].layout().addWidget(self.plot_canvas[index])
            except:
                pass
        self.tabs.setCurrentIndex(0)

    def check_fields(self):
        self.nx = congruence.checkStrictlyPositiveNumber(self.nx, "Points X")
        self.ny = congruence.checkStrictlyPositiveNumber(self.ny, "Points Y")
        self.theta = congruence.checkStrictlyPositiveNumber(self.theta, "Grazing angle")
        self.semilength_x = congruence.checkStrictlyPositiveNumber(self.semilength_x, "Half length X")
        self.semilength_y = congruence.checkStrictlyPositiveNumber(self.semilength_y, "Half length Y")
        self.source_diaboloid = congruence.checkNumber(self.source_diaboloid, "Distance source-mirror")
        self.diaboloid_image = congruence.checkNumber(self.diaboloid_image, "Distance mirror-image")

    def writeStdOut(self, text="", initialize=False):
        cursor = self.profileInfo.textCursor()
        if initialize:
            self.profileInfo.setText(text)
        else:
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertText(text)

    def calculate(self):
        self.writeStdOut(initialize=True)
        sys.stdout = EmittingStream(textWritten=self.writeStdOut)

        self.check_fields()

        x = numpy.linspace(-self.semilength_x, self.semilength_x, self.nx)
        y = numpy.linspace(-self.semilength_y, self.semilength_y, self.ny)

        p = self.source_diaboloid
        q = self.diaboloid_image
        theta = self.theta * 1e-3
        print("Inputs: p=%g m, q=%g m, theta=%g rad: " % (p, q, theta))

        mirror_txt = "Diaboloid"
        if self.configuration == 0: #
            Z, X, Y = ken_diaboloid_point_to_segment(p=p, q=q, theta=theta, x=x, y=y, detrend=1)
        elif self.configuration == 1:  #
            Z, X, Y = ken_diaboloid_segment_to_point(p=p, q=q, theta=theta, x=x, y=y, detrend=1)
        elif self.configuration == 2:  #
            Z, X, Y = valeriy_diaboloid_exact_point_to_segment(p=p, q=q, theta=theta, x=x, y=y)
        elif self.configuration == 3:  #
            Z, X, Y = valeriy_diaboloid_exact_segment_to_point(p=p, q=q, theta=theta, x=x, y=y)
        elif self.configuration == 4:  # point to segment
            Z = toroid_point_to_segment(p=p, q=q, theta=theta, x=x, y=y)
            mirror_txt = "Toroid"
        elif self.configuration == 5:  #
            Z = toroid_segment_to_point(p=p, q=q, theta=theta, x=x, y=y)
            mirror_txt = "Toroid"
        elif self.configuration == 6:  #
            Z, X, Y = valeriy_parabolic_cone_point_to_segment(p=p, q=q, theta=theta, x=x, y=y)
            mirror_txt = "Parabolic-Cone"
        elif self.configuration == 7:  #
            Z, X, Y = valeriy_parabolic_cone_segment_to_point(p=p, q=q, theta=theta, x=x, y=y)
            mirror_txt = "Parabolic-Cone"
        elif self.configuration == 8:  #
            Z, X, Y = valeriy_parabolic_cone_linearized_point_to_segment(p=p, q=q, theta=theta, x=x, y=y)
            mirror_txt = "Parabolic-Cone"
        elif self.configuration == 9:  #
            Z, X, Y = valeriy_parabolic_cone_linearized_segment_to_point(p=p, q=q, theta=theta, x=x, y=y)
            mirror_txt = "Parabolic-Cone"

        else:
            raise Exception("Not implemented")

        if self.detrend_toroid == 0:
            Ztor = 0
        elif self.detrend_toroid == 1:  # detrend toroid
            mirror_txt += " (toroid removed)"
            if self.configuration in [0, 2, 4, 6, 8]:  # point to segment
                Ztor = toroid_point_to_segment(p=p, q=q, theta=theta, x=x, y=y)
            elif self.configuration in [1, 3, 5, 7, 9]:  # segment-to-point
                Ztor = toroid_segment_to_point(p=p, q=q, theta=theta, x=x, y=y)
        elif self.detrend_toroid == 2: # detrend diaboloid
            mirror_txt += " (diaboloid removed)"
            if self.configuration in [0, 2, 4, 6, 8]:  # point to segment
                Ztor, Xtor, Ytor = valeriy_diaboloid_exact_point_to_segment(p=p, q=q, theta=theta, x=x, y=y)
            elif self.configuration in [1, 3, 5, 7, 9]:  # segment-to-point
                Ztor, Xtor, Ytor = valeriy_diaboloid_exact_segment_to_point(p=p, q=q, theta=theta, x=x, y=y,)

            #
            #
            # if self.configuration == 0:  #
            #     Ztor, Xtor, Ytor = ken_diaboloid_point_to_segment(p=p, q=q, theta=theta, x=x, y=y, detrend=1)
            # elif self.configuration == 1:  #
            #     Ztor, Xtor, Ytor = ken_diaboloid_segment_to_point(p=p, q=q, theta=theta, x=x, y=y, detrend=1)
            # elif self.configuration == 2:  #
            #     Ztor, Xtor, Ytor = valeriy_diaboloid_exact_point_to_segment(p=p, q=q, theta=theta, x=x, y=y)
            # elif self.configuration == 3:  #
            #     Ztor, Xtor, Ytor = valeriy_diaboloid_exact_segment_to_point(p=p, q=q, theta=theta, x=x, y=y,)
            # elif self.configuration == 4:  # point to segment
            #     Ztor, Xtor, Ytor = valeriy_diaboloid_exact_point_to_segment(p=p, q=q, theta=theta, x=x, y=y)
            # elif self.configuration == 5:  #
            #     Ztor, Xtor, Ytor = valeriy_diaboloid_exact_segment_to_point(p=p, q=q, theta=theta, x=x, y=y)
            # elif self.configuration == 6:  #
            #     Ztor, Xtor, Ytor = valeriy_diaboloid_exact_point_to_segment(p=p, q=q, theta=theta, x=x, y=y)
            # elif self.configuration == 7:  #
            #     Ztor, Xtor, Ytor = valeriy_diaboloid_exact_segment_to_point(p=p, q=q, theta=theta, x=x, y=y)
            # elif self.configuration == 8:  #
            #     Ztor, Xtor, Ytor = valeriy_diaboloid_exact_point_to_segment(p=p, q=q, theta=theta, x=x, y=y)
            # elif self.configuration == 9:  #
            #     Ztor, Xtor, Ytor = valeriy_diaboloid_exact_segment_to_point(p=p, q=q, theta=theta, x=x, y=y)

            else:
                raise Exception("Not implemented")

        #
        # shape modifications
        #
        nx, ny = Z.shape
        if self.cylindrize == 1:
            sagittal_central_profile = Z[:,ny//2] - Z[nx//2,ny//2]
            for i in range(ny):
                Z[:,i] = Z[nx//2,i] + sagittal_central_profile

        Z -= Ztor
        


        self.plot_data2D(Z, x, y, self.tab[0],
                         title="%s p:%6.3f m, q:%6.3f %6.3f mrad" %
                               (mirror_txt, self.source_diaboloid, self.diaboloid_image, self.theta),
                         xtitle="x (sagittal) [m] (%d pixels)" % x.size,
                         ytitle="y (tangential) [m] (%d pixels)" % y.size)


        write_surface_file(Z.T, x, y, self.filename_h5, overwrite=True)
        print("HDF5 file %s written to disk." % self.filename_h5)


        self.send("Surface Data",
                  OasysSurfaceData(xx=x,
                                   yy=y,
                                   zz=Z.T,
                                   surface_data_file=self.filename_h5))


    def plot_data2D(self, data2D, dataX, dataY, canvas_widget_id, title="title", xtitle="X", ytitle="Y"):

        try:
            canvas_widget_id.layout().removeItem(canvas_widget_id.layout().itemAt(0))
        except:
            pass

        origin = (dataX[0], dataY[0])
        scale = (dataX[1] - dataX[0], dataY[1] - dataY[0])

        colormap = {"name": "temperature", "normalization": "linear",
                    "autoscale": True, "vmin": 0, "vmax": 0, "colors": 256}

        tmp = Plot2D()
        tmp.resetZoom()
        tmp.setXAxisAutoScale(True)
        tmp.setYAxisAutoScale(True)
        tmp.setGraphGrid(False)
        tmp.setKeepDataAspectRatio(True)
        tmp.yAxisInvertedAction.setVisible(False)
        tmp.setXAxisLogarithmic(False)
        tmp.setYAxisLogarithmic(False)
        tmp.getMaskAction().setVisible(False)
        tmp.getRoiAction().setVisible(False)
        tmp.getColormapAction().setVisible(True)
        tmp.setKeepDataAspectRatio(False)
        tmp.addImage(data2D.T,legend="1",scale=scale,origin=origin,colormap=colormap,replace=True)
        tmp.setActiveImage("1")
        tmp.setGraphXLabel(xtitle)
        tmp.setGraphYLabel(ytitle)
        tmp.setGraphTitle(title)

        canvas_widget_id.layout().addWidget(tmp)

def ken_diaboloid_point_to_segment(
        p=29.3,
        q=19.53,
        theta=4.5e-3,
        x=numpy.linspace(-0.01, 0.01, 101),
        y=numpy.linspace(-0.1, 0.1, 1001),
        detrend=0):
    X = numpy.outer(x, numpy.ones_like(y))
    Y = numpy.outer(numpy.ones_like(x), y)

    s = p * numpy.cos(2 * theta)
    z0 = p * numpy.sin(2 * theta)
    c = p + q

    Z = - numpy.sqrt(c ** 2 + q ** 2 - s ** 2 - 2 * Y * (s + q) - 2 * c * numpy.sqrt(X ** 2 + (q - Y) ** 2))
    Z += z0

    if detrend == 0:
        zfit = 0
    elif detrend == 1:
        zfit = -theta * y
    elif detrend == 2:
        zcentral = Z[Z.shape[0] // 2, :]
        zcoeff = numpy.polyfit(y[(y.size // 2 - 10):(y.size // 2 + 10)],
                               zcentral[(y.size // 2 - 10):(y.size // 2 + 10)], 1)
        zfit = zcoeff[1] + y * zcoeff[0]

    for i in range(Z.shape[0]):
        Z[i, :] = Z[i, :] - zfit

    return Z, X, Y


def ken_diaboloid_segment_to_point(
        p=29.3,
        q=19.53,
        theta=4.5e-3,
        x=numpy.linspace(-0.01, 0.01, 101),
        y=numpy.linspace(-0.1, 0.1, 1001),
        detrend=0):

    Z, X, Y = ken_diaboloid_point_to_segment(p=q, q=p, theta=theta, x=x, y=y,
                                              detrend=detrend)
    for i in range(x.size):
        Z[i,:] = numpy.flip(Z[i,:])

    return Z, X, Y

def toroid_point_to_segment(
        p=29.3,
        q=19.53,
        theta=4.5e-3,
        x=numpy.linspace(-0.01, 0.01, 101),
        y=numpy.linspace(-0.1, 0.1, 1001)):

    Rt = 2.0 / numpy.sin(theta) / (1 / p)

    Rs = 2.0 * numpy.sin(theta) / (1 / p + 1 / q)

    print("Toroid Rt: %9.6f m, Rs: %9.6f m" % (Rt, Rs))

    height_tangential = Rt - numpy.sqrt(Rt ** 2 - y ** 2)
    height_sagittal = Rs - numpy.sqrt(Rs ** 2 - x ** 2)

    Z = numpy.zeros((x.size, y.size))

    for i in range(x.size):
        Z[i,:] = height_tangential

    for i in range(y.size):
        Z[:,i] += height_sagittal

    return Z

def toroid_segment_to_point(
        p=29.3,
        q=19.53,
        theta=4.5e-3,
        x=numpy.linspace(-0.01, 0.01, 101),
        y=numpy.linspace(-0.1, 0.1, 1001)):

    Z = toroid_point_to_segment(p=q, q=p, theta=theta, x=x, y=y)
    for i in range(x.size):
        Z[i,:] = numpy.flip(Z[i,:])
    return Z

def valeriy_parabolic_cone_point_to_segment(
        p=29.3,
        q=19.53,
        theta=4.5e-3,
        x=numpy.linspace(-0.01, 0.01, 101),
        y=numpy.linspace(-0.1, 0.1, 1001)):
    X = numpy.outer(x, numpy.ones_like(y))
    Y = numpy.outer(numpy.ones_like(x), y)

    c = numpy.cos(theta)
    s = numpy.sin(theta)
    c2 = numpy.cos(2 * theta)
    s2 = numpy.sin(2 * theta)
    pq = p + q

    k1 = p * q * c * s2 / pq
    k2 = s2 * (q - 2 * p * c**2 ) / 2 / pq
    Z = Y * s / c - \
        2  * s / c**2 * numpy.sqrt(Y * p * c + p**2) + \
        2 * p * s / c**2 + \
        k1 + k2 * Y \
        - numpy.sqrt( (k1 + k2 * Y)**2 - X**2 )

    return Z, X, Y

def valeriy_parabolic_cone_segment_to_point(
        p=29.3,
        q=19.53,
        theta=4.5e-3,
        x=numpy.linspace(-0.01, 0.01, 101),
        y=numpy.linspace(-0.1, 0.1, 1001)):
    Z, X, Y = valeriy_parabolic_cone_point_to_segment(p=q, q=p, theta=theta, x=x, y=y)
    for i in range(x.size):
        Z[i,:] = numpy.flip(Z[i,:])

    return Z, X, Y


def valeriy_parabolic_cone_linearized_point_to_segment(
        p=29.3,
        q=19.53,
        theta=4.5e-3,
        x=numpy.linspace(-0.01, 0.01, 101),
        y=numpy.linspace(-0.1, 0.1, 1001)):
    X = numpy.outer(x, numpy.ones_like(y))
    Y = numpy.outer(numpy.ones_like(x), y)

    c = numpy.cos(theta)
    s = numpy.sin(theta)
    c2 = numpy.cos(2 * theta)
    s2 = numpy.sin(2 * theta)
    pq = p + q

    Z = Y * s / c - 2  * s / c**2 * numpy.sqrt(Y * p * c + p**2) + 2 * p * s / c**2 \
        - numpy.sqrt( \
        (p * q * c * s2 / pq + s2 * (q - 2 * p * c**2 ) / 2 / pq * Y)**2 - (X*0)**2) + \
        p * q * c * s2 / pq + s2 * (q - 2 * p * c**2) / 2 / pq * Y

    for j in range(y.size):
        Rs = p * q * numpy.sin(2 * theta) / (p + q)
        Rs += (q * numpy.tan(theta) - 2 * p * numpy.sin(theta) * numpy.cos(theta)) / (p + q) * y[j]
        height_sagittal = Rs - numpy.sqrt(Rs ** 2 - x ** 2)
        print("y=%f Rs=%f" % (y[j], Rs))
        Z[:,j] += height_sagittal

    return Z, X, Y

def valeriy_parabolic_cone_linearized_segment_to_point(
        p=29.3,
        q=19.53,
        theta=4.5e-3,
        x=numpy.linspace(-0.01, 0.01, 101),
        y=numpy.linspace(-0.1, 0.1, 1001)):
    Z, X, Y = valeriy_parabolic_cone_linearized_point_to_segment(p=q, q=p, theta=theta, x=x, y=y)
    for i in range(x.size):
        Z[i,:] = numpy.flip(Z[i,:])

    return Z, X, Y

def valeriy_diaboloid_exact_point_to_segment(
        p=29.3,
        q=19.53,
        theta=4.5e-3,
        x=numpy.linspace(-0.01, 0.01, 101),
        y=numpy.linspace(-0.1, 0.1, 1001),
        ):

    X = numpy.outer(x, numpy.ones_like(y))
    Y = numpy.outer(numpy.ones_like(x), y)

    c = numpy.cos(theta)
    s = numpy.sin(theta)

    c2 = numpy.cos(2 * theta)
    s2 = numpy.sin(2 * theta)

    # A = −Cos[θ] 4 .
    # B = 4(r1 − r2)Cos[θ] 2 Sin[θ] + 4Cos[θ] 3 Sin[θ]z;
    # C = 4r2((r1 + r2)Cos[θ] 2 + 4r1Sin[θ] 2 ) + 2Cos[θ](−3r1 + r2 + (r1 − 3r2)Cos[2θ])z − 6(Cos[θ] 2 Sin[θ] 2 )z 2 ;
    # D = −16r1r2(r1 + r2)Sin[θ] + 4(r1 + r2)(2r1 − r2)Sin[2θ]z + 2(3r1 + r2 + (r1 + 3r2)Cos[2θ])Sin[θ]z 2 + 4Cos[θ]Sin[θ] 3 z 3 ;
    # E = 4(r1 + r2) 2 x 2 + 4r2(r1 + r2)Sin[θ] 2 z 2 − 4((r1 + r2)Cos[θ]Sin[θ] 2 )z 3 − Sin[θ] 4 z 4 ;

    A = -c**4 * numpy.ones_like(X)
    B = 4 * (p - q) * c**2 * s \
                + 4 * c**3 * s * Y
    C = 4 * q * ( (p + q) * c**2 + 4 * p * s**2 ) \
                + 2 * c * (q - 3 * p + (p - 3 * q) * c2) * Y \
                - 6 * c**2 * s**2 * Y**2
    D = -16 * p * q * (p + q) * s \
                + 4 * (p + q) * (2 * p - q) * s2 * Y \
                + 2 * (3 * p + q + (3 * q + p) * c2) * s * Y**2 \
                + 4 * c * s**3 * Y**3
    E = 4 * (p + q)**2 * X**2 \
            + 4 * q * (p + q) * s**2 * Y**2 \
            - 4 * (p + q) * c * s**2 * Y**3 \
            - s**4 * Y**4

    # get good solution: the one that is zero at (0,0)
    ix = x.size // 2
    iy = y.size // 2
    solutions = single_quartic(A[ix, iy], B[ix, iy], C[ix, iy], D[ix, iy], E[ix, iy])
    aa = []
    for sol in solutions:
        if numpy.abs(sol.imag) < 1e-15:
            aa.append(numpy.abs(sol.real))
        else:
            aa.append(1e10)
    isel = numpy.argmin(aa)


    # calculate solutions array
    P = numpy.zeros((A.size, 5))
    P[:, 0] = A.flatten()
    P[:, 1] = B.flatten()
    P[:, 2] = C.flatten()
    P[:, 3] = D.flatten()
    P[:, 4] = E.flatten()
    SOLUTION = quartic_roots(P)

    # return result
    SOLUTION_GOOD = (SOLUTION[:,isel]).flatten()
    SOLUTION_GOOD.shape = A.shape
    Z = SOLUTION_GOOD.real
    return Z, X, Y

def valeriy_diaboloid_exact_segment_to_point(
        p=29.3,
        q=19.53,
        theta=4.5e-3,
        x=numpy.linspace(-0.01, 0.01, 101),
        y=numpy.linspace(-0.1, 0.1, 1001),
        ):
    Z, X, Y = valeriy_diaboloid_exact_point_to_segment(p=q, q=p, theta=theta, x=x, y=y)
    for i in range(x.size):
        Z[i,:] = numpy.flip(Z[i,:])

    return Z, X, Y

if __name__ == "__main__":


    app = QApplication(sys.argv)
    w = OWALSDiaboloid()
    w.show()
    app.exec()
    w.saveSettings()


    # x = numpy.linspace(-10e-3, 10e-3, 101)
    # y = numpy.linspace(-100e-3, 100e-3, 1001)
    #
    # Z, X, Y =  valeriy_diaboloid_exact_point_to_segment(p=29.3,q=19.53,theta=4.5e-3,x=x,y=y,)
    # Z0, X, Y = ken_diaboloid_point_to_segment(p=29.3, q=19.53, theta=4.5e-3, x=x, y=y, detrend=1)
    #
    # from srxraylib.plot.gol import plot_image, plot
    # plot_image((Z0) * 1e-6, x * 1e-3, y * 1e-3, xtitle="X/mm", ytitle="Y/mm", title="Z (approximated)/um", aspect="auto")
    # plot_image((Z) * 1e-6, x * 1e-3, y * 1e-3, xtitle="X/mm", ytitle="Y/mm", title="Z (exact)/um", aspect="auto")
    # plot_image((Z-Z0) * 1e-6, x * 1e-3, y * 1e-3, xtitle="X/mm", ytitle="Y/mm", title="Z (exact)-Z(approximated)/um", aspect="auto")
    #
    # ZZ0 = Z0[:, y.size//2]
    # ZZ  = Z[:, y.size//2]
    # plot(x, ZZ0 - ZZ0.min(),
    #      x,  ZZ - ZZ.min(),
    #      xtitle="X", ytitle="Z", legend=["Z (approximated)","Z (exact)"])
    #
    # ZZ0 = Z0[x.size//2, :]
    # ZZ  = Z[x.size//2, :]
    # plot(y,  ZZ0 - ZZ0.min(),
    #      y,   ZZ - ZZ.min(),
    #      xtitle="Y", ytitle="Z", legend=["Z (approximated)","Z (exact)"])
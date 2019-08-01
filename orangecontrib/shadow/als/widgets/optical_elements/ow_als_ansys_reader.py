
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QPalette, QColor, QFont
from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence
from orangewidget import widget

from orangecontrib.shadow.als.widgets.gui.ow_als_shadow_widget import ALSShadowWidget

from orangecontrib.shadow.util.shadow_objects import ShadowPreProcessorData

class Distribution:
    POSITION = 0
    DIVERGENCE = 1

class ALSAnsysReader(ALSShadowWidget):

    name = "ANSYS Reader"
    description = "Reader for ANSYS HHLO files"
    icon = "icons/hhlo.png"
    priority = 1
    maintainer = "Antoine Wojdyla"
    maintainer_email = "awojdyla@lbl.gov"
    category = ""
    keywords = ["Ansys", "file", "load", "read","HHLO", "ALS-U"]

    outputs = [{"name": "PreProcessor_Data",
                "type": ShadowPreProcessorData,
                "doc": "PreProcessor Data",
                "id": "PreProcessor_Data"}]

    want_main_area = 0

    height_profile_load_file = Setting("/Users/awojdyla/data/hhlo/steady_state_disp_49_7.txt")
    height_profile_save_file = Setting("hhlo_oasys_profile.dat")

    ansys_nx = Setting(101)
    ansys_ny = Setting(51)

    save_hhlo = Setting(1)

    def __init__(self, show_automatic_box=False):
        super().__init__(show_automatic_box=show_automatic_box)

        self.runaction = widget.OWAction("Compute", self)
        self.runaction.triggered.connect(self.compute)
        self.addAction(self.runaction)

        self.general_options_box.setVisible(False)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Compute", callback=self.compute)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)

        button = gui.button(button_box, self, "Reset Fields", callback=self.callResetSettings)
        font = QFont(button.font())
        font.setItalic(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Red'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)
        button.setFixedWidth(150)

        gui.separator(self.controlArea)

        ######################################

        self.setMaximumWidth(self.CONTROL_AREA_WIDTH + 10)

        # create a label and a box

        # container panel
        settings_box = oasysgui.widgetBox(self.controlArea, "", addSpace=True, orientation="horizontal", height=300)

        oasysgui.lineEdit(settings_box, self, "ansys_nx", "Number of interpolation points [x]", labelWidth=260, valueType=float,
                          orientation="horizontal")
        oasysgui.lineEdit(settings_box, self, "ansys_ny", "Number of interpolation points [y]", labelWidth=260, valueType=float,
                          orientation="horizontal")

        # line edit with callback
        self.le_hhlo_file = oasysgui.lineEdit(settings_box, self, "height_profile_load_file", "HHLO file",
                                                       labelWidth=180, valueType=str, orientation="vertical")
        #button for selection
        gui.button(settings_box, self, "...", height=45, callback=self.select_hhlo_file)


        ###### Save results
        save_box = oasysgui.widgetBox(self.controlArea, "", addSpace=True, orientation="horizontal", height=300)
        gui.comboBox(save_box, self, "height_profile_save_file", label="Save HHLO file", labelWidth=310,
                     items=["No", "Yes"], orientation="horizontal", callback=self.set_save_hhlo)

        self.save_file_box =        oasysgui.widgetBox(save_box, "", addSpace=False, orientation="vertical")
        self.save_file_box_empty =  oasysgui.widgetBox(save_box, "", addSpace=False, orientation="vertical", height=55)

    #callback for buttons
    def select_hhlo_file(self):
        self.le_hhlo_file.setText(
            oasysgui.selectFileFromDialog(self, self.height_profile_load_file, "Open HHLO File"))
        print(self.height_profile_load_file)

    def set_save_hhlo(self):
        self.save_file_box.setVisible(self.save_hhlo == 1)
        self.save_file_box_empty.setVisible(self.save_hhlo == 0)

    def compute(self):
        """
        Compute the HHLO profile that works with Oasys

        :param filename: full filename of the file to read
        :param nx: number
        :returns: (X, Y, Z) 2D arrays of (X,Y) locations and corresponding height Z, in meter
        """
        try:

            import numpy as np

            congruence.checkFile(self.height_profile_load_file)
            X, Y, Z = self.ansys_height(filename=self.height_profile_load_file, nx=101, ny=51)

            xx_m = X[1, :]
            yy_m = Y[:, 1]

            self.heigth_profile_file_name = 'hhlo49_7.dat'

            congruence.checkDir(self.height_profile_save_file)

            self.write_shadow_surface(Z, xx_m, yy_m, self.height_profile_save_file)

            self.send("PreProcessor_Data", ShadowPreProcessorData(error_profile_data_file=self.height_profile_save_file,
                                                                  error_profile_x_dim=101,
                                                                  error_profile_y_dim=51))

        except Exception as exception:
            QMessageBox.critical(self, "Error", exception.args[0], QMessageBox.Ok)

            raise exception



    # last updated May 22nd, 2017

    def ansys_read(self, filename, nx=101, ny=51):
        """
        Read an High heatload deformation files (ALS-U standards)

        :param filename: full filename of the file to read
        :param nx: number
        :returns: (X, Y, Z) 2D arrays of (X,Y) locations and corresponding height Z, in meter
        """

        import numpy
        import csv
        import scipy.interpolate as interpolate

        # read data wih csv
        with open(filename, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=" ", skipinitialspace=True)
            row_count = sum(1 for row in csvreader)

        data = numpy.zeros((row_count, 7))

        with open(filename, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=" ", skipinitialspace=True)
            i = 0
            for row in csvreader:
                data[i, :] = numpy.asarray(row).astype(numpy.float)
                i = i + 1

        # parse data
        x = data[:, 1]
        dx = data[:, 4]
        y = data[:, 2]
        dy = data[:, 5]
        z = data[:, 3]
        dz = data[:, 6]

        # deformation coordinate
        xdx = x + dx
        ydy = y + dy
        zdz = z + dz

        # interpolation on regular grid
        xp = numpy.linspace(numpy.min(x), numpy.max(x), nx)
        yp = numpy.linspace(numpy.min(y), numpy.max(y), ny)
        X, Y = numpy.meshgrid(xp, yp)
        Z = interpolate.griddata((xdx, ydy), zdz, (X, Y), method='linear')

        return X, Y, Z


    def ansys_height(self, filename, nx=101, ny=51):
        import numpy
        Xq, Yq, Zq = self.ansys_read(filename, nx, ny)
        Nx = Xq.shape[0]
        Ny = Yq.shape[1]
        X_m, Y_m = numpy.meshgrid(numpy.linspace(-Xq[0, -1], Xq[0, -1], 2 * Ny), numpy.linspace(-Yq[-1, 0], Yq[-1, 0], 2 * Nx))
        Z_m = numpy.concatenate((numpy.flip(numpy.concatenate((numpy.flip(Zq, axis=0), Zq), axis=0), axis=1),
                                 numpy.concatenate((numpy.flip(Zq, axis=0), Zq), axis=0)), axis=1)
        return X_m, Y_m, Z_m

    def write_shadow_surface(self, s, xx, yy, outFile='presurface.dat'):
        """
          write_shadowSurface: writes a mesh in the SHADOW/presurface format
          SYNTAX:
               out = write_shadowSurface(z,x,y,outFile=outFile)
          INPUTS:
               z - 2D array of heights
               x - 1D array of spatial coordinates along mirror width.
               y - 1D array of spatial coordinates along mirror length.

          OUTPUTS:
               out - 1=Success, 0=Failure
               outFile - output file in SHADOW format. If undefined, the
                         file is names "presurface.dat"

        """
        out = 1

        try:
            fs = open(outFile, 'w')
        except IOError:
            out = 0
            print("Error: can\'t open file: " + outFile)
            return
        else:
            # dimensions
            fs.write(repr(xx.size) + " " + repr(yy.size) + " \n")
            # y array
            for i in range(yy.size):
                fs.write(' ' + repr(yy[i]))
            fs.write("\n")
            # for each x element, the x value and the corresponding z(y)
            # profile
            for i in range(xx.size):
                tmps = ""
                for j in range(yy.size):
                    tmps = tmps + "  " + repr(s[j, i])
                fs.write(' ' + repr(xx[i]) + " " + tmps)
                fs.write("\n")
            fs.close()
            print("write_shadow_surface: File for SHADOW " + outFile + " written to disk.")
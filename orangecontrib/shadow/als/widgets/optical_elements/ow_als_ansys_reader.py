
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtGui import QPalette, QColor, QFont
from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence
from orangewidget import widget

from orangecontrib.shadow.util.shadow_objects import ShadowTriggerOut, ShadowBeam, ShadowSource
from orangecontrib.shadow.als.widgets.gui.ow_als_shadow_widget import ALSShadowWidget
from orangecontrib.shadow.widgets.gui.ow_generic_element import GenericElement

from orangecontrib.shadow.util.shadow_objects import ShadowPreProcessorData

import scipy.constants as codata

from srwlib import *

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

    #inputs = [("Trigger", ShadowTriggerOut, "sendNewBeam")]

    outputs = [{"name": "PreProcessor_Data",
                "type": ShadowPreProcessorData,
                "doc": "PreProcessor Data",
                "id": "PreProcessor_Data"}]

    want_main_area = 0

    height_profile_name = Setting("/Users/awojdyla/data/hhlo/steady_state_disp_49_7.txt")

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
        file_box = oasysgui.widgetBox(self.controlArea, "", addSpace=True, orientation="horizontal", height=45)
        # line edit with callback
        self.le_hhlo_file = oasysgui.lineEdit(file_box, self, "height_profile_name", "HHLO file",
                                                       labelWidth=180, valueType=str, orientation="vertical")
        #button for selection
        gui.button(file_box, self, "...", height=45, callback=self.select_hhlo_file)

    #callback for button
    def select_hhlo_file(self):
        self.le_hhlo_file.setText(
            oasysgui.selectFileFromDialog(self, self.height_profile_name, "Open HHLO File"))

    def compute(self):
        try:

            import numpy as np
            import sys
            sys.path.insert(0, "/Users/awojdyla/python/coppy/")
            import wavefit
            from import_utilities import ansys_opde, oasys

            X, Y, Z = ansys_opde.ansys_height("/Users/awojdyla/data/hhlo/steady_state_disp_49_7.txt", nx=101, ny=51)

            xx_m = X[1, :]
            yy_m = Y[:, 1]

            self.heigth_profile_file_name = 'hhlo49_7.dat'

            congruence.checkDir(self.heigth_profile_file_name)

            oasys.write_shadow_surface(Z, xx_m, yy_m, self.heigth_profile_file_name)

            congruence.checkFileName(self.heigth_profile_file_name)

            self.send("PreProcessor_Data", ShadowPreProcessorData(error_profile_data_file=self.heigth_profile_file_name,
                                                                  error_profile_x_dim=101,
                                                                  error_profile_y_dim=51))

        except Exception as exception:
            QMessageBox.critical(self, "Error", exception.args[0], QMessageBox.Ok)

            raise exception
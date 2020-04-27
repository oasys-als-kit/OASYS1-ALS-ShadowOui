from PyQt5 import QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui

from orangecontrib.shadow.util.shadow_objects import ShadowBeam
from orangecontrib.shadow.util.shadow_util import ShadowCongruence
from orangecontrib.shadow.widgets.gui import ow_automatic_element

from srxraylib.plot.gol import plot_scatter
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar


import numpy

class ALSResolvingPower(ow_automatic_element.AutomaticElement):

    name = "ALS Resolving Power"
    description = "Shadow: ALS Resolving Power"
    icon = "icons/resolving_power.png"
    maintainer = "APS team"
    maintainer_email = "srio@lbl.gov"
    priority = 8
    category = "Data Display Tools"
    keywords = ["data", "file", "load", "read"]

    inputs = [("Input Beam 1", ShadowBeam, "setBeam1")]

    IMAGE_WIDTH = 860
    IMAGE_HEIGHT = 675

    want_main_area=1
    want_control_area = 1

    input_beam1=None
    input_beam2 = None

    normalize = Setting(0)
    hlim = Setting(10.0) # 0=round, 1=square
    shadow_column = Setting(0) # 0 = X (col1), 1 = Z (column 3)
    photon_wavelenth_or_energy = Setting(1)
    no_lost  = Setting(1)
    labelsize = Setting(10)

    def __init__(self, show_automatic_box=True):
        super().__init__()

        gui.button(self.controlArea, self, "Calculate", callback=self.calculate, height=45)

        general_box = oasysgui.widgetBox(self.controlArea, "General Settings", addSpace=True, orientation="vertical",
                                         width=self.CONTROL_AREA_WIDTH-8, height=400)


        gui.comboBox(general_box, self, "no_lost", label="Rays",labelWidth=220,
                                     items=["All rays","Good only","Lost only"],
                                     sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(general_box, self, "shadow_column", label="Dispersion direction",labelWidth=220,
                                     items=["X (column 1)","Z (column 3)"],
                                     sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(general_box, self, "photon_wavelenth_or_energy", label="Photon wavelength/energy",labelWidth=220,
                                     items=["Wavelength [A]","Energy [eV]"],
                                     sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(general_box, self, "hlim", "Width at percent of max:", labelWidth=260, valueType=int,orientation="horizontal")

        oasysgui.lineEdit(general_box, self, "labelsize", "label size (for plots):", labelWidth=260, valueType=int,
                          orientation="horizontal")

        gui.separator(self.controlArea, height=200)

        tabs_setting = oasysgui.tabWidget(self.mainArea)
        tabs_setting.setFixedHeight(self.IMAGE_HEIGHT+5)
        tabs_setting.setFixedWidth(self.IMAGE_WIDTH)


        tmp = oasysgui.createTabPage(tabs_setting, "Dispersion Detrended")
        self.detrended_id = gui.widgetBox(tmp, "", addSpace=True, orientation="vertical")
        self.detrended_id.setFixedHeight(self.IMAGE_HEIGHT - 30)
        self.detrended_id.setFixedWidth(self.IMAGE_WIDTH - 20)

        tmp = oasysgui.createTabPage(tabs_setting, "Dispersion")
        self.dispersion_id = gui.widgetBox(tmp, "", addSpace=True, orientation="vertical")
        self.dispersion_id.setFixedHeight(self.IMAGE_HEIGHT - 30)
        self.dispersion_id.setFixedWidth(self.IMAGE_WIDTH - 20)


        tmp = oasysgui.createTabPage(tabs_setting, "Info")
        self.info_id = oasysgui.textArea(height=self.IMAGE_HEIGHT-35)
        info_box = oasysgui.widgetBox(tmp, "", addSpace=True, orientation="horizontal", height = self.IMAGE_HEIGHT-20, width = self.IMAGE_WIDTH-20)
        info_box.layout().addWidget(self.info_id)


    def setBeam1(self, beam):
        if ShadowCongruence.checkEmptyBeam(beam):
            if ShadowCongruence.checkGoodBeam(beam):
                self.input_beam1 = beam

                if self.is_automatic_run:
                    self.calculate()
            else:
                QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data not displayable: No good rays or bad content",
                                           QtWidgets.QMessageBox.Ok)


    def get_shadow3_beam1(self):
        if ShadowCongruence.checkEmptyBeam(self.input_beam1):
            if ShadowCongruence.checkGoodBeam(self.input_beam1):
                beam_to_analize = self.input_beam1._beam
                return beam_to_analize


    def calculate(self):

        self.writeStdOut("",initialize=True)
        beam_to_analize1 = self.get_shadow3_beam1()

        if beam_to_analize1 is None:
            print("No SHADOW Beam")
            return

        if self.shadow_column == 0:
            col = 1
        elif self.shadow_column == 1:
            col = 3

        if self.photon_wavelenth_or_energy == 0:
            colE = 19
        elif self.photon_wavelenth_or_energy == 1:
            colE = 11


        dict = self.respower(beam_to_analize1,colE,col,hlimit=1e-2*self.hlim,nolost=self.no_lost)
        for key in dict.keys():
            print(key," = ",dict[key])

        self.respower_plot(beam_to_analize1,dict,nolost=self.no_lost)

        self.writeStdOut(dict["info"], initialize=True)

    def writeStdOut(self, text, initialize=True):
        cursor = self.info_id.textCursor()
        if initialize:
            self.info_id.setText(text)
        else:
            cursor.movePosition(QtGui.QTextCursor.End)
            cursor.insertText(text)
            self.info_id.setTextCursor(cursor)
            self.info_id.ensureCursorVisible()


    #+
    #
    #  NAME:
    # 	respower
    #  PURPOSE:
    # 	to compute the resolving power E/DE from the dispersion in a plane (usually the exit slit plane).
    #  CATEGORY:
    #        SHADOW's utilities
    #  CALLING SEQUENCE:
    # 	respower(beam,col_E, col_D)
    #  INPUTS:
    # 	beam  a Shadow.Beam() object
    #       col_E:  the SHADOW column with the energy information, either:
    #                   11: Energy in eV
    #                   19: Wavelength in A
    #       col_D:  the SHADOW column with the legth in the dispersion direction (1 or 3)
    #  KEYWORD PARAMETERS:
    #       nbins              number of bins for the histogram
    # 		hlimit             the normalized height at which the histogram limits are taken for calculating the
    #                          resolving power. Default: 0.1
    # 		title              title to be written at the top
    # 		do_plot            True: display plots, False: No plots             Z
    #
    #  OUTPUTS:
    #       a dictionaire with tags:
    #       "resolvingPower"
    #       "deltaE": the minimum DE (at zero exist slit opening)
    #       "pendent":  P
    #       "origin"
    #
    #       Note that for any exit slit aperture  DE = deltaE + DZ/P
    #
    #  PROCEDURE:
    # 	Compute the dispersion plot (Z vs DE) then calculate the dispersion band by
    #         i) Removing the regression line
    #        ii) Calculate Z histogram
    #       iii) Calculate the histogram limits at hlimit height (bottom plot),
    #        iv) Plot these limits in the dispersion graphic (Z vs E) to define the dispersion band,
    #         v) compute related parameters:
    #          The "pendent" P from the regression fit gives the disperion DZ/DE
    #          The "origin" is the Eo value at the upper boundary of the dispersion band
    #          The Resolving Power is  Eo/P
    #          The "Delta" value is the DE corresponding to the histogram limits, or
    #              equivalently, the DE at zero slit opening
    #
    #          The energy bandwith at a given slit opening Z is DE= Delta+ Z/P
    #
    #  MODIFICATION HISTORY:
    # 	by M. Sanchez del Rio. ESRF. Grenoble, around 1995
    # 	2013/03/18 srio@esrf.eu documented, extracted some parameters
    #   2019/07/24 srio@lbl.gov python version
    #
    #-

    def respower(self,beam0,colE,col1,nolost=True,nbins=100,hlimit=0.1,do_plot=True,title=""):


        if  colE == 11 or colE == 19:
            pass
        else:
            raise Exception('First column is NOT energy or wavelength.')

        beam = beam0.duplicate()

        #
        # get data
        #
        energy = beam.getshonecol(colE,nolost=nolost)
        energy_all_rays = beam.getshonecol(colE, nolost=False)
        z = beam.getshonecol(col1, nolost=nolost)


        degree=1
        coeff = numpy.polyfit(energy, z, degree, rcond=None, full=False, w=None, cov=False)

        yfit = coeff[1] + coeff[0] * energy_all_rays
        beam.rays[:,col1-1] -= yfit

        #
        # histogram
        #
        tkt = beam.histo1(col1,nbins=nbins,nolost=nolost,calculate_widths=True)
        hx = tkt["bin_center"]
        hy = tkt["histogram"]

        # ;
        # ; get histo maximum and limits
        # ;
        tt = numpy.where(hy >= (hy.max() * hlimit))
        if hy[tt].size > 1:
            binSize = hx[1] - hx[0]
            width_at_hlimit = binSize * (tt[0][-1] - tt[0][0])
            coordinates_at_hlimit = (hx[tt[0][0]], hx[tt[0][-1]])
            coordinates_at_center = hx[numpy.argmax(hy)]

        else:
            raise Exception("Failed to compute width at %f height"%hlimit)

        deltax1 = numpy.abs((coordinates_at_hlimit[0] - coordinates_at_center) / coeff[0])
        deltax2 = numpy.abs((coordinates_at_hlimit[1] - coordinates_at_center) / coeff[0])
        deltaE = deltax1 + deltax2
        # deltaE = numpy.abs((coordinates_at_hlimit[1] - coordinates_at_hlimit[0]) / coeff[0])

        abscissas_at_hlimit = (coordinates_at_hlimit[0] - coeff[1]) / coeff[0] , (coordinates_at_hlimit[1] - coeff[1]) / coeff[0]
        abscissas_at_center = (coordinates_at_center - coeff[1]) / coeff[0]
        # b1 = coordinates_at_hlimit[0] - coeff[0] * abscissas_at_hlimit[0]
        # b2 = coordinates_at_hlimit[1] - coeff[0] * abscissas_at_hlimit[1]
        # ;
        # ; data
        # ;
        orig = -1.0 * (coeff[1] + coordinates_at_center) / coeff[0]
        resolvingPower = orig/deltaE
        pendent = coeff[0]

        info_txt = ""
        info_txt += "\n\n*********************************************************"
        info_txt += '\n\n Resolving Power E/DE= %g \n\n'%resolvingPower
        info_txt += '\n Resolution DE/E= %g' % (1.0/resolvingPower)
        info_txt += '\n The linear fit parameters are y = %f + %f x'%(coeff[1],coeff[0])
        info_txt += '\n Mean of residuals: %g'%beam.rays[:,col1-1].mean()
        info_txt += '\n StDev of residuals: %g'%beam.rays[:,col1-1].std()
        info_txt += "\n width_at_hlimit: %g "%width_at_hlimit
        info_txt += "\n ordinates_at_hlimit = (%g,%g)" % (coordinates_at_hlimit)
        info_txt += "\n ordinates_at_center = (%g)" % (coordinates_at_center)
        info_txt += '\n Linear fit pendent P: %f'%pendent
        info_txt += '\n Histogram peak at: %g'%coordinates_at_center
        info_txt += '\n Histogram base line: %f'%hlimit
        info_txt += '\n DeltaE(DZ=0) = %f'%deltaE
        info_txt += '\n Origin E = %f'%orig
        info_txt += '\n Intensity = %f'%beam.intensity(nolost=nolost)
        info_txt += '\n DE ~ DeltaE + DZ/|P|'
        info_txt += "\n*********************************************************\n\n"


        return {"colE":colE,"col1":col1,"nbins":nbins,"nolost":nolost,"hlimit":hlimit,"title":title, # inputs
                "resolvingPower":resolvingPower,
                "origin":orig,
                "pendent":pendent,
                "deltaE":deltaE,
                "coeff":coeff,
                "coordinates_at_hlimit":coordinates_at_hlimit,
                "coordinates_at_center":coordinates_at_center,
                "deltax1":deltax1,
                "deltax2":deltax2,
                "info":info_txt}

    def respower_plot(self,beam,d,nolost=True):


        colE = d["colE"]
        col1 = d["col1"]
        coeff = d["coeff"]
        nolost = d["nolost"]
        coordinates_at_hlimit = d["coordinates_at_hlimit"]
        orig = d["origin"]
        title = d["title"]
        deltax1 = d["deltax1"]
        deltax2 = d["deltax2"]

        if colE == 11:
            xtitle = "Photon energy [eV]"
            unit = "eV"
        elif colE == 19:
            xtitle = "Photon wavelength [A]"
            unit = "A"

        ytitle = "column %i [user units]"%col1

        energy = beam.getshonecol(colE,nolost=nolost)
        z = beam.getshonecol(col1, nolost=nolost)
        yfit = coeff[1] + coeff[0] * energy

        #
        # substracted plot
        #
        f = plot_scatter(energy, z-(coeff[1]+coeff[0]*energy),xtitle=xtitle, ytitle=ytitle, title=title,show=0)
        f[1].plot(energy, energy*0+coordinates_at_hlimit[0])
        f[1].plot(energy, energy*0+coordinates_at_hlimit[1])

        f[1].xaxis.label.set_size(self.labelsize)
        f[1].tick_params(axis='x', labelsize=self.labelsize)
        f[1].yaxis.label.set_size(self.labelsize)
        f[1].tick_params(axis='y', labelsize=self.labelsize)
        f[2].tick_params(axis='y', labelsize=self.labelsize)
        f[3].tick_params(axis='x', labelsize=self.labelsize)

        figure_canvas = FigureCanvasQTAgg(f[0])
        toolbar = NavigationToolbar(figure_canvas, self)
        self.detrended_id.layout().removeItem(self.detrended_id.layout().itemAt(1))
        self.detrended_id.layout().removeItem(self.detrended_id.layout().itemAt(0))
        self.detrended_id.layout().addWidget(toolbar)
        self.detrended_id.layout().addWidget(figure_canvas)


        #
        # main plot
        #

        g = plot_scatter(energy, z,show=0,xtitle=xtitle,ytitle=ytitle,
                         title=title+" E/DE=%d, DE=%f %s"%(d["resolvingPower"],d["deltaE"],unit))
        g[1].plot(energy, yfit)
        g[1].plot(energy, yfit+coordinates_at_hlimit[0])
        g[1].plot(energy, yfit+coordinates_at_hlimit[1])

        g[1].plot(energy, energy*0)
        if colE == 19: # wavelength
            g[1].plot(numpy.array((orig + deltax1, orig + deltax1)), numpy.array((-1000, 1000)))
            g[1].plot(numpy.array((orig - deltax2, orig - deltax2)), numpy.array((-1000, 1000)))
        else: # energy
            g[1].plot(numpy.array((orig - deltax1, orig - deltax1)), numpy.array((-1000, 1000)))
            g[1].plot(numpy.array((orig + deltax2, orig + deltax2)), numpy.array((-1000, 1000)))

        g[1].xaxis.label.set_size(self.labelsize)
        g[1].tick_params(axis='x', labelsize=self.labelsize)
        g[1].yaxis.label.set_size(self.labelsize)
        g[1].tick_params(axis='y', labelsize=self.labelsize)
        g[2].tick_params(axis='y', labelsize=self.labelsize)
        g[3].tick_params(axis='x', labelsize=self.labelsize)

        figure_canvas = FigureCanvasQTAgg(g[0])
        toolbar = NavigationToolbar(figure_canvas, self)
        self.dispersion_id.layout().removeItem(self.dispersion_id.layout().itemAt(1))
        self.dispersion_id.layout().removeItem(self.dispersion_id.layout().itemAt(0))
        self.dispersion_id.layout().addWidget(toolbar)
        self.dispersion_id.layout().addWidget(figure_canvas)





if __name__ == "__main__":
    import sys
    import Shadow

    # import matplotlib
    # matplotlib.rcParams.update({'font.size': 6})

    class MyBeam():
        pass
    beam_to_analize = Shadow.Beam()
    beam_to_analize.load("/home/manuel/Oasys/tmp.dat") #star.02")
    my_beam = MyBeam()
    my_beam._beam = beam_to_analize

    a = QApplication(sys.argv)
    ow = ALSResolvingPower()
    ow.setBeam1(my_beam)
    ow.show()
    a.exec_()
    ow.saveSettings()

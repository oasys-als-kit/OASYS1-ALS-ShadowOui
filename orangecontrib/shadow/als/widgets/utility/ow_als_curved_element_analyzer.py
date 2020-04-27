import numpy

from orangecontrib.shadow.als.widgets.gui.ow_als_generic_analyzer import ALSGenericAnalyzer

class ALSCurvedElementAnalyzer(ALSGenericAnalyzer):

    name = "ALS Curved Element Analyzer"
    description = "Shadow Utility: ALS Curved Element Analyzer"
    icon = "icons/curved_element_analyzer.png"
    priority = 1

    oe_name = ""

    def __init__(self):
        super().__init__()


    def complete_input_form(self):

        shadowOui_input_beam, oe_number, shadowOui_OE_before_tracing, shadowOui_OE_after_tracing, widget_class_name = self.get_shadowOui_objects()

        if "Ellipsoid" in widget_class_name:
            self.oe_name = "Ellipsoid"
            variables_to_change_list = ["Major Axis", "Minor Axis"]
        elif "Hyperboloid" in widget_class_name:
            self.oe_name = "Hyperboloid"
            variables_to_change_list = ["Major Axis", "Minor Axis"]
        elif "Paraboloid" in widget_class_name:
            self.oe_name = "Paraboloid"
            variables_to_change_list = ["Parabola Parameters"]
        elif "Spheric" in widget_class_name:
            self.oe_name = "Spheric"
            variables_to_change_list = ["Radius"]
        elif "Toroidal" in widget_class_name:
            self.oe_name = "Torus"
            variables_to_change_list = ["Major Radius", "Minor Radius"]
        else:
            raise ValueError("Input Optical Element is not Valid (only: Ellipsoid, Hyperboloid, Paraboloid, Spheric and Toruses")

        self.oe_settings_box.setTitle(self.oe_name + " Setting")
        self.cb_variable_to_change.clear()
        for item in variables_to_change_list:
            self.cb_variable_to_change.addItem(item)

        self.cb_variable_to_change.setCurrentIndex(self.variable_to_change)

    def get_OE_name(self):
        return self.oe_name

    def get_variables_to_change_list(self):
        return []

    def get_current_value(self, shadow_OE_before_tracing, shadow_OE_after_tracing):
        if "Ellipsoid" in self.oe_name or "Hyperboloid" in self.oe_name:
            if self.variable_to_change == 0:
                return str(shadow_OE_after_tracing.AXMAJ) + " [" + self.workspace_units_label + "]"
            elif self.variable_to_change == 1:
                return str(shadow_OE_after_tracing.AXMIN) + " [" + self.workspace_units_label + "]"
        elif "Paraboloid" in self.oe_name:
            if self.variable_to_change == 0:
                return str(shadow_OE_after_tracing.PARAM) + " [" + self.workspace_units_label + "]"
        elif "Spheric" in self.oe_name:
            if self.variable_to_change == 0:
                return str(shadow_OE_after_tracing.RMIRR) + " [" + self.workspace_units_label + "]"
        elif "Torus" in self.oe_name:
            if self.variable_to_change == 0:
                return str(shadow_OE_after_tracing.R_MAJ) + " [" + self.workspace_units_label + "]"
            elif self.variable_to_change == 1:
                return str(shadow_OE_after_tracing.R_MIN) + " [" + self.workspace_units_label + "]"

    def create_auxiliary_data(self, shadow_OE_before_tracing, shadow_OE_after_tracing):
        if "Ellipsoid" in self.oe_name or "Hyperboloid" in self.oe_name:
            AXMIN = shadow_OE_after_tracing.AXMIN
            AXMAJ = shadow_OE_after_tracing.AXMAJ

            SSOUR = shadow_OE_before_tracing.SSOUR
            SIMAG = shadow_OE_before_tracing.SIMAG

            #### FROM SHADOW3 KERNEL
            #! C Computes the mirror center position
            #! C
            #! C The center is computed on the basis of the object and image positions
            #! C

            AFOCI 	=  numpy.sqrt(AXMAJ**2-AXMIN**2)
            ECCENT 	=  AFOCI/AXMAJ

            YCEN  = (SSOUR-SIMAG)*0.5/ECCENT
            ZCEN  = -numpy.sqrt(1-YCEN**2/AXMAJ**2)*AXMIN

            # ANGLE OF AXMAJ AND POLE (CCW): NOT RETURNED BY SHADOW!
            ELL_THE = numpy.degrees(numpy.arctan(numpy.abs(ZCEN/YCEN)))

            return AXMIN, AXMAJ, ELL_THE
        elif "Torus" in self.oe_name:
            R_MIN = shadow_OE_after_tracing.R_MIN
            R_MAJ = shadow_OE_after_tracing.R_MAJ

            return R_MIN, R_MAJ

    def modify_OE(self, shadow_OE, scanned_value, auxiliary_data=None):
        #switch to external/user defined surface shape parameters
        shadow_OE.F_EXT   = 1

        if "Ellipsoid" in self.oe_name or "Hyperboloid" in self.oe_name:

            AXMIN, AXMAJ, ELL_THE = auxiliary_data

            if self.variable_to_change == 0:
                shadow_OE.AXMIN   = AXMIN
                shadow_OE.AXMAJ   = scanned_value
            elif self.variable_to_change == 1:
                shadow_OE.AXMIN   = scanned_value
                shadow_OE.AXMAJ   = AXMAJ

            shadow_OE.ELL_THE = ELL_THE
        elif "Paraboloid" in self.oe_name:
            shadow_OE.PARAM   = scanned_value
        elif "Spheric" in self.oe_name:
            shadow_OE.RMIRR   = scanned_value
        elif "Torus" in self.oe_name:
            R_MIN, R_MAJ = auxiliary_data

            if self.variable_to_change == 0:
                shadow_OE.R_MIN   = R_MIN
                shadow_OE.R_MAJ   = scanned_value
            elif self.variable_to_change == 1:
                shadow_OE.R_MIN   = scanned_value
                shadow_OE.R_MAJ   = R_MAJ

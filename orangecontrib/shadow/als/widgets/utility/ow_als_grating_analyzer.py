import numpy

from orangecontrib.shadow.als.widgets.gui.ow_als_generic_analyzer import ALSGenericAnalyzer

class ALSGratingAnalyzer(ALSGenericAnalyzer):

    name = "ALS Grating Analyzer"
    description = "Shadow Utility: ALS Grating Analyzer"
    icon = "icons/grating_analyzer.png"
    priority = 2

    def __init__(self):
        super().__init__()

    def get_OE_name(self):
        return "VLS Grating"

    def get_variables_to_change_list(self):
        return ["Ruling Density Coefficient 0th",
                "Ruling Density Coefficient 1th",
                "Ruling Density Coefficient 2th",
                "Ruling Density Coefficient 3th",
                "Ruling Density Coefficient 4th"]

    def get_current_value(self, shadow_OE_before_tracing, shadow_OE_after_tracing):
        if self.variable_to_change == 0:
            return str(shadow_OE_before_tracing.RULING) + " [l/" + self.workspace_units_label + "]"
        elif self.variable_to_change == 1:
            return str(shadow_OE_before_tracing.RUL_A1) + " [(l/" + self.workspace_units_label + ")^2]"
        elif self.variable_to_change == 2:
            return str(shadow_OE_before_tracing.RUL_A2) + " [(l/" + self.workspace_units_label + ")^3]"
        elif self.variable_to_change == 3:
            return str(shadow_OE_before_tracing.RUL_A3) + " [(l/" + self.workspace_units_label + ")^4]"
        elif self.variable_to_change == 4:
            return str(shadow_OE_before_tracing.RUL_A4) + " [(l/" + self.workspace_units_label + ")^5]"

    def create_auxiliary_data(self, shadow_OE_before_tracing, shadow_OE_after_tracing):
        return None

    def modify_OE(self, shadow_OE, scanned_value, auxiliary_data=None):
        if self.variable_to_change == 0:
            shadow_OE.RULING = scanned_value
        elif self.variable_to_change == 1:
            shadow_OE.RUL_A1 = scanned_value
        elif self.variable_to_change == 2:
            shadow_OE.RUL_A2 = scanned_value
        elif self.variable_to_change == 3:
            shadow_OE.RUL_A3 = scanned_value
        elif self.variable_to_change == 4:
            shadow_OE.RUL_A4 = scanned_value




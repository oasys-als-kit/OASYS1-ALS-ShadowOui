import numpy

from orangecontrib.shadow.als.widgets.gui.ow_als_generic_analyzer import ALSGenericAnalyzer

class ALSGratingAnalyzer(ALSGenericAnalyzer):

    name = "ALS Grating Analyzer"
    description = "Shadow Utility: ALS Grating Analyzer"
    icon = "icons/grating_analyzer.png"
    priority = 2

    def __init__(self):
        super().__init__()

    def get_plot_ranges(self):

        x_min = -0.15
        x_max = 0.15
        z_min = -0.002
        z_max = 0.002
        nbins=101

        return x_min, x_max, z_min, z_max, nbins

    def create_auxiliary_data(self, shadow_OE_before_tracing, shadow_OE_after_tracing):
        return None

    def create_scanned_values(self, shadow_OE_before_tracing, shadow_OE_after_tracing):
        C0 = shadow_OE_before_tracing.RULING
        C1 = shadow_OE_before_tracing.RUL_A1
        C2 = shadow_OE_before_tracing.RUL_A2
        C3 = shadow_OE_before_tracing.RUL_A3

        print("RULING DENSITY", C0, C1, C2, C3)

        return -5 + C3 + numpy.arange(0, 41)*(10/40)

    def modify_OE(self, shadow_OE, scanned_value, auxiliary_data=None):

        shadow_OE.RUL_A3= scanned_value


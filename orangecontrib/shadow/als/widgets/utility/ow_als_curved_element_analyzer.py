import numpy

from orangecontrib.shadow.als.widgets.gui.ow_als_generic_analyzer import ALSGenericAnalyzer

class ALSCurvedElementAnalyzer(ALSGenericAnalyzer):

    name = "ALS Curved Element Analyzer"
    description = "Shadow Utility: ALS Curved Element Analyzer"
    icon = "icons/curved_element_analyzer.png"
    priority = 1

    def __init__(self):
        super().__init__()

    def get_plot_ranges(self):

        x_min = -0.005
        x_max = 0.005
        z_min = -0.005
        z_max = 0.005
        nbins=501

        return x_min, x_max, z_min, z_max, nbins

    def create_auxiliary_data(self, shadow_OE_before_tracing, shadow_OE_after_tracing):
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

    def create_scanned_values(self, shadow_OE_before_tracing, shadow_OE_after_tracing):
        AXMAJ = shadow_OE_after_tracing.AXMAJ

        return -1 + AXMAJ + numpy.arange(0, 41)*(2/40)

    def modify_OE(self, shadow_OE, scanned_value, auxiliary_data=None):
        AXMIN, AXMAJ, ELL_THE = auxiliary_data

        #switch to external/user defined surface shape parameters
        shadow_OE.F_EXT   = 1
        shadow_OE.AXMIN   = AXMIN
        shadow_OE.AXMAJ   = scanned_value
        shadow_OE.ELL_THE = ELL_THE


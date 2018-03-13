# OASYS1-ALS-ShadowOui
ALS widgets to extend ShadowOui functionalities

![addons menu](https://github.com/awojdyla/OASYS1-ALS-ShadowOui/blob/master/images/addons.png "Add-on menu")

![side menu](https://github.com/awojdyla/OASYS1-ALS-ShadowOui/blob/master/images/addons.png "side menu")

## Shadow ALS Sources
The Shadow ALS Sources add mostly one new element, the ALS undulator, which allows to use the SRW engine to compute realistic synchrotron sources, even when slightly detuned.
### ALS undulator
![ALS undulator](https://github.com/awojdyla/OASYS1-ALS-ShadowOui/blob/master/images/als_undulator.png "ALS undulator") 
![SRW source](https://github.com/awojdyla/OASYS1-ALS-ShadowOui/blob/master/images/srw_tab2.png "SRW  source")

## Shadow ALS utility
The Shadow ALS utility adds new elements to Oasys capable of scanning a parameter for mirrors or grating, in order to study and optimize their performances.

![analyzer menu](https://github.com/awojdyla/OASYS1-ALS-ShadowOui/blob/master/images/analyzer_menu.png "analyzer menu")

The analyzers need to be places right *after* the element to study.
### ALS curved element Analyzer
The ALS curved element Analyzer allows to change the parameter of any reflective surface. Depending on the shape complexity (from flat mirror to toroid), the scanning parameter can be chosen.
![mirror analyzer](https://github.com/awojdyla/OASYS1-ALS-ShadowOui/blob/master/images/mirror_analyzer.png "mirror_analyzer")
### ALS grating analyzer
For gratings, the higher order grating parameters can be scanned, to study focusing or mitigate aberrations.
![grating analyzer](https://github.com/awojdyla/OASYS1-ALS-ShadowOui/blob/master/images/grating_analyzer.png "grating_analyzer")

## Shadow ALS Optical Elements
Among the new ALS Optical elements are the ANSYS reader, which allows to use files exported from ANSYS in order to accurately model the effect of thermal deformations of mirror under high heat load.
### ANSYS reader
![ANSYS reader](https://github.com/awojdyla/OASYS1-ALS-ShadowOui/blob/master/images/ansys_reader.png "ANSYS reader")

### Coming soon 
diaboloids and angeloids!

## To do list
+ wavefront sensors
+ adaptive optics

FUSION for Processing
---------------------
A QGIS plugin to use FUSION tools for LiDAR analysis and visualization.

This plugin is a port to QGIS3 of the original FUSION provider that was a core element of Processing in QGIS2

It is based on the initial porting of the FUSION provider to QGIS3, done by Alexander Bruy.

Installation
------------
*This plugin is only availabe for Windows users since the FUSION binaries only are avialable for Windows.*

Install the plugin via **Manage and Install Plugins** in QGIS. 

You can also clone this repository and copy the `processing_fusion` folder to your QGIS plugins folder (in the folder correspodning to your current active QGIS profile). Activate the plugin and activate the provider in the Processing settings. FUSION algorithms will appear in the Processing toolbox.

You need to downlaod and install FUSION separately (http://forsys.sefs.uw.edu/FUSION/fusionlatest.html). 

After installing the plugin and FUSION/LDV, activate and configure **FUSION for processing** in the Options-window in the **Processing Toolbox**. 

Known limitations
-----------------
For some users, multiple files cannot to be selected for the QgsProcessingParameterFile class. That means that, although most of the FUSION algorithms accept a set of .las files as input, you will only be able to select one in the corresponding file selector. You can, however, use a multiple input by directly typing the filepaths (not selecting it in the file selector) in the textbox, separated by semicolons (;).

Using FUSION/LDV in a stand-alone Python script
-----------------------------------------------
As from version 3.x the fusion tools can also be accessed and used via the processing library in QGIS3 using the following code example:

`from qgis.core import QgsApplication`

`import sys`

`sys.path.append(r'C:\Users\YOURWINDOWSUSERNAME\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins')`

`from processing_fusion.processing_fusion_provider import ProcessingFUSIONProvider`

`fusion_provider = ProcessingFUSIONProvider()`

`QgsApplication.processingRegistry().addProvider(fusion_provider)`

`import processing`

`from processing.core.Processing import Processing`

`Processing.initialize()`

`parin = { 'CSV' : False, 'INPUT' : 'C:/temp/ground.dtm', 'MULTIPLIER' : None, 'OUTPUT' : 'C:/temp/test.tif', 'RASTER' : False }`

`processing.run('fusion:dtm2ascii', parin)`

Contributors
------------
QGISSweden (http://www.qgis.se/) provided funding to finilize the porting of this plugin into QGIS3.


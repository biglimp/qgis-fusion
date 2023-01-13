# -*- coding: utf-8 -*-

"""
***************************************************************************
    fusionProvider.py
    ---------------------
    Date                 : March 2019
    Copyright            : (C) 2019 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'March 2019'
__copyright__ = '(C) 2019, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

# import os
# from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import QCoreApplication
# from qgis.core import QgsProcessingProvider
from processing.core.ProcessingConfig import ProcessingConfig, Setting
from qgis.core import QgsProcessingProvider
from processing.core.ProcessingConfig import ProcessingConfig
from processing_fusion.algs.ascii2dtm import ascii2dtm
from processing_fusion.algs.csv2grid import csv2grid
from processing_fusion.algs.dtm2ascii import dtm2ascii
from processing_fusion.algs.dtm2envi import dtm2envi
from processing_fusion.algs.dtm2tif import dtm2tif
from processing_fusion.algs.dtm2xyz import dtm2xyz
from processing_fusion.algs.xyz2dtm import xyz2dtm
from processing_fusion.algs.canopymaxima import CanopyMaxima
from processing_fusion.algs.canopymodel import CanopyModel
from processing_fusion.algs.catalog import Catalog
from processing_fusion.algs.clipdata import ClipData
from processing_fusion.algs.cloudmetrics import CloudMetrics
from processing_fusion.algs.cover import Cover
from processing_fusion.algs.densitymetrics import DensityMetrics
from processing_fusion.algs.filterdata import FilterData
from processing_fusion.algs.firstlastreturn import FirstLastReturn
from processing_fusion.algs.gridmetrics import GridMetrics
from processing_fusion.algs.gridsurfacecreate import GridSurfaceCreate
from processing_fusion.algs.gridsurfacestats import GridSurfaceStats
from processing_fusion.algs.groundfilter import GroundFilter
from processing_fusion.algs.intensityimage import IntensityImage
from processing_fusion.algs.imagecreate import ImageCreate
from processing_fusion.algs.mergedata import MergeData
from processing_fusion.algs.polyclipdata import PolyClipData
from processing_fusion.algs.returndensity import ReturnDensity
from processing_fusion.algs.thindata import ThinData
from processing_fusion.algs.tinsurfacecreate import TinSurfaceCreate
from processing_fusion.algs.topometrics import TopoMetrics
from processing_fusion.algs.treeseg import TreeSeg
from processing_fusion.algs.openviewer import OpenViewer

from processing_fusion import fusionUtils
import os.path
from qgis.PyQt.QtGui import QIcon
import inspect

pluginPath = os.path.dirname(__file__)

class ProcessingFUSIONProvider(QgsProcessingProvider):

    def __init__(self):
        """
        Default constructor.
        """
        self.plugin_dir = os.path.dirname(__file__)
        QgsProcessingProvider.__init__(self)
    
    def unload(self):
        ProcessingConfig.removeSetting(fusionUtils.FUSION_ACTIVE)
        ProcessingConfig.removeSetting(fusionUtils.FUSION_VERBOSE)
        pass

    def loadAlgorithms(self):
        self.addAlgorithm(ascii2dtm())
        self.addAlgorithm(csv2grid())
        self.addAlgorithm(dtm2ascii())
        self.addAlgorithm(dtm2envi())
        self.addAlgorithm(dtm2tif())
        self.addAlgorithm(dtm2xyz())
        self.addAlgorithm(xyz2dtm())
        self.addAlgorithm(CanopyMaxima())
        self.addAlgorithm(CanopyModel())
        self.addAlgorithm(Catalog())
        self.addAlgorithm(ClipData())
        self.addAlgorithm(CloudMetrics())
        self.addAlgorithm(Cover())
        self.addAlgorithm(DensityMetrics())
        self.addAlgorithm(FilterData())
        self.addAlgorithm(FirstLastReturn())
        self.addAlgorithm(GridMetrics())
        self.addAlgorithm(GridSurfaceCreate())
        self.addAlgorithm(GridSurfaceStats())
        self.addAlgorithm(GroundFilter())
        self.addAlgorithm(ImageCreate())
        self.addAlgorithm(IntensityImage())
        self.addAlgorithm(MergeData())
        self.addAlgorithm(PolyClipData())
        self.addAlgorithm(ReturnDensity())
        self.addAlgorithm(ThinData())
        self.addAlgorithm(TinSurfaceCreate())
        self.addAlgorithm(TreeSeg())
        self.addAlgorithm(TopoMetrics())
        self.addAlgorithm(OpenViewer())

    def id(self):
        return 'fusion'

    def name(self):
        return 'FUSION'

    def icon(self):
        return QIcon(os.path.join(pluginPath, 'icons', 'fusion.svg'))

    def load(self):
        ProcessingConfig.settingIcons[self.name()] = self.icon()
        ProcessingConfig.addSetting(Setting(self.name(),
                                            fusionUtils.FUSION_ACTIVE,
                                            self.tr('Activate'),
                                            False))
        ProcessingConfig.addSetting(Setting(self.name(),
                                            fusionUtils.FUSION_DIRECTORY,
                                            self.tr('FUSION directory'),
                                            fusionUtils.fusionDirectory(),
                                            valuetype=Setting.FOLDER))        
        ProcessingConfig.addSetting(Setting(self.name(),
                                            fusionUtils.FUSION_VERBOSE,
                                            self.tr('Log commands output'),
                                            False))
        ProcessingConfig.readSettings()
        self.refreshAlgorithms()
        return True

    def longName(self):
        """
        Returns the a longer version of the provider name, which can include
        extra details such as version numbers. E.g. "Lastools LIDAR tools
        (version 2.2.1)". This string should be localised. The default
        implementation returns the same string as name().
        """
        return 'FUSION for Processing, Version 3.5'


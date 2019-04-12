# -*- coding: utf-8 -*-

"""
***************************************************************************
    OpenViewer.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""


__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os
from qgis.core import (QgsProcessingException,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile
                      )
import subprocess

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils

class OpenViewer(FusionAlgorithm):

    def name(self):
        return 'openviewer'

    def displayName(self):
        return self.tr('Open viewer')

    def group(self):
        return self.tr('Visualization')

    def groupId(self):
        return 'visualization'

    def tags(self):
        return [self.tr('lidar')]

    def shortHelpString(self):
        return ''

    def __init__(self):
        super().__init__()


    def initAlgorithm(self, config=None):
        pass 
        
    def processAlgorithm(self, parameters, context, feedback):
        f = os.path.join(fusionUtils.fusionDirectory(), 'pdq.exe')
        subprocess.Popen(f)
        return {}
        
# -*- coding: utf-8 -*-

"""
***************************************************************************
    MergeData.py
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
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils

class MergeData(FusionAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'

    def name(self):
        return 'mergelasfiles'

    def displayName(self):
        return self.tr('Merge LAS files')

    def group(self):
        return self.tr('Point cloud analysis')

    def groupId(self):
        return 'points'

    def tags(self):
        return [self.tr('lidar')]

    def shortHelpString(self):
        return ''

    def __init__(self):
        super().__init__()


    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, self.tr('Input LAS layers'), extension = 'las'))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output merged LAS file'),
                                                                self.tr('LAS files (*.las *.LAS)')))
        self.addAdvancedModifiers()

    def processAlgorithm(self, parameters, context, feedback):
        commands = [os.path.join(fusionUtils.fusionDirectory(), 'MergeData.exe')]
        self.addAdvancedModifiersToCommands(commands, parameters, context)
        
        self.addInputFilesToCommands(commands, parameters, self.INPUT, context)        
        
        outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        commands.append('"%s"' % outputFile)

        fusionUtils.execute(commands, feedback)

        return self.prepareReturn(parameters)

# -*- coding: utf-8 -*-

"""
***************************************************************************
    GroundFilter.py
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
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils

class GroundFilter(FusionAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    CELLSIZE = 'CELLSIZE'
    SURFACE = 'SURFACE'

    def name(self):
        return 'groundfilter'

    def displayName(self):
        return self.tr('Ground filter')

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
            self.INPUT, self.tr('Input LAS layer'), extension = 'las'))   
        self.addParameter(QgsProcessingParameterNumber(
            self.CELLSIZE, self.tr('Cellsize for intermediate surfaces'), QgsProcessingParameterNumber.Double,
            minValue = 0, defaultValue = 10.0))        

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output ground LAS file'),
                                                                self.tr('LAS files (*.las *.LAS)')))
        self.addParameter(QgsProcessingParameterBoolean(
            self.SURFACE, self.tr('Create .dtm surface'), False))
        self.addAdvancedModifiers()
    
    def processAlgorithm(self, parameters, context, feedback):
        commands = [os.path.join(fusionUtils.fusionDirectory(), 'GroundFilter.exe')]        
        self.addAdvancedModifiersToCommands(commands, parameters, context)
        if self.parameterAsBool(parameters, self.SURFACE, context):
            commands.append('/surface')

        outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        commands.append('"%s"' % outputFile)
        commands.append(str(self.parameterAsDouble(parameters, self.CELLSIZE, context)))
        self.addInputFilesToCommands(commands, parameters, self.INPUT, context)        

        fusionUtils.execute(commands, feedback)

        return self.prepareReturn(parameters)

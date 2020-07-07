# -*- coding: utf-8 -*-

"""
***************************************************************************
    ClipData.py
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
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils

class ClipData(FusionAlgorithm):

    def name(self):
        return 'clipdata'

    def displayName(self):
        return self.tr('Clip data')

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

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    EXTENT = 'EXTENT'
    SHAPE = 'SHAPE'
    DTM = 'DTM'
    HEIGHT = 'HEIGHT'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, self.tr('Input LAS layer'), extension = 'las'))     
        self.addParameter(QgsProcessingParameterExtent(self.EXTENT, self.tr('Extent')))
        # self.addParameter(QgsProcessingParameterEnum(
            # self.SHAPE, self.tr('Shape'), ['Rectangle', 'Circle'], optional = True, defaultValue=0))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output'),
                                                                self.tr('LAS files (*.las *.LAS)')))
        ground = QgsProcessingParameterFile(
            self.DTM, self.tr('Ground file for height normalization'), optional = True, extension = 'dtm')
        ground.setFlags(ground.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(ground)        
        height = QgsProcessingParameterBoolean(
            self.HEIGHT, self.tr('Convert point elevations into heights above ground (used with the above command)'), False)
        height.setFlags(height.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(height)

        self.addAdvancedModifiers()

    def processAlgorithm(self, parameters, context, feedback):
        commands = [os.path.join(fusionUtils.fusionDirectory(), 'ClipData.exe')]
        self.addAdvancedModifiersToCommands(commands, parameters, context)
        # commands.append('/shape:' + str(self.parameterAsEnum(parameters, self.SHAPE, context)))
        dtm = self.parameterAsString(parameters, self.DTM, context)
        if dtm:
            commands.append('/dtm:' + dtm)
        height = self.parameterAsString(parameters, self.HEIGHT, context)
        if height:
            commands.append('/height')

        self.addInputFilesToCommands(commands, parameters, self.INPUT, context)        
        
        outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        commands.append('"%s"' % outputFile)

        extent = self.parameterAsExtent(parameters, self.EXTENT, context)
        commands.append(extent.xMinimum())
        commands.append(extent.yMinimum())
        commands.append(extent.xMaximum())
        commands.append(extent.yMaximum())
        
        fusionUtils.execute(commands, feedback)

        return self.prepareReturn(parameters)

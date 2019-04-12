# -*- coding: utf-8 -*-

"""
***************************************************************************
    CanopyMaxima.py
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

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils


class CanopyMaxima(FusionAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    THRESHOLD = 'THRESHOLD'
    GROUND = 'GROUND'
    PARAM_A = "PARAM_A"
    PARAM_C = "PARAM_C"
    SUMMARY = "SUMMARY"

    def name(self):
        return 'canopymaxima'

    def displayName(self):
        return self.tr('Canopy maxima')

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
            self.INPUT, self.tr('Input FUSION canopy height model')))
        self.addParameter(QgsProcessingParameterFile(
            self.GROUND, self.tr('Input ground .dtm layer'), extension = 'dtm',
            optional = True))
        self.addParameter(QgsProcessingParameterNumber(
            self.THRESHOLD, self.tr('Height threshold'), QgsProcessingParameterNumber.Double,
            minValue = 0, defaultValue = 10.0))
        self.addParameter(QgsProcessingParameterNumber(
            self.PARAM_A, self.tr('Variable window size: parameter A'), QgsProcessingParameterNumber.Double,
            minValue = 0, defaultValue = 2.51503))
        self.addParameter(QgsProcessingParameterNumber(
            self.PARAM_C, self.tr('Parameter C'), QgsProcessingParameterNumber.Double,
            minValue = 0, defaultValue = 0.00901))
        self.addParameter(QgsProcessingParameterBoolean(
            self.SUMMARY, self.tr('Summary (tree height summary statistics)'), False))

        self.addAdvancedModifiers()

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output'),
                                                                self.tr('DTM files (*.dtm *.DTM)')))


    def processAlgorithm(self, parameters, context, feedback):
        commands = [os.path.join(fusionUtils.fusionDirectory(), 'CanopyMaxima.exe')]
        commands.append('/wse:{},0,{},0'.format(self.parameterAsDouble(parameters, self.PARAM_A, context), 
                                            self.parameterAsDouble(parameters, self.PARAM_C, context)))
        
        summary = self.parameterAsBool(parameters, self.SUMMARY, context)
        if summary:
            commands.append('/summary')
        
        self.addAdvancedModifiersToCommands(commands, parameters, context)

        ground = self.parameterAsString(parameters, self.GROUND, context).strip()       
        if ground:
            commands.append('/ground:' + ground)
        commands.append('/threshold:{}'.format(self.parameterAsDouble(parameters, self.THRESHOLD, context)))                        
        self.addInputFilesToCommands(commands, parameters, self.INPUT, context)        
        
        self.addAdvancedModifiersToCommands(commands, parameters, context)
        outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        commands.append('"%s"' % outputFile)
        
        fusionUtils.execute(commands, feedback)

        return self.prepareReturn(parameters)

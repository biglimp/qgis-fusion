# -*- coding: utf-8 -*-

"""
***************************************************************************
    IntensityImage.py
    ---------------------
    Date                 : January 2016
    Copyright            : (C) 2016 by Niccolo' Marchi
    Email                : sciurusurbanus at hotmail dot it
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = "Niccolo' Marchi"
__date__ = 'January 2016'
__copyright__ = "(C) 2016 by Niccolo' Marchi"

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

class IntensityImage(FusionAlgorithm):

    INPUT = 'INPUT'
    ALLRET = 'ALLRET'
    LOWEST = 'LOWEST'
    HIST = 'HIST'
    PIXEL = 'PIXEL'
    SWITCH = 'SWITCH'
    OUTPUT = 'OUTPUT'

    def name(self):
        return 'intensityimage'

    def displayName(self):
        return self.tr('Intensity image')

    def group(self):
        return self.tr('Surface')

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
            self.INPUT, self.tr('Input file')))
        self.addParameter(QgsProcessingParameterBoolean(
            self.ALLRET, self.tr('Use all returns instead of only first'), False))
        self.addParameter(QgsProcessingParameterBoolean(
            self.LOWEST, self.tr('Use the lowest return in pixel area to assign the intensity value'), False))
        self.addParameter(QgsProcessingParameterBoolean(
            self.HIST, self.tr('Produce a CSV intensity histogram data file'), False))
        self.addParameter(QgsProcessingParameterNumber(
            self.PIXEL, self.tr('Pixel size'), QgsProcessingParameterNumber.Double,
            minValue = 0, defaultValue = 1.0))
        self.addParameter(QgsProcessingParameterEnum(
            self.SWITCH, self.tr('Output format'), ['Bitmap', 'JPEG']))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output image')))
        self.addAdvancedModifiers()

    def processAlgorithm(self, parameters, context, feedback):
        commands = [os.path.join(fusionUtils.fusionDirectory(), 'IntensityImage.exe')]
        if self.parameterAsBool(parameters, self.ALLRET, context):
            commands.append('/allreturns')
        if self.parameterAsBool(parameters, self.LOWEST, context):
            commands.append('/lowest')
        if self.parameterAsBool(parameters, self.HIST, context):
            commands.append('/hist')
        if self.parameterAsEnum(parameters, self.SWITCH, context) == 0:
            commands.append('/jpg')
        commands.append(str(self.parameterAsDouble(parameters, self.PIXEL, context)))
        
        outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        commands.append('"%s"' % outputFile)
        self.addInputFilesToCommands(commands, parameters, self.INPUT, context)        

        fusionUtils.execute(commands, feedback)

        return self.prepareReturn(parameters)

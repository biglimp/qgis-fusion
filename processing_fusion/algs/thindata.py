# -*- coding: utf-8 -*-

"""
***************************************************************************
    ThinData.py
    ---------------------
    Date                 : October 2020
    Copyright            : (C) 2020 by Niccolo' Marchi
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
__date__ = 'October 2020'
__copyright__ = "(C) 2020 by Niccolo' Marchi"

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.core import (QgsProcessingException,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterFileDestination
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils


class ThinData(FusionAlgorithm):

    INPUT = 'INPUT'
    DENSITY = 'DENSITY'
    CELLSIZE = 'CELLSIZE'
    RSEED = 'RSEED'
    IGNOREOVERLAP = 'IGNOREOVERLAP'
    CLASS = 'CLASS'
    VERSION64 = 'VERSION64'
    OUTPUT = 'OUTPUT'

    def name(self):
        return 'thindata'

    def displayName(self):
        return self.tr('ThinData')

    def group(self):
        return self.tr('Point cloud analysis')

    def groupId(self):
        return 'points'

    def tags(self):
        return [self.tr('lidar')]

    def shortHelpString(self):
        return self.tr('Thin LIDAR data to specific pulse densities')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     self.tr('Input LAS layer'),
                                                     fileFilter = '(*.las *.laz)'))
        self.addParameter(QgsProcessingParameterNumber(self.DENSITY,
                                                       self.tr('Desired pulse density per square unit'),
                                                       QgsProcessingParameterNumber.Integer,
                                                       minValue = 0,
                                                       defaultValue = 1))
        self.addParameter(QgsProcessingParameterNumber(self.CELLSIZE,
                                                       self.tr('Cellsize (in square units)'),
                                                       QgsProcessingParameterNumber.Integer,
                                                       minValue=0,
                                                       defaultValue=0.0))


        params = []
        params.append(QgsProcessingParameterNumber(self.RSEED,
                                                       self.tr('Use random number (can range from 0 to 99)'),
                                                       QgsProcessingParameterNumber.Integer,
                                                       minValue = 0,
                                                       maxValue = 99,
                                                       defaultValue=None,
                                                       optional = True))
        params.append(QgsProcessingParameterString(self.CLASS,
                                                   self.tr('Use only a specific LAS class'),
                                                   defaultValue='',
                                                   optional = True))
        params.append(QgsProcessingParameterBoolean(self.IGNOREOVERLAP,
                                                        self.tr('Ignore points with the overlap flag set'),
                                                        defaultValue=False,
                                                        optional = True))
        for p in params:
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)

        self.addParameter(QgsProcessingParameterBoolean(self.VERSION64,
                                                        self.tr('Use 64-bit version'),
                                                        defaultValue=True))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output'),
                                                                self.tr('LAS files (*.las)')))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        
        if self.VERSION64:
            arguments.append('"' + os.path.join(fusionUtils.fusionDirectory(), 'ThinData64.exe') + '"')
        else:
            arguments.append('"' + os.path.join(fusionUtils.fusionDirectory(), 'ThinData.exe') + '"')

        if self.IGNOREOVERLAP in parameters and parameters[self.IGNOREOVERLAP]:
            arguments.append('/ignoreoverlap')

        class_var = self.parameterAsString(parameters, self.CLASS, context).strip()
        if class_var:
            arguments.append('/class:' + class_var)

        if self.RSEED in parameters and parameters[self.RSEED] is not None:
            arguments.append('/rseed:{}'.format(self.parameterAsInt(parameters, self.RSEED, context)))

        arguments.append(self.parameterAsFileOutput(parameters, self.OUTPUT, context))
        arguments.append(str(self.parameterAsInt(parameters, self.DENSITY, context)))
        arguments.append(str(self.parameterAsInt(parameters, self.CELLSIZE, context)))
        arguments.append(self.parameterAsFile(parameters, self.INPUT, context))

        fusionUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results

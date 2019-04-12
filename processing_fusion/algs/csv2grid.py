# -*- coding: utf-8 -*-

"""
***************************************************************************
    csv2grid.py
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

import os

from qgis.core import (QgsProcessingException,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterRasterDestination
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils


class csv2grid(FusionAlgorithm):

    INPUT = 'INPUT'
    COLUMN = 'COLUMN'
    MULTIPLIER = 'MULTIPLIER'
    NDZERO = 'NDZERO'
    OUTPUT = 'OUTPUT'

    def name(self):
        return 'csv2grid'

    def displayName(self):
        return self.tr('CSV to grid')

    def group(self):
        return self.tr('Conversion')

    def groupId(self):
        return 'conversion'

    def tags(self):
        return self.tr('lidar,csv,grid,convert').split(',')

    def shortHelpString(self):
        return self.tr('Converts data stored in comma separated value '
                       '(CSV) format into ASCII raster format.')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     'Input CSV file',
                                                     QgsProcessingParameterFile.File,
                                                     'csv'))
        self.addParameter(QgsProcessingParameterNumber(self.COLUMN,
                                                       self.tr('Column number for the values'),
                                                       QgsProcessingParameterNumber.Integer,
                                                       minValue=1,
                                                       defaultValue=0))

        params = []
        params.append(QgsProcessingParameterNumber(self.MULTIPLIER,
                                                   self.tr('Multiply all data values by the constant'),
                                                   QgsProcessingParameterNumber.Double,
                                                   defaultValue=None,
                                                   optional=True))
        params.append(QgsProcessingParameterNumber(self.NDZERO,
                                                   self.tr('Reference column number to change NODATA to 0'),
                                                   QgsProcessingParameterNumber.Integer,
                                                   minValue=1,
                                                   defaultValue=None,
                                                   optional=True))
        for p in params:
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)

        self.addParameter(QgsProcessingParameterRasterDestination(self.OUTPUT,
                                                                  self.tr('Output')))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(fusionUtils.fusionDirectory(), self.name()))

        if self.MULTIPLIER in parameters and parameters[self.MULTIPLIER] is not None:
            arguments.append('/multiplier:{}'.format(self.parameterAsDouble(parameters, self.MULTIPLIER, context)))

        if self.NDZERO in parameters and parameters[self.NDZERO] is not None:
            arguments.append('/ndzero:{}'.format(self.parameterAsDouble(parameters, self.NDZERO, context)))

        arguments.append(self.parameterAsFile(parameters, self.INPUT, context))
        arguments.append(str(self.parameterAsInt(parameters, self.COLUMN, context)))
        arguments.append(self.parameterAsOutputLayer(parameters, self.OUTPUT, context))

        fusionUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results

# -*- coding: utf-8 -*-

"""
***************************************************************************
    dtm2ascii.py
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
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterRasterDestination
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils


class dtm2ascii(FusionAlgorithm):

    INPUT = 'INPUT'
    CSV = 'CSV'
    RASTER = 'RASTER'
    MULTIPLIER = 'MULTIPLIER'
    OUTPUT = 'OUTPUT'

    def name(self):
        return 'dtm2ascii'

    def displayName(self):
        return self.tr('DTM to ASCII')

    def group(self):
        return self.tr('Conversion')

    def groupId(self):
        return 'conversion'

    def tags(self):
        return self.tr('lidar,ascii,dtm,convert').split(',')

    def shortHelpString(self):
        return self.tr('Converts data stored in the PLANS DTM format '
                       'into ASCII raster files.')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     'Input PLANS DTM file',
                                                     QgsProcessingParameterFile.File,
                                                     'dtm'))

        params = []
        params.append(QgsProcessingParameterBoolean(self.CSV,
                                                    self.tr('Output data values in comma separated value format'),
                                                    defaultValue=None,
                                                    optional=True))
        params.append(QgsProcessingParameterBoolean(self.RASTER,
                                                    self.tr('Output data values in ASCII raster format'),
                                                    defaultValue=None,
                                                    optional=True))
        params.append(QgsProcessingParameterNumber(self.MULTIPLIER,
                                                   self.tr('Multiply all data values by the constant'),
                                                   QgsProcessingParameterNumber.Double,
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

        if self.CSV in parameters and parameters[self.CSV]:
            arguments.append('/csv')

        if self.RASTER in parameters and parameters[self.RASTER]:
           if self.CSV in parameters and parameters[self.CSV]:
               raise QgsProcessingException(self.tr('Switches "/csv" and "/raster" are mutually exclusive.'))
           else:
               arguments.append('/raster')

        if self.MULTIPLIER in parameters and parameters[self.MULTIPLIER] is not None:
            arguments.append('/multiplier:{}'.format(self.parameterAsDouble(parameters, self.MULTIPLIER, context)))

        arguments.append(self.parameterAsFile(parameters, self.INPUT, context))
        arguments.append(self.parameterAsOutputLayer(parameters, self.OUTPUT, context))

        fusionUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results

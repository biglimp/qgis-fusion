# -*- coding: utf-8 -*-

"""
***************************************************************************
    TopoMetrics.py
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
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterString,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils

class TopoMetrics(FusionAlgorithm):

    INPUT = 'INPUT'
    CELLSIZE ='CELLSIZE'
    POINTSPACING = 'POINTSPACING'
    LATITUDE = 'LATITUDE'
    WSIZE = 'WSIZE'
    OUTPUT = 'OUTPUT'
    SQUARE = 'SQUARE'
    VERSION64 = 'VERSION64'

    def name(self):
        return 'topometrics'

    def displayName(self):
        return self.tr('Topographic metrics')

    def group(self):
        return self.tr('Surface')

    def groupId(self):
        return 'surface'

    def tags(self):
        return [self.tr('lidar')]

    def shortHelpString(self):
        return '''TopoMetrics computes topographic metrics using surface models.
               The logic it uses is exactly the same as that used in GridMetrics except TopoMetrics computes a topographic position index (TPI) based on methods described by Weiss (2001) and Jenness (2006)'''

    def __init__(self):
        super().__init__()


    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     'Input PLANS DTM file',
                                                     QgsProcessingParameterFile.File,
                                                     'dtm'))
        self.addParameter(QgsProcessingParameterNumber(self.CELLSIZE,
                                                       self.tr('Size of the cell used to report topographic metrics'),
                                                       QgsProcessingParameterNumber.Double,
                                                       minValue=0,
                                                       defaultValue=10.0))
        self.addParameter(QgsProcessingParameterNumber(self.POINTSPACING,
                                                       self.tr('Point spacing'),
                                                       QgsProcessingParameterNumber.Double,
                                                       minValue = 0,
                                                       defaultValue = 1))
        self.addParameter(QgsProcessingParameterNumber(self.LATITUDE,
                                                       self.tr('Latitude of the data area (used to compute the solar radiation index)'),
                                                       QgsProcessingParameterNumber.Integer,
                                                       minValue=-90,
                                                       maxValue=90,
                                                       defaultValue=0.0))
        self.addParameter(QgsProcessingParameterNumber(self.WSIZE,
                                                       self.tr('The size of the window used to compute the Topographic Position Index'),
                                                       QgsProcessingParameterNumber.Integer,
                                                       minValue=0,
                                                       defaultValue=10.0))
        self.addParameter(QgsProcessingParameterBoolean(self.SQUARE,
                                                        self.tr('Use a square-shaped mask when computing the TPI'),
                                                        defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(self.VERSION64,
                                                        self.tr('Use 64-bit version'),
                                                        defaultValue=True))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output file with tabular metric information'),
                                                                self.tr('CSV files (*.csv *.CSV)')))

        self.addAdvancedModifiers()

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        if self.VERSION64 in parameters and parameters[self.VERSION64]:
            arguments.append('"' + os.path.join(fusionUtils.fusionDirectory(), 'TopoMetrics64.exe') + '"')
        else:
            arguments.append('"' + os.path.join(fusionUtils.fusionDirectory(), 'TopoMetrics.exe') + '"')

        if self.SQUARE in parameters and parameters[self.SQUARE]:
            arguments.append('/square')

        self.addAdvancedModifiersToCommands(arguments, parameters, context)

        arguments.append(self.parameterAsFile(parameters, self.INPUT, context))
        arguments.append(str(self.parameterAsDouble(parameters, self.CELLSIZE, context)))
        arguments.append(str(self.parameterAsDouble(parameters, self.POINTSPACING, context)))
        arguments.append(str(self.parameterAsInt(parameters, self.LATITUDE, context)))
        arguments.append(str(self.parameterAsInt(parameters, self.WSIZE, context)))

        arguments.append(self.parameterAsFileOutput(parameters, self.OUTPUT, context))       

        fusionUtils.execute(arguments, feedback)

        return self.prepareReturn(parameters)

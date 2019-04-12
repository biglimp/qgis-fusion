# -*- coding: utf-8 -*-

"""
***************************************************************************
    xyz2dtm.py
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

from qgis.core import (QgsProcessing,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterFileDestination
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils


class xyz2dtm(FusionAlgorithm):

    INPUT = 'INPUT'
    XYUNITS = 'XYUNITS'
    ZUNITS = 'ZUNITS'
    COORDSYS = 'COORDSYS'
    ZONE = 'ZONE'
    HDATUM = 'HDATUM'
    VDATUM = 'VDATUM'
    FILL_HOLES = 'FILL_HOLES'
    OUTPUT = 'OUTPUT'

    def name(self):
        return 'xyz2dtm'

    def displayName(self):
        return self.tr('XYZ to DTM')

    def group(self):
        return self.tr('Conversion')

    def groupId(self):
        return 'conversion'

    def tags(self):
        return self.tr('lidar,xyz,dtm,convert').split(',')

    def shortHelpString(self):
        return self.tr('Converts surface models stored as ACSII XYZ '
                       'point files into the PLANS DTM format.')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.units = ((self.tr('Meters'), 'm'),
                      (self.tr('Feet'), 'f'))

        self.csystems = ((self.tr('Unknown'), '0'),
                         (self.tr('UTM'), '1'),
                         (self.tr('State plane'), '2'))

        self.hdatums = ((self.tr('Unknown'), '0'),
                        (self.tr('NAD27'), '1'),
                        (self.tr('NAD83'), '2'))

        self.vdatums = ((self.tr('Unknown'), '0'),
                        (self.tr('NGVD29'), '1'),
                        (self.tr('NAVD88'), '2'),
                        (self.tr('GRS80'), '3'))

        self.addParameter(QgsProcessingParameterMultipleLayers(self.INPUT,
                                                               self.tr('XYZ files'),
                                                               QgsProcessing.TypeFile))
        self.addParameter(QgsProcessingParameterEnum(self.XYUNITS,
                                                     self.tr('Units for LIDAR data XY'),
                                                     options=[i[0] for i in self.units],
                                                     defaultValue=0))
        self.addParameter(QgsProcessingParameterEnum(self.ZUNITS,
                                                     self.tr('Units for LIDAR data elevations'),
                                                     options=[i[0] for i in self.units],
                                                     defaultValue=0))
        self.addParameter(QgsProcessingParameterEnum(self.COORDSYS,
                                                     self.tr('Coordinate system'),
                                                     options=[i[0] for i in self.csystems],
                                                     defaultValue=0))
        self.addParameter(QgsProcessingParameterNumber(self.ZONE,
                                                       self.tr('Coordinate system zone (0 for unknown)'),
                                                       QgsProcessingParameterNumber.Integer,
                                                       minValue=0,
                                                       maxValue=60,
                                                       defaultValue=0))
        self.addParameter(QgsProcessingParameterEnum(self.HDATUM,
                                                     self.tr('Horizontal datum'),
                                                     options=[i[0] for i in self.hdatums],
                                                     defaultValue=0))
        self.addParameter(QgsProcessingParameterEnum(self.VDATUM,
                                                     self.tr('Vertical datum'),
                                                     options=[i[0] for i in self.vdatums],
                                                     defaultValue=0))
        params = []
        params.append(QgsProcessingParameterNumber(self.FILL_HOLES,
                                                   self.tr('Fill holes with specified size'),
                                                   QgsProcessingParameterNumber.Integer,
                                                   defaultValue=None,
                                                   optional=True))

        for p in params:
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output'),
                                                                self.tr('DTM files (*.dtm *.DTM)')))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        arguments.append(os.path.join(fusionUtils.fusionDirectory(), self.name()))

        if self.FILL_HOLES in parameters and parameters[self.FILL_HOLES] is not None:
            arguments.append('/fillholes:{}'.format(self.parameterAsInt(parameters, self.FILL_HOLES, context)))

        arguments.append(self.parameterAsFileOutput(parameters, self.OUTPUT, context))
        arguments.append(self.units[self.parameterAsEnum(parameters, self.XYUNITS, context)][1])
        arguments.append(self.units[self.parameterAsEnum(parameters, self.ZUNITS, context)][1])
        arguments.append(self.csystems[self.parameterAsEnum(parameters, self.COORDSYS, context)][1])
        arguments.append(str(self.parameterAsInt(parameters, self.ZONE, context)))
        arguments.append(self.hdatums[self.parameterAsEnum(parameters, self.HDATUM, context)][1])
        arguments.append(self.vdatums[self.parameterAsEnum(parameters, self.VDATUM, context)][1])

        fileList = fusionUtils.layersToFile('xyzDataFiles.txt', self, parameters, self.INPUT, context)
        arguments.append(fileList)

        fusionUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results

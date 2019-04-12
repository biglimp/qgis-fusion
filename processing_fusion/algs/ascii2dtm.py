# -*- coding: utf-8 -*-

"""
***************************************************************************
    ascii2dtm.py
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
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFileDestination
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils


class ascii2dtm(FusionAlgorithm):

    INPUT = 'INPUT'
    XYUNITS = 'XYUNITS'
    ZUNITS = 'ZUNITS'
    COORDSYS = 'COORDSYS'
    ZONE = 'ZONE'
    HDATUM = 'HDATUM'
    VDATUM = 'VDATUM'
    MULTIPLIER = 'MULTIPLIER'
    OFFSET = 'OFFSET'
    NAN = 'NAN'
    OUTPUT = 'OUTPUT'

    def name(self):
        return 'ascii2dtm'

    def displayName(self):
        return self.tr('ASCII to DTM')

    def group(self):
        return self.tr('Conversion')

    def groupId(self):
        return 'conversion'

    def tags(self):
        return self.tr('lidar,ascii,dtm,convert').split(',')

    def shortHelpString(self):
        return self.tr('Converts an ASCII raster surface model into '
                       'the PLANS format used by FUSION.')

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

        self.addParameter(QgsProcessingParameterRasterLayer(self.INPUT,
                                                            self.tr('Surface raster')))
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
        params.append(QgsProcessingParameterNumber(self.MULTIPLIER,
                                                   self.tr('Multiply all data values by the constant'),
                                                   QgsProcessingParameterNumber.Double,
                                                   defaultValue=None,
                                                   optional=True))
        params.append(QgsProcessingParameterNumber(self.OFFSET,
                                                   self.tr('Add the constant to all data values'),
                                                   QgsProcessingParameterNumber.Double,
                                                   defaultValue=None,
                                                   optional=True))
        params.append(QgsProcessingParameterBoolean(self.NAN,
                                                    self.tr('Use more robust (but slower) logic for parsing NAN values'),
                                                    defaultValue=None,
                                                    optional=True))

        for p in params:
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output'),
                                                                self.tr('DTM files (*.dtm *.DTM)')))

    def processAlgorithm(self, parameters, context, feedback):
        inLayer = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        if inLayer is None:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.INPUT))

        arguments = []
        arguments.append(os.path.join(fusionUtils.fusionDirectory(), self.name()))

        if self.MULTIPLIER in parameters and parameters[self.MULTIPLIER] is not None:
            arguments.append('/multiplier:{}'.format(self.parameterAsDouble(parameters, self.MULTIPLIER, context)))

        if self.OFFSET in parameters and parameters[self.OFFSET] is not None:
            arguments.append('/offset:{}'.format(self.parameterAsDouble(parameters, self.OFFSET, context)))

        if self.NAN in parameters and parameters[self.NAN]:
            arguments.append('/nan')

        arguments.append(self.parameterAsFileOutput(parameters, self.OUTPUT, context))
        arguments.append(self.units[self.parameterAsEnum(parameters, self.XYUNITS, context)][1])
        arguments.append(self.units[self.parameterAsEnum(parameters, self.ZUNITS, context)][1])
        arguments.append(self.csystems[self.parameterAsEnum(parameters, self.COORDSYS, context)][1])
        arguments.append(str(self.parameterAsInt(parameters, self.ZONE, context)))
        arguments.append(self.hdatums[self.parameterAsEnum(parameters, self.HDATUM, context)][1])
        arguments.append(self.vdatums[self.parameterAsEnum(parameters, self.VDATUM, context)][1])
        arguments.append(inLayer.source())

        fusionUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results

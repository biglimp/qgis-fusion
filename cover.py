# -*- coding: utf-8 -*-

"""
***************************************************************************
    Cover.py
    ---------------------
    Date                 : November 2016
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
__date__ = 'November 2016'
__copyright__ = "(C) 2016 by Niccolo' Marchi"

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.core import (QgsProcessing,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterString
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils


class Cover(FusionAlgorithm):

    INPUT = 'INPUT'
    XYUNITS = 'XYUNITS'
    ZUNITS = 'ZUNITS'
    COORDSYS = 'COORDSYS'
    ZONE = 'ZONE'
    HDATUM = 'HDATUM'
    VDATUM = 'VDATUM'
    GROUND = 'GROUND'
    CELLSIZE ='CELLSIZE'
    HEIGHTBREAK = 'HEIGHTBREAK'
    ALL = 'ALL'
    IGNOREOVERLAP = 'IGNOREOVERLAP'
    CLASS = 'CLASS'
    PENETRATION = 'PENETRATION'
    UPPER = 'UPPER'
    VERSION64 = 'VERSION64'
    OUTPUT = 'OUTPUT'

    def name(self):
        return 'cover'

    def displayName(self):
        return self.tr('Cover')

    def group(self):
        return self.tr('Point cloud analysis')

    def groupId(self):
        return 'points'

    def tags(self):
        return self.tr('lidar,cover').split(',')

    def shortHelpString(self):
        return self.tr('Computes estimates of canopy closure using a grid')

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

        # self.addParameter(QgsProcessingParameterMultipleLayers(self.INPUT,
                                                               # self.tr('LAS files'),
                                                               # QgsProcessing.TypeFile))
        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     self.tr('Input LAS layer'),
                                                     fileFilter = '(*.las *.laz)'))
        self.addParameter(QgsProcessingParameterFile(self.GROUND,
                                                     self.tr('Ground file for height normalization'),
                                                     extension = 'dtm'))
        self.addParameter(QgsProcessingParameterNumber(self.CELLSIZE,
                                                       self.tr('Cellsize'),
                                                       QgsProcessingParameterNumber.Double,
                                                       minValue=0,
                                                       defaultValue=10.0))
        self.addParameter(QgsProcessingParameterNumber(self.HEIGHTBREAK,
                                                       self.tr('Slice thickness'),
                                                       QgsProcessingParameterNumber.Double,
                                                       minValue = 0,
                                                       defaultValue = 1))
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
        params.append(QgsProcessingParameterBoolean(self.ALL,
                                                        self.tr('Use all returns (default is only first returns) '),
                                                        defaultValue=False,
                                                        optional = True))
        params.append(QgsProcessingParameterString(self.CLASS,
                                                   self.tr('Use only a specific LAS class'),
                                                   defaultValue='',
                                                   optional = True))
        params.append(QgsProcessingParameterBoolean(self.IGNOREOVERLAP,
                                                        self.tr('Ignore points with the overlap flag set'),
                                                        defaultValue=False,
                                                        optional = True))
        params.append(QgsProcessingParameterBoolean(self.PENETRATION,
                                                        self.tr('Compute penetration rate'),
                                                        defaultValue=False,
                                                        optional = True))
        params.append(QgsProcessingParameterNumber(self.UPPER,
                                                       self.tr('Set an upperlimit for cover calculation'),
                                                       QgsProcessingParameterNumber.Integer,
                                                       minValue = 0,
                                                       defaultValue=0,
                                                       optional = True))

        for p in params:
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)

        self.addParameter(QgsProcessingParameterBoolean(self.VERSION64,
                                                        self.tr('Use 64-bit version'),
                                                        defaultValue=True))

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output'),
                                                                self.tr('DTM files (*.dtm *.DTM)')))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        
        if self.VERSION64:
            arguments.append(os.path.join(fusionUtils.fusionDirectory(), 'Cover64.exe'))
        else:
            arguments.append(os.path.join(fusionUtils.fusionDirectory(), 'Cover.exe'))

        if self.ALL in parameters and parameters[self.ALL]:
            arguments.append('/all')
        if self.PENETRATION in parameters and parameters[self.PENETRATION]:
            arguments.append('/penetration')
        if self.IGNOREOVERLAP in parameters and parameters[self.IGNOREOVERLAP]:
            arguments.append('/ignoreoverlap')

        class_var = self.parameterAsString(parameters, self.CLASS, context).strip()
        if class_var:
            arguments.append('/class:' + class_var)

        if self.UPPER in parameters and parameters[self.UPPER] is not 0:
            arguments.append('/upper:{}'.format(self.parameterAsInt(parameters, self.UPPER, context)))

        arguments.append(self.parameterAsFile(parameters, self.GROUND, context))
        arguments.append(self.parameterAsFileOutput(parameters, self.OUTPUT, context))
        arguments.append(str(self.parameterAsDouble(parameters, self.HEIGHTBREAK, context)))
        arguments.append(str(self.parameterAsDouble(parameters, self.CELLSIZE, context)))
        arguments.append(self.units[self.parameterAsEnum(parameters, self.XYUNITS, context)][1])
        arguments.append(self.units[self.parameterAsEnum(parameters, self.ZUNITS, context)][1])
        arguments.append(self.csystems[self.parameterAsEnum(parameters, self.COORDSYS, context)][1])
        arguments.append(str(self.parameterAsInt(parameters, self.ZONE, context)))
        arguments.append(self.hdatums[self.parameterAsEnum(parameters, self.HDATUM, context)][1])
        arguments.append(self.vdatums[self.parameterAsEnum(parameters, self.VDATUM, context)][1])
        arguments.append(self.parameterAsFile(parameters, self.INPUT, context))# remove when method for multiple files is fixed

        # fileList = fusionUtils.layersToFile('DataFiles.txt', self, parameters, self.INPUT, context)
        # arguments.append(fileList)

        fusionUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results

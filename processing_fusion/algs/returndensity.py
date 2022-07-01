# -*- coding: utf-8 -*-

"""
***************************************************************************
    ReturnDensity.py
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
                       QgsProcessingParameterFile,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterString,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterFileDestination
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils



class ReturnDensity(FusionAlgorithm):

    INPUT = 'INPUT'
    CELLSIZE = 'CELLSIZE'
    FIRST = 'FIRST'
    ASCII = 'ASCII'
    CLASS = 'CLASS'
    VERSION64 = 'VERSION64'
    OUTPUT = 'OUTPUT'

    def name(self):
        return 'returndensity'

    def displayName(self):
        return self.tr("Return Density")

    def group(self):
        return self.tr('Point cloud analysis')

    def groupId(self):
        return 'points'

    def tags(self):
        return [self.tr('lidar')]

    def shortHelpString(self):
        return self.tr('Returns a raster with the point density')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     self.tr('Input LAS layer'),
                                                     optional=False))

        self.addParameter(QgsProcessingParameterNumber(self.CELLSIZE,
                                                       self.tr('Cellsize'),
                                                       QgsProcessingParameterNumber.Double,
                                                       minValue=0,
                                                       defaultValue=10.0))

        self.addParameter(QgsProcessingParameterBoolean(self.VERSION64,
                                                        self.tr('Use 64-bit version'),
                                                        defaultValue=True))

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output surface'),
                                                                self.tr('DTM files (*.dtm *.DTM)')))

        params = []
        
        params.append(QgsProcessingParameterBoolean(self.FIRST,
                                                    self.tr('Use only first returns when computing return counts'),
                                                    defaultValue=False,
                                                    optional=True))
        params.append(QgsProcessingParameterBoolean(self.ASCII,
                                                    self.tr('Output raster data in ASCII raster format instead of PLANS DTM format'),
                                                    defaultValue=False,
                                                    optional=True))
        params.append(QgsProcessingParameterString(self.CLASS,
                                                   self.tr('Use only a specific LAS class'),
                                                   defaultValue=None,
                                                   optional=True))

        for p in params:
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)
        

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []

        if self.VERSION64:
            arguments.append('"' + os.path.join(fusionUtils.fusionDirectory(), 'ReturnDensity64.exe') + '"')
        else:
            arguments.append('"' + os.path.join(fusionUtils.fusionDirectory(), 'ReturnDensity.exe') + '"')

        if self.FIRST in parameters and parameters[self.FIRST]:
            arguments.append('/first')
        if self.ASCII in parameters and parameters[self.ASCII]:
            arguments.append('/ascii')

        class_var = self.parameterAsString(parameters, self.CLASS, context).strip()
        if class_var:
            arguments.append('/class:' + class_var)

        #self.addAdvancedModifiersToCommand(arguments)
        arguments.append(self.parameterAsFileOutput(parameters, self.OUTPUT, context))
        arguments.append(str(self.parameterAsInt(parameters, self.CELLSIZE, context)))
        self.addInputFilesToCommands(arguments, parameters, self.INPUT, context)
        #arguments.append(self.parameterAsFile(parameters, self.INPUT, context))

        fusionUtils.execute(arguments, feedback)

        return self.prepareReturn(parameters)

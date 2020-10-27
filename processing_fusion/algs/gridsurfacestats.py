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
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils

class GridSurfaceStats(FusionAlgorithm):

    def name(self):
        return 'gridsurfacestats'

    def displayName(self):
        return self.tr('Grid Surface Stats')

    def group(self):
        return self.tr('Surface')

    def groupId(self):
        return 'surface'

    def tags(self):
        return [self.tr('lidar')]

    def shortHelpString(self):
        return '''GridSurfaceStats computes the surface area and volume under a surface (or between
                the surface and a ground surface). When used with a canopy height or surface model, it
                provides information useful for describing canopy surface roughness and the volume
                occupied by tree canopies.'''

    def __init__(self):
        super().__init__()

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    SAMPLEFACTOR = 'SAMPLEFACTOR'
    SVONLY = 'SVONLY'
    DTM = 'DTM'
    ASCII = 'ASCII'
    AREA = 'AREA'
    VERSION64 = 'VERSION64'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     'Input PLANS DTM file',
                                                     QgsProcessingParameterFile.File,
                                                     'dtm'))
        self.addParameter(QgsProcessingParameterNumber(self.SAMPLEFACTOR,
                                                       self.tr('Multiplier for outputfile cell size'),
                                                       QgsProcessingParameterNumber.Integer,
                                                       minValue = 0,
                                                       defaultValue=3))
        self.addParameter(QgsProcessingParameterBoolean(self.ASCII,
                                                        self.tr('Output raster data in ASCII raster format instead of PLANS DTM format'),
                                                        defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(self.VERSION64,
                                                        self.tr('Use 64-bit version'),
                                                        defaultValue=True))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output surface'),
                                                                self.tr('DTM files (*.dtm *.DTM)')))


        params = []
        params.append(QgsProcessingParameterFile(self.DTM,
                                                 self.tr('Ground file for height normalization'),
                                                 optional = True,
                                                 extension = 'dtm'))
        params.append(QgsProcessingParameterBoolean(self.AREA,
                                                    self.tr('Compute the surface area of inputfile instead of the surface area divided by the flat cell area'),
                                                    defaultValue=False,
                                                    optional = True))
        params.append(QgsProcessingParameterBoolean(self.SVONLY,
                                                        self.tr('Output only the surface volume metric layer'),
                                                        defaultValue=False,
                                                        optional = True))

        for p in params:
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)

        self.addAdvancedModifiers()

    def processAlgorithm(self, parameters, context, feedback):
        version64 = self.parameterAsBool(parameters, self.VERSION64, context)
        if version64:
            arguments = [os.path.join(fusionUtils.fusionDirectory(), 'GridSurfaceStats64.exe')]
        else:
            arguments = [os.path.join(fusionUtils.fusionDirectory(), 'GridSurfaceStats.exe')]
                   
        dtm = self.parameterAsString(parameters, self.DTM, context)
        if dtm:
            arguments.append('/ground:' + dtm)
        if self.AREA in parameters and parameters[self.AREA]:
            arguments.append('/area')
        if self.ASCII in parameters and parameters[self.ASCII]:
            arguments.append('/ascii')
        if self.SVONLY in parameters and parameters[self.SVONLY]:
            arguments.append('/svonly')

        self.addAdvancedModifiersToCommands(arguments, parameters, context)
        
        self.addInputFilesToCommands(arguments, parameters, self.INPUT, context)        
        
        outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        arguments.append('"%s"' % outputFile)

        arguments.append(self.parameterAsInt(parameters, self.SAMPLEFACTOR, context))
        
        fusionUtils.execute(arguments, feedback)

        return self.prepareReturn(parameters)

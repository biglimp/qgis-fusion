# -*- coding: utf-8 -*-

"""
***************************************************************************
    DensityMetrics.py
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

class DensityMetrics(FusionAlgorithm):

    INPUT = 'INPUT'
    GROUND = 'GROUND'
    CELLSIZE ='CELLSIZE'
    OUTPUT = 'OUTPUT'
    SLICETHICKNESS = 'SLICETHICKNESS'
    NOCSV = 'NOCSV'
    FIRST = 'FIRST'
    IGNOREOVERLAP = 'IGNOREOVERLAP'
    CLASS = 'CLASS'
    VERSION64 = 'VERSION64'

    def name(self):
        return 'densitymetrics'

    def displayName(self):
        return self.tr('Density metrics')

    def group(self):
        return self.tr('Point cloud analysis')

    def groupId(self):
        return 'points'

    def tags(self):
        return [self.tr('lidar')]

    def shortHelpString(self):
        return 'Computes point density metrics using elevation-based slices'

    def __init__(self):
        super().__init__()


    def initAlgorithm(self, config=None):
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
        self.addParameter(QgsProcessingParameterNumber(self.SLICETHICKNESS,
                                                       self.tr('Slice thickness'),
                                                       QgsProcessingParameterNumber.Double,
                                                       minValue = 0,
                                                       defaultValue = 1))
        self.addParameter(QgsProcessingParameterBoolean(self.NOCSV,
                                                        self.tr('Do not create a CSV output file for cell metrics'),
                                                        defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(self.FIRST,
                                                        self.tr('Use only first returns'),
                                                        defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(self.VERSION64,
                                                        self.tr('Use 64-bit version'),
                                                        defaultValue=True))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Base name for output files')))

        params = []
        params.append(QgsProcessingParameterBoolean(self.IGNOREOVERLAP,
                                                        self.tr('Ignore points with the overlap flag set '),
                                                        defaultValue=False,
                                                        optional = True))
        params.append(QgsProcessingParameterString(self.CLASS,
                                                   self.tr('Use only a specific LAS class'),
                                                   defaultValue='',
                                                   optional = True))

        for p in params:
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)

        self.addAdvancedModifiers()

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []
        if self.VERSION64 in parameters and parameters[self.VERSION64]:
            arguments.append(os.path.join(fusionUtils.fusionDirectory(), 'DensityMetrics64.exe'))
        else:
            arguments.append(os.path.join(fusionUtils.fusionDirectory(), 'DensityMetrics.exe'))

        if self.FIRST in parameters and parameters[self.FIRST]:
            arguments.append('/first')
        if self.NOCSV in parameters and parameters[self.NOCSV]:
            arguments.append('/nocsv')
        if self.IGNOREOVERLAP in parameters and parameters[self.IGNOREOVERLAP]:
            arguments.append('/ignoreoverlap')

        class_var = self.parameterAsString(parameters, self.CLASS, context).strip()
        if class_var:
            arguments.append('/class:' + class_var)
        self.addAdvancedModifiersToCommands(arguments, parameters, context)

        arguments.append(self.parameterAsFile(parameters, self.GROUND, context))
        arguments.append(str(self.parameterAsDouble(parameters, self.CELLSIZE, context)))
        arguments.append(str(self.parameterAsDouble(parameters, self.SLICETHICKNESS, context)))
        
        arguments.append(self.parameterAsFileOutput(parameters, self.OUTPUT, context))

        arguments.append(self.parameterAsFile(parameters, self.INPUT, context))

        # arguments.append('outlier')
        # arguments.append(str(self.parameterAsDouble(parameters, self.VALUE, context)))
        # arguments.append(str(self.parameterAsDouble(parameters, self.WINDOWSIZE, context)))

        # outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        # arguments.append('"%s"' % outputFile)

        # self.addInputFilesToCommands(arguments, parameters, self.INPUT, context)        

        fusionUtils.execute(arguments, feedback)

        return self.prepareReturn(parameters)

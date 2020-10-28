# -*- coding: utf-8 -*-

"""
***************************************************************************
    GridMetrics.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
    ---------------------
    Date                 : June 2014
    Copyright            : (C) 2014 by Agresta S. Coop.
    Email                : iescamochero at agresta dot org
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Victor Olaya'
__date__ = 'August 2012'
__copyright__ = '(C) 2012, Victor Olaya'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

import os
from qgis.core import (QgsProcessingException,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterString,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils


class GridMetrics(FusionAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    GROUND = 'GROUND'
    HEIGHT = 'HEIGHT'
    CELLSIZE = 'CELLSIZE'
    OUTLIER = 'OUTLIER'
    FIRST = 'FIRST'
    NOINTENSITY = 'NOINTENSITY'
    FUEL = 'FUEL'
    IGNOREOVERLAP = 'IGNOREOVERLAP'
    ASCII = 'ASCII'
    HTMIN = 'HTMIN'
    CLASS = 'CLASS'
    VERSION64 = 'VERSION64'

    def name(self):
        return 'gridmetrics'

    def displayName(self):
        return self.tr('Grid metrics')

    def group(self):
        return self.tr('Point cloud analysis')

    def groupId(self):
        return 'points'

    def tags(self):
        return [self.tr('lidar')]

    def shortHelpString(self):
        return '''GridMetrics computes a series of descriptive statistics for a LIDAR data set using both elevation and intensity.
        GridMetrics can apply the fuel models developed to predict canopy fuel characteristics in Douglas-fir forest type in Western Washington (Andersen, et al. 2005).
        Application of the fuel models to other stand types or geographic regions may produce questionable results.'''

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     self.tr('Input LAS layer'),
                                                     fileFilter = '(*.las *.laz)'))
        self.addParameter(QgsProcessingParameterFile(self.GROUND,
                                                     self.tr('Input ground DTM file'),
                                                     extension = 'dtm'))
        self.addParameter(QgsProcessingParameterNumber(self.HEIGHT,
                                                       self.tr('Height break'),
                                                       QgsProcessingParameterNumber.Double,
                                                       minValue=0,
                                                       defaultValue=10.0))
        self.addParameter(QgsProcessingParameterNumber(self.CELLSIZE,
                                                       self.tr('Cell size'),
                                                       QgsProcessingParameterNumber.Double,
                                                       minValue=0,
                                                       defaultValue=10.0))
        self.addParameter(QgsProcessingParameterBoolean(self.ASCII,
                                                        self.tr('Output raster data in ASCII raster format instead of PLANS DTM format'),
                                                        defaultValue=False))
        self.addParameter(QgsProcessingParameterBoolean(self.VERSION64,
                                                        self.tr('Use 64-bit version'),
                                                        defaultValue = True))

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output table with grid metrics'),
                                                                self.tr('CSV files (*.csv *.CSV)')))


        params = []
        params.append(QgsProcessingParameterString(self.OUTLIER,
                                                   self.tr('Outlier:low,high'),
                                                   defaultValue='',
                                                   optional = True))
        params.append(QgsProcessingParameterString(self.HTMIN,
                                                   self.tr('Htmin'),
                                                   defaultValue='',
                                                   optional = True))
        params.append(QgsProcessingParameterBoolean(self.FIRST,
                                                    self.tr('First'),
                                                    defaultValue=False,
                                                    optional = True))
        params.append(QgsProcessingParameterBoolean(self.NOINTENSITY,
                                                    self.tr('Do not compute metrics using intensity values '),
                                                    defaultValue=False,
                                                    optional = True))
        params.append(QgsProcessingParameterBoolean(self.FUEL,
                                                        self.tr('Apply fuel parameter models (cannot be used with /first switch) '),
                                                        defaultValue=False,
                                                        optional = True))
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
        version64 = self.parameterAsBool(parameters, self.VERSION64, context)
        if version64:
            arguments = [os.path.join(fusionUtils.fusionDirectory(), 'GridMetrics64.exe')]
        else:
            arguments = [os.path.join(fusionUtils.fusionDirectory(), 'GridMetrics.exe')]

        self.addAdvancedModifiersToCommands(arguments, parameters, context)

        outlier = self.parameterAsString(parameters, self.OUTLIER, context).strip()
        if outlier:
            arguments.append('/outlier:' + outlier)

        if self.FIRST in parameters and parameters[self.FIRST]:
            arguments.append('/first')
        if self.NOINTENSITY in parameters and parameters[self.NOINTENSITY]:
            arguments.append('/nointensity')
        if self.FUEL in parameters and parameters[self.FUEL]:
            arguments.append('/fuel')
        if self.ASCII in parameters and parameters[self.ASCII]:
            arguments.append('/ascii')
        if self.IGNOREOVERLAP in parameters and parameters[self.IGNOREOVERLAP]:
            arguments.append('/ignoreoverlap')
        htmin = self.parameterAsString(parameters, self.HTMIN, context).strip()
        if htmin:
            arguments.append('/minht:' + htmin)
        class_var = self.parameterAsString(parameters, self.CLASS, context).strip()
        if class_var:
            arguments.append('/class:' + class_var)
        arguments.append(self.parameterAsString(parameters, self.GROUND, context))
        arguments.append(str(self.parameterAsDouble(parameters, self.HEIGHT, context)))
        arguments.append(str(self.parameterAsDouble(parameters, self.CELLSIZE, context)))
        arguments.append('"%s"' % self.parameterAsFileOutput(parameters, self.OUTPUT, context))
        self.addInputFilesToCommands(arguments, parameters, self.INPUT, context) 

        fusionUtils.execute(arguments, feedback)

        return self.prepareReturn(parameters)

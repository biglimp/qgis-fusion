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
    OUTPUT_CSV_ELEVATION = 'OUTPUT_CSV_ELEVATION'
    OUTPUT_CSV_INTENSITY = 'OUTPUT_CSV_INTENSITY'
    OUTPUT_TXT_ELEVATION = 'OUTPUT_TXT_ELEVATION'
    OUTPUT_TXT_INTENSITY = 'OUTPUT_TXT_INTENSITY'
    GROUND = 'GROUND'
    HEIGHT = 'HEIGHT'
    CELLSIZE = 'CELLSIZE'
    OUTLIER = 'OUTLIER'
    FIRST = 'FIRST'
    MINHT = 'MINHT'
    CLASS = 'CLASS'

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
        return ''

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, self.tr('Input LAS layer'), extension = 'las'))
        self.addParameter(QgsProcessingParameterFile(
            self.GROUND, self.tr('Input ground DTM file'), extension = 'dtm'))
        self.addParameter(QgsProcessingParameterNumber(
            self.HEIGHT, self.tr('Height break')))
        self.addParameter(QgsProcessingParameterNumber(
            self.CELLSIZE, self.tr('Cellsize')))

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT_CSV_ELEVATION,
                                                                self.tr('Output table with grid metrics'),
                                                                self.tr('CSV files (*.csv *.CSV)')))
        self.addOutput(OutputFile(
            self.OUTPUT_CSV_ELEVATION, self.tr('Output table with grid metrics')))

        outlier = QgsProcessingParameterString(
            self.OUTLIER, self.tr('Outlier:low,high'), '', optional = True)
        outlier.setFlags(outlier.flags() | QgsProcessingParameterDefinition.FlagAdvanced)        
        self.addParameter(outlier)
        
        htmin = QgsProcessingParameterString(
            self.HTMIN, self.tr('Htmin'), '', optional = True)
        htmin.setFlags(htmin.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(htmin)
        first = QgsProcessingParameterBoolean(
            self.FIRST, self.tr('First'), False)
        first.setFlags(first.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(first)

        class_var = QgsProcessingParameterString(
            self.CLASS, self.tr('Class'), '', optional = True)
        class_var.setFlags(class_var.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(class_var)


    def processAlgorithm(self, parameters, context, feedback):
        commands = [os.path.join(fusionUtils.fusionDirectory(), 'GridMetrics.exe')]
        outlier = self.parametersAsBool(parameters, self.OUTLIER, context).strip()
        if outlier:
            commands.append('/outlier:' + outlier)
        first = self.parametersAsBool(parameters, self.FIRST, context)
        if first:
            commands.append('/first')
        htmin = self.parameterAsString(parameters, self.HTMIN, context).strip()
        if htmin:
            commands.append('/minht:' + htmin)
        class_var = self.parameterAsString(parameters, self.CLASS, context).strip()
        if class_var:
            commands.append('/class:' + class_var)
        commands.append(self.parameterAsString(parameters, self.GROUND, context))
        commands.append(str(self.parameterAsDouble(parameters, self.HEIGHT, context)))
        commands.append(str(self.parameterAsDouble(parameters, self.CELLSIZE, context)))
        commands.append('"%s"' % self.parameterAsFileOutput(parameters, self.OUTPUT_CSV_ELEVATION, context))
        self.addInputFilesToCommands(commands, parameters, self.INPUT, context) 

        fusionUtils.execute(commands, feedback)

        return self.prepareReturn(parameters)
        
        '''
        basePath = self.getOutputValue(self.OUTPUT_CSV_ELEVATION)
        basePath = os.path.join(os.path.dirname(basePath), os.path.splitext(os.path.basename(basePath))[0])
        self.setOutputValue(self.OUTPUT_CSV_ELEVATION, basePath + '_all_returns_elevation_stats.csv')
        self.setOutputValue(self.OUTPUT_CSV_INTENSITY, basePath + '_all_returns_intensity_stats.csv')
        self.setOutputValue(self.OUTPUT_TXT_ELEVATION, basePath + '_all_returns_elevation_stats_ascii_header.txt')
        self.setOutputValue(self.OUTPUT_TXT_INTENSITY, basePath + '_all_returns_intensity_stats_ascii_header.txt')
        '''

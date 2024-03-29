# -*- coding: utf-8 -*-

"""
***************************************************************************
    GridSurfaceCreate.py
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
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterString,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils


class GridSurfaceCreate(FusionAlgorithm):

    INPUT = 'INPUT'
    OUTPUT_DTM = 'OUTPUT_DTM'
    CELLSIZE = 'CELLSIZE'
    XYUNITS = 'XYUNITS'
    ZUNITS = 'ZUNITS'
    UNITS = ['Meter', 'Feet']
    SPIKE = 'SPIKE'
    MEDIAN = 'MEDIAN'
    SMOOTH = 'SMOOTH'
    SLOPE = 'SLOPE'
    MINIMUM = 'MINIMUM'
    CLASS = 'CLASS'
    VERSION64 = 'VERSION64'


    def name(self):
        return 'gridsurfacecreate'

    def displayName(self):
        return self.tr('Grid surface create')

    def group(self):
        return self.tr('Surface')

    def groupId(self):
        return 'surface'

    def tags(self):
        return [self.tr('lidar')]

    def shortHelpString(self):
        return 'Creates a gridded surface model using collections of random points. Individual cell elevations are calculated using the average elevation of all points within the cell.'

    def __init__(self):
        super().__init__()


    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, self.tr('Input LAS layer'),  fileFilter = '(*.las *.laz)'))
        self.addParameter(QgsProcessingParameterNumber(
            self.CELLSIZE, self.tr('Cellsize'), QgsProcessingParameterNumber.Double,
            minValue = 0, defaultValue = 10.0))
        self.addParameter(QgsProcessingParameterEnum(
            self.XYUNITS, self.tr('XY Units'), self.UNITS))
        self.addParameter(QgsProcessingParameterEnum(
            self.ZUNITS, self.tr('Z Units'), self.UNITS))
        self.addParameter(QgsProcessingParameterBoolean(self.VERSION64,
                                                        self.tr('Use 64-bit version'),
                                                        defaultValue=True))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT_DTM,
                                                                self.tr('Output surface'),
                                                                self.tr('DTM files (*.dtm *.DTM)')))
        spike = QgsProcessingParameterString(
            self.SPIKE, self.tr('Spike (set blank if not used)'), '', optional = True)
        spike.setFlags(spike.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(spike)

        median = QgsProcessingParameterString(
            self.MEDIAN, self.tr('Median'), '', optional = True)
        median.setFlags(median.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(median)
        smooth = QgsProcessingParameterString(
            self.SMOOTH, self.tr('Smooth'), '', optional = True)
        smooth.setFlags(smooth.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(smooth)
        minimum = QgsProcessingParameterString(
            self.MINIMUM, self.tr('Minimum'), '', optional = True)
        minimum.setFlags(minimum.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(minimum)
        class_var = QgsProcessingParameterString(
            self.CLASS, self.tr('Class(es)'), '', optional = True)
        class_var.setFlags(class_var.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(class_var)
        slope = QgsProcessingParameterString(self.SLOPE, self.tr('Slope'), optional = True)
        slope.setFlags(slope.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(slope)

        self.addAdvancedModifiers()

    def processAlgorithm(self, parameters, context, feedback):
        version64 = self.parameterAsBool(parameters, self.VERSION64, context)
        if version64:
            commands = ['"' + os.path.join(fusionUtils.fusionDirectory(), 'GridSurfaceCreate64.exe') + '"']
        else:
            commands = ['"' + os.path.join(fusionUtils.fusionDirectory(), 'GridSurfaceCreate.exe') + '"']
        spike = self.parameterAsString(parameters, self.SPIKE, context).strip()
        if spike:
            commands.append('/spike:' + spike)
        median = self.parameterAsString(parameters, self.MEDIAN, context).strip()
        if median:
            commands.append('/median:' + median)
        smooth= self.parameterAsString(parameters, self.SMOOTH, context).strip()
        if smooth:
            commands.append('/smooth:' + smooth)
        slope = self.parameterAsBool(parameters, self.SLOPE, context)
        if slope:
            commands.append('/slope')
        minimum = self.parameterAsBool(parameters, self.MINIMUM, context)
        if minimum:
            commands.append('/minimum:' + minimum) 
        class_var = self.parameterAsString(parameters, self.CLASS, context).strip()
        if class_var:
            commands.append('/class:' + class_var)

        self.addAdvancedModifiersToCommands(commands, parameters, context)
        
        outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT_DTM, context)
        commands.append('"%s"' % outputFile)
        commands.append(str(self.parameterAsDouble(parameters, self.CELLSIZE, context)))
        commands.append(self.UNITS[self.parameterAsEnum(parameters, self.XYUNITS, context)][0])
        commands.append(self.UNITS[self.parameterAsEnum(parameters, self.ZUNITS, context)][0])
        commands.append('0')
        commands.append('0')
        commands.append('0')
        commands.append('0')

        self.addInputFilesToCommands(commands, parameters, self.INPUT, context)        

        fusionUtils.execute(commands, feedback)

        return self.prepareReturn(parameters)

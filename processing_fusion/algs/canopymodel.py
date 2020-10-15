# -*- coding: utf-8 -*-

"""
***************************************************************************
    CanopyModel.py
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


class CanopyModel(FusionAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    CELLSIZE = 'CELLSIZE'
    XYUNITS = 'XYUNITS'
    ZUNITS = 'ZUNITS'
    UNITS = ['Meter', 'Feet']
    GROUND = 'GROUND'
    MEDIAN = 'MEDIAN'
    SMOOTH = 'SMOOTH'
    SLOPE = 'SLOPE'
    CLASS = 'CLASS'
    ASCII = 'ASCII'
    VERSION64 = 'VERSION64'

    def name(self):
        return 'canopymodel'

    def displayName(self):
        return self.tr('Canopy model')

    def group(self):
        return self.tr('Surface')

    def groupId(self):
        return 'surface'

    def tags(self):
        return [self.tr('lidar')]

    def shortHelpString(self):
        return ''

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
        self.addParameter(QgsProcessingParameterBoolean(
            self.VERSION64, self.tr('Use 64-bit version'), True))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output surface'),
                                                                self.tr('DTM files (*.dtm *.DTM)')))

        ground = QgsProcessingParameterFile(self.GROUND,
                                            self.tr('Input PLANS DTM ground model'),
                                            extension = 'dtm',
                                            optional = True)
        ground.setFlags(ground.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(ground)
        median = QgsProcessingParameterString(
            self.MEDIAN, self.tr('Size of the window for Median filter'), '', optional = True)
        median.setFlags(median.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(median)
        smooth = QgsProcessingParameterString(
            self.SMOOTH, self.tr('Size of the window for mean filter (Smooth)'), '', optional = True)
        smooth.setFlags(smooth.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(smooth)
        class_var = QgsProcessingParameterString(
            self.CLASS, self.tr('Class'), '', optional = True)
        class_var.setFlags(class_var.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(class_var)
        slope = QgsProcessingParameterBoolean(self.SLOPE, self.tr('Calculate slope'), False)
        slope.setFlags(slope.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(slope)
        self.addParameter(QgsProcessingParameterBoolean(
            self.ASCII, self.tr('Add an ASCII output'), False))
        self.addAdvancedModifiers()
        
        self.addParameter(QgsProcessingParameterBoolean(self.VERSION64,
                                                        self.tr('Use 64-bit version'),
                                                        defaultValue=True))

    def processAlgorithm(self, parameters, context, feedback):
        version64 = self.parameterAsBool(parameters, self.VERSION64, context)
        if version64:
            arguments = [os.path.join(fusionUtils.fusionDirectory(), 'CanopyModel64.exe')]
        else:
            arguments = [os.path.join(fusionUtils.fusionDirectory(), 'CanopyModel.exe')]
        arguments.append('/verbose')
        ground = self.parameterAsString(parameters, self.GROUND, context).strip()
        if ground:
            arguments.append('/ground:' + ground)
        median = self.parameterAsString(parameters, self.MEDIAN, context).strip()
        if median:
            arguments.append('/median:' + median)
        smooth= self.parameterAsString(parameters, self.SMOOTH, context).strip()
        if smooth:
            arguments.append('/smooth:' + smooth)
        slope = self.parameterAsBool(parameters, self.SLOPE, context)
        if slope:
            arguments.append('/slope') 
        class_var = self.parameterAsString(parameters, self.CLASS, context).strip()
        if class_var:
            arguments.append('/class:' + class_var)
        asciioutput = self.parameterAsBool(parameters, self.ASCII, context)
        if asciioutput:
            arguments.append('/ascii')
        
        self.addAdvancedModifiersToCommands(arguments, parameters, context)

        outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        arguments.append('"%s"' % outputFile)
        arguments.append(str(self.parameterAsDouble(parameters, self.CELLSIZE, context)))
        arguments.append(self.UNITS[self.parameterAsEnum(parameters, self.XYUNITS, context)][0])
        arguments.append(self.UNITS[self.parameterAsEnum(parameters, self.ZUNITS, context)][0])
        arguments.append('0')
        arguments.append('0')
        arguments.append('0')
        arguments.append('0')
        self.addInputFilesToCommands(arguments, parameters, self.INPUT, context)        

        fusionUtils.execute(arguments, feedback)

        return self.prepareReturn(parameters)

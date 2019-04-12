# -*- coding: utf-8 -*-

"""
***************************************************************************
    PolyClipData.py
    ---------------------
    Date                 : May 2014
    Copyright            : (C) 2014 by Niccolo' Marchi
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
__date__ = 'May 2014'
__copyright__ = "(C) 2014 by Niccolo' Marchi"

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


class PolyClipData(FusionAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    SHAPE = 'SHAPE'
    MASK = 'MASK'
    FIELD = 'FIELD'
    VALUE = 'VALUE'

    def name(self):
        return 'pollyclipdata'

    def displayName(self):
        return self.tr('Poly clip data')

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
        self.addParameter(QgsProcessingParameterFile(self.MASK, self.tr('Mask layer'),
            extension = self.tr('Shapefile files (*.shp *.SHP)')))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output clipped LAS file'),
                                                                self.tr('LAS files (*.las *.LAS)')))
        self.addParameter(QgsProcessingParameterBoolean(self.SHAPE,
                                           self.tr('Use Shape attribute'), False))
        ##  'field' e 'value' box should appear or get activated if Shape attribute is switched ON
        self.addParameter(QgsProcessingParameterString(self.FIELD,
                                          self.tr('Shape field index')))
        self.addParameter(QgsProcessingParameterString(self.VALUE, self.tr("Shape value")))
        self.addAdvancedModifiers()

    def processAlgorithm(self, parameters, context, feedback):
        commands = [os.path.join(fusionUtils.fusionDirectory(), 'PolyClipData.exe')]
        if self.parameterAsBool(parameters, self.SHAPE, context):
            commands.append('/shape:' + self.parameterAsString(parameters, self.FIELD, context) + ','
                            + self.parameterAsString(parameters, self.VALUE, context))
        self.addAdvancedModifiersToCommands(commands, parameters, context)
        commands.append(self.parameterAsString(parameters, self.MASK, context))
        
        outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        commands.append('"%s"' % outputFile)
        self.addInputFilesToCommands(commands, parameters, self.INPUT, context)        
          
        fusionUtils.execute(commands, feedback)

        return self.prepareReturn(parameters)
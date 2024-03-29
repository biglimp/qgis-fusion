# -*- coding: utf-8 -*-

"""
***************************************************************************
    FilterData.py
    ---------------------
    Date                 : August 2012
    Copyright            : (C) 2012 by Victor Olaya
    Email                : volayaf at gmail dot com
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
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils

class FilterData(FusionAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    VALUE = 'VALUE'
    SHAPE = 'SHAPE'
    WINDOWSIZE = 'WINDOWSIZE'
    VERSION64 = 'VERSION64'

    def name(self):
        return 'filterdata'

    def displayName(self):
        return self.tr('Filter data outliers')

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
            self.INPUT, self.tr('Input LAS layer'),  fileFilter = '(*.las *.laz)'))
        self.addParameter(QgsProcessingParameterNumber(
            self.VALUE, self.tr('Standard Deviation multiplier'), 
            QgsProcessingParameterNumber.Double,
            defaultValue = 1))
        self.addParameter(QgsProcessingParameterNumber(
            self.WINDOWSIZE, self.tr('Window size'), 
            QgsProcessingParameterNumber.Double, 
            defaultValue = 10))
        self.addParameter(QgsProcessingParameterBoolean(self.VERSION64,
                                                        self.tr('Use 64-bit version'),
                                                        defaultValue=True))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output filtered LAS file'),
                                                                self.tr('LAS files (*.las *.LAS)')))
        self.addAdvancedModifiers()

    def processAlgorithm(self, parameters, context, feedback):
        version64 = self.parameterAsBool(parameters, self.VERSION64, context)
        if version64:
            arguments = ['"' + os.path.join(fusionUtils.fusionDirectory(), 'FilterData64.exe') + '"']
        else:
            arguments = ['"' + os.path.join(fusionUtils.fusionDirectory(), 'FilterData.exe') + '"']
        self.addAdvancedModifiersToCommands(arguments, parameters, context)
        arguments.append('outlier')
        arguments.append(str(self.parameterAsDouble(parameters, self.VALUE, context)))
        arguments.append(str(self.parameterAsDouble(parameters, self.WINDOWSIZE, context)))

        outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        arguments.append('"%s"' % outputFile)

        self.addInputFilesToCommands(arguments, parameters, self.INPUT, context)        

        fusionUtils.execute(arguments, feedback)

        return self.prepareReturn(parameters)

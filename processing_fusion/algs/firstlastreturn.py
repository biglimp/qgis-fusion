# -*- coding: utf-8 -*-

"""
***************************************************************************
    FirstLastReturn.py
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
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils

class FirstLastReturn(FusionAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    SWITCH = 'SWITCH'

    def name(self):
        return 'firstlastreturn'

    def displayName(self):
        return self.tr('First & last return')

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
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output')))
        self.addParameter(QgsProcessingParameterBoolean(
            self.SWITCH, self.tr('Use LAS info'), True))
        self.addAdvancedModifiers()

    def processAlgorithm(self, parameters, context, feedback):
        commands = [os.path.join(fusionUtils.fusionDirectory(), 'FirstLastReturn.exe')]
        if self.parameterAsBool(parameters, self.SWITCH, context):
            commands.append('/uselas')        
        outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        commands.append('"%s"' % outputFile)
        self.addInputFilesToCommands(commands, parameters, self.INPUT, context)        

        fusionUtils.execute(commands, feedback)

        return self.prepareReturn(parameters)


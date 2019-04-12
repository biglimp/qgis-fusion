# -*- coding: utf-8 -*-

"""
***************************************************************************
    Catalog.py
    ---------------------
    Date                 : June 2014
    Copyright            : (C) 2014 by Agresta S. Coop
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

__author__ = 'Agresta S. Coop - www.agresta.org'
__date__ = 'June 2014'
__copyright__ = '(C) 2014, Agresta S. Coop'
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


class Catalog(FusionAlgorithm):

    def name(self):
        return 'catalog'

    def displayName(self):
        return self.tr('Catalog')

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

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    DENSITY = 'DENSITY'
    FIRSTDENSITY = 'FIRSTDENSITY'
    INTENSITY = 'INTENSITY'

    def initAlgorithm(self, config=None):

        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, self.tr('Input LAS layer'), extension = 'las'))        
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output')))

        density = QgsProcessingParameterString(
            self.DENSITY, self.tr('Density - area, min, max (set blank if not used)'), '', optional = True)
        density.setFlags(density.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(density)

        first = QgsProcessingParameterString(
            self.FIRSTDENSITY, self.tr('First density - area, min, max (set blank if not used)'), '', optional = True)
        first.setFlags(first.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(first)

        intensity = QgsProcessingParameterString(
            self.INTENSITY, self.tr('Intensity - area, min, max (set blank if not used)'), '', optional = True)
        intensity.setFlags(intensity.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(intensity)
        
        self.addAdvancedModifiers()

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output'),
                                                                'las'))

    def processAlgorithm(self, parameters, context, feedback):
        commands = [os.path.join(fusionUtils.fusionDirectory(), 'Catalog.exe')]

        intensity = self.parameterAsString(parameters, self.INTENSITY, context).strip()
        if intensity:
            commands.append('/intensity:' + intensity)
        density = self.parameterAsString(parameters, self.DENSITY, context).strip()
        if density:
            commands.append('/density:' + density)
        first = self.parameterAsString(parameters, self.FIRSTDENSITY, context).strip()
        if first:
            commands.append('/first:' + first)
        
        self.addAdvancedModifiersToCommands(commands, parameters, context)

        self.addInputFilesToCommands(commands, parameters, self.INPUT, context)        

        outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        commands.append('"%s"' % outputFile)
        
        fusionUtils.execute(commands, feedback)

        return self.prepareReturn(parameters)


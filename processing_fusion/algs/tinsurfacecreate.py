# -*- coding: utf-8 -*-

"""
***************************************************************************
    TINSurfaceCreate.py
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
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterString
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils

class TinSurfaceCreate(FusionAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    CELLSIZE = 'CELLSIZE'
    XYUNITS = 'XYUNITS'
    ZUNITS = 'ZUNITS'
    UNITS = ['Meter', 'Feet']
    CLASS = 'CLASS'
    RETURN = 'RETURN'

    def name(self):
        return 'tinsurfacecreate'

    def displayName(self):
        return self.tr('Tin surface create')

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
            self.INPUT, self.tr('Input LAS layer'), extension = 'las'))
        self.addParameter(QgsProcessingParameterNumber(self.CELLSIZE,
                                          self.tr('Cellsize'), QgsProcessingParameterNumber.Double,
                                          minValue = 0, defaultValue = 10.0))
        self.addParameter(QgsProcessingParameterEnum(self.XYUNITS,
                                             self.tr('XY Units'), self.UNITS))
        self.addParameter(QgsProcessingParameterEnum(self.ZUNITS,
                                             self.tr('Z Units'), self.UNITS))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output DTM file'),
                                                                self.tr('DTM files (*.dtm *.DTM)')))
        class_var = QgsProcessingParameterString(
            self.CLASS, self.tr('Class'), '', optional = True)
        class_var.setFlags(class_var.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(class_var)
        return_sel = QgsProcessingParameterString(
            self.RETURN, self.tr('Select specific return'), '', optional = True)
        return_sel.setFlags(return_sel.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(return_sel)        

    def processAlgorithm(self, parameters, context, feedback):
        commands = [os.path.join(fusionUtils.fusionDirectory(), 'TINSurfaceCreate.exe')]        
        class_var = self.parameterAsString(parameters, self.CLASS, context).strip()
        if class_var:
            commands.append('/class:' + class_var)
        return_sel = self.parameterAsString(parameters, self.RETURN, context).strip()
        if return_sel:
            commands.append('/return:' + return_sel)
        
        outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
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

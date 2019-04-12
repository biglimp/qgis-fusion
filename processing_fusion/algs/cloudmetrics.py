# -*- coding: utf-8 -*-

"""
***************************************************************************
    CloudMetrics.py
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
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils

class CloudMetrics(FusionAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    ABOVE = 'ABOVE'
    FIRSTIMPULSE = 'FIRSTIMPULSE'
    FIRSTRETURN = 'FIRSTRETURN'
    HTMIN = 'HTMIN'

    def name(self):
        return 'canopymodel'

    def displayName(self):
        return self.tr('Canopy model')

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
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT_DTM,
                                                                self.tr('Output file with tabular metric information'),
                                                                self.tr('CSV files (*.csv *.CSV)')))

        above = QgsProcessingParameterString(
            self.ABOVE, self.tr('Above'), '', optional = True)
        above.setFlags(above.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(above)
        htmin = QgsProcessingParameterString(
            self.HTMIN, self.tr('Htmin'), '', optional = True)
        htmin.setFlags(htmin.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(htmin)


        firstImpulse = QgsProcessingParameterBoolean(
            self.FIRSTIMPULSE, self.tr('First impulse'), False)
        firstImpulse.setFlags(firstImpulse.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(firstImpulse)
        firstReturn = QgsProcessingParameterBoolean(
            self.FIRSTRETURN, self.tr('First return'), False)
        firstReturn.setFlags(firstReturn.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(firstReturn)

    def processAlgorithm(self, parameters, context, feedback):
        commands = [os.path.join(fusionUtils.fusionDirectory(), 'CloudMetrics.exe')]

        above = self.parameterAsString(parameters, self.ABOVE, context).strip()
        if above:
            commands.append('/abve:' + above)
        htmin = self.parameterAsString(parameters, self.HTMIN, context).strip()
        if htmin:
            commands.append('/minht:' + htmin)
        
        firstImpulse = self.parameterAsBool(parameters, self.FIRSTIMPULSE, context)
        if firstImpulse:
            commands.append('/firstinpulse') 
        firstReturn = self.parameterAsBool(parameters, self.FIRSTRETURN, context)
        if firstReturn:
            commands.append('/firstreturn') 

        self.addInputFilesToCommands(commands, parameters, self.INPUT, context)        
     
        outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        commands.append('"%s"' % outputFile)

        fusionUtils.execute(commands, feedback)

        return self.prepareReturn(parameters)

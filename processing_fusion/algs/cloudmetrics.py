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
                       QgsProcessingParameterString,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils

class CloudMetrics(FusionAlgorithm):

    INPUT = 'INPUT'
    OUTPUT_CSV = 'OUTPUT_CSV'
    NEW = 'NEW'
    ABOVE = 'ABOVE'
    FIRSTIMPULSE = 'FIRSTIMPULSE'
    FIRSTRETURN = 'FIRSTRETURN'
    HTMIN = 'HTMIN'
    PROFILEAREA = 'PROFILEAREA'
    IGNOREOVERLAP = 'IGNOREOVERLAP'
    VERSION64 = 'VERSION64'

    def name(self):
        return 'CloudMetrics'

    def displayName(self):
        return self.tr('Cloud Metrics')

    def group(self):
        return self.tr('Point cloud analysis')

    def groupId(self):
        return 'points'

    def tags(self):
        return [self.tr('lidar')]

    def shortHelpString(self):
        return 'Computes different metrics at a point cloud level. For other similar analyses check GridMetrics or DensityMetrics'

    def __init__(self):
        super().__init__()


    def initAlgorithm(self, config=None):    
        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     self.tr('Input LAS layer'),
                                                     fileFilter = '(*.las *.laz)'))
        self.addParameter(QgsProcessingParameterBoolean(self.VERSION64,
                                                        self.tr('Use 64-bit version'),
                                                        defaultValue=True))
        self.addParameter(QgsProcessingParameterBoolean(self.NEW,
                                                        self.tr('Overwrite existing output file with the same name'),
                                                        defaultValue=False))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT_CSV,
                                                                self.tr('Output file with tabular metric information'),
                                                                self.tr('CSV files (*.csv *.CSV)')))

        params = []
        params.append(QgsProcessingParameterString(self.ABOVE,
                                                   self.tr('Above'),
                                                   defaultValue='',
                                                   optional = True))
        params.append(QgsProcessingParameterString(self.HTMIN,
                                                   self.tr('Htmin'),
                                                   defaultValue='',
                                                   optional = True))
        params.append(QgsProcessingParameterBoolean(self.FIRSTIMPULSE,
                                                    self.tr('First impulse'),
                                                    defaultValue=False,
                                                    optional = True))
        params.append(QgsProcessingParameterBoolean(self.PROFILEAREA,
                                                    self.tr('Output detailed percentile data used to compute the canopy profile area'),
                                                    defaultValue=False,
                                                    optional = True))
        params.append(QgsProcessingParameterBoolean(self.IGNOREOVERLAP,
                                                        self.tr('Ignore points with the overlap flag set '),
                                                        defaultValue=False,
                                                        optional = True))


        for p in params:
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)


        self.addAdvancedModifiers()

    def processAlgorithm(self, parameters, context, feedback):
        version64 = self.parameterAsBool(parameters, self.VERSION64, context)
        if version64:
            arguments = [os.path.join(fusionUtils.fusionDirectory(), 'CloudMetrics64.exe')]
        else:
            arguments = [os.path.join(fusionUtils.fusionDirectory(), 'CloudMetrics.exe')]

        above = self.parameterAsString(parameters, self.ABOVE, context).strip()
        if above:
            arguments.append('/above:' + above)
        htmin = self.parameterAsString(parameters, self.HTMIN, context).strip()
        if htmin:
            arguments.append('/minht:' + htmin)
        
        firstImpulse = self.parameterAsBool(parameters, self.FIRSTIMPULSE, context)
        if firstImpulse:
            arguments.append('/firstinpulse') 
        firstReturn = self.parameterAsBool(parameters, self.FIRSTRETURN, context)
        if firstReturn:
            arguments.append('/firstreturn')
        if self.NEW in parameters and parameters[self.NEW]:
            arguments.append('/new')
        if self.PROFILEAREA in parameters and parameters[self.PROFILEAREA]:
            arguments.append('/pa')
        if self.IGNOREOVERLAP in parameters and parameters[self.IGNOREOVERLAP]:
            arguments.append('/ignoreoverlap')

        self.addAdvancedModifiersToCommands(arguments, parameters, context)

        self.addInputFilesToCommands(arguments, parameters, self.INPUT, context)        
     
        outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT_CSV, context)
        arguments.append('"%s"' % outputFile)

        fusionUtils.execute(arguments, feedback)

        return self.prepareReturn(parameters)

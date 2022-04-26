# -*- coding: utf-8 -*-

"""
***************************************************************************
    ClipData.py
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
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterString
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils

class ClipData(FusionAlgorithm):

    def name(self):
        return 'clipdata'

    def displayName(self):
        return self.tr('Clip data')

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
    EXTENT = 'EXTENT'
    SHAPE = 'SHAPE'
    DTM = 'DTM'
    HEIGHT = 'HEIGHT'
    IGNOREOVERLAP = 'IGNOREOVERLAP'
    CLASS = 'CLASS'
    VERSION64 = 'VERSION64'

    def initAlgorithm(self, config=None):
        self.shape = ((self.tr('Rectangle'), '0'),
                      (self.tr('Circle'), '1'))

        self.addParameter(QgsProcessingParameterFile(
            self.INPUT, self.tr('Input LAS layer'),  fileFilter = '(*.las *.laz)'))     
        self.addParameter(QgsProcessingParameterExtent(self.EXTENT, self.tr('Extent')))
        self.addParameter(QgsProcessingParameterEnum(self.SHAPE,
                                                     self.tr('Shape for clipping'),
                                                     options=[i[0] for i in self.shape],
                                                     optional = True,
                                                     defaultValue=0))
        self.addParameter(QgsProcessingParameterBoolean(self.VERSION64,
                                                        self.tr('Use 64-bit version'),
                                                        defaultValue=True))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output'),
                                                                self.tr('LAS files (*.las *.LAS)')))
        # ground = QgsProcessingParameterFile(
            # self.DTM, self.tr('Ground file for height normalization'), optional = True, extension = 'dtm')
        # ground.setFlags(ground.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        # self.addParameter(ground)        
        # height = QgsProcessingParameterBoolean(
            # self.HEIGHT, self.tr('Convert point elevations into heights above ground (used with the above command)'), False)
        # height.setFlags(height.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        # self.addParameter(height)


        params = []
        params.append(QgsProcessingParameterFile(self.DTM,
                                                 self.tr('Ground file for height normalization'),
                                                 optional = True,
                                                 extension = 'dtm'))
        params.append(QgsProcessingParameterBoolean(self.HEIGHT,
                                                    self.tr('Convert point elevations into heights above ground (used with the above command)'),
                                                    defaultValue=False,
                                                    optional = True))

        params.append(QgsProcessingParameterBoolean(self.IGNOREOVERLAP,
                                                        self.tr('Ignore points with the overlap flag set '),
                                                        defaultValue=False,
                                                        optional = True))
        params.append(QgsProcessingParameterString(self.CLASS,
                                                   self.tr('Use only a specific LAS class'),
                                                   defaultValue='',
                                                   optional = True))

        for p in params:
            p.setFlags(p.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
            self.addParameter(p)

        self.addAdvancedModifiers()

    def processAlgorithm(self, parameters, context, feedback):
        version64 = self.parameterAsBool(parameters, self.VERSION64, context)
        if version64:
            arguments = ['"' + os.path.join(fusionUtils.fusionDirectory(), 'ClipData64.exe') + '"']
        else:
            arguments = ['"' + os.path.join(fusionUtils.fusionDirectory(), 'ClipData.exe') + '"']
        self.addAdvancedModifiersToCommands(arguments, parameters, context)
        
        arguments.append('/shape:' + str(self.parameterAsEnum(parameters, self.SHAPE, context)))
        
        dtm = self.parameterAsString(parameters, self.DTM, context)
        if dtm:
            arguments.append('/dtm:' + dtm)
        height = self.parameterAsString(parameters, self.HEIGHT, context)
        if height:
            arguments.append('/height')
        if self.IGNOREOVERLAP in parameters and parameters[self.IGNOREOVERLAP]:
            arguments.append('/ignoreoverlap')

        class_var = self.parameterAsString(parameters, self.CLASS, context).strip()
        if class_var:
            arguments.append('/class:' + class_var)
        self.addInputFilesToCommands(arguments, parameters, self.INPUT, context)        
        
        outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        arguments.append('"%s"' % outputFile)

        extent = self.parameterAsExtent(parameters, self.EXTENT, context)
        arguments.append(extent.xMinimum())
        arguments.append(extent.yMinimum())
        arguments.append(extent.xMaximum())
        arguments.append(extent.yMaximum())
        
        fusionUtils.execute(arguments, feedback)

        return self.prepareReturn(parameters)

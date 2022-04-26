# -*- coding: utf-8 -*-

"""
***************************************************************************
    GroundFilter.py
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
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterExtent,
                       QgsProcessingParameterFileDestination,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterString
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils

class GroundFilter(FusionAlgorithm):

    INPUT = 'INPUT'
    OUTPUT = 'OUTPUT'
    CELLSIZE = 'CELLSIZE'
    SURFACE = 'SURFACE'
    MEDIAN ='MEDIAN'
    SMOOTH = 'SMOOTH'
    ITERATIONS = 'ITERATIONS'
    CLASS ='CLASS'
    FINALSMOOTH = 'FINALSMOOTH'
    IGNOREOVERLAP = 'IGNOREOVERLAP'
    VERSION64 = 'VERSION64'

    def name(self):
        return 'groundfilter'

    def displayName(self):
        return self.tr('Ground filter')

    def group(self):
        return self.tr('Point cloud analysis')

    def groupId(self):
        return 'points'

    def tags(self):
        return [self.tr('lidar')]

    def shortHelpString(self):
        return '''GroundFilter is designed to filter a cloud of LIDAR returns to identify those returns that lie on the probable ground surface.
               Experimentation showed that the default coefficients for the weight function produce good results in high-density point clouds (> 4 returns/sq m).
               
               IMPORTANT
               The order of the /median and /smooth switches is important: the first filter specified will be the first filter applied to the model.
               Slope filtering takes place after all other smoothing operations.'''

    def __init__(self):
        super().__init__()


    def initAlgorithm(self, config=None):

        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     self.tr('Input LAS layer'),
                                                     fileFilter = '(*.las *.laz)'))   
        self.addParameter(QgsProcessingParameterNumber(self.CELLSIZE,
                                                       self.tr('Cellsize for intermediate surfaces'),
                                                       QgsProcessingParameterNumber.Double,
                                                       minValue = 0,
                                                       defaultValue = 10.0))        
        self.addParameter(QgsProcessingParameterBoolean(self.SURFACE,
                                                        self.tr('Create .dtm surface'),
                                                        defaultValue = False))
        self.addParameter(QgsProcessingParameterBoolean(self.VERSION64,
                                                        self.tr('Use 64-bit version'),
                                                        defaultValue=True))
        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Output ground LAS file'),
                                                                self.tr('LAS files (*.las *.LAS)')))


        params = []
        params.append(QgsProcessingParameterString(self.MEDIAN,
                                                   self.tr('Size of the window for Median filter'),
                                                   defaultValue='',
                                                   optional = True))
        params.append(QgsProcessingParameterString(self.SMOOTH,
                                                   self.tr('Size of the window for mean filter (Smooth)'),
                                                   defaultValue='',
                                                   optional = True))
        params.append(QgsProcessingParameterString(self.ITERATIONS,
                                                   self.tr('Number of iterations for the filtering logic (default is 5)'),
                                                   defaultValue='',
                                                   optional = True))
        params.append(QgsProcessingParameterString(self.CLASS,
                                                   self.tr('Use only a specific LAS class'),
                                                   defaultValue='',
                                                   optional = True))
        params.append(QgsProcessingParameterBoolean(self.FINALSMOOTH,
                                                        self.tr('Apply final smoothing (only used with smooth or median filter)'),
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
            arguments = ['"' + os.path.join(fusionUtils.fusionDirectory(), 'GroundFilter64.exe') + '"']
        else:
            arguments = ['"' + os.path.join(fusionUtils.fusionDirectory(), 'GroundFilter.exe') + '"']

        if self.parameterAsBool(parameters, self.SURFACE, context):
            arguments.append('/surface')

        median = self.parameterAsString(parameters, self.MEDIAN, context).strip()
        if median:
            arguments.append('/median:' + median)
        smooth= self.parameterAsString(parameters, self.SMOOTH, context).strip()
        if smooth:
            arguments.append('/smooth:' + smooth)
        iterations= self.parameterAsString(parameters, self.ITERATIONS, context).strip()
        if iterations:
            arguments.append('/iterations:' + smooth)
        finalsmooth = self.parameterAsBool(parameters, self.FINALSMOOTH, context)
        if finalsmooth:
            arguments.append('/finalsmooth') 
        class_var = self.parameterAsString(parameters, self.CLASS, context).strip()
        if class_var:
            arguments.append('/class:' + class_var)
        if self.IGNOREOVERLAP in parameters and parameters[self.IGNOREOVERLAP]:
            arguments.append('/ignoreoverlap')

        self.addAdvancedModifiersToCommands(arguments, parameters, context)

        outputFile = self.parameterAsFileOutput(parameters, self.OUTPUT, context)
        arguments.append('"%s"' % outputFile)
        arguments.append(str(self.parameterAsDouble(parameters, self.CELLSIZE, context)))
        self.addInputFilesToCommands(arguments, parameters, self.INPUT, context)        

        fusionUtils.execute(arguments, feedback)

        return self.prepareReturn(parameters)

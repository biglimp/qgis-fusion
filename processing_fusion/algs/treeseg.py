# -*- coding: utf-8 -*-

"""
***************************************************************************
    TreeSeg.py
    ---------------------
    Date                 : November 2016
    Copyright            : (C) 2016 by Niccolo' Marchi
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
__date__ = 'November 2016'
__copyright__ = "(C) 2016 by Niccolo' Marchi"

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.core import (QgsProcessing,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterFileDestination
                      )

from processing_fusion.fusionAlgorithm import FusionAlgorithm
from processing_fusion import fusionUtils


class TreeSeg(FusionAlgorithm):

    INPUT = 'INPUT'
    GROUND = 'GROUND'
    HEIGHT_TH = 'HEIGHT_TH'
    HEIGHT_NORM = 'HEIGHT_NORM'
    HEIGHT_PTS = 'HEIGHT_PTS'
    LASPTS = 'LASPTS'
    SEGMENTPTS = 'SEGMENTPTS'
    SHAPE = 'SHAPE'
    VERSION64 = 'VERSION64'
    OUTPUT = 'OUTPUT'

    def name(self):
        return 'treeseg'

    def displayName(self):
        return self.tr("Trees Segmentation")

    def group(self):
        return self.tr('Point cloud analysis')

    def groupId(self):
        return 'points'

    def tags(self):
        return [self.tr('lidar')]

    def shortHelpString(self):
        return self.tr('Segments single trees from a Canopy Height Model')

    def __init__(self):
        super().__init__()

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFile(self.INPUT,
                                                     self.tr('Input CHM in PLANS DTM format'),
                                                     QgsProcessingParameterFile.File,
                                                     extension = 'dtm'))
        # self.addParameter(QgsProcessingParameterFile(
            # self.GROUND, self.tr('Input ground model in PLANS DTM format'), extension = 'dtm', optional=True))
        self.addParameter(QgsProcessingParameterNumber(self.HEIGHT_TH,
                                                       self.tr('Minimum height for object segmentation'),
                                                       QgsProcessingParameterNumber.Integer,
                                                       minValue = 0,
                                                       defaultValue=0))
        self.addParameter(QgsProcessingParameterBoolean(self.VERSION64,
                                                        self.tr('Use 64-bit version'),
                                                        defaultValue=True))


        ground = QgsProcessingParameterFile(self.GROUND,
                                            self.tr('Input ground surface file (PLANS DTM format)'),
                                            extension = 'dtm',
                                            optional=True)
        ground.setFlags(ground.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(ground)
        
        heightNorm = QgsProcessingParameterBoolean(self.HEIGHT_NORM,
                                                   self.tr('Normalize height model using a ground model'),
                                                   defaultValue=False)
        heightNorm.setFlags(heightNorm.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(heightNorm)
        
        heightPts = QgsProcessingParameterBoolean(self.HEIGHT_PTS,
                                                  self.tr("Normalize points' height using a ground model"),
                                                  defaultValue=False)
        heightPts.setFlags(heightPts.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(heightPts)

        lasPts = QgsProcessingParameterFile(self.LASPTS,
                                            self.tr("Input LAS layer(s)"),
                                            extension = ('LAS/LAZ files (*.las *.laz)'),
                                            optional=True)
        lasPts.setFlags(lasPts.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(lasPts)

        segmentPts = QgsProcessingParameterBoolean(self.SEGMENTPTS,
                                                   self.tr("Output points for the raster segments instead of crown polygons"),
                                                   defaultValue=False)
        segmentPts.setFlags(segmentPts.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(segmentPts)
        
        shape = QgsProcessingParameterBoolean(self.SHAPE,
                                              self.tr("Create basin/crown shapefiles with metrics"),
                                              defaultValue=False)
        shape.setFlags(shape.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(shape)

        self.addParameter(QgsProcessingParameterFileDestination(self.OUTPUT,
                                                                self.tr('Base name for (multiple) output files')))

    def processAlgorithm(self, parameters, context, feedback):
        arguments = []

        if self.VERSION64:
            arguments.append(os.path.join(fusionUtils.fusionDirectory(), 'TreeSeg64.exe'))
        else:
            arguments.append(os.path.join(fusionUtils.fusionDirectory(), 'TreeSeg.exe'))

        if self.HEIGHT_NORM in parameters and parameters[self.HEIGHT_NORM]:
            arguments.append('/height')
        if self.HEIGHT_PTS in parameters and parameters[self.HEIGHT_PTS]:
            arguments.append('/ptheight')            

        if self.GROUND in parameters and parameters[self.GROUND] is not None:
            arguments.append('/ground:{}'.format(self.parameterAsInt(parameters, self.GROUND, context)))

        if self.LASPTS in parameters and parameters[self.LASPTS] is not None:
            arguments.append('/points:{}'.format(self.parameterAsInt(parameters, self.LASPTS, context)))

        if self.SEGMENTPTS in parameters and parameters[self.SEGMENTPTS]:
            arguments.append('/segmentpts')
        if self.SHAPE in parameters and parameters[self.SHAPE]:
            arguments.append('/shape')

        # arguments.append(self.parameterAsFileOutput(parameters, self.OUTPUT, context))
        # arguments.append(self.units[self.parameterAsEnum(parameters, self.XYUNITS, context)][1])
        # arguments.append(self.units[self.parameterAsEnum(parameters, self.ZUNITS, context)][1])
        # arguments.append(self.csystems[self.parameterAsEnum(parameters, self.COORDSYS, context)][1])
        # arguments.append(str(self.parameterAsInt(parameters, self.ZONE, context)))
        # arguments.append(self.hdatums[self.parameterAsEnum(parameters, self.HDATUM, context)][1])
        # arguments.append(self.vdatums[self.parameterAsEnum(parameters, self.VDATUM, context)][1])
        
        arguments.append(self.parameterAsFile(parameters, self.INPUT, context))

        arguments.append(self.parameterAsInt(parameters, self.HEIGHT_TH, context))
        arguments.append(self.parameterAsFileOutput(parameters, self.OUTPUT, context))
        
        # fileList = fusionUtils.layersToFile('xyzDataFiles.txt', self, parameters, self.INPUT, context)
        # arguments.append(fileList)

        fusionUtils.execute(arguments, feedback)

        results = {}
        for output in self.outputDefinitions():
            outputName = output.name()
            if outputName in parameters:
                results[outputName] = parameters[outputName]

        return results

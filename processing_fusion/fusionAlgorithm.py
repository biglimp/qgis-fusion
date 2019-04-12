# -*- coding: utf-8 -*-

"""
***************************************************************************
    fusionAlgorithm.py
    ---------------------
    Date                 : March 2019
    Copyright            : (C) 2019 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'March 2019'
__copyright__ = '(C) 2019, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtCore import QCoreApplication
from qgis.PyQt.QtGui import QIcon

from qgis.core import QgsProcessingAlgorithm, QgsProcessingParameterString, QgsProcessingParameterDefinition

from processing_fusion import fusionUtils

pluginPath = os.path.dirname(__file__)


class FusionAlgorithm(QgsProcessingAlgorithm):

    ADVANCED_MODIFIERS = 'ADVANCED_MODIFIERS'

    def __init__(self):
        super().__init__()
        self.output_values = {}

    def createInstance(self):
        return type(self)()

    def addAdvancedModifiers(self):
        param = QgsProcessingParameterString(
            self.ADVANCED_MODIFIERS, self.tr('Additional modifiers'), '', optional=True)
        param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(param)

    def addAdvancedModifiersToCommands(self, commands, parameters, context):
        s = self.parameterAsString(parameters, self.ADVANCED_MODIFIERS, context).strip()
        if s:
            commands.append(s)

    def addInputFilesToCommands(self, commands, parameters, parameterName, context):
        files = self.parameterAsString(parameters, parameterName, context).split(';')
        if len(files) == 1:
            commands.append('"%s"' % files[0])
        else:
            commands.append(fusionUtils.filenamesToFile(files))

    def setOutputValue(self, name, value):
        self.output_values[name] = value

    def prepareReturn(self, parameters):
        results = {}
        for o in self.outputDefinitions():
            if o.name() in parameters:
                results[o.name()] = parameters[o.name()]
        for k, v in self.output_values.items():
            results[k] = v

        return results         

    def helpUrl(self):
        return "http://forsys.cfr.washington.edu/Software/FUSION/FUSION_manual.pdf"

    def icon(self):
        return QIcon(os.path.join(pluginPath, 'icons', 'fusion.svg'))

    def tr(self, text):
        return QCoreApplication.translate(self.__class__.__name__, text)

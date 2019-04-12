# -*- coding: utf-8 -*-

"""
***************************************************************************
    fusionUtils.py
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
import subprocess

from qgis.core import (Qgis,
                       QgsMessageLog,
                       QgsProcessingFeedback,
                       QgsProcessingUtils
                      )
from processing.core.ProcessingLog import ProcessingLog
from processing.core.ProcessingConfig import ProcessingConfig

FUSION_ACTIVE = 'FUSION_ACTIVE'
FUSION_VERBOSE = 'FUSION_VERBOSE'
FUSION_DIRECTORY = 'FUSION_DIRECTORY'


def fusionDirectory():
    filePath = ProcessingConfig.getSetting(FUSION_DIRECTORY)
    return filePath if filePath is not None else ''


def execute(commands, feedback=None):
    if feedback is None:
        feedback = QgsProcessingFeedback()

    fused_command = ' '.join([str(c) for c in commands])
    QgsMessageLog.logMessage(fused_command, 'Processing', Qgis.Info)
    feedback.pushInfo('FUSION command:')
    feedback.pushCommandInfo(fused_command)
    feedback.pushInfo('FUSION command output:')

    loglines = []
    with subprocess.Popen(fused_command,
                          shell=True,
                          stdout=subprocess.PIPE,
                          stdin=subprocess.DEVNULL,
                          stderr=subprocess.STDOUT,
                          universal_newlines=True) as proc:
        try:
            for line in iter(proc.stdout.readline, ''):
                feedback.pushConsoleInfo(line)
                loglines.append(line)
        except:
            pass

    if ProcessingConfig.getSetting(FUSION_VERBOSE):
        QgsMessageLog.logMessage('\n'.join(loglines), 'Processing', Qgis.Info)


def layersToFile(fileName, alg, parameters, parameter, context, quote=True):
    layers = []
    for l in alg.parameterAsLayerList(parameters, parameter, context):
        if quote:
            layers.append('"{}"'.format(l.source()))
        else:
            layers.append(l.source())

    listFile = QgsProcessingUtils.generateTempFilename(fileName)
    with open(listFile, 'w', encoding='utf-8') as f:
        f.write('\n'.join(layers))

    return listFile

def filenamesToFile(files):
    listFile = QgsProcessingUtils.generateTempFilename("inputfiles.txt")
    with open(listFile, 'w', encoding='utf-8') as f:
        f.write('\n'.join(files))

    return listFile




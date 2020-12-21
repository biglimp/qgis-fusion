# -*- coding: utf-8 -*-

"""
***************************************************************************
    __init__.py
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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Alexander Bruy'
__date__ = 'March 2019'
__copyright__ = '(C) 2019, Alexander Bruy'



# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load ProcessingUMEP class from file ProcessingUMEP.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .processing_fusion import ProcessingFUSIONPlugin
    return ProcessingFUSIONPlugin()

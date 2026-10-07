# ==================================================================================================================== #
#               _____           _ _               ____  _                                                              #
#    _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \(_) __ _  __ _ _ __ __ _ _ __ ___                               #
#   | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | | | | |/ _` |/ _` | '__/ _` | '_ ` _ \                              #
#   | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |_| | | (_| | (_| | | | (_| | | | | | |                             #
#   | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/|_|\__,_|\__, |_|  \__,_|_| |_| |_|                             #
#   |_|    |___/                          |___/                 |___/                                                  #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
#                                                                                                                      #
# Licensed under the Apache License, Version 2.0 (the "License");                                                      #
# you may not use this file except in compliance with the License.                                                     #
# You may obtain a copy of the License at                                                                              #
#                                                                                                                      #
#   http://www.apache.org/licenses/LICENSE-2.0                                                                         #
#                                                                                                                      #
# Unless required by applicable law or agreed to in writing, software                                                  #
# distributed under the License is distributed on an "AS IS" BASIS,                                                    #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.                                             #
# See the License for the specific language governing permissions and                                                  #
# limitations under the License.                                                                                       #
#                                                                                                                      #
# SPDX-License-Identifier: Apache-2.0                                                                                  #
# ==================================================================================================================== #
#
"""
Data models of diagrams, independent of the library drawing them.

A diagram is described here and drawn elsewhere: :mod:`pyTooling.Diagram.Gantt` describes a Gantt chart - rows of
bars on a time scale - and a renderer turns that description into a picture. A producer of data derives from these
classes and adds what its own domain knows, as :mod:`pyTooling.Tracing.Render` does for a software execution trace.

.. seealso::

   :mod:`pyTooling.Diagram.Gantt`
      |rarr| Rows of bars on a time scale.
   :mod:`pyTooling.Tracing.Render`
      |rarr| A software execution trace as a Gantt chart.
"""
from pyTooling.Decorators import export
from pyTooling.Exceptions import ToolingException


@export
class DiagramError(ToolingException):
	"""An error raised when a diagram is asked for something its elements don't describe."""

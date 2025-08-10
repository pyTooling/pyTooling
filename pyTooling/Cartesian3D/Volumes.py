# ==================================================================================================================== #
#             _____           _ _               ____           _            _             _____ ____                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|__ _ _ __| |_ ___  ___(_) __ _ _ __ |___ /|  _ \                  #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _` | '__| __/ _ \/ __| |/ _` | '_ \  |_ \| | | |                 #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_| | |  | ||  __/\__ \ | (_| | | | |___) | |_| |                 #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\__,_|_|   \__\___||___/_|\__,_|_| |_|____/|____/                  #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2025-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""An implementation of 3D cartesian volumes for Python."""

try:
	from pyTooling.Decorators  import readonly, export
	from pyTooling.Exceptions  import ToolingException
	from pyTooling.MetaClasses import ExtendedType
	from pyTooling.Common      import getFullyQualifiedName
	from pyTooling.Cartesian3D import Point3D, Offset3D
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Cartesian3D] Could not import from 'pyTooling.*'!")

	try:
		from Decorators  import readonly, export
		from Exceptions  import ToolingException
		from MetaClasses import ExtendedType
		from Common      import getFullyQualifiedName
		from Cartesian3D import Point3D, Offset3D
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Cartesian3D] Could not import directly!")
		raise ex


@export
class Volume:
	"""Base-class for all 3D cartesian volumes."""


@export
class Cuboid(Volume):
	"""
	A cuboid is a volume made out of 6 rectangles.
	"""


@export
class Cube(Cuboid):
	"""
	A cube is a Cuboid made out of 6 equally sized squares.
	"""

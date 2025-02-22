# ==================================================================================================================== #
#            _   _   _        _ _           _                 _              ____                                      #
#           / \ | |_| |_ _ __(_) |__  _   _| |_ ___  ___     / \   _ __ __ _|  _ \ __ _ _ __ ___  ___                  #
#          / _ \| __| __| '__| | '_ \| | | | __/ _ \/ __|   / _ \ | '__/ _` | |_) / _` | '__/ __|/ _ \                 #
#   _ _ _ / ___ \ |_| |_| |  | | |_) | |_| | ||  __/\__ \_ / ___ \| | | (_| |  __/ (_| | |  \__ \  __/                 #
#  (_|_|_)_/   \_\__|\__|_|  |_|_.__/ \__,_|\__\___||___(_)_/   \_\_|  \__, |_|   \__,_|_|  |___/\___|                 #
#                                                                      |___/                                           #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
# Copyright 2007-2016 Patrick Lehmann - Dresden, Germany                                                               #
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
try:
	from pyTooling.Decorators                   import export
	from pyTooling.Attributes.ArgParse.Argument import NamedArgument, ValuedArgument
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Attributes.ArgParse.BooleanFlag] Could not import from 'pyTooling.*'!")

	try:
		from Decorators                           import export
		from Attributes.ArgParse.Argument         import NamedArgument, ValuedArgument
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Attributes.ArgParse.BooleanFlag] Could not import directly!")
		raise ex


@export
class BooleanFlag(NamedArgument, ValuedArgument):
	pass


@export
class ShortBooleanFlag(BooleanFlag):  #, pattern="-with-{0}", falsePattern="-without-{0}"):
	pass


@export
class LongBooleanFlag(BooleanFlag):  #, pattern="--with-{0}", falsePattern="--without-{0}"):
	pass


@export
class WindowsBooleanFlag(BooleanFlag):  #, pattern="/with-{0}", falsePattern="/without-{0}"):
	pass

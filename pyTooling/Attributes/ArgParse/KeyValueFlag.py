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
from typing   import Optional as Nullable

try:
	from pyTooling.Decorators                   import export
	from pyTooling.Attributes.ArgParse.Argument import NamedAndValuedArgument
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Attributes.ArgParse.KeyValueFlag] Could not import from 'pyTooling.*'!")

	try:
		from Decorators                           import export
		from Attributes.ArgParse.Argument         import NamedAndValuedArgument
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Attributes.ArgParse.KeyValueFlag] Could not import directly!")
		raise ex


@export
class NamedKeyValuePairsArgument(NamedAndValuedArgument):
	"""
	Defines a switch argument like ``--help``.

	Some of the named parameters passed to :meth:`~ArgumentParser.add_argument` are predefined (or overwritten) to create
	a boolean parameter passed to the registered handler method. The boolean parameter is ``True`` if the switch argument
	is present in the commandline arguments, otherwise ``False``.
	"""

	def __init__(self, short: Nullable[str] = None, long: Nullable[str] = None, dest: Nullable[str] = None, help: Nullable[str] = None):
		"""
		The constructor expects positional (``*args``), the destination parameter name ``dest`` and/or named parameters
		(``**kwargs``) which are passed to :meth:`~ArgumentParser.add_argument`.

		To implement a switch argument, the following named parameters are predefined:

		* ``action="store_const"``
		* ``const=True``
		* ``default=False``

		This implements a boolean parameter passed to the handler method.
		"""
		args = []
		if short is not None:
			args.append(short)
		if long is not None:
			args.append(long)

		kwargs = {
			"dest":    dest,
			"action":  "store_const",
			"const":   True,
			"default": False,
			"help":    help,
		}
		super().__init__(*args, **kwargs)


@export
class ShortKeyValueFlag(NamedKeyValuePairsArgument):
	def __init__(self, short: Nullable[str] = None, dest: Nullable[str] = None, help: Nullable[str] = None):
		super().__init__(short=short, dest=dest, help=help)


@export
class LongKeyValueFlag(NamedKeyValuePairsArgument):
	def __init__(self, long: Nullable[str] = None, dest: Nullable[str] = None, help: Nullable[str] = None):
		super().__init__(long=long, dest=dest, help=help)

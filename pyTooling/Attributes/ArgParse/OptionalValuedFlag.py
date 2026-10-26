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
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""
Attributes describing options whose value may be omitted, like ``--repeat[=1]``.

Without a value, the option is still recognized; the handler method sees the default instead.
"""
from typing import Optional as Nullable

from pyTooling.Decorators                   import export
from pyTooling.Attributes.ArgParse.Argument import NamedAndValuedArgument


@export
class OptionalValuedFlag(NamedAndValuedArgument):
	"""
	Defines a switch argument with an optional value like ``--repeat[=1]``.

	Some of the named parameters passed to :meth:`~ArgumentParser.add_argument` are predefined (or overwritten), so the
	registered handler method receives the option's value: the given value (``--repeat=3``), ``defaultValue`` if the
	option is given without a value (``--repeat``), or ``None`` if the option isn't given.
	"""

	def __init__(
		self,
		short:        Nullable[str] = None,
		long:         Nullable[str] = None,
		dest:         Nullable[str] = None,
		metaName:     str = "VALUE",
		defaultValue: str = "",
		help:         Nullable[str] = None
	) -> None:
		"""
		Initializes a switch argument with an optional value.

		.. admonition:: ArgParse parameterization

		   :meth:`~argparse.ArgumentParser.add_argument` is called with the option strings from ``short`` and ``long``
		   as positional parameters, and with these named parameters:

		   * ``dest=dest``
		   * ``nargs="?"``
		   * ``metavar=metaName``
		   * ``const=defaultValue``
		   * ``default=None``
		   * ``help=help``

		   ``nargs="?"`` makes the value optional: ``--repeat=3`` (or ``--repeat 3``) passes ``"3"`` to the handler
		   method, ``--repeat`` passes ``defaultValue`` (``const``), and without the option the handler method receives
		   ``None`` (``default``).

		:param short:        Optional, short option name including the dash, e.g. ``"-r"``. Default: ``None``.
		:param long:         Optional, long option name including the dashes, e.g. ``"--repeat"``. Default: ``None``.
		:param dest:         Optional, name the parsed value is stored under in the :class:`~argparse.Namespace`, and the
		                     name the handler method reads it by.
		:param metaName:     Optional, name shown for the value in the help page (``metavar``). Default: ``"VALUE"``.
		:param defaultValue: Optional, value the handler method receives, if the option is given without a value.
		                     Default: ``""``.
		:param help:         Optional, help text shown for this argument in the help page. Default: ``None``.
		"""
		args = []
		if short is not None:
			args.append(short)

		if long is not None:
			args.append(long)

		kwargs = {
			"dest":    dest,
			"nargs":   "?",
			"metavar": metaName,
			"const":   defaultValue,
			"default": None,
			"help":    help,
		}
		super().__init__(*args, **kwargs)


@export
class ShortOptionalValuedFlag(OptionalValuedFlag):
	"""Defines a switch argument with an optional value in short form like ``-r[=1]``."""

	def __init__(
		self,
		short:        Nullable[str] = None,
		dest:         Nullable[str] = None,
		metaName:     str = "VALUE",
		defaultValue: str = "",
		help:         Nullable[str] = None
	) -> None:
		"""
		Initialize a switch argument with an optional value in its short form.

		:param short:        Optional, short form of the option, including its dash, e.g. :pycode:`short="-r"`.
		:param dest:         Optional, name of the parameter the parsed value is passed to the handler method as.
		:param metaName:     Optional, name of the value in the help page. Default: ``"VALUE"``.
		:param defaultValue: Optional, value passed, if the option is given without a value. Default: ``""``.
		:param help:         Optional, help text of the option, displayed in the help page.
		"""
		super().__init__(short=short, dest=dest, metaName=metaName, defaultValue=defaultValue, help=help)


@export
class LongOptionalValuedFlag(OptionalValuedFlag):
	"""Defines a switch argument with an optional value in long form like ``--repeat[=1]``."""

	def __init__(
		self,
		long:         Nullable[str] = None,
		dest:         Nullable[str] = None,
		metaName:     str = "VALUE",
		defaultValue: str = "",
		help:         Nullable[str] = None
	) -> None:
		"""
		Initialize a switch argument with an optional value in its long form.

		:param long:         Optional, long form of the option, including its dashes, e.g. :pycode:`long="--repeat"`.
		:param dest:         Optional, name of the parameter the parsed value is passed to the handler method as.
		:param metaName:     Optional, name of the value in the help page. Default: ``"VALUE"``.
		:param defaultValue: Optional, value passed, if the option is given without a value. Default: ``""``.
		:param help:         Optional, help text of the option, displayed in the help page.
		"""
		super().__init__(long=long, dest=dest, metaName=metaName, defaultValue=defaultValue, help=help)

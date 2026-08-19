# ==================================================================================================================== #
#             _____           _ _               ____             __ _                       _   _                      #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|___  _ __  / _(_) __ _ _   _ _ __ __ _| |_(_) ___  _ __           #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _ \| '_ \| |_| |/ _` | | | | '__/ _` | __| |/ _ \| '_ \          #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_) | | | |  _| | (_| | |_| | | | (_| | |_| | (_) | | | |         #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\___/|_| |_|_| |_|\__, |\__,_|_|  \__,_|\__|_|\___/|_| |_|         #
# |_|    |___/                          |___/                         |___/                                            #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2021-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for the abstract base-classes of :mod:`pyTooling.Configuration`.

The four stubs on :class:`~pyTooling.Configuration.Node` are declared abstract, so a backend that forgets one is
rejected at class-creation time instead of raising :exc:`NotImplementedError` at runtime.
"""
from pyTooling.Configuration import Node, Dictionary, Sequence
from pyTooling.MetaClasses   import AbstractClassError
from pyTooling.Testing       import Testcase


class Abstract(Testcase):
	def test_NodeIsAbstract(self) -> None:
		with self.assertRaises(AbstractClassError) as context:
			_ = Node()

		self.assertIn("__getitem__", str(context.exception))

	def test_DictionaryIsAbstract(self) -> None:
		with self.assertRaises(AbstractClassError):
			_ = Dictionary()

	def test_SequenceIsAbstract(self) -> None:
		with self.assertRaises(AbstractClassError):
			_ = Sequence()

	def test_ABackendImplementsAllOfThem(self) -> None:
		"""A backend is instantiable, which is what the abstract declaration must not break."""
		from pyTooling.Configuration.YAML import Configuration as YAMLConfiguration
		from pyTooling.Configuration.JSON import Configuration as JSONConfiguration

		for configuration in (YAMLConfiguration, JSONConfiguration):
			for method in ("__len__", "__getitem__", "__iter__", "QueryPath"):
				self.assertTrue(hasattr(configuration, method))

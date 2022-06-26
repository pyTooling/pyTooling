# ==================================================================================================================== #
#             _____           _ _               __  __      _         ____ _                                           #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  \/  | ___| |_ __ _ / ___| | __ _ ___ ___  ___  ___                   #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |\/| |/ _ \ __/ _` | |   | |/ _` / __/ __|/ _ \/ __|                  #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_| |  | |  __/ || (_| | |___| | (_| \__ \__ \  __/\__ \                  #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|  |_|\___|\__\__,_|\____|_|\__,_|___/___/\___||___/                  #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2022 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for class :py:class:`pyTooling.MetaClasses.Singleton`.

:copyright: Copyright 2007-2022 Patrick Lehmann - Bötzingen, Germany
:license: Apache License, Version 2.0
"""
from unittest import TestCase

from pytest   import mark

from pyTooling.MetaClasses import ExtendedType


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class App1WithoutParameters(metaclass=ExtendedType, singleton=True):
	X = 10

	def __init__(self):
		print("Instance of 'App1WithoutParameters' was created")

		self.X = 11


class App2WithoutParameters(metaclass=ExtendedType, singleton=True):
	X = 20

	def __init__(self):
		print("Instance of 'App2WithoutParameters' was created")

		self.X = 21


class App3WithParameters(metaclass=ExtendedType, singleton=True):
	X = 30

	def __init__(self, x: int = 31):
		print("Instance of 'App1WithParameters' was created")

		self.X = x


class DerivedApp2WithoutParameters(App2WithoutParameters):
	X = 120

	def __init__(self):
		super().__init__()
		print("Instance of 'DerivedApp2WithoutParameters' was created")


class DerivedApp3WithInnerParameters(App3WithParameters):
	X = 130

	def __init__(self):
		super().__init__(x=131)
		print("Instance of 'DerivedApp3WithInnerParameters' was created")


class DerivedApp3WithOuterParameters(App3WithParameters):
	X = 135

	def __init__(self, x: int = 136):
		super().__init__(x)
		print("Instance of 'DerivedApp3WithOuterParameters' was created")


class Singleton(TestCase):
	def test_CrossRelations(self) -> None:
		self.assertEqual(10, App1WithoutParameters.X)
		self.assertEqual(20, App2WithoutParameters.X)

		app_1 = App1WithoutParameters()
		self.assertEqual(11, app_1.X)

		app_1.X = 12
		self.assertEqual(12, app_1.X)

		app_1same = App1WithoutParameters()
		self.assertIs(app_1, app_1same)
		self.assertEqual(12, app_1same.X)

		self.assertEqual(10, App1WithoutParameters.X)

		app_2 = App2WithoutParameters()
		self.assertIsNot(app_1, app_2)
		self.assertEqual(12, app_1.X)
		self.assertEqual(21, app_2.X)

		app_2.X = 22
		self.assertEqual(12, app_1.X)
		self.assertEqual(22, app_2.X)

	def test_SecondInstanceWithParameters(self):
		# ensure at least one instance was created
		App1WithoutParameters()

		with self.assertRaises(ValueError) as ExceptionCapture:
			App1WithoutParameters(x = 35)

		self.assertEqual("A further instance of a singleton can't be reinitialized with parameters.", str(ExceptionCapture.exception))

	def test_DerivedClassNoParameters(self):
		self.assertEqual(120, DerivedApp2WithoutParameters.X)

		app = DerivedApp2WithoutParameters()
		self.assertEqual(21, app.X)

		app.X = 22
		self.assertEqual(22, app.X)

		app2 = DerivedApp2WithoutParameters()
		self.assertIs(app, app2)
		self.assertEqual(22, app2.X)

		self.assertEqual(120, DerivedApp2WithoutParameters.X)

	def test_DerivedClassWithInnerParameters(self):
		app = DerivedApp3WithInnerParameters()
		self.assertEqual(131, app.X)

		appSame = DerivedApp3WithInnerParameters()
		self.assertIs(app, appSame)

	@mark.xfail(reason="This case is not yet supported.")
	def test_DerivedClassWithOuterParameters(self):
		app = DerivedApp3WithOuterParameters(x=137)
		self.assertEqual(137, app.X)

		appSame = DerivedApp3WithOuterParameters()
		self.assertIs(app, appSame)

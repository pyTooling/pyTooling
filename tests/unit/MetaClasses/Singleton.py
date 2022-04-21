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
from unittest       import TestCase

from pyTooling.MetaClasses import Singleton


if __name__ == "__main__": # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unitest <testcase module>'")
	exit(1)


class Application1(metaclass=Singleton):
	X = 0

	def __init__(self):
		print("Instance of 'Application1' was created")

		self.X = 1


# class Application2(metaclass=Singleton, includeDerivedVariants=True):
# 	X = 0
#
# 	def __init__(self, x=5):
# 		print("setting X")
#
# 		self.X = x


# class Application3(Application2):
#
# 	def __init__(self, x):
# 		super().__init__(x)
# 		print("Instance created")


class Singleton(TestCase):
	def test_1(self) -> None:
		self.assertEqual(Application1.X, 0)

		app = Application1()
		self.assertEqual(app.X, 1)

		app.X = 2
		self.assertEqual(app.X, 2)

		app2 = Application1()
		self.assertEqual(app2.X, 2)

		self.assertEqual(Application1.X, 0)

	# def test_2(self):
	# 	self.assertEqual(Application3.X, 0)
	#
	# 	app = Application3(1)
	# 	self.assertEqual(app.X, 1)
	#
	# 	app.X = 2
	# 	self.assertEqual(app.X, 2)
	#
	# 	app2 = Application3(3)
	# 	self.assertEqual(app2.X, 2)
	#
	# 	self.assertEqual(Application3.X, 0)

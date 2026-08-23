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
"""
Unit tests for the ``expects`` class keyword argument of :class:`pyTooling.MetaClasses.ExtendedType`.

A mixin-class lists the members it needs from whichever class it is mixed into. The expectation is resolved when the
class is constructed and rejected on instantiation, the same way an abstract class is handled.
"""
from pyTooling.MetaClasses import AbstractClassError, ExtendedType, UnfulfilledExpectationError
from pyTooling.MetaClasses import abstractclass, abstractmethod, mixin
from pyTooling.Testing     import Testcase

if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Host(metaclass=ExtendedType, slots=True):
	"""A host class providing both members the mixin below expects."""

	_counter: int

	def __init__(self) -> None:
		self._counter = 0

	def Write(self, message: str) -> bool:
		return True


class HalfHost(metaclass=ExtendedType, slots=True):
	"""A host class providing only one of the two expected members."""

	_counter: int


class Mixin(metaclass=ExtendedType, mixin=True, expects=("_counter", "Write")):
	"""A mixin-class expecting a field and a method from its host class."""

	def Report(self) -> bool:
		return self.Write(f"{self._counter}")


class ExpectedMembers(Testcase):
	"""A mixin-class' expectations are collected at class construction time and checked on instantiation."""

	def test_AMixinIsNeverMissingAnything(self) -> None:
		"""A mixin-class can't provide what it expects from its host class, so it is never incomplete."""

		self.assertEqual({"_counter": "Mixin", "Write": "Mixin"}, Mixin.__expectedMembers__)
		self.assertEqual(tuple(), Mixin.__missingMembers__)

	def test_FulfilledExpectation(self) -> None:
		class Application(Host, Mixin):
			pass

		self.assertEqual({"_counter": "Mixin", "Write": "Mixin"}, Application.__expectedMembers__)
		self.assertEqual(tuple(), Application.__missingMembers__)
		self.assertTrue(Application().Report())

	def test_MissingMethod(self) -> None:
		class Application(HalfHost, Mixin):
			pass

		self.assertEqual(("Write", ), Application.__missingMembers__)
		with self.assertRaises(UnfulfilledExpectationError) as exceptionCapture:
			Application()

		self.assertEqual("Class 'Application' doesn't provide every expected member.", str(exceptionCapture.exception))
		self.assertIn("Missing 'Write', expected by 'Mixin'.", exceptionCapture.exception.__notes__)

	def test_MissingField(self) -> None:
		class NoCounter(metaclass=ExtendedType, slots=True):
			def Write(self, message: str) -> bool:
				return True

		class Application(NoCounter, Mixin):
			pass

		with self.assertRaises(UnfulfilledExpectationError) as exceptionCapture:
			Application()

		self.assertIn("Missing '_counter', expected by 'Mixin'.", exceptionCapture.exception.__notes__)

	def test_EveryMissingMemberIsReported(self) -> None:
		class Empty(metaclass=ExtendedType, slots=True):
			pass

		class Application(Empty, Mixin):
			pass

		self.assertEqual(("_counter", "Write"), Application.__missingMembers__)
		with self.assertRaises(UnfulfilledExpectationError) as exceptionCapture:
			Application()

		notes = exceptionCapture.exception.__notes__
		self.assertIn("Missing '_counter', expected by 'Mixin'.", notes)
		self.assertIn("Missing 'Write', expected by 'Mixin'.", notes)

	def test_NoExpectationIsAlwaysFulfilled(self) -> None:
		class Plain(metaclass=ExtendedType, slots=True):
			pass

		self.assertEqual({}, Plain.__expectedMembers__)
		self.assertEqual(tuple(), Plain.__missingMembers__)


class AbstractClasses(Testcase):
	"""An abstract class is allowed to stay incomplete, and abstractness wins over an unfulfilled expectation."""

	def test_AbstractClassReportsAbstractness(self) -> None:
		@abstractclass
		class Application(HalfHost, Mixin):
			pass

		self.assertTrue(Application.__isAbstract__)
		self.assertEqual(("Write", ), Application.__missingMembers__)
		with self.assertRaises(AbstractClassError):
			Application()

	def test_ClassWithAnAbstractMethodFulfillsTheExpectation(self) -> None:
		"""An abstract method is a member, so it satisfies the expectation - and abstractness rejects instantiation."""

		class Intermediate(HalfHost, Mixin):
			@abstractmethod
			def Write(self, message: str) -> bool:
				...

		self.assertTrue(Intermediate.__isAbstract__)
		self.assertEqual(tuple(), Intermediate.__missingMembers__)

	def test_TheDerivedClassIsCheckedAgain(self) -> None:
		@abstractclass
		class Intermediate(HalfHost, Mixin):
			pass

		class Application(Intermediate):
			pass

		with self.assertRaises(UnfulfilledExpectationError) as exceptionCapture:
			Application()

		self.assertIn("Missing 'Write', expected by 'Mixin'.", exceptionCapture.exception.__notes__)

	def test_ASubclassThatFulfillsItIsInstantiable(self) -> None:
		class Incomplete(HalfHost, Mixin):
			pass

		class Application(Incomplete):
			def Write(self, message: str) -> bool:
				return True

		self.assertEqual(tuple(), Application.__missingMembers__)
		self.assertIsInstance(Application(), Application)


class Inheritance(Testcase):
	"""An expectation survives until a class can satisfy it."""

	def test_ExpectationIsInherited(self) -> None:
		class DerivedMixin(Mixin, mixin=True):
			pass

		self.assertEqual({"_counter": "Mixin", "Write": "Mixin"}, DerivedMixin.__expectedMembers__)

		class Application(Host, DerivedMixin):
			pass

		self.assertTrue(Application().Report())

	def test_ExpectationsAreUnioned(self) -> None:
		"""Two mixins expecting the same member: the leftmost base is reported, deterministically."""

		class SecondMixin(metaclass=ExtendedType, mixin=True, expects=("Write",)):
			pass

		class Application(Host, Mixin, SecondMixin):
			pass

		self.assertEqual({"_counter": "Mixin", "Write": "Mixin"}, Application.__expectedMembers__)

	def test_AClassCanExpectFromItsOwnSubclasses(self) -> None:
		"""'expects' isn't limited to mixins - a base-class can state what its subclasses must provide."""

		@abstractclass
		class Base(metaclass=ExtendedType, slots=True, expects=("Write",)):
			pass

		class Application(Base):
			pass

		with self.assertRaises(UnfulfilledExpectationError):
			Application()

	def test_TheDecoratorFormKeepsTheExpectation(self) -> None:
		"""'@mixin' recreates the class, which must not drop what it expects."""

		class Decorated(metaclass=ExtendedType, mixin=True, expects=("Write",)):
			pass

		Recreated = mixin(Decorated)

		self.assertEqual({"Write": "Decorated"}, Recreated.__expectedMembers__)

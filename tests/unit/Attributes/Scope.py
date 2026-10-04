# ==================================================================================================================== #
#             _____           _ _                  _   _   _        _ _           _                                    #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _     / \ | |_| |_ _ __(_) |__  _   _| |_ ___  ___                         #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` |   / _ \| __| __| '__| | '_ \| | | | __/ _ \/ __|                        #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_ / ___ \ |_| |_| |  | | |_) | |_| | ||  __/\__ \                        #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_/   \_\__|\__|_|  |_|_.__/ \__,_|\__\___||___/                        #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
Unit tests for an attribute's scope: the language entities - classes, methods, functions - it can be applied to.
"""
from pyTooling.Attributes  import Attribute, AttributeScope, AttributeScopeError
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Testing     import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class ClassOnly(Attribute):
	_scope = AttributeScope.Class


class MethodOnly(Attribute):
	_scope = AttributeScope.Method


class FunctionOnly(Attribute):
	_scope = AttributeScope.Function


class Enforcement(Testcase):
	"""An attribute applied to an entity its scope doesn't allow raises, naming the attribute and the entity."""

	def test_ClassScopedOnAFunction(self) -> None:
		with self.assertRaises(AttributeScopeError) as context:
			@ClassOnly()
			def function() -> None:
				pass

		self.assertEqual(
			"Attribute 'ClassOnly' can't be applied to function 'Enforcement.test_ClassScopedOnAFunction.<locals>.function'.",
			str(context.exception)
		)
		self.assertIn("Its scope is 'Class'.", context.exception.__notes__)

	def test_FunctionScopedOnAClass(self) -> None:
		with self.assertRaises(AttributeScopeError):
			@FunctionOnly()
			class Class:
				pass

	def test_FunctionScopedOnAMethod(self) -> None:
		"""A function defined in a class body is a method, although the class doesn't exist while the decorator runs."""
		with self.assertRaises(AttributeScopeError):
			class Class:
				@FunctionOnly()
				def method(self) -> None:
					pass

	def test_MethodScopedOnAFunction(self) -> None:
		with self.assertRaises(AttributeScopeError):
			@MethodOnly()
			def function() -> None:
				pass

	def test_NothingIsRegisteredWhenRejected(self) -> None:
		with self.assertRaises(AttributeScopeError):
			@ClassOnly()
			def function() -> None:
				pass

		self.assertEqual([], list(ClassOnly.GetFunctions()))


class Allowed(Testcase):
	"""An entity the scope allows is accepted and registered."""

	def test_MethodScopedOnAMethod(self) -> None:
		class Class(metaclass=ExtendedType):
			@MethodOnly()
			def method(self) -> None:
				pass

		self.assertIn(Class.method, list(MethodOnly.GetMethods()))

	def test_FunctionScopedOnANestedFunction(self) -> None:
		@FunctionOnly()
		def function() -> None:
			pass

		self.assertIn(function, list(FunctionOnly.GetFunctions()))

	def test_ClassScopedOnAClass(self) -> None:
		@ClassOnly()
		class Class:
			pass

		self.assertIn(Class, list(ClassOnly.GetClasses()))

	def test_AnyScopeAcceptsEverything(self) -> None:
		@Attribute()
		class Class:
			@Attribute()
			def method(self) -> None:
				pass

		@Attribute()
		def function() -> None:
			pass


class ScopeProperty(Testcase):
	"""'Scope' is read from an attribute instance; '_scope' on the class."""

	def test_Instance(self) -> None:
		self.assertEqual(AttributeScope.Method, MethodOnly().Scope)
		self.assertEqual(AttributeScope.Any, Attribute().Scope)


class SubClassFilter(Testcase):
	"""'GetAttributes' includes the attributes of derived attribute classes only when asked to."""

	def test_IncludeSubClasses(self) -> None:
		class Base(Attribute):
			pass

		class Derived(Base):
			pass

		class Class(metaclass=ExtendedType):
			@Base()
			@Derived()
			def method(self) -> None:
				pass

		self.assertEqual(2, len(Base.GetAttributes(Class.method)))
		self.assertEqual(1, len(Base.GetAttributes(Class.method, includeSubClasses=False)))
		self.assertIs(Base, type(Base.GetAttributes(Class.method, includeSubClasses=False)[0]))

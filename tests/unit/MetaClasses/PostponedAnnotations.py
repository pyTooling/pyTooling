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
#
"""
Unit tests for :class:`~pyTooling.MetaClasses.ExtendedType` under postponed annotation evaluation.

This module opts into :pep:`563` - ``from __future__ import annotations`` - which turns every annotation in it into
a string. The meta-class has to reach the same conclusions as it does for evaluated annotations; the rest of the
testsuite covers that other half.
"""
from __future__ import annotations

from typing import ClassVar, Optional as Nullable, List, Dict

from pyTooling.MetaClasses import ExtendedType, mixin
from pyTooling.Testing     import Testcase


class Node(metaclass=ExtendedType, slots=True):
	"""A class referencing itself without quotes - the reason to use the future import at all."""

	COUNT:     ClassVar[int] = 0        #: Number of nodes created so far.
	_parent:   Nullable[Node]           #: Reference to the parent node.
	_children: List[Node]               #: References to the child nodes.
	_index:    Dict[str, Node]          #: Lookup table of nodes by name.

	def __init__(self, parent: Nullable[Node] = None) -> None:
		"""
		Initialize a node.

		:param parent: Optional, reference to the parent node.
		"""
		self._parent = parent
		self._children = []
		self._index = {}
		Node.COUNT += 1


@mixin
class Extension(metaclass=ExtendedType):
	"""A mixin contributing one field."""

	_extra: str                         #: Field contributed by the mixin.


class Derived(Node, Extension):
	"""A class combining an inherited class and a mixin, both annotated as strings."""

	_own: int                           #: Field of this class.

	def __init__(self) -> None:
		"""Initialize the derived node."""
		super().__init__()
		self._extra = "extra"
		self._own = 1


class Unresolvable(metaclass=ExtendedType, slots=True):
	"""Annotations naming something that exists nowhere - the class must still be created."""

	MARKER: ClassVar[NotAType] = "kept"  # noqa: F821  #: A class variable annotated with an unknown type.
	_field: AlsoNotAType                 # noqa: F821  #: A field annotated with an unknown type.


class PostponedAnnotations(Testcase):
	def test_AClassVariableIsNotASlot(self) -> None:
		"""``ClassVar[int]`` reads as the string ``"ClassVar[int]"`` here, and must still not become a slot."""
		self.assertNotIn("COUNT", Node.__slots__)
		self.assertEqual(("_parent", "_children", "_index"), Node.__slots__)

	def test_AClassVariableKeepsItsValue(self) -> None:
		"""A ``ClassVar`` turned into a slot loses its initial value to the slot descriptor."""
		self.assertIsInstance(Node.COUNT, int)

	def test_AnUnquotedSelfReferenceWorks(self) -> None:
		root = Node()
		child = Node(root)

		self.assertIs(root, child._parent)

	def test_SlotsAreEnforced(self) -> None:
		node = Node()

		with self.assertRaises(AttributeError):
			node.unknown = 1

	def test_AMixinContributesItsField(self) -> None:
		derived = Derived()

		self.assertEqual("extra", derived._extra)
		self.assertEqual(1, derived._own)
		self.assertIn("_extra", Derived.__slots__)
		self.assertIn("_own", Derived.__slots__)

	def test_AnUnresolvableAnnotationIsNoError(self) -> None:
		"""A forward reference nothing can resolve keeps its string form, and is classified by its text."""
		self.assertEqual("kept", Unresolvable.MARKER)
		self.assertEqual(("_field", ), Unresolvable.__slots__)

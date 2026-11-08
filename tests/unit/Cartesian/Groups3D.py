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
# Copyright 2026-2026 Patrick Lehmann - Boetzingen, Germany                                                            #
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
Unit tests for :mod:`pyTooling.Cartesian3D.Groups` - groups, frames, absolute coordinates and mirroring.
"""
from math                         import isclose, pi

from pyTooling.Cartesian3D        import Point3D, Offset3D, BoundingBox3D, Alignment3D, Element3D, Segment3D, \
                                         LineSegment3D
from pyTooling.Cartesian3D.Groups import Group3D
from pyTooling.Cartesian2D        import AlreadyOwnedError, NotOwnedError, DuplicatePointError, GroupCycleError, \
                                         NotInSameFrameError
from pyTooling.Cartesian2D.Groups import EmptyGroupError
from pyTooling.Exceptions         import EmptyError
from pyTooling.MetaClasses        import AbstractClassError
from pyTooling.Testing            import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(Testcase):
	def test_Element(self) -> None:
		with self.assertRaises(AbstractClassError):
			_ = Element3D()

	def test_Group(self) -> None:
		group = Group3D()

		self.assertIsInstance(group, Element3D)
		self.assertTupleEqual((0, 0, 0), group.Offset.ToTuple())
		self.assertTupleEqual((), group.Children)
		self.assertIsNone(group.Parent)
		self.assertIsNone(group.Frame)

	def test_Group_Offset(self) -> None:
		"""The offset is copied."""
		offset = Offset3D(3, 4, 5)

		group = Group3D(offset)

		self.assertIsNot(offset, group.Offset)
		self.assertTupleEqual((3, 4, 5), group.Offset.ToTuple())

	def test_Group_Children(self) -> None:
		line1 =    LineSegment3D(Point3D(0, 0, 0), Point3D(2, 0, 0))
		line2 =    LineSegment3D(Point3D(0, 0, 0), Point3D(0, 0, 2))
		subgroup = Group3D()

		group = Group3D(Offset3D(5, 5, 5), (line1, line2, subgroup))

		self.assertEqual(3, len(group.Children))
		self.assertIs(line1, group.Children[0])
		self.assertIs(line2, group.Children[1])
		self.assertIs(subgroup, group.Children[2])
		self.assertIs(group, line1.Parent)
		self.assertIs(group, line2.Parent)
		self.assertIs(group, subgroup.Parent)

	def test_Group_Generator(self) -> None:
		group = Group3D(children=(LineSegment3D(Point3D(x, 0, 0), Point3D(x, 1, 1)) for x in range(3)))

		self.assertEqual(3, len(group.Children))
		for child in group.Children:
			self.assertIs(group, child.Parent)

	def test_Group_OffsetTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Group3D((3, 4, 5))

		self.assertEqual("Parameter 'offset' is not of type 'Offset3D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_Group_ChildrenInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Group3D(children=3)

		self.assertEqual("Parameter 'children' is not iterable.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Group_ChildNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Group3D(children=(LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1)), None))

		self.assertEqual("An element of parameter 'children' is None.", str(context.exception))

	def test_Group_ChildPoint(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Group3D(children=(Point3D(1, 1, 1), ))

		self.assertEqual("An element of parameter 'children' is not of type 'Element3D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian3D.Point3D'."], context.exception.__notes__)

	def test_Group_ChildOwned(self) -> None:
		line =   LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1))
		group1 = Group3D(children=(line, ))

		with self.assertRaises(AlreadyOwnedError) as context:
			_ = Group3D(children=(line, ))

		self.assertEqual("Element is owned by another element already.", str(context.exception))
		self.assertListEqual(
			["Got LineSegment3D((0, 0, 0), (1, 1, 1)) owned by Group3D((0, 0, 0), children=1)."],
			context.exception.__notes__
		)
		self.assertIsInstance(context.exception.__cause__, ValueError)
		self.assertEqual(
			"An element of parameter 'children' belongs to another element.",
			str(context.exception.__cause__)
		)
		self.assertIs(group1, line.Parent)

	def test_Group_ChildTwice(self) -> None:
		line1 = LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1))
		line2 = LineSegment3D(Point3D(0, 0, 0), Point3D(2, 0, 0))

		with self.assertRaises(ValueError) as context:
			_ = Group3D(children=(line2, line1, line1))

		self.assertEqual("An element of parameter 'children' is given twice.", str(context.exception))
		self.assertListEqual(["Got LineSegment3D((0, 0, 0), (1, 1, 1))."], context.exception.__notes__)
		self.assertIsNone(line1.Parent)
		self.assertIsNone(line2.Parent)

	def test_repr(self) -> None:
		group = Group3D(Offset3D(1, 2, 3), (LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1)), ))

		self.assertEqual("Group3D((1, 2, 3), children=1)", repr(group))


class Hashing(Testcase):
	def test_Group(self) -> None:
		"""A group defines no ``__eq__``: it hashes by identity."""
		self.assertEqual(2, len({Group3D(), Group3D()}))


class Membership(Testcase):
	def test_AddChild(self) -> None:
		line1 = LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1))
		line2 = LineSegment3D(Point3D(0, 0, 0), Point3D(2, 0, 0))
		group = Group3D(children=(line1, ))

		group.AddChild(line2)

		self.assertIs(group, line2.Parent)
		self.assertTupleEqual((line1, line2), group.Children)
		self.assertTupleEqual(((0, 0, 0), (2, 0, 0)), line2.ToTuple())

	def test_AddChild_None(self) -> None:
		group = Group3D()

		with self.assertRaises(ValueError) as context:
			group.AddChild(None)

		self.assertEqual("Parameter 'child' is None.", str(context.exception))

	def test_AddChild_Point(self) -> None:
		group = Group3D()

		with self.assertRaises(TypeError) as context:
			group.AddChild(Point3D(1, 1, 1))

		self.assertEqual("Parameter 'child' is not of type 'Element3D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian3D.Point3D'."], context.exception.__notes__)

	def test_AddChild_Owned(self) -> None:
		line =   LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1))
		group1 = Group3D(children=(line, ))
		group2 = Group3D()

		with self.assertRaises(AlreadyOwnedError) as context:
			group2.AddChild(line)

		self.assertEqual("Element is owned by another element already.", str(context.exception))
		self.assertListEqual(
			[
				"Got LineSegment3D((0, 0, 0), (1, 1, 1)) owned by Group3D((0, 0, 0), children=1).",
				"Use 'MoveTo' to move it between groups."
			],
			context.exception.__notes__
		)
		self.assertEqual("Parameter 'child' belongs to another element.", str(context.exception.__cause__))
		self.assertIs(group1, line.Parent)
		self.assertTupleEqual((), group2.Children)

	def test_AddChild_Itself(self) -> None:
		group = Group3D()

		with self.assertRaises(GroupCycleError) as context:
			group.AddChild(group)

		self.assertEqual("Group would contain itself.", str(context.exception))
		self.assertListEqual(
			["Got Group3D((0, 0, 0), children=0) as parent of Group3D((0, 0, 0), children=0)."],
			context.exception.__notes__
		)
		self.assertEqual(
			"Parameter 'parent' is this element or one of its descendants.",
			str(context.exception.__cause__)
		)
		self.assertIsNone(group.Parent)

	def test_AddChild_Ancestor(self) -> None:
		inner = Group3D()
		outer = Group3D(children=(Group3D(children=(inner, )), ))

		with self.assertRaises(GroupCycleError):
			inner.AddChild(outer)

		self.assertIsNone(outer.Parent)
		self.assertTupleEqual((), inner.Children)

	def test_RemoveChild(self) -> None:
		line =  LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1))
		group = Group3D(Offset3D(5, 5, 5), (line, ))

		group.RemoveChild(line)

		self.assertIsNone(line.Parent)
		self.assertTupleEqual((), group.Children)
		self.assertTupleEqual(((0, 0, 0), (1, 1, 1)), line.ToTuple())

	def test_RemoveChild_None(self) -> None:
		group = Group3D()

		with self.assertRaises(ValueError) as context:
			group.RemoveChild(None)

		self.assertEqual("Parameter 'child' is None.", str(context.exception))

	def test_RemoveChild_Point(self) -> None:
		group = Group3D()

		with self.assertRaises(TypeError) as context:
			group.RemoveChild(Point3D(1, 1, 1))

		self.assertEqual("Parameter 'child' is not of type 'Element3D'.", str(context.exception))

	def test_RemoveChild_NotAChild(self) -> None:
		line =   LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1))
		group1 = Group3D(children=(line, ))
		group2 = Group3D()

		with self.assertRaises(NotOwnedError) as context:
			group2.RemoveChild(line)

		self.assertEqual("Element isn't a child of this Group3D.", str(context.exception))
		self.assertListEqual(
			["Got LineSegment3D((0, 0, 0), (1, 1, 1)) owned by Group3D((0, 0, 0), children=1)."],
			context.exception.__notes__
		)
		self.assertEqual("Parameter 'child' isn't a child of this Group3D.", str(context.exception.__cause__))
		self.assertIs(group1, line.Parent)

	def test_Parent(self) -> None:
		"""Assigning a parent moves the element and keeps its local coordinates."""
		line =   LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1))
		group1 = Group3D(Offset3D(5, 0, 0), (line, ))
		group2 = Group3D(Offset3D(0, 5, 0))

		line.Parent = group2

		self.assertIs(group2, line.Parent)
		self.assertTupleEqual((), group1.Children)
		self.assertTupleEqual((line, ), group2.Children)
		self.assertTupleEqual((1, 1, 1), line.End.ToTuple())
		self.assertTupleEqual((1, 6, 1), line.End.Absolute.ToTuple())

	def test_Parent_None(self) -> None:
		line =  LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1))
		group = Group3D(Offset3D(5, 0, 0), (line, ))

		line.Parent = None

		self.assertIsNone(line.Parent)
		self.assertTupleEqual((), group.Children)

	def test_Parent_Same(self) -> None:
		line1 = LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1))
		line2 = LineSegment3D(Point3D(0, 0, 0), Point3D(2, 0, 0))
		group = Group3D(children=(line1, line2))

		line1.Parent = group

		self.assertTupleEqual((line1, line2), group.Children)

	def test_Parent_int(self) -> None:
		line = LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1))

		with self.assertRaises(TypeError) as context:
			line.Parent = 1

		self.assertEqual("Parameter 'parent' is not of type 'Group3D'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)
		self.assertIsNone(line.Parent)


class ParentParameter(Testcase):
	"""Parameter 'parent' registers the new element in the group, as ``AddChild`` does."""

	def test_Segment(self) -> None:
		group = Group3D()

		segment = Segment3D(Point3D(1, 2, 3), Point3D(4, 6, 8), parent=group)

		self.assertIs(group, segment.Parent)
		self.assertTupleEqual((segment, ), group.Children)
		self.assertIs(segment, segment.Start.Parent)
		self.assertIs(segment, segment.End.Parent)
		self.assertIs(group, segment.Start.Frame)

	def test_LineSegment(self) -> None:
		group = Group3D()

		segment = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8), parent=group)

		self.assertIs(group, segment.Parent)
		self.assertTupleEqual((segment, ), group.Children)
		self.assertIs(group, segment.Frame)

	def test_LineSegment_Reference(self) -> None:
		"""A segment in a group owns its points, as a standalone one."""
		group = Group3D()
		start = Point3D(1, 2, 3)
		end =   Point3D(4, 6, 8)

		segment = LineSegment3D(start, end, copyPoints=False, parent=group)

		self.assertIs(start, segment.Start)
		self.assertIs(end, segment.End)
		self.assertIs(segment, start.Parent)
		self.assertIs(segment, end.Parent)

		replacement =   Point3D(7, 8, 9)
		segment.Start = replacement

		self.assertIs(segment, replacement.Parent)
		self.assertIsNone(start.Parent)

	def test_LineSegment_Int(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8), parent=1)

		self.assertEqual("Parameter 'parent' is not of type 'Group3D'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_LineSegment_Positional(self) -> None:
		with self.assertRaises(TypeError):
			_ = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8), Group3D())

	def test_LineSegment_Failing(self) -> None:
		group = Group3D()
		point = Point3D(1, 2, 3)

		with self.assertRaises(DuplicatePointError):
			_ = LineSegment3D(point, point, copyPoints=False, parent=group)

		self.assertTupleEqual((), group.Children)

	def test_Group(self) -> None:
		parent = Group3D()
		child =  LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		group = Group3D(Offset3D(1, 1, 1), (child, ), parent=parent)

		self.assertIs(parent, group.Parent)
		self.assertTupleEqual((group, ), parent.Children)
		self.assertIs(group, child.Parent)
		self.assertTupleEqual((2, 3, 4), child.Start.Absolute.ToTuple())

	def test_Group_Int(self) -> None:
		"""A wrong parent is found before the group takes the given children."""
		child = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(TypeError) as context:
			_ = Group3D(children=(child, ), parent=1)

		self.assertEqual("Parameter 'parent' is not of type 'Group3D'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)
		self.assertIsNone(child.Parent)

	def test_Group_Positional(self) -> None:
		with self.assertRaises(TypeError):
			_ = Group3D(None, None, Group3D())

	def test_Group_Failing(self) -> None:
		group = Group3D()

		with self.assertRaises(TypeError):
			_ = Group3D(offset=(1, 1, 1), parent=group)

		self.assertTupleEqual((), group.Children)

	def test_Group_ParentIsChild(self) -> None:
		"""The new group can't be a child of its own child. The child stays free."""
		child = Group3D()

		with self.assertRaises(GroupCycleError) as context:
			_ = Group3D(children=(child, ), parent=child)

		self.assertEqual("Group would contain itself.", str(context.exception))
		self.assertEqual("Parameter 'parent' is this element or one of its descendants.", str(context.exception.__cause__))
		self.assertIsNone(child.Parent)
		self.assertTupleEqual((), child.Children)

	def test_Group_ParentInsideChild(self) -> None:
		inner = Group3D()
		child = Group3D(children=(inner, ))

		with self.assertRaises(GroupCycleError):
			_ = Group3D(children=(child, ), parent=inner)

		self.assertIsNone(child.Parent)
		self.assertTupleEqual((), inner.Children)

	def test_Point(self) -> None:
		"""A point's parent sets the owner only: the group's children don't change."""
		group = Group3D()

		point = Point3D(1, 2, 3, parent=group)

		self.assertIs(group, point.Parent)
		self.assertIs(group, point.Frame)
		self.assertTupleEqual((), group.Children)


class Frames(Testcase):
	def test_Frame(self) -> None:
		line =  LineSegment3D(Point3D(0, 0, 0), Point3D(2, 0, 0))
		inner = Group3D(children=(line, ))
		outer = Group3D(children=(inner, ))

		self.assertIs(inner, line.Frame)
		self.assertIs(inner, line.Start.Frame)
		self.assertIs(outer, inner.Frame)
		self.assertIsNone(outer.Frame)

	def test_Point_Minus_Point(self) -> None:
		line1 = LineSegment3D(Point3D(1, 1, 1), Point3D(2, 2, 2))
		line2 = LineSegment3D(Point3D(4, 5, 6), Point3D(7, 7, 7))
		_ =     Group3D(Offset3D(10, 10, 10), (line1, line2))

		offset = line2.Start - line1.Start

		self.assertTupleEqual((3, 4, 5), offset.ToTuple())

	def test_Point_Minus_Point_OtherGroup(self) -> None:
		line1 = LineSegment3D(Point3D(1, 1, 1), Point3D(2, 2, 2))
		line2 = LineSegment3D(Point3D(4, 5, 6), Point3D(7, 7, 7))
		_ =     Group3D(Offset3D(10, 10, 10), (line1, ))
		_ =     Group3D(Offset3D(20, 20, 20), (line2, ))

		with self.assertRaises(NotInSameFrameError) as context:
			_ = line2.Start - line1.Start

		self.assertEqual("Points are in different frames.", str(context.exception))
		self.assertListEqual(
			["Got points (4, 5, 6) and (1, 1, 1).", "Subtract the points' 'Absolute' positions instead."],
			context.exception.__notes__
		)
		self.assertEqual("Parameter 'other' is in another frame.", str(context.exception.__cause__))

	def test_Point_Minus_Point_Absolute(self) -> None:
		line1 = LineSegment3D(Point3D(1, 1, 1), Point3D(2, 2, 2))
		line2 = LineSegment3D(Point3D(4, 5, 6), Point3D(7, 7, 7))
		_ =     Group3D(Offset3D(10, 10, 10), (line1, ))
		_ =     Group3D(Offset3D(20, 20, 20), (line2, ))

		offset = line2.Start.Absolute - line1.Start.Absolute

		self.assertTupleEqual((13, 14, 15), offset.ToTuple())

	def test_AngleTo_OtherGroup(self) -> None:
		line1 = LineSegment3D(Point3D(0, 0, 0), Point3D(1, 0, 0))
		line2 = LineSegment3D(Point3D(0, 0, 0), Point3D(0, 0, 1))
		_ =     Group3D(children=(line1, ))

		with self.assertRaises(NotInSameFrameError) as context:
			_ = line1.AngleTo(line2)

		self.assertEqual("Line segments are in different frames.", str(context.exception))
		self.assertEqual("Parameter 'other' is in another frame.", str(context.exception.__cause__))

	def test_AngleTo_SameGroup(self) -> None:
		line1 = LineSegment3D(Point3D(0, 0, 0), Point3D(1, 0, 0))
		line2 = LineSegment3D(Point3D(0, 0, 0), Point3D(0, 0, 1))
		_ =     Group3D(children=(line1, line2))

		self.assertTrue(isclose(pi / 2, line1.AngleTo(line2)))


class Absolute(Testcase):
	def test_Point(self) -> None:
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		inner = Group3D(Offset3D(10, 0, 0), (line, ))
		_ =     Group3D(Offset3D(0, 20, 30), (inner, ))

		point = line.Start.Absolute

		self.assertIs(Point3D, type(point))
		self.assertIsNone(point.Parent)
		self.assertTupleEqual((11, 22, 33), point.ToTuple())
		self.assertTupleEqual((1, 2, 3), line.Start.ToTuple())

	def test_Point_NoFrame(self) -> None:
		point = Point3D(1, 2, 3)

		absolute = point.Absolute

		self.assertIsNot(point, absolute)
		self.assertTupleEqual((1, 2, 3), absolute.ToTuple())

	def test_AbsoluteOffset(self) -> None:
		inner = Group3D(Offset3D(10, 0, 0))
		outer = Group3D(Offset3D(0, 20, 30), (inner, ))

		self.assertTupleEqual((10, 20, 30), inner.AbsoluteOffset.ToTuple())
		self.assertTupleEqual((0, 20, 30), outer.AbsoluteOffset.ToTuple())
		self.assertIsNot(outer.Offset, outer.AbsoluteOffset)

	def test_AbsoluteBoundingBox(self) -> None:
		line1 = LineSegment3D(Point3D(1, 2, 3), Point3D(2, 3, 4))
		line2 = LineSegment3D(Point3D(0, 0, 0), Point3D(2, 0, 0))
		inner = Group3D(Offset3D(10, 0, 0), (line1, line2))
		outer = Group3D(Offset3D(0, 20, 30), (inner, ))

		self.assertEqual(BoundingBox3D(11, 22, 33, 12, 23, 34), line1.AbsoluteBoundingBox)
		self.assertEqual(BoundingBox3D(10, 20, 30, 12, 20, 30), line2.AbsoluteBoundingBox)
		self.assertEqual(BoundingBox3D(10, 20, 30, 12, 23, 34), inner.AbsoluteBoundingBox)
		self.assertEqual(BoundingBox3D(10, 20, 30, 12, 23, 34), outer.AbsoluteBoundingBox)


class Bounds(Testcase):
	def test_Group(self) -> None:
		line1 = LineSegment3D(Point3D(0, 1, 2), Point3D(2, 3, 4))
		line2 = LineSegment3D(Point3D(-3, 0, 0), Point3D(0, 0, 0))
		group = Group3D(Offset3D(10, 0, 0), (line1, line2))

		self.assertEqual(BoundingBox3D(7, 0, 0, 12, 3, 4), group.BoundingBox)

	def test_Group_Nested(self) -> None:
		inner = Group3D(Offset3D(5, 5, 5), (LineSegment3D(Point3D(-1, -1, -1), Point3D(1, 1, 1)), ))
		outer = Group3D(Offset3D(100, 0, 0), (inner, LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1))))

		self.assertEqual(BoundingBox3D(4, 4, 4, 6, 6, 6), inner.BoundingBox)
		self.assertEqual(BoundingBox3D(100, 0, 0, 106, 6, 6), outer.BoundingBox)

	def test_Group_Empty(self) -> None:
		group = Group3D(Offset3D(1, 2, 3))

		with self.assertRaises(EmptyGroupError) as context:
			_ = group.BoundingBox

		self.assertIsInstance(context.exception, EmptyError)
		self.assertEqual("Group3D has no children.", str(context.exception))
		self.assertListEqual(["Got Group3D((1, 2, 3), children=0)."], context.exception.__notes__)

	def test_Group_NestedEmpty(self) -> None:
		group = Group3D(children=(LineSegment3D(Point3D(0, 0, 0), Point3D(1, 1, 1)), Group3D()))

		with self.assertRaises(EmptyGroupError):
			_ = group.BoundingBox


class Moving(Testcase):
	def test_Move(self) -> None:
		"""Moving a group changes its offset only."""
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		group = Group3D(Offset3D(10, 0, 0), (line, ))

		group.Move(Offset3D(1, 1, 1))

		self.assertTupleEqual((11, 1, 1), group.Offset.ToTuple())
		self.assertTupleEqual((1, 2, 3), line.Start.ToTuple())
		self.assertTupleEqual((12, 3, 4), line.Start.Absolute.ToTuple())

	def test_Move_None(self) -> None:
		group = Group3D()

		with self.assertRaises(ValueError) as context:
			group.Move(None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))

	def test_Move_tuple(self) -> None:
		group = Group3D()

		with self.assertRaises(TypeError) as context:
			group.Move((1, 1, 1))

		self.assertEqual("Parameter 'offset' is not of type 'Offset3D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_Offset(self) -> None:
		group =  Group3D()
		offset = Offset3D(3, 4, 5)

		group.Offset = offset

		self.assertIsNot(offset, group.Offset)
		self.assertTupleEqual((3, 4, 5), group.Offset.ToTuple())

	def test_Offset_None(self) -> None:
		group = Group3D(Offset3D(1, 2, 3))

		with self.assertRaises(ValueError) as context:
			group.Offset = None

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), group.Offset.ToTuple())

	def test_Offset_tuple(self) -> None:
		group = Group3D(Offset3D(1, 2, 3))

		with self.assertRaises(TypeError) as context:
			group.Offset = (3, 4, 5)

		self.assertEqual("Parameter 'offset' is not of type 'Offset3D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_MoveTo(self) -> None:
		"""Moving a segment to another group keeps its absolute position."""
		line =   LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		_ =      Group3D(Offset3D(10, 0, 0), (line, ))
		target = Group3D(Offset3D(0, 20, 30))

		line.MoveTo(target)

		self.assertIs(target, line.Parent)
		self.assertTupleEqual((11, -18, -27), line.Start.ToTuple())
		self.assertTupleEqual((11, 2, 3), line.Start.Absolute.ToTuple())

	def test_MoveTo_LocalPosition(self) -> None:
		line =   LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		_ =      Group3D(Offset3D(10, 0, 0), (line, ))
		target = Group3D(Offset3D(0, 20, 30))

		line.MoveTo(target, keepPosition=False)

		self.assertIs(target, line.Parent)
		self.assertTupleEqual((1, 2, 3), line.Start.ToTuple())
		self.assertTupleEqual((1, 22, 33), line.Start.Absolute.ToTuple())

	def test_MoveTo_None(self) -> None:
		line = LineSegment3D(Point3D(0, 0, 0), Point3D(2, 0, 0))
		_ =    Group3D(Offset3D(10, 5, 1), (line, ))

		line.MoveTo(None)

		self.assertIsNone(line.Parent)
		self.assertTupleEqual(((10, 5, 1), (12, 5, 1)), line.ToTuple())

	def test_MoveTo_Group(self) -> None:
		"""Moving a group changes its offset only: its children keep their local coordinates."""
		line =   LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))
		inner =  Group3D(Offset3D(3, 3, 3), (line, ))
		_ =      Group3D(Offset3D(10, 0, 0), (inner, ))
		target = Group3D(Offset3D(0, 20, 30))

		inner.MoveTo(target)

		self.assertTupleEqual((13, -17, -27), inner.Offset.ToTuple())
		self.assertTupleEqual((1, 2, 3), line.Start.ToTuple())
		self.assertTupleEqual((14, 5, 6), line.Start.Absolute.ToTuple())

	def test_MoveTo_keepPositionNone(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(ValueError) as context:
			line.MoveTo(Group3D(), keepPosition=None)

		self.assertEqual("Parameter 'keepPosition' is None.", str(context.exception))
		self.assertIsNone(line.Parent)

	def test_MoveTo_keepPositionInt(self) -> None:
		line = LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8))

		with self.assertRaises(TypeError) as context:
			line.MoveTo(Group3D(), keepPosition=1)

		self.assertEqual("Parameter 'keepPosition' is not of type 'bool'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_MoveTo_Cycle(self) -> None:
		inner = Group3D(Offset3D(1, 1, 1))
		outer = Group3D(children=(inner, ))

		with self.assertRaises(GroupCycleError):
			outer.MoveTo(inner)

		self.assertTupleEqual((0, 0, 0), outer.Offset.ToTuple())
		self.assertIsNone(outer.Parent)


class Distributing(Testcase):
	def test_X(self) -> None:
		line1 = LineSegment3D(Point3D(-1, 0, 0), Point3D(1, 0, 0))
		line2 = LineSegment3D(Point3D(1, 0, 0), Point3D(5, 0, 0))
		line3 = LineSegment3D(Point3D(3, 5, 1), Point3D(5, 5, 1))
		line4 = LineSegment3D(Point3D(19, 0, 0), Point3D(21, 0, 0))
		group = Group3D(children=(line4, line2, line1, line3))

		group.DistributeX()

		self.assertEqual(BoundingBox3D(-1, 0, 0, 1, 0, 0), line1.BoundingBox)
		self.assertEqual(BoundingBox3D(5, 0, 0, 9, 0, 0), line2.BoundingBox)
		self.assertEqual(BoundingBox3D(13, 5, 1, 15, 5, 1), line3.BoundingBox)
		self.assertEqual(BoundingBox3D(19, 0, 0, 21, 0, 0), line4.BoundingBox)

	def test_Y(self) -> None:
		line1 = LineSegment3D(Point3D(0, 0, 0), Point3D(0, 2, 0))
		line2 = LineSegment3D(Point3D(5, 3, 1), Point3D(5, 4, 1))
		line3 = LineSegment3D(Point3D(1, 9, 2), Point3D(1, 12, 2))
		group = Group3D(children=(line1, line2, line3))

		group.DistributeY()

		self.assertEqual(BoundingBox3D(5, 5, 1, 5, 6, 1), line2.BoundingBox)
		self.assertEqual(BoundingBox3D(1, 9, 2, 1, 12, 2), line3.BoundingBox)

	def test_Z(self) -> None:
		line1 = LineSegment3D(Point3D(0, 0, 0), Point3D(0, 0, 2))
		line2 = LineSegment3D(Point3D(1, 5, 3), Point3D(1, 5, 4))
		line3 = LineSegment3D(Point3D(2, 1, 9), Point3D(2, 1, 12))
		group = Group3D(children=(line3, line1, line2))

		group.DistributeZ()

		self.assertEqual(BoundingBox3D(0, 0, 0, 0, 0, 2), line1.BoundingBox)
		self.assertEqual(BoundingBox3D(1, 5, 5, 1, 5, 6), line2.BoundingBox)
		self.assertEqual(BoundingBox3D(2, 1, 9, 2, 1, 12), line3.BoundingBox)

	def test_TwoChildren(self) -> None:
		line1 = LineSegment3D(Point3D(0, 0, 0), Point3D(1, 0, 0))
		line2 = LineSegment3D(Point3D(3, 0, 0), Point3D(4, 0, 0))
		group = Group3D(children=(line1, line2))

		group.DistributeX()

		self.assertTupleEqual(((0, 0, 0), (1, 0, 0)), line1.ToTuple())
		self.assertTupleEqual(((3, 0, 0), (4, 0, 0)), line2.ToTuple())

	def test_Gap_X(self) -> None:
		line1 = LineSegment3D(Point3D(-1, 0, 0), Point3D(1, 0, 0))
		line2 = LineSegment3D(Point3D(1, 0, 0), Point3D(5, 0, 0))
		line3 = LineSegment3D(Point3D(19, 5, 1), Point3D(21, 5, 1))
		group = Group3D(children=(line3, line2, line1))

		group.DistributeX(3)

		self.assertEqual(BoundingBox3D(-1, 0, 0, 1, 0, 0), line1.BoundingBox)
		self.assertEqual(BoundingBox3D(4, 0, 0, 8, 0, 0), line2.BoundingBox)
		self.assertEqual(BoundingBox3D(11, 5, 1, 13, 5, 1), line3.BoundingBox)

	def test_Gap_Y(self) -> None:
		line1 = LineSegment3D(Point3D(0, 0, 0), Point3D(0, 2, 0))
		line2 = LineSegment3D(Point3D(5, 3, 1), Point3D(5, 4, 1))
		group = Group3D(children=(line1, line2))

		group.DistributeY(0.5)

		self.assertEqual(BoundingBox3D(0, 0, 0, 0, 2, 0), line1.BoundingBox)
		self.assertEqual(BoundingBox3D(5, 2.5, 1, 5, 3.5, 1), line2.BoundingBox)

	def test_Gap_Z(self) -> None:
		line1 = LineSegment3D(Point3D(0, 0, 0), Point3D(0, 0, 2))
		line2 = LineSegment3D(Point3D(1, 5, 3), Point3D(1, 5, 4))
		group = Group3D(children=(line2, line1))

		group.DistributeZ(2)

		self.assertEqual(BoundingBox3D(0, 0, 0, 0, 0, 2), line1.BoundingBox)
		self.assertEqual(BoundingBox3D(1, 5, 4, 1, 5, 5), line2.BoundingBox)

	def test_Gap_Zero(self) -> None:
		line1 = LineSegment3D(Point3D(0, 0, 0), Point3D(1, 0, 0))
		line2 = LineSegment3D(Point3D(5, 0, 0), Point3D(6, 0, 0))
		group = Group3D(children=(line1, line2))

		group.DistributeX(0)

		self.assertTupleEqual(((1, 0, 0), (2, 0, 0)), line2.ToTuple())

	def test_Gap_OneChild(self) -> None:
		line =  LineSegment3D(Point3D(3, 0, 0), Point3D(4, 0, 0))
		group = Group3D(children=(line, ))

		group.DistributeX(1)

		self.assertTupleEqual(((3, 0, 0), (4, 0, 0)), line.ToTuple())

	def test_Gap_Str(self) -> None:
		group = Group3D()

		with self.assertRaises(TypeError) as context:
			group.DistributeX("1")

		self.assertEqual("Parameter 'gap' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Gap_Negative(self) -> None:
		group = Group3D()

		with self.assertRaises(ValueError) as context:
			group.DistributeX(-1)

		self.assertEqual("Parameter 'gap' is negative.", str(context.exception))
		self.assertListEqual(["Got value '-1'."], context.exception.__notes__)

	def test_Gap_Y_Str(self) -> None:
		group = Group3D()

		with self.assertRaises(TypeError) as context:
			group.DistributeY("1")

		self.assertEqual("Parameter 'gap' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Gap_Y_Negative(self) -> None:
		group = Group3D()

		with self.assertRaises(ValueError) as context:
			group.DistributeY(-1)

		self.assertEqual("Parameter 'gap' is negative.", str(context.exception))
		self.assertListEqual(["Got value '-1'."], context.exception.__notes__)

	def test_Gap_Z_Str(self) -> None:
		group = Group3D()

		with self.assertRaises(TypeError) as context:
			group.DistributeZ("1")

		self.assertEqual("Parameter 'gap' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Gap_Z_Negative(self) -> None:
		group = Group3D()

		with self.assertRaises(ValueError) as context:
			group.DistributeZ(-1)

		self.assertEqual("Parameter 'gap' is negative.", str(context.exception))
		self.assertListEqual(["Got value '-1'."], context.exception.__notes__)


class Mirroring(Testcase):
	def test_MirrorX(self) -> None:
		"""A group mirrors its offset at the plane, its children are mirrored at the group's origin."""
		line =  LineSegment3D(Point3D(1, 2, 3), Point3D(3, 4, 5))
		inner = Group3D(Offset3D(3, 4, 5), (line, ))
		outer = Group3D(Offset3D(10, 20, 30), (inner, ))

		outer.MirrorX(Alignment3D.MaxX, 5)

		self.assertTupleEqual((32, 20, 30), outer.Offset.ToTuple())
		self.assertTupleEqual((-3, 4, 5), inner.Offset.ToTuple())
		self.assertTupleEqual(((-1, 2, 3), (-3, 4, 5)), line.ToTuple())
		self.assertTupleEqual((28, 26, 38), line.Start.Absolute.ToTuple())
		self.assertEqual(BoundingBox3D(26, 26, 38, 28, 28, 40), outer.BoundingBox)

	def test_MirrorX_OffsetNone(self) -> None:
		group = Group3D(Offset3D(1, 2, 3))

		with self.assertRaises(ValueError) as context:
			group.MirrorX(Alignment3D.MinX, None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), group.Offset.ToTuple())

	def test_MirrorY_Default(self) -> None:
		"""A group mirrored at its center keeps its bounding box."""
		line =  LineSegment3D(Point3D(0, 0, 0), Point3D(4, 2, 6))
		inner = Group3D(Offset3D(1, 1, 1), (line, ))
		outer = Group3D(Offset3D(10, 20, 30), (inner, ))

		outer.MirrorY()

		self.assertTupleEqual((10, 24, 30), outer.Offset.ToTuple())
		self.assertTupleEqual((1, -1, 1), inner.Offset.ToTuple())
		self.assertTupleEqual(((0, 0, 0), (4, -2, 6)), line.ToTuple())
		self.assertEqual(BoundingBox3D(11, 21, 31, 15, 23, 37), outer.BoundingBox)

	def test_MirrorZ_MinZ(self) -> None:
		line =  LineSegment3D(Point3D(0, 0, 0), Point3D(4, 2, 6))
		group = Group3D(Offset3D(10, 20, 30), (line, ))

		group.MirrorZ(Alignment3D.MinZ)

		self.assertTupleEqual((10, 20, 30), group.Offset.ToTuple())
		self.assertTupleEqual(((0, 0, 0), (4, 2, -6)), line.ToTuple())
		self.assertEqual(BoundingBox3D(10, 20, 24, 14, 22, 30), group.BoundingBox)

	def test_MirrorZ_PlaneMaxY(self) -> None:
		group = Group3D(Offset3D(1, 2, 3))

		with self.assertRaises(ValueError) as context:
			group.MirrorZ(Alignment3D.MaxY)

		self.assertEqual(
			"Parameter 'plane' is not Alignment3D.MinZ, Alignment3D.CenterZ or Alignment3D.MaxZ.",
			str(context.exception)
		)
		self.assertListEqual(["Got value 'Alignment3D.MaxY'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2, 3), group.Offset.ToTuple())

	def test_MirrorZ_Empty(self) -> None:
		group = Group3D(Offset3D(1, 2, 3))

		with self.assertRaises(EmptyGroupError) as context:
			group.MirrorZ()

		self.assertEqual("Group3D has no children.", str(context.exception))
		self.assertTupleEqual((1, 2, 3), group.Offset.ToTuple())


class ElementData(Testcase):
	def test_Group(self) -> None:
		value = object()
		pairs = {"layer": 1}
		group = Group3D(Offset3D(1, 2, 3), value=value, keyValuePairs=pairs)

		self.assertIs(value, group.Value)
		self.assertEqual(1, group["layer"])
		self.assertIsNot(pairs, group._dict)

	def test_Group_Default(self) -> None:
		group = Group3D()

		self.assertIsNone(group.Value)
		self.assertEqual(0, len(group))

	def test_Group_keyValuePairsInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Group3D(keyValuePairs=1)

		self.assertEqual("Parameter 'keyValuePairs' is not a mapping ('dict', ...).", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Group_Value(self) -> None:
		group = Group3D(value=1)

		group.Value = "layer"

		self.assertEqual("layer", group.Value)

	def test_Group_Pairs(self) -> None:
		"""The dictionary syntax addresses the key-value-pairs, not the children."""
		group = Group3D(children=(LineSegment3D(Point3D(1, 2, 3), Point3D(4, 6, 8)), ))

		group["layer"] = 1

		self.assertEqual(1, len(group))
		self.assertIn("layer", group)
		self.assertListEqual(["layer"], list(group))
		self.assertEqual(1, len(group.Children))

		del group["layer"]

		self.assertEqual(0, len(group))

	def test_Group_Parent(self) -> None:
		"""A child with a value and key-value-pairs registers in its parent like any other."""
		parent = Group3D()
		group =  Group3D(value=1, keyValuePairs={"layer": 1}, parent=parent)

		self.assertIs(parent, group.Parent)
		self.assertTupleEqual((group, ), parent.Children)

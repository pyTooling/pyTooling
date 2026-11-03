# ==================================================================================================================== #
#             _____           _ _               ____           _            _             ____  ____                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|__ _ _ __| |_ ___  ___(_) __ _ _ __ |___ \|  _ \                  #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` || |   / _` | '__| __/ _ \/ __| |/ _` | '_ \  __) | | | |                 #
# | |_) | |_| || | (_) | (_) | | | | | | (_| || |__| (_| | |  | ||  __/\__ \ | (_| | | | |/ __/| |_| |                 #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____\__,_|_|   \__\___||___/_|\__,_|_| |_|_____|____/                  #
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
Unit tests for :mod:`pyTooling.Cartesian2D.Groups` - groups, frames, absolute coordinates and distribution.
"""
from math                         import isclose, pi

from pyTooling.Cartesian2D        import Point2D, Offset2D, BoundingBox, Element2D, LineSegment2D, AlreadyOwnedError, \
                                         NotOwnedError, NotInSameFrameError, GroupCycleError
from pyTooling.Cartesian2D.Shapes import Polygon, Circle
from pyTooling.Cartesian2D.Groups import Group, Axis, EmptyGroupError
from pyTooling.MetaClasses        import AbstractClassError
from pyTooling.Testing            import Testcase


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(Testcase):
	def test_Element(self) -> None:
		with self.assertRaises(AbstractClassError):
			_ = Element2D()

	def test_Group(self) -> None:
		group = Group()

		self.assertIsInstance(group, Element2D)
		self.assertTupleEqual((0, 0), group.Offset.ToTuple())
		self.assertTupleEqual((), group.Children)
		self.assertIsNone(group.Parent)
		self.assertIsNone(group.Frame)

	def test_Group_Offset(self) -> None:
		"""The offset is copied."""
		offset = Offset2D(3, 4)

		group = Group(offset)

		self.assertIsNot(offset, group.Offset)
		self.assertTupleEqual((3, 4), group.Offset.ToTuple())

	def test_Group_Children(self) -> None:
		circle =   Circle(Point2D(1, 1), 1)
		line =     LineSegment2D(Point2D(0, 0), Point2D(2, 0))
		subgroup = Group()

		group = Group(Offset2D(5, 5), (circle, line, subgroup))

		self.assertEqual(3, len(group.Children))
		self.assertIs(circle, group.Children[0])
		self.assertIs(line, group.Children[1])
		self.assertIs(subgroup, group.Children[2])
		self.assertIs(group, circle.Parent)
		self.assertIs(group, line.Parent)
		self.assertIs(group, subgroup.Parent)

	def test_Group_Generator(self) -> None:
		group = Group(children=(Circle(Point2D(x, 0), 1) for x in range(3)))

		self.assertEqual(3, len(group.Children))
		for child in group.Children:
			self.assertIs(group, child.Parent)

	def test_Group_OffsetTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Group((3, 4))

		self.assertEqual("Parameter 'offset' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_Group_ChildrenInt(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Group(children=3)

		self.assertEqual("Parameter 'children' is not iterable.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Group_ChildNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Group(children=(Circle(Point2D(1, 1), 1), None))

		self.assertEqual("An element of parameter 'children' is None.", str(context.exception))

	def test_Group_ChildPoint(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Group(children=(Point2D(1, 1), ))

		self.assertEqual("An element of parameter 'children' is not of type 'Element2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Point2D'."], context.exception.__notes__)

	def test_Group_ChildOwned(self) -> None:
		circle = Circle(Point2D(1, 1), 1)
		group1 = Group(children=(circle, ))

		with self.assertRaises(AlreadyOwnedError) as context:
			_ = Group(children=(circle, ))

		self.assertEqual("Element is owned by another element already.", str(context.exception))
		self.assertListEqual(
			["Got Circle((1, 1), 1) owned by Group((0, 0), children=1)."],
			context.exception.__notes__
		)
		self.assertIsInstance(context.exception.__cause__, ValueError)
		self.assertEqual(
			"An element of parameter 'children' belongs to another element.",
			str(context.exception.__cause__)
		)
		self.assertIs(group1, circle.Parent)

	def test_Group_ChildEdge(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		with self.assertRaises(AlreadyOwnedError):
			_ = Group(children=(polygon.Segments[0], ))

		self.assertIs(polygon, polygon.Segments[0].Parent)

	def test_Group_ChildTwice(self) -> None:
		circle = Circle(Point2D(1, 1), 1)
		line =   LineSegment2D(Point2D(0, 0), Point2D(2, 0))

		with self.assertRaises(ValueError) as context:
			_ = Group(children=(line, circle, circle))

		self.assertEqual("An element of parameter 'children' is given twice.", str(context.exception))
		self.assertListEqual(["Got Circle((1, 1), 1)."], context.exception.__notes__)
		self.assertIsNone(circle.Parent)
		self.assertIsNone(line.Parent)

	def test_repr(self) -> None:
		group = Group(Offset2D(1, 2), (Circle(Point2D(1, 1), 1), ))

		self.assertEqual("Group((1, 2), children=1)", repr(group))


class Hashing(Testcase):
	def test_Group(self) -> None:
		"""A group defines no ``__eq__``: it hashes by identity."""
		self.assertEqual(2, len({Group(), Group()}))


class Membership(Testcase):
	def test_AddChild(self) -> None:
		circle = Circle(Point2D(1, 1), 1)
		line =   LineSegment2D(Point2D(0, 0), Point2D(2, 0))
		group =  Group(children=(circle, ))

		group.AddChild(line)

		self.assertIs(group, line.Parent)
		self.assertTupleEqual((circle, line), group.Children)
		self.assertTupleEqual(((0, 0), (2, 0)), line.ToTuple())

	def test_AddChild_None(self) -> None:
		group = Group()

		with self.assertRaises(ValueError) as context:
			group.AddChild(None)

		self.assertEqual("Parameter 'child' is None.", str(context.exception))

	def test_AddChild_Point(self) -> None:
		group = Group()

		with self.assertRaises(TypeError) as context:
			group.AddChild(Point2D(1, 1))

		self.assertEqual("Parameter 'child' is not of type 'Element2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Point2D'."], context.exception.__notes__)

	def test_AddChild_Owned(self) -> None:
		circle = Circle(Point2D(1, 1), 1)
		group1 = Group(children=(circle, ))
		group2 = Group()

		with self.assertRaises(AlreadyOwnedError) as context:
			group2.AddChild(circle)

		self.assertEqual("Element is owned by another element already.", str(context.exception))
		self.assertListEqual(
			["Got Circle((1, 1), 1) owned by Group((0, 0), children=1).", "Use 'MoveTo' to move it between groups."],
			context.exception.__notes__
		)
		self.assertEqual("Parameter 'child' belongs to another element.", str(context.exception.__cause__))
		self.assertIs(group1, circle.Parent)
		self.assertTupleEqual((), group2.Children)

	def test_AddChild_Itself(self) -> None:
		group = Group()

		with self.assertRaises(GroupCycleError) as context:
			group.AddChild(group)

		self.assertEqual("Group would contain itself.", str(context.exception))
		self.assertListEqual(
			["Got Group((0, 0), children=0) as parent of Group((0, 0), children=0)."],
			context.exception.__notes__
		)
		self.assertEqual(
			"Parameter 'parent' is this element or one of its descendants.",
			str(context.exception.__cause__)
		)
		self.assertIsNone(group.Parent)

	def test_AddChild_Ancestor(self) -> None:
		inner = Group()
		outer = Group(children=(Group(children=(inner, )), ))

		with self.assertRaises(GroupCycleError):
			inner.AddChild(outer)

		self.assertIsNone(outer.Parent)
		self.assertTupleEqual((), inner.Children)

	def test_RemoveChild(self) -> None:
		circle = Circle(Point2D(1, 1), 1)
		group =  Group(Offset2D(5, 5), (circle, ))

		group.RemoveChild(circle)

		self.assertIsNone(circle.Parent)
		self.assertTupleEqual((), group.Children)
		self.assertTupleEqual((1, 1), circle.Center.ToTuple())

	def test_RemoveChild_None(self) -> None:
		group = Group()

		with self.assertRaises(ValueError) as context:
			group.RemoveChild(None)

		self.assertEqual("Parameter 'child' is None.", str(context.exception))

	def test_RemoveChild_Point(self) -> None:
		group = Group()

		with self.assertRaises(TypeError) as context:
			group.RemoveChild(Point2D(1, 1))

		self.assertEqual("Parameter 'child' is not of type 'Element2D'.", str(context.exception))

	def test_RemoveChild_NotAChild(self) -> None:
		circle = Circle(Point2D(1, 1), 1)
		group1 = Group(children=(circle, ))
		group2 = Group()

		with self.assertRaises(NotOwnedError) as context:
			group2.RemoveChild(circle)

		self.assertEqual("Element isn't a child of this group.", str(context.exception))
		self.assertListEqual(["Got Circle((1, 1), 1) owned by Group((0, 0), children=1)."], context.exception.__notes__)
		self.assertEqual("Parameter 'child' isn't a child of this group.", str(context.exception.__cause__))
		self.assertIs(group1, circle.Parent)

	def test_Parent(self) -> None:
		"""Assigning a parent moves the element and keeps its local coordinates."""
		circle = Circle(Point2D(1, 1), 1)
		group1 = Group(Offset2D(5, 0), (circle, ))
		group2 = Group(Offset2D(0, 5))

		circle.Parent = group2

		self.assertIs(group2, circle.Parent)
		self.assertTupleEqual((), group1.Children)
		self.assertTupleEqual((circle, ), group2.Children)
		self.assertTupleEqual((1, 1), circle.Center.ToTuple())
		self.assertTupleEqual((1, 6), circle.Center.Absolute.ToTuple())

	def test_Parent_None(self) -> None:
		circle = Circle(Point2D(1, 1), 1)
		group =  Group(Offset2D(5, 0), (circle, ))

		circle.Parent = None

		self.assertIsNone(circle.Parent)
		self.assertTupleEqual((), group.Children)

	def test_Parent_Same(self) -> None:
		circle = Circle(Point2D(1, 1), 1)
		line =   LineSegment2D(Point2D(0, 0), Point2D(2, 0))
		group =  Group(children=(circle, line))

		circle.Parent = group

		self.assertTupleEqual((circle, line), group.Children)

	def test_Parent_int(self) -> None:
		circle = Circle(Point2D(1, 1), 1)

		with self.assertRaises(TypeError) as context:
			circle.Parent = 1

		self.assertEqual("Parameter 'parent' is not of type 'Group'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)
		self.assertIsNone(circle.Parent)

	def test_Parent_Edge(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))
		edge =    polygon.Segments[0]

		with self.assertRaises(AlreadyOwnedError) as context:
			edge.Parent = Group()

		self.assertEqual("Element is owned by another element already.", str(context.exception))
		self.assertListEqual(
			["Got LineSegment2D((0, 0), (4, 0)) owned by Polygon((0, 0), (4, 0), (2, 3))."],
			context.exception.__notes__
		)
		self.assertEqual("Parameter 'parent' can't replace the shape of an edge.", str(context.exception.__cause__))
		self.assertIs(polygon, edge.Parent)

	def test_Polygon(self) -> None:
		"""A polygon in a group: its corners and edges are in the group's frame."""
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))
		group =   Group(children=(polygon, ))

		self.assertIs(group, polygon.Frame)
		for corner in polygon.Points:
			self.assertIs(group, corner.Frame)

		for edge in polygon.Segments:
			self.assertIs(polygon, edge.Parent)
			self.assertIs(group, edge.Frame)


class Frames(Testcase):
	def test_Frame(self) -> None:
		line =  LineSegment2D(Point2D(0, 0), Point2D(2, 0))
		inner = Group(children=(line, ))
		outer = Group(children=(inner, ))

		self.assertIs(inner, line.Frame)
		self.assertIs(inner, line.Start.Frame)
		self.assertIs(outer, inner.Frame)
		self.assertIsNone(outer.Frame)

	def test_Point_Minus_Point(self) -> None:
		circle1 = Circle(Point2D(1, 1), 1)
		circle2 = Circle(Point2D(4, 5), 1)
		_ =       Group(Offset2D(10, 10), (circle1, circle2))

		offset = circle2.Center - circle1.Center

		self.assertTupleEqual((3, 4), offset.ToTuple())

	def test_Point_Minus_Point_OtherGroup(self) -> None:
		circle1 = Circle(Point2D(1, 1), 1)
		circle2 = Circle(Point2D(4, 5), 1)
		_ =       Group(Offset2D(10, 10), (circle1, ))
		_ =       Group(Offset2D(20, 20), (circle2, ))

		with self.assertRaises(NotInSameFrameError) as context:
			_ = circle2.Center - circle1.Center

		self.assertEqual("Points are in different frames.", str(context.exception))

	def test_Point_Minus_Point_Absolute(self) -> None:
		circle1 = Circle(Point2D(1, 1), 1)
		circle2 = Circle(Point2D(4, 5), 1)
		_ =       Group(Offset2D(10, 10), (circle1, ))
		_ =       Group(Offset2D(20, 20), (circle2, ))

		offset = circle2.Center.Absolute - circle1.Center.Absolute

		self.assertTupleEqual((13, 14), offset.ToTuple())

	def test_AngleTo_OtherGroup(self) -> None:
		line1 = LineSegment2D(Point2D(0, 0), Point2D(1, 0))
		line2 = LineSegment2D(Point2D(0, 0), Point2D(0, 1))
		_ =     Group(children=(line1, ))

		with self.assertRaises(NotInSameFrameError):
			_ = line1.AngleTo(line2)

	def test_AngleTo_SameGroup(self) -> None:
		line1 = LineSegment2D(Point2D(0, 0), Point2D(1, 0))
		line2 = LineSegment2D(Point2D(0, 0), Point2D(0, 1))
		_ =     Group(children=(line1, line2))

		self.assertTrue(isclose(pi / 2, line1.AngleTo(line2)))


class Absolute(Testcase):
	def test_Point(self) -> None:
		circle = Circle(Point2D(1, 2), 1)
		inner =  Group(Offset2D(10, 0), (circle, ))
		_ =      Group(Offset2D(0, 20), (inner, ))

		point = circle.Center.Absolute

		self.assertIs(Point2D, type(point))
		self.assertIsNone(point.Parent)
		self.assertTupleEqual((11, 22), point.ToTuple())
		self.assertTupleEqual((1, 2), circle.Center.ToTuple())

	def test_Point_NoFrame(self) -> None:
		point = Point2D(1, 2)

		absolute = point.Absolute

		self.assertIsNot(point, absolute)
		self.assertTupleEqual((1, 2), absolute.ToTuple())

	def test_AbsoluteOffset(self) -> None:
		inner = Group(Offset2D(10, 0))
		outer = Group(Offset2D(0, 20), (inner, ))

		self.assertTupleEqual((10, 20), inner.AbsoluteOffset.ToTuple())
		self.assertTupleEqual((0, 20), outer.AbsoluteOffset.ToTuple())
		self.assertIsNot(outer.Offset, outer.AbsoluteOffset)

	def test_AbsoluteBoundingBox(self) -> None:
		circle = Circle(Point2D(1, 2), 1)
		line =   LineSegment2D(Point2D(0, 0), Point2D(2, 0))
		inner =  Group(Offset2D(10, 0), (circle, line))
		outer =  Group(Offset2D(0, 20), (inner, ))

		self.assertEqual(BoundingBox(10, 21, 12, 23), circle.AbsoluteBoundingBox)
		self.assertEqual(BoundingBox(10, 20, 12, 20), line.AbsoluteBoundingBox)
		self.assertEqual(BoundingBox(10, 20, 12, 23), inner.AbsoluteBoundingBox)
		self.assertEqual(BoundingBox(10, 20, 12, 23), outer.AbsoluteBoundingBox)


class Bounds(Testcase):
	def test_Group(self) -> None:
		circle = Circle(Point2D(1, 2), 1)
		line =   LineSegment2D(Point2D(-3, 0), Point2D(0, 0))
		group =  Group(Offset2D(10, 0), (circle, line))

		self.assertEqual(BoundingBox(7, 0, 12, 3), group.BoundingBox)

	def test_Group_Nested(self) -> None:
		inner = Group(Offset2D(5, 5), (Circle(Point2D(0, 0), 1), ))
		outer = Group(Offset2D(100, 0), (inner, LineSegment2D(Point2D(0, 0), Point2D(1, 1))))

		self.assertEqual(BoundingBox(4, 4, 6, 6), inner.BoundingBox)
		self.assertEqual(BoundingBox(100, 0, 106, 6), outer.BoundingBox)

	def test_Group_Empty(self) -> None:
		group = Group(Offset2D(1, 2))

		with self.assertRaises(EmptyGroupError) as context:
			_ = group.BoundingBox

		self.assertEqual("Group has no children.", str(context.exception))
		self.assertListEqual(["Got Group((1, 2), children=0)."], context.exception.__notes__)

	def test_Group_NestedEmpty(self) -> None:
		group = Group(children=(Circle(Point2D(0, 0), 1), Group()))

		with self.assertRaises(EmptyGroupError):
			_ = group.BoundingBox


class Moving(Testcase):
	def test_Move(self) -> None:
		"""Moving a group changes its offset only."""
		circle = Circle(Point2D(1, 2), 1)
		group =  Group(Offset2D(10, 0), (circle, ))

		group.Move(Offset2D(1, 1))

		self.assertTupleEqual((11, 1), group.Offset.ToTuple())
		self.assertTupleEqual((1, 2), circle.Center.ToTuple())
		self.assertTupleEqual((12, 3), circle.Center.Absolute.ToTuple())

	def test_Move_None(self) -> None:
		group = Group()

		with self.assertRaises(ValueError) as context:
			group.Move(None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))

	def test_Move_tuple(self) -> None:
		group = Group()

		with self.assertRaises(TypeError) as context:
			group.Move((1, 1))

		self.assertEqual("Parameter 'offset' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_Offset(self) -> None:
		group =  Group()
		offset = Offset2D(3, 4)

		group.Offset = offset

		self.assertIsNot(offset, group.Offset)
		self.assertTupleEqual((3, 4), group.Offset.ToTuple())

	def test_Offset_None(self) -> None:
		group = Group(Offset2D(1, 2))

		with self.assertRaises(ValueError) as context:
			group.Offset = None

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))
		self.assertTupleEqual((1, 2), group.Offset.ToTuple())

	def test_Offset_tuple(self) -> None:
		group = Group(Offset2D(1, 2))

		with self.assertRaises(TypeError) as context:
			group.Offset = (3, 4)

		self.assertEqual("Parameter 'offset' is not of type 'Offset2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_MoveTo(self) -> None:
		"""Moving a shape to another group keeps its absolute position."""
		circle = Circle(Point2D(1, 2), 1)
		_ =      Group(Offset2D(10, 0), (circle, ))
		target = Group(Offset2D(0, 20))

		circle.MoveTo(target)

		self.assertIs(target, circle.Parent)
		self.assertTupleEqual((11, -18), circle.Center.ToTuple())
		self.assertTupleEqual((11, 2), circle.Center.Absolute.ToTuple())

	def test_MoveTo_LocalPosition(self) -> None:
		circle = Circle(Point2D(1, 2), 1)
		_ =      Group(Offset2D(10, 0), (circle, ))
		target = Group(Offset2D(0, 20))

		circle.MoveTo(target, keepPosition=False)

		self.assertIs(target, circle.Parent)
		self.assertTupleEqual((1, 2), circle.Center.ToTuple())
		self.assertTupleEqual((1, 22), circle.Center.Absolute.ToTuple())

	def test_MoveTo_None(self) -> None:
		line = LineSegment2D(Point2D(0, 0), Point2D(2, 0))
		_ =    Group(Offset2D(10, 5), (line, ))

		line.MoveTo(None)

		self.assertIsNone(line.Parent)
		self.assertTupleEqual(((10, 5), (12, 5)), line.ToTuple())

	def test_MoveTo_Group(self) -> None:
		"""Moving a group changes its offset only: its children keep their local coordinates."""
		circle = Circle(Point2D(1, 2), 1)
		inner =  Group(Offset2D(3, 3), (circle, ))
		_ =      Group(Offset2D(10, 0), (inner, ))
		target = Group(Offset2D(0, 20))

		inner.MoveTo(target)

		self.assertTupleEqual((13, -17), inner.Offset.ToTuple())
		self.assertTupleEqual((1, 2), circle.Center.ToTuple())
		self.assertTupleEqual((14, 5), circle.Center.Absolute.ToTuple())

	def test_MoveTo_keepPositionNone(self) -> None:
		circle = Circle(Point2D(1, 2), 1)

		with self.assertRaises(ValueError) as context:
			circle.MoveTo(Group(), keepPosition=None)

		self.assertEqual("Parameter 'keepPosition' is None.", str(context.exception))
		self.assertIsNone(circle.Parent)

	def test_MoveTo_keepPositionInt(self) -> None:
		circle = Circle(Point2D(1, 2), 1)

		with self.assertRaises(TypeError) as context:
			circle.MoveTo(Group(), keepPosition=1)

		self.assertEqual("Parameter 'keepPosition' is not of type 'bool'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_MoveTo_Edge(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		with self.assertRaises(AlreadyOwnedError):
			polygon.Segments[0].MoveTo(Group(Offset2D(5, 5)))

		self.assertTupleEqual(((0, 0), (4, 0), (2, 3)), tuple(point.ToTuple() for point in polygon.Points))

	def test_MoveTo_Cycle(self) -> None:
		inner = Group(Offset2D(1, 1))
		outer = Group(children=(inner, ))

		with self.assertRaises(GroupCycleError):
			outer.MoveTo(inner)

		self.assertTupleEqual((0, 0), outer.Offset.ToTuple())
		self.assertIsNone(outer.Parent)


class Distributing(Testcase):
	def test_X(self) -> None:
		circle1 = Circle(Point2D(0, 0), 1)
		circle2 = Circle(Point2D(3, 0), 2)
		circle3 = Circle(Point2D(4, 5), 1)
		circle4 = Circle(Point2D(20, 0), 1)
		group =   Group(children=(circle4, circle2, circle1, circle3))

		group.Distribute(Axis.X)

		self.assertEqual(BoundingBox(-1, -1, 1, 1), circle1.BoundingBox)
		self.assertEqual(BoundingBox(5, -2, 9, 2), circle2.BoundingBox)
		self.assertEqual(BoundingBox(13, 4, 15, 6), circle3.BoundingBox)
		self.assertEqual(BoundingBox(19, -1, 21, 1), circle4.BoundingBox)

	def test_Y(self) -> None:
		line1 = LineSegment2D(Point2D(0, 0), Point2D(0, 2))
		line2 = LineSegment2D(Point2D(5, 3), Point2D(5, 4))
		line3 = LineSegment2D(Point2D(1, 9), Point2D(1, 12))
		group = Group(children=(line1, line2, line3))

		group.Distribute(Axis.Y)

		self.assertEqual(BoundingBox(5, 5, 5, 6), line2.BoundingBox)
		self.assertEqual(BoundingBox(1, 9, 1, 12), line3.BoundingBox)

	def test_TwoChildren(self) -> None:
		circle1 = Circle(Point2D(0, 0), 1)
		circle2 = Circle(Point2D(3, 0), 1)
		group =   Group(children=(circle1, circle2))

		group.Distribute(Axis.X)

		self.assertTupleEqual((0, 0), circle1.Center.ToTuple())
		self.assertTupleEqual((3, 0), circle2.Center.ToTuple())

	def test_AxisNone(self) -> None:
		group = Group()

		with self.assertRaises(ValueError) as context:
			group.Distribute(None)

		self.assertEqual("Parameter 'axis' is None.", str(context.exception))

	def test_AxisStr(self) -> None:
		group = Group()

		with self.assertRaises(TypeError) as context:
			group.Distribute("X")

		self.assertEqual("Parameter 'axis' is not of type 'Axis'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

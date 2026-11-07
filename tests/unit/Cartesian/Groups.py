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
Unit tests for :mod:`pyTooling.Cartesian2D.Groups` - groups, canvases, frames, absolute coordinates and mirroring.
"""
from math                         import isclose, pi

from pyTooling.Cartesian2D        import Base, Point2D, Offset2D, Size2D, BoundingBox, Alignment, Element2D, \
                                         Segment2D, LineSegment2D, AlreadyOwnedError, DuplicatePointError, \
                                         NotEnoughCornersError, NotOwnedError, NotInSameFrameError, GroupCycleError
from pyTooling.Cartesian2D.Shapes import Polygon, Trapezium, Rectangle, Square, Circle
from pyTooling.Cartesian2D.Groups import Group, Canvas, YAxisDirection, EmptyGroupError
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

		self.assertEqual("Parameter 'parent' is not of type 'Group' or 'Canvas'.", str(context.exception))
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


class ParentParameter(Testcase):
	"""Parameter 'parent' registers the new element in the group, as ``AddChild`` does."""

	def test_Segment(self) -> None:
		group = Group()

		segment = Segment2D(Point2D(1, 2), Point2D(4, 6), parent=group)

		self.assertIs(group, segment.Parent)
		self.assertTupleEqual((segment, ), group.Children)
		self.assertIs(segment, segment.Start.Parent)
		self.assertIs(segment, segment.End.Parent)
		self.assertIs(group, segment.Start.Frame)

	def test_LineSegment(self) -> None:
		group = Group()

		segment = LineSegment2D(Point2D(1, 2), Point2D(4, 6), parent=group)

		self.assertIs(group, segment.Parent)
		self.assertTupleEqual((segment, ), group.Children)
		self.assertIs(group, segment.Frame)

	def test_LineSegment_Reference(self) -> None:
		"""A segment in a group owns its points, as a standalone one."""
		group = Group()
		start = Point2D(1, 2)
		end =   Point2D(4, 6)

		segment = LineSegment2D(start, end, copyPoints=False, parent=group)

		self.assertIs(start, segment.Start)
		self.assertIs(end, segment.End)
		self.assertIs(segment, start.Parent)
		self.assertIs(segment, end.Parent)

		replacement = Point2D(7, 8)
		segment.Start = replacement

		self.assertIs(segment, replacement.Parent)
		self.assertIsNone(start.Parent)

	def test_LineSegment_Shape(self) -> None:
		"""A segment with a shape as parent is an edge, not a child of a group."""
		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)))

		edge = LineSegment2D(polygon.Points[0], polygon.Points[2], copyPoints=False, parent=polygon)

		self.assertIs(polygon, edge.Parent)
		self.assertIs(polygon, edge.Start.Parent)

	def test_LineSegment_Int(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = LineSegment2D(Point2D(1, 2), Point2D(4, 6), parent=1)

		self.assertEqual("Parameter 'parent' is not of type 'Shape' or 'Group' or 'Canvas'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_LineSegment_Positional(self) -> None:
		with self.assertRaises(TypeError):
			_ = LineSegment2D(Point2D(1, 2), Point2D(4, 6), Group())

	def test_LineSegment_Failing(self) -> None:
		group = Group()
		point = Point2D(1, 2)

		with self.assertRaises(DuplicatePointError):
			_ = LineSegment2D(point, point, copyPoints=False, parent=group)

		self.assertTupleEqual((), group.Children)

	def test_Polygon(self) -> None:
		group = Group()

		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), parent=group)

		self.assertIs(group, polygon.Parent)
		self.assertTupleEqual((polygon, ), group.Children)
		self.assertIs(group, polygon.Points[0].Frame)
		self.assertIs(group, polygon.Segments[0].Frame)

	def test_Polygon_Int(self) -> None:
		"""A wrong parent is found before the polygon takes the given points."""
		points = (Point2D(0, 0), Point2D(4, 0), Point2D(2, 3))

		with self.assertRaises(TypeError) as context:
			_ = Polygon(points, copyPoints=False, parent=1)

		self.assertEqual("Parameter 'parent' is not of type 'Group' or 'Canvas'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)
		self.assertIsNone(points[0].Parent)

	def test_Polygon_Positional(self) -> None:
		with self.assertRaises(TypeError):
			_ = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), Group())

	def test_Polygon_Failing(self) -> None:
		group = Group()

		with self.assertRaises(NotEnoughCornersError):
			_ = Polygon((Point2D(0, 0), Point2D(4, 0)), parent=group)

		self.assertTupleEqual((), group.Children)

	def test_Trapezium(self) -> None:
		group = Group()

		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3), parent=group)

		self.assertIs(group, trapezium.Parent)
		self.assertTupleEqual((trapezium, ), group.Children)
		self.assertIs(group, trapezium.Points[0].Frame)

	def test_Trapezium_Int(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3), parent=1)

		self.assertEqual("Parameter 'parent' is not of type 'Group' or 'Canvas'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Trapezium_Positional(self) -> None:
		with self.assertRaises(TypeError):
			_ = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3), Group())

	def test_Trapezium_Failing(self) -> None:
		group = Group()

		with self.assertRaises(ValueError):
			_ = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), None, parent=group)

		self.assertTupleEqual((), group.Children)

	def test_Rectangle(self) -> None:
		group = Group()

		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2), parent=group)

		self.assertIs(group, rectangle.Parent)
		self.assertTupleEqual((rectangle, ), group.Children)

	def test_Rectangle_Int(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2), parent=1)

		self.assertEqual("Parameter 'parent' is not of type 'Group' or 'Canvas'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Rectangle_Positional(self) -> None:
		with self.assertRaises(TypeError):
			_ = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2), Group())

	def test_Rectangle_Failing(self) -> None:
		"""The rectangle's own checks run before it registers: a parallelogram leaves no child in the group."""
		group = Group()

		with self.assertRaises(ValueError):
			_ = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(5, 2), Point2D(1, 2), parent=group)

		self.assertTupleEqual((), group.Children)

	def test_Square(self) -> None:
		group = Group()

		square = Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2), parent=group)

		self.assertIs(group, square.Parent)
		self.assertTupleEqual((square, ), group.Children)

	def test_Square_Int(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2), parent=1)

		self.assertEqual("Parameter 'parent' is not of type 'Group' or 'Canvas'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)

	def test_Square_Positional(self) -> None:
		with self.assertRaises(TypeError):
			_ = Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2), Group())

	def test_Square_Failing(self) -> None:
		"""The square's own checks run before it registers: a rectangle leaves no child in the group."""
		group = Group()

		with self.assertRaises(ValueError):
			_ = Square(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2), parent=group)

		self.assertTupleEqual((), group.Children)

	def test_Circle(self) -> None:
		group = Group()

		circle = Circle(Point2D(1, 2), 3, parent=group)

		self.assertIs(group, circle.Parent)
		self.assertTupleEqual((circle, ), group.Children)
		self.assertIs(group, circle.Center.Frame)

	def test_Circle_Int(self) -> None:
		"""A wrong parent is found before the circle takes the given center."""
		center = Point2D(1, 2)

		with self.assertRaises(TypeError) as context:
			_ = Circle(center, 3, copyPoints=False, parent=1)

		self.assertEqual("Parameter 'parent' is not of type 'Group' or 'Canvas'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)
		self.assertIsNone(center.Parent)

	def test_Circle_Positional(self) -> None:
		with self.assertRaises(TypeError):
			_ = Circle(Point2D(1, 2), 3, Group())

	def test_Circle_Failing(self) -> None:
		group = Group()

		with self.assertRaises(ValueError):
			_ = Circle(Point2D(1, 2), 0, parent=group)

		self.assertTupleEqual((), group.Children)

	def test_Group(self) -> None:
		parent = Group()
		child =  Circle(Point2D(1, 2), 3)

		group = Group(Offset2D(1, 1), (child, ), parent=parent)

		self.assertIs(parent, group.Parent)
		self.assertTupleEqual((group, ), parent.Children)
		self.assertIs(group, child.Parent)
		self.assertTupleEqual((2, 3), child.Center.Absolute.ToTuple())

	def test_Group_Int(self) -> None:
		"""A wrong parent is found before the group takes the given children."""
		child = Circle(Point2D(1, 2), 3)

		with self.assertRaises(TypeError) as context:
			_ = Group(children=(child, ), parent=1)

		self.assertEqual("Parameter 'parent' is not of type 'Group' or 'Canvas'.", str(context.exception))
		self.assertListEqual(["Got type 'int'."], context.exception.__notes__)
		self.assertIsNone(child.Parent)

	def test_Group_Positional(self) -> None:
		with self.assertRaises(TypeError):
			_ = Group(None, None, Group())

	def test_Group_Failing(self) -> None:
		group = Group()

		with self.assertRaises(TypeError):
			_ = Group(offset=(1, 1), parent=group)

		self.assertTupleEqual((), group.Children)

	def test_Group_ParentIsChild(self) -> None:
		"""The new group can't be a child of its own child. The child stays free."""
		child = Group()

		with self.assertRaises(GroupCycleError) as context:
			_ = Group(children=(child, ), parent=child)

		self.assertEqual("Group would contain itself.", str(context.exception))
		self.assertEqual("Parameter 'parent' is this element or one of its descendants.", str(context.exception.__cause__))
		self.assertIsNone(child.Parent)
		self.assertTupleEqual((), child.Children)

	def test_Group_ParentInsideChild(self) -> None:
		inner = Group()
		child = Group(children=(inner, ))

		with self.assertRaises(GroupCycleError):
			_ = Group(children=(child, ), parent=inner)

		self.assertIsNone(child.Parent)
		self.assertTupleEqual((), inner.Children)

	def test_Point(self) -> None:
		"""A point's parent sets the owner only: the group's children don't change."""
		group = Group()

		point = Point2D(1, 2, parent=group)

		self.assertIs(group, point.Parent)
		self.assertIs(group, point.Frame)
		self.assertTupleEqual((), group.Children)


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

		self.assertIsInstance(context.exception, EmptyError)
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

		group.DistributeX()

		self.assertEqual(BoundingBox(-1, -1, 1, 1), circle1.BoundingBox)
		self.assertEqual(BoundingBox(5, -2, 9, 2), circle2.BoundingBox)
		self.assertEqual(BoundingBox(13, 4, 15, 6), circle3.BoundingBox)
		self.assertEqual(BoundingBox(19, -1, 21, 1), circle4.BoundingBox)

	def test_Y(self) -> None:
		line1 = LineSegment2D(Point2D(0, 0), Point2D(0, 2))
		line2 = LineSegment2D(Point2D(5, 3), Point2D(5, 4))
		line3 = LineSegment2D(Point2D(1, 9), Point2D(1, 12))
		group = Group(children=(line1, line2, line3))

		group.DistributeY()

		self.assertEqual(BoundingBox(5, 5, 5, 6), line2.BoundingBox)
		self.assertEqual(BoundingBox(1, 9, 1, 12), line3.BoundingBox)

	def test_TwoChildren(self) -> None:
		circle1 = Circle(Point2D(0, 0), 1)
		circle2 = Circle(Point2D(3, 0), 1)
		group =   Group(children=(circle1, circle2))

		group.DistributeX()

		self.assertTupleEqual((0, 0), circle1.Center.ToTuple())
		self.assertTupleEqual((3, 0), circle2.Center.ToTuple())

	def test_Gap_X(self) -> None:
		circle1 = Circle(Point2D(0, 0), 1)
		circle2 = Circle(Point2D(3, 0), 2)
		circle3 = Circle(Point2D(20, 5), 1)
		group =   Group(children=(circle3, circle2, circle1))

		group.DistributeX(3)

		self.assertEqual(BoundingBox(-1, -1, 1, 1), circle1.BoundingBox)
		self.assertEqual(BoundingBox(4, -2, 8, 2), circle2.BoundingBox)
		self.assertEqual(BoundingBox(11, 4, 13, 6), circle3.BoundingBox)

	def test_Gap_Y(self) -> None:
		line1 = LineSegment2D(Point2D(0, 0), Point2D(0, 2))
		line2 = LineSegment2D(Point2D(5, 3), Point2D(5, 4))
		group = Group(children=(line1, line2))

		group.DistributeY(0.5)

		self.assertEqual(BoundingBox(0, 0, 0, 2), line1.BoundingBox)
		self.assertEqual(BoundingBox(5, 2.5, 5, 3.5), line2.BoundingBox)

	def test_Gap_Zero(self) -> None:
		circle1 = Circle(Point2D(0, 0), 1)
		circle2 = Circle(Point2D(5, 0), 1)
		group =   Group(children=(circle1, circle2))

		group.DistributeX(0)

		self.assertTupleEqual((2, 0), circle2.Center.ToTuple())

	def test_Gap_OneChild(self) -> None:
		circle = Circle(Point2D(3, 0), 1)
		group =  Group(children=(circle, ))

		group.DistributeX(1)

		self.assertTupleEqual((3, 0), circle.Center.ToTuple())

	def test_Gap_Str(self) -> None:
		group = Group()

		with self.assertRaises(TypeError) as context:
			group.DistributeX("1")

		self.assertEqual("Parameter 'gap' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Gap_Negative(self) -> None:
		group = Group()

		with self.assertRaises(ValueError) as context:
			group.DistributeX(-1)

		self.assertEqual("Parameter 'gap' is negative.", str(context.exception))
		self.assertListEqual(["Got value '-1'."], context.exception.__notes__)

	def test_Gap_Y_Str(self) -> None:
		group = Group()

		with self.assertRaises(TypeError) as context:
			group.DistributeY("1")

		self.assertEqual("Parameter 'gap' is not of type 'float' or 'int'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Gap_Y_Negative(self) -> None:
		group = Group()

		with self.assertRaises(ValueError) as context:
			group.DistributeY(-1)

		self.assertEqual("Parameter 'gap' is negative.", str(context.exception))
		self.assertListEqual(["Got value '-1'."], context.exception.__notes__)


class CanvasInstantiation(Testcase):
	def test_Canvas(self) -> None:
		canvas = Canvas()

		self.assertIs(YAxisDirection.Up, canvas.Direction)
		self.assertIsNone(canvas.Size)
		self.assertIsNone(canvas.Frame)
		self.assertTupleEqual((), canvas.Children)
		self.assertTupleEqual((0, 0), canvas.AbsoluteOffset.ToTuple())

	def test_Canvas_Size(self) -> None:
		size = Size2D(400, 300)

		canvas = Canvas(YAxisDirection.Down, size)

		self.assertIs(YAxisDirection.Down, canvas.Direction)
		self.assertIsNot(size, canvas.Size)
		self.assertTupleEqual((400, 300), canvas.Size.ToTuple())

	def test_Canvas_Children(self) -> None:
		circle = Circle(Point2D(1, 1), 1)
		group =  Group(Offset2D(5, 5), (LineSegment2D(Point2D(0, 0), Point2D(2, 0)), ))

		canvas = Canvas(children=(circle, group))

		self.assertTupleEqual((circle, group), canvas.Children)
		self.assertIs(canvas, circle.Parent)
		self.assertIs(canvas, group.Parent)
		self.assertIs(canvas, circle.Frame)
		self.assertIs(canvas, circle.Center.Frame)
		self.assertIs(canvas, group.Frame)

	def test_Canvas_Base(self) -> None:
		"""A canvas is a frame like a group, and the root: it never has a parent."""
		canvas = Canvas()

		self.assertIsInstance(canvas, Base)
		self.assertNotIsInstance(canvas, Element2D)
		self.assertIsNone(canvas.Parent)
		self.assertIsNone(canvas.Frame)

		with self.assertRaises(TypeError):
			canvas.Parent = Group()

		self.assertIsNone(canvas.Parent)

	def test_Canvas_ParentParameter(self) -> None:
		with self.assertRaises(TypeError):
			_ = Canvas(parent=Group())

	def test_Canvas_Slots(self) -> None:
		self.assertFalse(hasattr(Canvas(), "__dict__"))
		self.assertFalse(hasattr(Group(), "__dict__"))

	def test_Canvas_Hash(self) -> None:
		"""A canvas defines no ``__eq__``: it hashes by identity."""
		self.assertEqual(2, len({Canvas(), Canvas()}))

	def test_Canvas_DirectionNone(self) -> None:
		with self.assertRaises(ValueError) as context:
			_ = Canvas(None)

		self.assertEqual("Parameter 'direction' is None.", str(context.exception))

	def test_Canvas_DirectionStr(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Canvas("Up")

		self.assertEqual("Parameter 'direction' is not of type 'YAxisDirection'.", str(context.exception))
		self.assertListEqual(["Got type 'str'."], context.exception.__notes__)

	def test_Canvas_SizeTuple(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = Canvas(size=(400, 300))

		self.assertEqual("Parameter 'size' is not of type 'Size2D'.", str(context.exception))
		self.assertListEqual(["Got type 'tuple'."], context.exception.__notes__)

	def test_Canvas_ChildOwned(self) -> None:
		circle = Circle(Point2D(1, 1), 1)
		group =  Group(children=(circle, ))

		with self.assertRaises(AlreadyOwnedError):
			_ = Canvas(children=(circle, ))

		self.assertIs(group, circle.Parent)

	def test_repr(self) -> None:
		canvas = Canvas(YAxisDirection.Down, Size2D(400, 300), (Circle(Point2D(1, 1), 1), ))

		self.assertEqual("Canvas(Down, (400, 300), children=1)", repr(canvas))


class CanvasFailing(Testcase):
	def test_Parent_Assign(self) -> None:
		canvas = Canvas()

		with self.assertRaises(TypeError) as context:
			canvas.Parent = Group()

		self.assertEqual("A 'pyTooling.Cartesian2D.Groups.Canvas' has no parent.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Groups.Group'."], context.exception.__notes__)
		self.assertIsNone(canvas.Parent)

	"""A failing check of a canvas or group leaves the given children free."""

	def test_Canvas_Direction(self) -> None:
		child = Circle(Point2D(1, 2), 3)

		with self.assertRaises(TypeError):
			_ = Canvas("up", children=(child, ))

		self.assertIsNone(child.Parent)

	def test_Canvas_Size(self) -> None:
		child = Circle(Point2D(1, 2), 3)

		with self.assertRaises(TypeError):
			_ = Canvas(size=(10, 10), children=(child, ))

		self.assertIsNone(child.Parent)

	def test_Group_Offset(self) -> None:
		child = Circle(Point2D(1, 2), 3)

		with self.assertRaises(TypeError):
			_ = Group((1, 1), (child, ))

		self.assertIsNone(child.Parent)


class CanvasParentParameter(Testcase):
	"""Parameter 'parent' registers the new element in the canvas, as ``AddChild`` does."""

	def test_Segment(self) -> None:
		canvas = Canvas()

		segment = Segment2D(Point2D(1, 2), Point2D(4, 6), parent=canvas)

		self.assertIs(canvas, segment.Parent)
		self.assertTupleEqual((segment, ), canvas.Children)
		self.assertIs(canvas, segment.Start.Frame)

	def test_LineSegment(self) -> None:
		canvas = Canvas()

		segment = LineSegment2D(Point2D(1, 2), Point2D(4, 6), parent=canvas)

		self.assertIs(canvas, segment.Parent)
		self.assertTupleEqual((segment, ), canvas.Children)
		self.assertIs(segment, segment.Start.Parent)

	def test_Polygon(self) -> None:
		canvas = Canvas()

		polygon = Polygon((Point2D(0, 0), Point2D(4, 0), Point2D(2, 3)), parent=canvas)

		self.assertIs(canvas, polygon.Parent)
		self.assertTupleEqual((polygon, ), canvas.Children)
		self.assertIs(canvas, polygon.Points[0].Frame)

	def test_Trapezium(self) -> None:
		canvas = Canvas()

		trapezium = Trapezium(Point2D(1, 1), Point2D(3, 1), Point2D(4, 3), Point2D(0, 3), parent=canvas)

		self.assertIs(canvas, trapezium.Parent)
		self.assertTupleEqual((trapezium, ), canvas.Children)

	def test_Rectangle(self) -> None:
		canvas = Canvas()

		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2), parent=canvas)

		self.assertIs(canvas, rectangle.Parent)
		self.assertTupleEqual((rectangle, ), canvas.Children)

	def test_Rectangle_Failing(self) -> None:
		canvas = Canvas()

		with self.assertRaises(ValueError):
			_ = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(5, 2), Point2D(1, 2), parent=canvas)

		self.assertTupleEqual((), canvas.Children)

	def test_Square(self) -> None:
		canvas = Canvas()

		square = Square(Point2D(0, 0), Point2D(2, 0), Point2D(2, 2), Point2D(0, 2), parent=canvas)

		self.assertIs(canvas, square.Parent)
		self.assertTupleEqual((square, ), canvas.Children)

	def test_Circle(self) -> None:
		canvas = Canvas()

		circle = Circle(Point2D(1, 2), 3, parent=canvas)

		self.assertIs(canvas, circle.Parent)
		self.assertTupleEqual((circle, ), canvas.Children)
		self.assertIs(canvas, circle.Center.Frame)

	def test_Group(self) -> None:
		canvas = Canvas()

		group = Group(Offset2D(1, 1), parent=canvas)

		self.assertIs(canvas, group.Parent)
		self.assertTupleEqual((group, ), canvas.Children)
		self.assertIs(canvas, group.Frame)
		self.assertTupleEqual((1, 1), group.AbsoluteOffset.ToTuple())

	def test_Point(self) -> None:
		"""A point's owner is an element, a canvas isn't one."""
		with self.assertRaises(TypeError) as context:
			_ = Point2D(1, 2, parent=Canvas())

		self.assertEqual("Parameter 'parent' is not of type 'Element2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Groups.Canvas'."], context.exception.__notes__)


class CanvasMembership(Testcase):
	def test_AddChild(self) -> None:
		canvas = Canvas()
		group =  Group()

		canvas.AddChild(group)

		self.assertIs(canvas, group.Parent)
		self.assertTupleEqual((group, ), canvas.Children)

	def test_RemoveChild(self) -> None:
		circle = Circle(Point2D(1, 1), 1)
		canvas = Canvas(children=(circle, ))

		canvas.RemoveChild(circle)

		self.assertIsNone(circle.Parent)
		self.assertTupleEqual((), canvas.Children)

	def test_RemoveChild_NotAChild(self) -> None:
		canvas = Canvas()

		with self.assertRaises(NotOwnedError) as context:
			canvas.RemoveChild(Circle(Point2D(1, 1), 1))

		self.assertEqual("Element isn't a child of this canvas.", str(context.exception))
		self.assertEqual("Parameter 'child' isn't a child of this canvas.", str(context.exception.__cause__))

	def test_MoveTo(self) -> None:
		circle = Circle(Point2D(1, 2), 1)
		_ =      Group(Offset2D(10, 0), (circle, ))
		canvas = Canvas()

		circle.MoveTo(canvas)

		self.assertIs(canvas, circle.Parent)
		self.assertTupleEqual((11, 2), circle.Center.ToTuple())

	def test_Cycle(self) -> None:
		"""A group on a canvas can't contain its parent group."""
		inner =  Group()
		outer =  Group(children=(inner, ))
		canvas = Canvas(children=(outer, ))

		with self.assertRaises(GroupCycleError):
			outer.Parent = inner

		self.assertIs(canvas, outer.Parent)

	def test_BoundingBox(self) -> None:
		canvas = Canvas(children=(Circle(Point2D(1, 1), 1), Group(Offset2D(10, 10), (Circle(Point2D(0, 0), 2), ))))

		self.assertEqual(BoundingBox(0, 0, 12, 12), canvas.BoundingBox)

	def test_BoundingBox_Empty(self) -> None:
		canvas = Canvas()

		with self.assertRaises(EmptyGroupError) as context:
			_ = canvas.BoundingBox

		self.assertEqual("Canvas has no children.", str(context.exception))
		self.assertListEqual(["Got Canvas(Up, None, children=0)."], context.exception.__notes__)

	def test_Distribute(self) -> None:
		circle1 = Circle(Point2D(0, 0), 1)
		circle2 = Circle(Point2D(1, 0), 1)
		circle3 = Circle(Point2D(10, 0), 1)
		canvas =  Canvas(children=(circle1, circle2, circle3))

		canvas.DistributeX()

		self.assertTupleEqual((5, 0), circle2.Center.ToTuple())


class Mirroring(Testcase):
	def test_MirrorVertically(self) -> None:
		"""A group mirrors its offset at the axis, its children are mirrored at the group's origin."""
		circle = Circle(Point2D(1, 2), 1)
		inner =  Group(Offset2D(3, 4), (circle, ))
		outer =  Group(Offset2D(10, 20), (inner, ))

		outer.MirrorVertically(Alignment.MinY, 10)

		self.assertTupleEqual((10, 50), outer.Offset.ToTuple())
		self.assertTupleEqual((3, -4), inner.Offset.ToTuple())
		self.assertTupleEqual((1, -2), circle.Center.ToTuple())
		self.assertTupleEqual((14, 44), circle.Center.Absolute.ToTuple())
		self.assertEqual(BoundingBox(13, 43, 15, 45), outer.BoundingBox)

	def test_MirrorVertically_Default(self) -> None:
		"""A group mirrored at its center keeps its bounding box."""
		line =  LineSegment2D(Point2D(0, 0), Point2D(4, 2))
		inner = Group(Offset2D(1, 1), (line, ))
		outer = Group(Offset2D(10, 20), (inner, ))

		outer.MirrorVertically()

		self.assertTupleEqual((10, 24), outer.Offset.ToTuple())
		self.assertTupleEqual((1, -1), inner.Offset.ToTuple())
		self.assertTupleEqual(((0, 0), (4, -2)), line.ToTuple())
		self.assertEqual(BoundingBox(11, 21, 15, 23), outer.BoundingBox)

	def test_MirrorVertically_MaxY(self) -> None:
		line =  LineSegment2D(Point2D(0, 0), Point2D(4, 2))
		group = Group(Offset2D(10, 20), (line, ))

		group.MirrorVertically(Alignment.MaxY)

		self.assertTupleEqual((10, 24), group.Offset.ToTuple())
		self.assertEqual(BoundingBox(10, 22, 14, 24), group.BoundingBox)

	def test_MirrorVertically_AxisMaxX(self) -> None:
		group = Group(Offset2D(1, 2))

		with self.assertRaises(ValueError) as context:
			group.MirrorVertically(Alignment.MaxX)

		self.assertEqual(
			"Parameter 'axis' is not Alignment.MinY, Alignment.CenterY or Alignment.MaxY.",
			str(context.exception)
		)
		self.assertListEqual(["Got value 'Alignment.MaxX'."], context.exception.__notes__)
		self.assertTupleEqual((1, 2), group.Offset.ToTuple())

	def test_MirrorVertically_Empty(self) -> None:
		group = Group(Offset2D(1, 2))

		with self.assertRaises(EmptyGroupError) as context:
			group.MirrorVertically()

		self.assertEqual("Group has no children.", str(context.exception))
		self.assertTupleEqual((1, 2), group.Offset.ToTuple())

	def test_MirrorHorizontally(self) -> None:
		"""A group mirrors its offset at the axis, its children are mirrored at the group's origin."""
		circle = Circle(Point2D(1, 2), 1)
		inner =  Group(Offset2D(3, 4), (circle, ))
		outer =  Group(Offset2D(10, 20), (inner, ))

		outer.MirrorHorizontally(Alignment.MaxX, 5)

		self.assertTupleEqual((30, 20), outer.Offset.ToTuple())
		self.assertTupleEqual((-3, 4), inner.Offset.ToTuple())
		self.assertTupleEqual((-1, 2), circle.Center.ToTuple())
		self.assertTupleEqual((26, 26), circle.Center.Absolute.ToTuple())
		self.assertEqual(BoundingBox(25, 25, 27, 27), outer.BoundingBox)

	def test_MirrorHorizontally_Default(self) -> None:
		"""A group mirrored at its center keeps its bounding box."""
		line =  LineSegment2D(Point2D(0, 0), Point2D(4, 2))
		inner = Group(Offset2D(1, 1), (line, ))
		outer = Group(Offset2D(10, 20), (inner, ))

		outer.MirrorHorizontally()

		self.assertTupleEqual((16, 20), outer.Offset.ToTuple())
		self.assertTupleEqual((-1, 1), inner.Offset.ToTuple())
		self.assertTupleEqual(((0, 0), (-4, 2)), line.ToTuple())
		self.assertEqual(BoundingBox(11, 21, 15, 23), outer.BoundingBox)

	def test_MirrorHorizontally_MinX(self) -> None:
		line =  LineSegment2D(Point2D(0, 0), Point2D(4, 2))
		group = Group(Offset2D(10, 20), (line, ))

		group.MirrorHorizontally(Alignment.MinX)

		self.assertTupleEqual((10, 20), group.Offset.ToTuple())
		self.assertTupleEqual(((0, 0), (-4, 2)), line.ToTuple())
		self.assertEqual(BoundingBox(6, 20, 10, 22), group.BoundingBox)

	def test_MirrorHorizontally_OffsetNone(self) -> None:
		group = Group(Offset2D(1, 2))

		with self.assertRaises(ValueError) as context:
			group.MirrorHorizontally(Alignment.MinX, None)

		self.assertEqual("Parameter 'offset' is None.", str(context.exception))
		self.assertTupleEqual((1, 2), group.Offset.ToTuple())

	def test_Canvas_Open(self) -> None:
		"""Without a size, every level negates its y-coordinates."""
		circle = Circle(Point2D(1, 2), 1)
		line =   LineSegment2D(Point2D(0, 5), Point2D(3, 7))
		group =  Group(Offset2D(10, 20), (circle, ))
		canvas = Canvas(YAxisDirection.Down, children=(group, line))

		canvas.Mirror()

		self.assertIs(YAxisDirection.Up, canvas.Direction)
		self.assertTupleEqual((10, -20), group.Offset.ToTuple())
		self.assertTupleEqual((1, -2), circle.Center.ToTuple())
		self.assertTupleEqual(((0, -5), (3, -7)), line.ToTuple())
		self.assertTupleEqual((11, -22), circle.Center.Absolute.ToTuple())

	def test_Canvas_Bounded(self) -> None:
		"""With a size, the top level uses height - y, deeper levels negate their y-coordinates."""
		circle = Circle(Point2D(1, 2), 1)
		line =   LineSegment2D(Point2D(0, 5), Point2D(3, 7))
		group =  Group(Offset2D(10, 20), (circle, ))
		canvas = Canvas(YAxisDirection.Down, Size2D(400, 300), (group, line))

		canvas.Mirror()

		self.assertTupleEqual((10, 280), group.Offset.ToTuple())
		self.assertTupleEqual((1, -2), circle.Center.ToTuple())
		self.assertTupleEqual(((0, 295), (3, 293)), line.ToTuple())
		self.assertTupleEqual((11, 278), circle.Center.Absolute.ToTuple())

	def test_Canvas_Twice(self) -> None:
		polygon = Polygon((Point2D(0, 0), Point2D(4, 1), Point2D(2, 3)))
		group =   Group(Offset2D(10, 20), (polygon, ))
		canvas =  Canvas(YAxisDirection.Up, Size2D(400, 300), (group, ))

		canvas.Mirror()
		canvas.Mirror()

		self.assertIs(YAxisDirection.Up, canvas.Direction)
		self.assertTupleEqual((10, 20), group.Offset.ToTuple())
		self.assertTupleEqual(((0, 0), (4, 1), (2, 3)), tuple(point.ToTuple() for point in polygon.Points))

	def test_Canvas_Top(self) -> None:
		"""The top edge of an element stays at the same distance from the canvas' visual top edge."""
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))
		group =     Group(Offset2D(10, 20), (rectangle, ))
		canvas =    Canvas(YAxisDirection.Down, Size2D(400, 300), (group, ))

		self.assertEqual(20, canvas.Top(rectangle))

		canvas.Mirror()

		self.assertEqual(280, canvas.Top(rectangle))
		self.assertEqual(BoundingBox(10, 278, 14, 280), rectangle.AbsoluteBoundingBox)


class CanvasEdges(Testcase):
	def test_Top_Up(self) -> None:
		circle = Circle(Point2D(1, 2), 1)
		canvas = Canvas(YAxisDirection.Up, children=(Group(Offset2D(10, 10), (circle, )), ))

		self.assertEqual(13, canvas.Top(circle))
		self.assertEqual(11, canvas.Bottom(circle))
		self.assertIs(Alignment.MaxY, canvas.TopAlignment)
		self.assertIs(Alignment.MinY, canvas.BottomAlignment)

	def test_Top_Down(self) -> None:
		circle = Circle(Point2D(1, 2), 1)
		canvas = Canvas(YAxisDirection.Down, children=(Group(Offset2D(10, 10), (circle, )), ))

		self.assertEqual(11, canvas.Top(circle))
		self.assertEqual(13, canvas.Bottom(circle))
		self.assertIs(Alignment.MinY, canvas.TopAlignment)
		self.assertIs(Alignment.MaxY, canvas.BottomAlignment)

	def test_AlignTop(self) -> None:
		rectangle = Rectangle(Point2D(0, 0), Point2D(4, 0), Point2D(4, 2), Point2D(0, 2))
		circle =    Circle(Point2D(10, 10), 1)
		canvas =    Canvas(YAxisDirection.Down, children=(rectangle, circle))

		circle.AlignTo(rectangle, canvas.TopAlignment)

		self.assertEqual(canvas.Top(rectangle), canvas.Top(circle))
		self.assertEqual(BoundingBox(9, 0, 11, 2), circle.BoundingBox)

	def test_Top_OtherCanvas(self) -> None:
		circle = Circle(Point2D(1, 2), 1)
		_ =      Canvas(children=(circle, ))
		canvas = Canvas()

		with self.assertRaises(NotInSameFrameError) as context:
			_ = canvas.Top(circle)

		self.assertEqual("Element isn't on this canvas.", str(context.exception))
		self.assertListEqual(["Got Circle((1, 2), 1)."], context.exception.__notes__)
		self.assertEqual("Parameter 'element' isn't on this canvas.", str(context.exception.__cause__))

	def test_Bottom_NoCanvas(self) -> None:
		canvas = Canvas()

		with self.assertRaises(NotInSameFrameError):
			_ = canvas.Bottom(Circle(Point2D(1, 2), 1))

	def test_Top_None(self) -> None:
		canvas = Canvas()

		with self.assertRaises(ValueError) as context:
			_ = canvas.Top(None)

		self.assertEqual("Parameter 'element' is None.", str(context.exception))

	def test_Bottom_Point(self) -> None:
		canvas = Canvas()

		with self.assertRaises(TypeError) as context:
			_ = canvas.Bottom(Point2D(1, 2))

		self.assertEqual("Parameter 'element' is not of type 'Element2D'.", str(context.exception))
		self.assertListEqual(["Got type 'pyTooling.Cartesian2D.Point2D'."], context.exception.__notes__)

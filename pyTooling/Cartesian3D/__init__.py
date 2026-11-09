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
# Copyright 2025-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
An implementation of 3D cartesian data structures for Python.

.. seealso::

   :mod:`pyTooling.Cartesian2D`
      |rarr| The same data structures in two dimensions.
   :mod:`pyTooling.Cartesian3D.Volumes`
      |rarr| Volumes built from these points and offsets.
   :mod:`pyTooling.Cartesian3D.Groups`
      |rarr| Groups of segments and groups, with coordinates relative to the group.
"""
from __future__            import annotations

from copy                  import deepcopy
from enum                  import Enum
from math                  import atan2, sqrt
from typing                import TYPE_CHECKING, Any, ClassVar, Generic, Hashable, Iterable, Mapping, \
                                  Optional as Nullable, Self, Union

from pyTooling.Decorators  import readonly, export
from pyTooling.MetaClasses import ExtendedType, abstractclass, abstractmethod
from pyTooling.Exceptions  import InvalidOperationError
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.DataModel   import KeyValuePairsMixin
from pyTooling.Cartesian2D import Coordinate, AlreadyOwnedError, DuplicatePointError, GroupCycleError, \
                                  NotInSameFrameError

if TYPE_CHECKING:
	from pyTooling.Cartesian3D.Groups import Group3D


@export
class Alignment3D(Enum):
	"""
	Edge or center of a bounding box, two elements are aligned at.

	The members name the smaller or larger coordinate, like :class:`BoundingBox3D`, so they don't depend on the direction
	of an axis.
	"""

	MinX =    0  #: Align the smallest x-coordinates.
	CenterX = 1  #: Align the centers in x-direction.
	MaxX =    2  #: Align the largest x-coordinates.
	MinY =    3  #: Align the smallest y-coordinates.
	CenterY = 4  #: Align the centers in y-direction.
	MaxY =    5  #: Align the largest y-coordinates.
	MinZ =    6  #: Align the smallest z-coordinates.
	CenterZ = 7  #: Align the centers in z-direction.
	MaxZ =    8  #: Align the largest z-coordinates.


@export
@abstractclass
class Base3D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""
	Abstract base-class of everything having a parent and coordinates relative to a frame: points, segments and groups.

	A frame is what the coordinates are relative to, and a group is the frame of its children. Every frame is an instance
	of this class.
	"""

	_PARENT_TYPE: ClassVar[tuple[type, ...]]  #: Types a parent of this class can have.

	_parent: Nullable[Base3D[Coordinate]]  #: Parent of this object, or ``None``.

	def __init__(self, *, parent: Nullable[Base3D[Coordinate]] = None) -> None:
		"""
		Initializes the parent relation.

		:param parent:     Optional, the parent of this object. Default: ``None``, no parent.
		:raises TypeError: If parameter 'parent' is not of a type in :attr:`_PARENT_TYPE`.
		"""
		if parent is not None and not isinstance(parent, self._PARENT_TYPE):
			typeNames = " or ".join(f"'{parentType.__name__}'" for parentType in self._PARENT_TYPE)
			ex =        TypeError(f"Parameter 'parent' is not of type {typeNames}.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		self._parent = parent

	@property
	def Parent(self) -> Nullable[Base3D[Coordinate]]:
		"""
		Property to access the parent of this object (:attr:`_parent`).

		A point's parent is the segment owning it. A segment's or group's parent is the group holding it.

		Only an :class:`Element3D` can be assigned a parent. Assigning a group moves the element into it, assigning
		``None`` removes it from its parent. The element keeps its local coordinates, so its absolute position changes with
		the frame. Use :meth:`Element3D.MoveTo` to keep the absolute position.

		:returns:                The parent, or ``None``, if this object has no parent.
		:raises TypeError:       If an assigned value is not of a type in :attr:`_PARENT_TYPE`.
		:raises TypeError:       If a parent is assigned to a :class:`Point3D`.
		:raises TypeError:       If an assigned value is not of type :class:`~pyTooling.Cartesian3D.Groups.Group3D`, while
		                         this object is an :class:`Element3D`.
		:raises GroupCycleError: If an assigned group is this element or one of its descendants.
		"""
		return self._parent

	@Parent.setter
	def Parent(self, parent: Nullable[Base3D[Coordinate]]) -> None:
		if parent is not None and not isinstance(parent, self._PARENT_TYPE):
			typeNames = " or ".join(f"'{parentType.__name__}'" for parentType in self._PARENT_TYPE)
			ex =        TypeError(f"Parameter 'parent' is not of type {typeNames}.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

		self._parent = parent

	@readonly
	def Frame(self) -> Nullable[Base3D[Coordinate]]:
		"""
		Read-only property to return the frame this object's coordinates are relative to.

		The frame comes from the parent. An object without a parent has no frame, its coordinates are relative to the
		origin.

		:returns: The frame, or ``None``, if this object has no frame.
		"""
		return None if self._parent is None else self._parent._ChildFrame

	@readonly
	def _ChildFrame(self) -> Nullable[Base3D[Coordinate]]:
		"""
		Read-only property to access the frame the coordinates of this object's children are relative to (:attr:`Frame`).

		:returns: This object's frame, or ``None``, if this object has no frame.
		"""
		return self.Frame


@export
class Point3D(Base3D[Coordinate], Generic[Coordinate]):
	"""An implementation of a 3D cartesian point."""

	_x: Coordinate  #: The x-direction coordinate.
	_y: Coordinate  #: The y-direction coordinate.
	_z: Coordinate  #: The z-direction coordinate.

	def __init__(
		self,
		x:      Coordinate,
		y:      Coordinate,
		z:      Coordinate,
		*,
		parent: Nullable[Element3D[Coordinate]] = None
	) -> None:
		"""
		Initializes a 3-dimensional point.

		A segment takes ownership of the point, when it's given the point instead of copying it.

		Parameter ``parent`` sets the owner, but doesn't register the point in it: the parent's points don't change. The
		point is in the parent's frame, so it can be combined with the parent's points.

		:param x:           X-coordinate.
		:param y:           Y-coordinate.
		:param z:           Z-coordinate.
		:param parent:      Optional, the segment owning the point. Default: ``None``, no owner.
		:raises ValueError: If parameter 'x' is None.
		:raises TypeError:  If parameter 'x' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'y' is None.
		:raises TypeError:  If parameter 'y' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'z' is None.
		:raises TypeError:  If parameter 'z' is not of type :class:`float` or :class:`int`.
		:raises TypeError:  If parameter 'parent' is not of type :class:`Element3D`.
		"""
		super().__init__(parent=parent)

		if x is None:
			raise ValueError("Parameter 'x' is None.")
		elif not isinstance(x, (int, float)):
			ex = TypeError("Parameter 'x' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(x)}'.")
			raise ex

		if y is None:
			raise ValueError("Parameter 'y' is None.")
		elif not isinstance(y, (int, float)):
			ex = TypeError("Parameter 'y' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(y)}'.")
			raise ex

		if z is None:
			raise ValueError("Parameter 'z' is None.")
		elif not isinstance(z, (int, float)):
			ex = TypeError("Parameter 'z' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(z)}'.")
			raise ex

		self._x = x
		self._y = y
		self._z = z

	@Base3D.Parent.setter
	def Parent(self, parent: Nullable[Element3D[Coordinate]]) -> None:
		ex = TypeError(f"The parent of a '{getFullyQualifiedName(self)}' is read-only.")
		ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
		ex.add_note("A segment takes ownership of a point, when it's given the point.")
		raise ex

	@property
	def X(self) -> Coordinate:
		"""
		Property to access the x-direction coordinate (:attr:`_x`).

		``x`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The x-direction coordinate.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._x

	@X.setter
	def X(self, x: Coordinate) -> None:
		if x is None:
			raise ValueError("Parameter 'x' is None.")
		elif not isinstance(x, (int, float)):
			ex = TypeError("Parameter 'x' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(x)}'.")
			raise ex

		self._x = x

	x = X

	@property
	def Y(self) -> Coordinate:
		"""
		Property to access the y-direction coordinate (:attr:`_y`).

		``y`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The y-direction coordinate.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._y

	@Y.setter
	def Y(self, y: Coordinate) -> None:
		if y is None:
			raise ValueError("Parameter 'y' is None.")
		elif not isinstance(y, (int, float)):
			ex = TypeError("Parameter 'y' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(y)}'.")
			raise ex

		self._y = y

	y = Y

	@property
	def Z(self) -> Coordinate:
		"""
		Property to access the z-direction coordinate (:attr:`_z`).

		``z`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The z-direction coordinate.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._z

	@Z.setter
	def Z(self, z: Coordinate) -> None:
		if z is None:
			raise ValueError("Parameter 'z' is None.")
		elif not isinstance(z, (int, float)):
			ex = TypeError("Parameter 'z' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(z)}'.")
			raise ex

		self._z = z

	z = Z

	@readonly
	def Absolute(self) -> Point3D[Coordinate]:
		"""
		Read-only property to return the point's position relative to the origin as a new 3D-point.

		The offsets of all groups up the parent chain are added to the point's coordinates. The new point has no owner.

		:returns: A new 3D-point with absolute coordinates.
		"""
		if (frame := self.Frame) is None:
			return Point3D(self._x, self._y, self._z)

		offset = frame.AbsoluteOffset
		return Point3D(self._x + offset._xOffset, self._y + offset._yOffset, self._z + offset._zOffset)

	def Copy(self) -> Self:
		"""
		Create a new 3D-point as a copy of this 3D point.

		The copy has no owner.

		:returns: Copy of this 3D-point.

		.. seealso::

		   :meth:`+ operator <__add__>`
		     Create a new 3D-point moved by a positive 3D-offset.
		   :meth:`- operator <__sub__>`
		     Create a new 3D-point moved by a negative 3D-offset.
		"""
		return self.__class__(self._x, self._y, self._z)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this 3D-point for :func:`copy.copy`.

		:returns: Copy of this 3D-point.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this 3D-point for :func:`copy.deepcopy`.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this 3D-point.
		"""
		return self.Copy()

	def ToTuple(self) -> tuple[Coordinate, Coordinate, Coordinate]:
		"""
		Convert this 3D-Point to a simple 3-element tuple.

		:returns: ``(x, y, z)`` tuple.
		"""
		return self._x, self._y, self._z

	def _MirrorAt(self, normal: Vector3D[float], distance: float) -> None:
		"""
		Mirror the point at the plane ``nx * x + ny * y + nz * z = distance`` in the point's frame (inplace).

		The point moves by ``-2 * (nx * x + ny * y + nz * z - distance)`` times the normal.

		:param normal:   The normal of the plane, of length 1.
		:param distance: The signed distance of the plane from the frame's origin.
		"""
		factor = 2 * (normal._xOffset * self._x + normal._yOffset * self._y + normal._zOffset * self._z - distance)
		self._x -= factor * normal._xOffset
		self._y -= factor * normal._yOffset
		self._z -= factor * normal._zOffset

	def __add__(self, other: Any) -> Point3D[Coordinate]:
		"""
		Adds a 3D-vector to this 3D-point and creates a new 3D-point.

		:param other:      A 3D-vector as :class:`Vector3D`, :class:`Offset3D` or tuple.
		:returns:          A new 3D-point shifted by the 3D-vector.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector3D` or :class:`tuple`.
		"""
		if isinstance(other, BaseVector3D):
			return self.__class__(
				self._x + other._xOffset,
				self._y + other._yOffset,
				self._z + other._zOffset
			)
		elif isinstance(other, tuple):
			return self.__class__(
				self._x + other[0],
				self._y + other[1],
				self._z + other[2]
			)
		else:
			ex = TypeError("Parameter 'other' is not of type 'BaseVector3D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __iadd__(self, other: Any) -> Self:
		"""
		Adds a 3D-vector to this 3D-point (inplace).

		:param other:      A 3D-vector as :class:`Vector3D`, :class:`Offset3D` or tuple.
		:returns:          This 3D-point.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector3D` or :class:`tuple`.
		"""
		if isinstance(other, BaseVector3D):
			self._x += other._xOffset
			self._y += other._yOffset
			self._z += other._zOffset
		elif isinstance(other, tuple):
			self.X += other[0]
			self.Y += other[1]
			self.Z += other[2]
		else:
			ex = TypeError("Parameter 'other' is not of type 'BaseVector3D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __sub__(self, other: Any) -> Union[Offset3D[Coordinate], Point3D[Coordinate]]:
		"""
		Subtract a 3D-point from this 3D-point and create a new 3D-offset, or a 3D-vector and create a new 3D-point.

		:param other:                The second 3D-point as :class:`Point3D`, or a 3D-vector as :class:`Vector3D` or
		                             :class:`Offset3D`.
		:returns:                    A new 3D-offset representing the distance between these two points, or a new 3D-point
		                             shifted back by the 3D-vector.
		:raises TypeError:           If parameter 'other' is not of type :class:`Point3D` or :class:`BaseVector3D`.
		:raises NotInSameFrameError: If parameter 'other' is in another frame than this point. |br|
		                             Subtract the points' :attr:`Absolute` positions instead.
		"""
		if isinstance(other, Point3D):
			if self.Frame is not other.Frame:
				ex = NotInSameFrameError("Points are in different frames.")
				ex.add_note(f"Got points {self} and {other}.")
				ex.add_note("Subtract the points' 'Absolute' positions instead.")
				raise ex from ValueError("Parameter 'other' is in another frame.")

			return Offset3D(
				self._x - other._x,
				self._y - other._y,
				self._z - other._z
			)
		elif isinstance(other, BaseVector3D):
			return Point3D(
				self._x - other._xOffset,
				self._y - other._yOffset,
				self._z - other._zOffset
			)
		else:
			ex = TypeError("Parameter 'other' is not of type 'Point3D' or 'BaseVector3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __isub__(self, other: Any) -> Self:
		"""
		Subtracts a 3D-vector from this 3D-point (inplace).

		:param other:      A 3D-vector as :class:`Vector3D`, :class:`Offset3D` or tuple.
		:returns:          This 3D-point.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector3D` or :class:`tuple`.
		"""
		if isinstance(other, BaseVector3D):
			self._x -= other._xOffset
			self._y -= other._yOffset
			self._z -= other._zOffset
		elif isinstance(other, tuple):
			self.X -= other[0]
			self.Y -= other[1]
			self.Z -= other[2]
		else:
			ex = TypeError("Parameter 'other' is not of type 'BaseVector3D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __repr__(self) -> str:
		"""
		Returns the 3D point's string representation.

		:returns: The string representation of the 3D point.
		"""
		return f"Point3D({self._x}, {self._y}, {self._z})"

	def __str__(self) -> str:
		"""
		Returns the 3D point's string equivalent.

		:returns: The string equivalent of the 3D point.
		"""
		return f"({self._x}, {self._y}, {self._z})"


@export
class Origin3D(Point3D[Coordinate], Generic[Coordinate]):
	"""An implementation of a 3D cartesian origin."""

	def __init__(self) -> None:
		"""
		Initializes a 3-dimensional origin.
		"""
		super().__init__(0, 0, 0)

	def Copy(self) -> Self:
		"""
		An origin is a singular point, so it can't be copied.

		:raises InvalidOperationError: Always, because an origin is a singular point.
		"""
		raise InvalidOperationError("An origin can't be copied.")

	def __repr__(self) -> str:
		"""
		Returns the 3D origin's string representation.

		:returns: The string representation of the 3D origin.
		"""
		return f"Origin3D({self._x}, {self._y}, {self._z})"


@export
@abstractclass
class Element3D(Base3D[Coordinate], KeyValuePairsMixin, Generic[Coordinate]):
	"""
	Abstract base-class of all elements a :class:`~pyTooling.Cartesian3D.Groups.Group3D` can hold: segments and groups.

	An element belongs to at most one group, its :attr:`Parent`. Its coordinates are relative to its parent, an element
	without a parent is relative to the origin.

	An element carries an optional :attr:`Value` and arbitrary key-value-pairs
	(:class:`~pyTooling.DataModel.KeyValuePairsMixin`). Use the dictionary syntax to get and set key-value-pairs:
	``in``, :pycode:`len(element)` and iterating an element address the key-value-pairs, not its points or children.

	A derived class implements :attr:`BoundingBox`, :meth:`Move`, :meth:`_MirrorX`, :meth:`_MirrorY`, :meth:`_MirrorZ`
	and :meth:`_MirrorAt`. Its initializer takes the keyword-only parameters ``value``, ``keyValuePairs`` and
	``parent``, and assigns ``parent`` to :attr:`Parent` as its last statement, when the element is fully initialized.
	"""

	# WORKAROUND: Python <3.13
	# A type variable with a default (PEP 696) isn't supported by Python 3.11 and 3.12. Use it when their support gets
	# dropped:
	# ValueType = TypeVar("ValueType", default=Any)
	# class Element3D(Base3D[Coordinate], KeyValuePairsMixin, Generic[Coordinate, ValueType]): ... _value: ValueType
	_value: Any  #: Value of the element.

	def __init__(
		self,
		*,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Group3D[Coordinate]] = None
	) -> None:
		"""
		Initializes an element without a parent and checks the group it will be registered in.

		:param value:         Optional, value of the element. Default: ``None``.
		:param keyValuePairs: Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:        Optional, the group the derived class registers the element in. Default: ``None``, no
		                      parent.
		:raises TypeError:    If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:    If parameter 'parent' is not of type :class:`~pyTooling.Cartesian3D.Groups.Group3D`.
		"""
		# Imported for its side effect: it assigns '_PARENT_TYPE' of the element classes.
		from pyTooling.Cartesian3D import Groups

		super().__init__(parent=parent)
		KeyValuePairsMixin.__init__(self, keyValuePairs)

		# The derived class registers the element by assigning 'Parent' as its last statement.
		self._parent = None
		self._value =  value

	@Base3D.Parent.setter
	def Parent(self, parent: Nullable[Group3D]) -> None:
		from pyTooling.Cartesian3D.Groups import Container3DMixin

		if parent is not None and not isinstance(parent, Container3DMixin):
			ex = TypeError("Parameter 'parent' is not of type 'Group3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex
		elif parent is self._parent:
			return

		frame = parent
		while frame is not None:
			if frame is self:
				ex = GroupCycleError("Group would contain itself.")
				ex.add_note(f"Got {parent!r} as parent of {self!r}.")
				raise ex from ValueError("Parameter 'parent' is this element or one of its descendants.")

			frame = frame.Frame

		if self._parent is not None:
			self._parent._children.remove(self)

		if parent is not None:
			parent._children.append(self)

		Base3D.Parent.fset(self, parent)

	@property
	def Value(self) -> Any:
		"""
		Property to access the element's value (:attr:`_value`).

		The value is any object attached to the element, for example the model object a segment draws. It is neither
		checked nor copied.

		:returns: The element's value, or ``None``, if it has no value.
		"""
		return self._value

	@Value.setter
	def Value(self, value: Any) -> None:
		self._value = value

	@readonly
	@abstractmethod
	def BoundingBox(self) -> BoundingBox3D[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing the element.

		The bounding box is in the element's frame.

		:returns: A new bounding box.
		"""

	@readonly
	def AbsoluteBoundingBox(self) -> BoundingBox3D[Coordinate]:
		"""
		Read-only property to return the element's bounding box relative to the origin.

		The offsets of all groups up the parent chain are added to :attr:`BoundingBox`.

		:returns: A new bounding box.
		"""
		frame = self.Frame
		return self.BoundingBox if frame is None else self.BoundingBox + frame.AbsoluteOffset

	@abstractmethod
	def Move(self, offset: BaseVector3D[Coordinate]) -> None:
		"""
		Move the element by an offset in its frame (inplace).

		:param offset: The 3D-vector or 3D-offset to move by.
		"""

	def MirrorX(self, plane: Alignment3D = Alignment3D.CenterX, offset: Coordinate = 0) -> None:
		r"""
		Mirror the element at a plane parallel to the yz-plane through its bounding box (inplace).

		The plane runs through the smallest x-coordinate (``MinX``), the center (``CenterX``) or the largest x-coordinate
		(``MaxX``) of the element's :attr:`BoundingBox`, shifted by ``offset`` in x-direction. For a plane at ``x = a``,
		every x-coordinate ``x`` becomes ``2a - x``; the y- and z-coordinates stay. A group mirrors its offset, and its
		children at the group's origin.

		Mirrored at ``Alignment3D.MaxX``, seen along the z-axis: the element on the left of the plane is mirrored to the
		right of it.

		.. code-block:: text

		             plane at MaxX
		             |
		        +----+----+
		        | \  |  / |
		        |  \ | /  |
		        +----+----+
		             |
		        before  after

		:param plane:       Optional, the edge or center of the bounding box the plane runs through. Default:
		                    ``Alignment3D.CenterX``.
		:param offset:      Optional, the distance of the plane from that edge or center in x-direction. Default: ``0``.
		:raises ValueError: If parameter 'plane' is None.
		:raises TypeError:  If parameter 'plane' is not of type :class:`Alignment3D`.
		:raises ValueError: If parameter 'plane' is not ``MinX``, ``CenterX`` or ``MaxX``.
		:raises ValueError: If parameter 'offset' is None.
		:raises TypeError:  If parameter 'offset' is not of type :class:`float` or :class:`int`.
		"""
		if plane is None:
			raise ValueError("Parameter 'plane' is None.")
		elif not isinstance(plane, Alignment3D):
			ex = TypeError("Parameter 'plane' is not of type 'Alignment3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(plane)}'.")
			raise ex
		elif plane not in (Alignment3D.MinX, Alignment3D.CenterX, Alignment3D.MaxX):
			ex = ValueError("Parameter 'plane' is not Alignment3D.MinX, Alignment3D.CenterX or Alignment3D.MaxX.")
			ex.add_note(f"Got value '{plane}'.")
			raise ex

		if offset is None:
			raise ValueError("Parameter 'offset' is None.")
		elif not isinstance(offset, (int, float)):
			ex = TypeError("Parameter 'offset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		box = self.BoundingBox
		if plane is Alignment3D.MinX:
			twiceAxis = 2 * box._minX
		elif plane is Alignment3D.CenterX:
			twiceAxis = box._minX + box._maxX
		else:
			twiceAxis = 2 * box._maxX

		self._MirrorX(twiceAxis + 2 * offset)

	@abstractmethod
	def _MirrorX(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the element at a plane parallel to the yz-plane, so ``x`` becomes ``twiceAxis - x`` (inplace).

		:param twiceAxis: Twice the x-coordinate of the plane.
		"""

	def MirrorY(self, plane: Alignment3D = Alignment3D.CenterY, offset: Coordinate = 0) -> None:
		r"""
		Mirror the element at a plane parallel to the xz-plane through its bounding box (inplace).

		The plane runs through the smallest y-coordinate (``MinY``), the center (``CenterY``) or the largest y-coordinate
		(``MaxY``) of the element's :attr:`BoundingBox`, shifted by ``offset`` in y-direction. For a plane at ``y = a``,
		every y-coordinate ``y`` becomes ``2a - y``; the x- and z-coordinates stay. A group mirrors its offset, and its
		children at the group's origin.

		Mirrored at ``Alignment3D.MinY``, seen along the z-axis with the y-axis pointing up: the element above the plane is
		mirrored below it.

		.. code-block:: text

		        +----+
		        |  \ |    before
		        |   \|
		     ---+----+--- plane at MinY
		        |   /|
		        |  / |    after
		        +----+

		:param plane:       Optional, the edge or center of the bounding box the plane runs through. Default:
		                    ``Alignment3D.CenterY``.
		:param offset:      Optional, the distance of the plane from that edge or center in y-direction. Default: ``0``.
		:raises ValueError: If parameter 'plane' is None.
		:raises TypeError:  If parameter 'plane' is not of type :class:`Alignment3D`.
		:raises ValueError: If parameter 'plane' is not ``MinY``, ``CenterY`` or ``MaxY``.
		:raises ValueError: If parameter 'offset' is None.
		:raises TypeError:  If parameter 'offset' is not of type :class:`float` or :class:`int`.
		"""
		if plane is None:
			raise ValueError("Parameter 'plane' is None.")
		elif not isinstance(plane, Alignment3D):
			ex = TypeError("Parameter 'plane' is not of type 'Alignment3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(plane)}'.")
			raise ex
		elif plane not in (Alignment3D.MinY, Alignment3D.CenterY, Alignment3D.MaxY):
			ex = ValueError("Parameter 'plane' is not Alignment3D.MinY, Alignment3D.CenterY or Alignment3D.MaxY.")
			ex.add_note(f"Got value '{plane}'.")
			raise ex

		if offset is None:
			raise ValueError("Parameter 'offset' is None.")
		elif not isinstance(offset, (int, float)):
			ex = TypeError("Parameter 'offset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		box = self.BoundingBox
		if plane is Alignment3D.MinY:
			twiceAxis = 2 * box._minY
		elif plane is Alignment3D.CenterY:
			twiceAxis = box._minY + box._maxY
		else:
			twiceAxis = 2 * box._maxY

		self._MirrorY(twiceAxis + 2 * offset)

	@abstractmethod
	def _MirrorY(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the element at a plane parallel to the xz-plane, so ``y`` becomes ``twiceAxis - y`` (inplace).

		:param twiceAxis: Twice the y-coordinate of the plane.
		"""

	def MirrorZ(self, plane: Alignment3D = Alignment3D.CenterZ, offset: Coordinate = 0) -> None:
		r"""
		Mirror the element at a plane parallel to the xy-plane through its bounding box (inplace).

		The plane runs through the smallest z-coordinate (``MinZ``), the center (``CenterZ``) or the largest z-coordinate
		(``MaxZ``) of the element's :attr:`BoundingBox`, shifted by ``offset`` in z-direction. For a plane at ``z = a``,
		every z-coordinate ``z`` becomes ``2a - z``; the x- and y-coordinates stay. A group mirrors its offset, and its
		children at the group's origin.

		Mirrored at ``Alignment3D.MaxZ``, seen along the y-axis with the z-axis pointing right: the element on the left of
		the plane is mirrored to the right of it.

		.. code-block:: text

		             plane at MaxZ
		             |
		        +----+----+
		        | \  |  / |
		        |  \ | /  |
		        +----+----+
		             |
		        before  after

		:param plane:       Optional, the edge or center of the bounding box the plane runs through. Default:
		                    ``Alignment3D.CenterZ``.
		:param offset:      Optional, the distance of the plane from that edge or center in z-direction. Default: ``0``.
		:raises ValueError: If parameter 'plane' is None.
		:raises TypeError:  If parameter 'plane' is not of type :class:`Alignment3D`.
		:raises ValueError: If parameter 'plane' is not ``MinZ``, ``CenterZ`` or ``MaxZ``.
		:raises ValueError: If parameter 'offset' is None.
		:raises TypeError:  If parameter 'offset' is not of type :class:`float` or :class:`int`.
		"""
		if plane is None:
			raise ValueError("Parameter 'plane' is None.")
		elif not isinstance(plane, Alignment3D):
			ex = TypeError("Parameter 'plane' is not of type 'Alignment3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(plane)}'.")
			raise ex
		elif plane not in (Alignment3D.MinZ, Alignment3D.CenterZ, Alignment3D.MaxZ):
			ex = ValueError("Parameter 'plane' is not Alignment3D.MinZ, Alignment3D.CenterZ or Alignment3D.MaxZ.")
			ex.add_note(f"Got value '{plane}'.")
			raise ex

		if offset is None:
			raise ValueError("Parameter 'offset' is None.")
		elif not isinstance(offset, (int, float)):
			ex = TypeError("Parameter 'offset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		box = self.BoundingBox
		if plane is Alignment3D.MinZ:
			twiceAxis = 2 * box._minZ
		elif plane is Alignment3D.CenterZ:
			twiceAxis = box._minZ + box._maxZ
		else:
			twiceAxis = 2 * box._maxZ

		self._MirrorZ(twiceAxis + 2 * offset)

	@abstractmethod
	def _MirrorZ(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the element at a plane parallel to the xy-plane, so ``z`` becomes ``twiceAxis - z`` (inplace).

		:param twiceAxis: Twice the z-coordinate of the plane.
		"""

	@abstractmethod
	def _MirrorAt(self, normal: Vector3D[float], distance: float) -> None:
		"""
		Mirror the element at the plane ``nx * x + ny * y + nz * z = distance`` in the element's frame (inplace).

		:param normal:   The normal of the plane, of length 1.
		:param distance: The signed distance of the plane from the frame's origin.
		"""

	def MirrorAt(self, plane: Plane3D[Coordinate]) -> None:
		r"""
		Mirror the element at a plane (inplace).

		The plane is in absolute coordinates, relative to the origin, so elements of different groups can be mirrored at
		the same plane. At a plane ``x = a``, every absolute x-coordinate ``x`` becomes ``2a - x``; the planes ``y = a`` and
		``z = a`` mirror the y- and z-coordinates the same way; a :class:`Plane3D` with normal ``(1, 0, 0)``, ``(0, 1, 0)``
		or ``(0, 0, 1)`` is such a plane too. At an oblique plane ``nx * x + ny * y + nz * z = d``, every absolute point
		moves by ``-2 * (nx * x + ny * y + nz * z - d)`` times the normal. A group mirrors its offset, and its children at
		the plane through the group's origin with the same normal.

		Mirrored at a plane ``x = a``, seen along the z-axis: the element on the left of the plane is mirrored to the
		right of it.

		.. code-block:: text

		                     x = a
		                       |
		        +----+         |         +----+
		        | \  |         |         |  / |
		        |  \ |         |         | /  |
		        +----+         |         +----+
		                       |
		        before                   after

		:param plane:       The plane to mirror at, like a :class:`YZPlane3D`, :class:`XZPlane3D` or :class:`XYPlane3D`.
		:raises ValueError: If parameter 'plane' is None.
		:raises TypeError:  If parameter 'plane' is not of type :class:`Plane3D`.
		"""
		if plane is None:
			raise ValueError("Parameter 'plane' is None.")
		elif not isinstance(plane, Plane3D):
			ex = TypeError("Parameter 'plane' is not of type 'Plane3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(plane)}'.")
			raise ex

		plane._MirrorElement(self)

	def MoveTo(self, parent: Nullable[Group3D], keepPosition: bool = True) -> None:
		"""
		Move the element into another group.

		With ``keepPosition``, the element is moved by the difference of both frames, so its absolute position stays.
		Otherwise, it keeps its local coordinates, like an assignment to :attr:`Parent`.

		:param parent:           The new parent group, or ``None`` for no parent.
		:param keepPosition:     Optional, if ``True``, the absolute position is kept. Default: ``True``.
		:raises TypeError:       If parameter 'parent' is not of type :class:`~pyTooling.Cartesian3D.Groups.Group3D`.
		:raises GroupCycleError: If parameter 'parent' is this element or one of its descendants.
		:raises ValueError:      If parameter 'keepPosition' is None.
		:raises TypeError:       If parameter 'keepPosition' is not of type :class:`bool`.
		"""
		if keepPosition is None:
			raise ValueError("Parameter 'keepPosition' is None.")
		elif not isinstance(keepPosition, bool):
			ex = TypeError("Parameter 'keepPosition' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(keepPosition)}'.")
			raise ex

		frame =          self.Frame
		previousOffset = Offset3D(0, 0, 0) if frame is None else frame.AbsoluteOffset

		self.Parent = parent

		if not keepPosition:
			return

		if (frame := self.Frame) is None:
			self.Move(previousOffset)
		else:
			self.Move(previousOffset - frame.AbsoluteOffset)

	def AlignTo(self, reference: Element3D[Coordinate], alignment: Alignment3D) -> None:
		"""
		Move the element, so an edge or the center of its bounding box aligns with the one of another element.

		Both elements may be in different frames: their absolute bounding boxes are compared.

		:param reference:   The element to align with. It isn't moved.
		:param alignment:   The edge or center to align.
		:raises ValueError: If parameter 'reference' is None.
		:raises TypeError:  If parameter 'reference' is not of type :class:`Element3D`.
		:raises ValueError: If parameter 'alignment' is None.
		:raises TypeError:  If parameter 'alignment' is not of type :class:`Alignment3D`.
		"""
		if reference is None:
			raise ValueError("Parameter 'reference' is None.")
		elif not isinstance(reference, Element3D):
			ex = TypeError("Parameter 'reference' is not of type 'Element3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(reference)}'.")
			raise ex

		if alignment is None:
			raise ValueError("Parameter 'alignment' is None.")
		elif not isinstance(alignment, Alignment3D):
			ex = TypeError("Parameter 'alignment' is not of type 'Alignment3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(alignment)}'.")
			raise ex

		box =          self.AbsoluteBoundingBox
		referenceBox = reference.AbsoluteBoundingBox
		if alignment is Alignment3D.MinX:
			offset = Offset3D(referenceBox._minX - box._minX, 0, 0)
		elif alignment is Alignment3D.CenterX:
			offset = Offset3D((referenceBox._minX + referenceBox._maxX - box._minX - box._maxX) / 2, 0, 0)
		elif alignment is Alignment3D.MaxX:
			offset = Offset3D(referenceBox._maxX - box._maxX, 0, 0)
		elif alignment is Alignment3D.MinY:
			offset = Offset3D(0, referenceBox._minY - box._minY, 0)
		elif alignment is Alignment3D.CenterY:
			offset = Offset3D(0, (referenceBox._minY + referenceBox._maxY - box._minY - box._maxY) / 2, 0)
		elif alignment is Alignment3D.MaxY:
			offset = Offset3D(0, referenceBox._maxY - box._maxY, 0)
		elif alignment is Alignment3D.MinZ:
			offset = Offset3D(0, 0, referenceBox._minZ - box._minZ)
		elif alignment is Alignment3D.CenterZ:
			offset = Offset3D(0, 0, (referenceBox._minZ + referenceBox._maxZ - box._minZ - box._maxZ) / 2)
		else:
			offset = Offset3D(0, 0, referenceBox._maxZ - box._maxZ)

		self.Move(offset)


Point3D._PARENT_TYPE = (Element3D, )


@export
@abstractclass
class BaseVector3D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""
	Abstract base-class of 3D cartesian vectors: the immutable :class:`Vector3D` and the mutable :class:`Offset3D`.

	An operator creating a new vector returns a vector of its left operand's class; the right operand can be a vector of
	either class or a tuple. Vectors of both classes compare equal, if their components are equal.
	"""

	_xOffset: Coordinate  #: The x-direction component.
	_yOffset: Coordinate  #: The y-direction component.
	_zOffset: Coordinate  #: The z-direction component.

	def __init__(self, xOffset: Coordinate, yOffset: Coordinate, zOffset: Coordinate) -> None:
		"""
		Initializes a 3-dimensional vector.

		:param xOffset:     x-direction component.
		:param yOffset:     y-direction component.
		:param zOffset:     z-direction component.
		:raises ValueError: If parameter 'xOffset' is None.
		:raises TypeError:  If parameter 'xOffset' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'yOffset' is None.
		:raises TypeError:  If parameter 'yOffset' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'zOffset' is None.
		:raises TypeError:  If parameter 'zOffset' is not of type :class:`float` or :class:`int`.
		"""
		if xOffset is None:
			raise ValueError("Parameter 'xOffset' is None.")
		elif not isinstance(xOffset, (int, float)):
			ex = TypeError("Parameter 'xOffset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(xOffset)}'.")
			raise ex

		if yOffset is None:
			raise ValueError("Parameter 'yOffset' is None.")
		elif not isinstance(yOffset, (int, float)):
			ex = TypeError("Parameter 'yOffset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(yOffset)}'.")
			raise ex

		if zOffset is None:
			raise ValueError("Parameter 'zOffset' is None.")
		elif not isinstance(zOffset, (int, float)):
			ex = TypeError("Parameter 'zOffset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(zOffset)}'.")
			raise ex

		self._xOffset = xOffset
		self._yOffset = yOffset
		self._zOffset = zOffset

	@readonly
	def XOffset(self) -> Coordinate:
		"""
		Read-only property to access the x-direction component (:attr:`_xOffset`).

		:returns: The x-direction component.
		"""
		return self._xOffset

	@readonly
	def YOffset(self) -> Coordinate:
		"""
		Read-only property to access the y-direction component (:attr:`_yOffset`).

		:returns: The y-direction component.
		"""
		return self._yOffset

	@readonly
	def ZOffset(self) -> Coordinate:
		"""
		Read-only property to access the z-direction component (:attr:`_zOffset`).

		:returns: The z-direction component.
		"""
		return self._zOffset

	@readonly
	def Length(self) -> float:
		"""
		Read-only property to return the Euclidean length of this 3D-vector.

		:returns: The Euclidean length.
		"""
		return sqrt(self._xOffset ** 2 + self._yOffset ** 2 + self._zOffset ** 2)

	def ScalarProduct(self, other: BaseVector3D[Coordinate]) -> Coordinate:
		"""
		Compute the :term:`dot product <Dot Product>` of this 3D-vector and another 3D-vector.

		The dot product ``x1 * x2 + y1 * y2 + z1 * z2`` is zero for perpendicular vectors.

		:param other:       The second 3D-vector.
		:returns:           The dot product.
		:raises ValueError: If parameter 'other' is None.
		:raises TypeError:  If parameter 'other' is not of type :class:`BaseVector3D`.
		"""
		if other is None:
			raise ValueError("Parameter 'other' is None.")
		elif not isinstance(other, BaseVector3D):
			ex = TypeError("Parameter 'other' is not of type 'BaseVector3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._xOffset * other._xOffset + self._yOffset * other._yOffset + self._zOffset * other._zOffset

	def VectorProduct(self, other: BaseVector3D[Coordinate]) -> Self:
		"""
		Compute the :term:`cross product <Cross Product>` of this 3D-vector and another 3D-vector as a new 3D-vector.

		The cross product is perpendicular to both vectors, its length is the area of the parallelogram they span, and it
		is a zero vector for parallel vectors. The vectors and the cross product form a right-handed system: the cross
		product of ``(1, 0, 0)`` and ``(0, 1, 0)`` is ``(0, 0, 1)``.

		:param other:       The second 3D-vector.
		:returns:           A new 3D-vector, of this vector's class.
		:raises ValueError: If parameter 'other' is None.
		:raises TypeError:  If parameter 'other' is not of type :class:`BaseVector3D`.
		"""
		if other is None:
			raise ValueError("Parameter 'other' is None.")
		elif not isinstance(other, BaseVector3D):
			ex = TypeError("Parameter 'other' is not of type 'BaseVector3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self.__class__(
			self._yOffset * other._zOffset - self._zOffset * other._yOffset,
			self._zOffset * other._xOffset - self._xOffset * other._zOffset,
			self._xOffset * other._yOffset - self._yOffset * other._xOffset
		)

	def Normalized(self) -> Self:
		"""
		Create a new 3D-vector of length 1 in the direction of this 3D-vector.

		:returns:                      A new 3D-vector of length 1, of this vector's class.
		:raises InvalidOperationError: If this 3D-vector is a zero vector. |br|
		                               A zero vector has no direction.
		"""
		if self._xOffset == 0 and self._yOffset == 0 and self._zOffset == 0:
			ex = InvalidOperationError("A zero vector can't be normalized.")
			ex.add_note(f"Got vector {self}.")
			ex.add_note("A zero vector has no direction.")
			raise ex

		length = self.Length
		return self.__class__(
			self._xOffset / length,
			self._yOffset / length,
			self._zOffset / length
		)

	def ToTuple(self) -> tuple[Coordinate, Coordinate, Coordinate]:
		"""
		Convert this 3D-vector to a simple 3-element tuple.

		:returns: ``(x, y, z)`` tuple.
		"""
		return self._xOffset, self._yOffset, self._zOffset

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two 3D-vectors for equality.

		A :class:`Vector3D` and an :class:`Offset3D` are equal, if their components are equal.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both 3D-vectors are equal.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector3D` or :class:`tuple`.
		"""
		if isinstance(other, BaseVector3D):
			return self._xOffset == other._xOffset and self._yOffset == other._yOffset and self._zOffset == other._zOffset
		elif isinstance(other, tuple):
			return self._xOffset == other[0] and self._yOffset == other[1] and self._zOffset == other[2]
		else:
			ex = TypeError("Parameter 'other' is not of type 'BaseVector3D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two 3D-vectors for inequality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both 3D-vectors are unequal.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector3D` or :class:`tuple`.
		"""
		return not self.__eq__(other)

	def __neg__(self) -> Self:
		"""
		Negate all components of this 3D-vector and create a new 3D-vector.

		:returns: A new 3D-vector with negated components, of this vector's class.
		"""
		return self.__class__(
			-self._xOffset,
			-self._yOffset,
			-self._zOffset
		)

	def __add__(self, other: Any) -> Self:
		"""
		Adds a 3D-vector to this 3D-vector and creates a new 3D-vector.

		:param other:      A 3D-vector as :class:`Vector3D`, :class:`Offset3D` or tuple.
		:returns:          A new 3D-vector extended by the 3D-vector, of this vector's class.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector3D` or :class:`tuple`.
		"""
		if isinstance(other, BaseVector3D):
			return self.__class__(
				self._xOffset + other._xOffset,
				self._yOffset + other._yOffset,
				self._zOffset + other._zOffset
			)
		elif isinstance(other, tuple):
			return self.__class__(
				self._xOffset + other[0],
				self._yOffset + other[1],
				self._zOffset + other[2]
			)
		else:
			ex = TypeError("Parameter 'other' is not of type 'BaseVector3D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __sub__(self, other: Any) -> Self:
		"""
		Subtracts a 3D-vector from this 3D-vector and creates a new 3D-vector.

		:param other:      A 3D-vector as :class:`Vector3D`, :class:`Offset3D` or tuple.
		:returns:          A new 3D-vector reduced by the 3D-vector, of this vector's class.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector3D` or :class:`tuple`.
		"""
		if isinstance(other, BaseVector3D):
			return self.__class__(
				self._xOffset - other._xOffset,
				self._yOffset - other._yOffset,
				self._zOffset - other._zOffset
			)
		elif isinstance(other, tuple):
			return self.__class__(
				self._xOffset - other[0],
				self._yOffset - other[1],
				self._zOffset - other[2]
			)
		else:
			ex = TypeError("Parameter 'other' is not of type 'BaseVector3D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

	def __mul__(self, other: Any) -> Self:
		"""
		Multiplies this 3D-vector by a number and creates a new 3D-vector (``vector * number``).

		:param other:      The factor.
		:returns:          A new 3D-vector scaled by the factor, of this vector's class.
		:raises TypeError: If the second operand is not of type :class:`float` or :class:`int`.
		"""
		if not isinstance(other, (int, float)):
			ex = TypeError("Second operand is not supported by * operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: float, int")
			raise ex

		return self.__class__(
			self._xOffset * other,
			self._yOffset * other,
			self._zOffset * other
		)

	def __rmul__(self, other: Any) -> Self:
		"""
		Multiplies a number by this 3D-vector and creates a new 3D-vector (``number * vector``).

		:param other:      The factor.
		:returns:          A new 3D-vector scaled by the factor, of this vector's class.
		:raises TypeError: If the first operand is not of type :class:`float` or :class:`int`.
		"""
		if not isinstance(other, (int, float)):
			ex = TypeError("First operand is not supported by * operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for first operand: float, int")
			raise ex

		return self.__class__(
			other * self._xOffset,
			other * self._yOffset,
			other * self._zOffset
		)

	def __repr__(self) -> str:
		"""
		Returns the 3D vector's string representation.

		:returns: The string representation of the 3D vector.
		"""
		return f"{self.__class__.__name__}({self._xOffset}, {self._yOffset}, {self._zOffset})"

	def __str__(self) -> str:
		"""
		Returns the 3D vector's string equivalent.

		:returns: The string equivalent of the 3D vector.
		"""
		return f"({self._xOffset}, {self._yOffset}, {self._zOffset})"


@export
class Vector3D(BaseVector3D[Coordinate], Generic[Coordinate]):
	"""
	An implementation of an immutable 3D cartesian vector.

	A vector is a value, like a direction or a normal: its components are read-only, and it is hashable, so it can be a
	dictionary key or a set member. ``vector += other`` binds a new vector to the name.
	"""

	_length: Nullable[float]  #: The Euclidean length, or ``None`` until it is read the first time.

	def __init__(self, xOffset: Coordinate, yOffset: Coordinate, zOffset: Coordinate) -> None:
		"""
		Initializes a 3-dimensional vector.

		:param xOffset:     x-direction component.
		:param yOffset:     y-direction component.
		:param zOffset:     z-direction component.
		:raises ValueError: If parameter 'xOffset' is None.
		:raises TypeError:  If parameter 'xOffset' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'yOffset' is None.
		:raises TypeError:  If parameter 'yOffset' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'zOffset' is None.
		:raises TypeError:  If parameter 'zOffset' is not of type :class:`float` or :class:`int`.
		"""
		super().__init__(xOffset, yOffset, zOffset)

		self._length = None

	@readonly
	def Length(self) -> float:
		"""
		Read-only property to return the Euclidean length of this 3D-vector.

		:returns: The Euclidean length.
		"""
		if (length := self._length) is None:
			self._length = length = sqrt(self._xOffset ** 2 + self._yOffset ** 2 + self._zOffset ** 2)

		return length

	def __hash__(self) -> int:
		"""
		Returns the hash of the 3D-vector's components.

		A vector equal to a tuple has the tuple's hash.

		:returns: The hash value.
		"""
		return hash((self._xOffset, self._yOffset, self._zOffset))


@export
class Offset3D(BaseVector3D[Coordinate], Generic[Coordinate]):
	"""
	An implementation of a mutable 3D cartesian offset.

	An offset is a displacement, like a group's offset: its components can be assigned, and it changes in place with
	``+=``, ``-=`` and ``*=``. It isn't hashable.
	"""

	@property
	def XOffset(self) -> Coordinate:
		"""
		Property to access the x-direction offset (:attr:`_xOffset`).

		``xOffset`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The x-direction offset.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._xOffset

	@XOffset.setter
	def XOffset(self, xOffset: Coordinate) -> None:
		if xOffset is None:
			raise ValueError("Parameter 'xOffset' is None.")
		elif not isinstance(xOffset, (int, float)):
			ex = TypeError("Parameter 'xOffset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(xOffset)}'.")
			raise ex

		self._xOffset = xOffset

	xOffset = XOffset

	@property
	def YOffset(self) -> Coordinate:
		"""
		Property to access the y-direction offset (:attr:`_yOffset`).

		``yOffset`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The y-direction offset.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._yOffset

	@YOffset.setter
	def YOffset(self, yOffset: Coordinate) -> None:
		if yOffset is None:
			raise ValueError("Parameter 'yOffset' is None.")
		elif not isinstance(yOffset, (int, float)):
			ex = TypeError("Parameter 'yOffset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(yOffset)}'.")
			raise ex

		self._yOffset = yOffset

	yOffset = YOffset

	@property
	def ZOffset(self) -> Coordinate:
		"""
		Property to access the z-direction offset (:attr:`_zOffset`).

		``zOffset`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The z-direction offset.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._zOffset

	@ZOffset.setter
	def ZOffset(self, zOffset: Coordinate) -> None:
		if zOffset is None:
			raise ValueError("Parameter 'zOffset' is None.")
		elif not isinstance(zOffset, (int, float)):
			ex = TypeError("Parameter 'zOffset' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(zOffset)}'.")
			raise ex

		self._zOffset = zOffset

	zOffset = ZOffset

	def Copy(self) -> Self:
		"""
		Create a new 3D-offset as a copy of this 3D-offset.

		:returns: Copy of this 3D-offset.

		.. seealso::

		   :meth:`+ operator <__add__>`
		     Create a new 3D-offset moved by a positive 3D-offset.
		   :meth:`- operator <__sub__>`
		     Create a new 3D-offset moved by a negative 3D-offset.
		"""
		return self.__class__(self._xOffset, self._yOffset, self._zOffset)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this 3D-offset for :func:`copy.copy`.

		:returns: Copy of this 3D-offset.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this 3D-offset for :func:`copy.deepcopy`.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this 3D-offset.
		"""
		return self.Copy()

	def __iadd__(self, other: Any) -> Self:
		"""
		Adds a 3D-vector to this 3D-offset (inplace).

		:param other:      A 3D-vector as :class:`Vector3D`, :class:`Offset3D` or tuple.
		:returns:          This 3D-offset.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector3D` or :class:`tuple`.
		"""
		if isinstance(other, BaseVector3D):
			self._xOffset += other._xOffset
			self._yOffset += other._yOffset
			self._zOffset += other._zOffset
		elif isinstance(other, tuple):
			self.XOffset += other[0]
			self.YOffset += other[1]
			self.ZOffset += other[2]
		else:
			ex = TypeError("Parameter 'other' is not of type 'BaseVector3D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __isub__(self, other: Any) -> Self:
		"""
		Subtracts a 3D-vector from this 3D-offset (inplace).

		:param other:      A 3D-vector as :class:`Vector3D`, :class:`Offset3D` or tuple.
		:returns:          This 3D-offset.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector3D` or :class:`tuple`.
		"""
		if isinstance(other, BaseVector3D):
			self._xOffset -= other._xOffset
			self._yOffset -= other._yOffset
			self._zOffset -= other._zOffset
		elif isinstance(other, tuple):
			self.XOffset -= other[0]
			self.YOffset -= other[1]
			self.ZOffset -= other[2]
		else:
			ex = TypeError("Parameter 'other' is not of type 'BaseVector3D' or 'tuple'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self

	def __imul__(self, other: Any) -> Self:
		"""
		Multiplies this 3D-offset by a number (inplace).

		:param other:      The factor.
		:returns:          This 3D-offset.
		:raises TypeError: If the second operand is not of type :class:`float` or :class:`int`.
		"""
		if not isinstance(other, (int, float)):
			ex = TypeError("Second operand is not supported by *= operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: float, int")
			raise ex

		self._xOffset *= other
		self._yOffset *= other
		self._zOffset *= other

		return self


@export
class Size3D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""An implementation of a 3D cartesian size."""

	_width:  Coordinate  #: width in x-direction.
	_height: Coordinate  #: height in y-direction.
	_depth:  Coordinate  #: depth in z-direction.

	def __init__(self, width: Coordinate, height: Coordinate, depth: Coordinate) -> None:
		"""
		Initializes a 3-dimensional size.

		:param width:       width in x-direction.
		:param height:      height in y-direction.
		:param depth:       depth in z-direction.
		:raises ValueError: If parameter 'width' is None.
		:raises TypeError:  If parameter 'width' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'height' is None.
		:raises TypeError:  If parameter 'height' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'depth' is None.
		:raises TypeError:  If parameter 'depth' is not of type :class:`float` or :class:`int`.
		"""
		if width is None:
			raise ValueError("Parameter 'width' is None.")
		elif not isinstance(width, (int, float)):
			ex = TypeError("Parameter 'width' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(width)}'.")
			raise ex

		if height is None:
			raise ValueError("Parameter 'height' is None.")
		elif not isinstance(height, (int, float)):
			ex = TypeError("Parameter 'height' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(height)}'.")
			raise ex

		if depth is None:
			raise ValueError("Parameter 'depth' is None.")
		elif not isinstance(depth, (int, float)):
			ex = TypeError("Parameter 'depth' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(depth)}'.")
			raise ex

		self._width =  width
		self._height = height
		self._depth =  depth

	@property
	def Width(self) -> Coordinate:
		"""
		Property to access the width in x-direction (:attr:`_width`).

		``width`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The width in x-direction.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._width

	@Width.setter
	def Width(self, width: Coordinate) -> None:
		if width is None:
			raise ValueError("Parameter 'width' is None.")
		elif not isinstance(width, (int, float)):
			ex = TypeError("Parameter 'width' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(width)}'.")
			raise ex

		self._width = width

	width = Width

	@property
	def Height(self) -> Coordinate:
		"""
		Property to access the height in y-direction (:attr:`_height`).

		``height`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The height in y-direction.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._height

	@Height.setter
	def Height(self, height: Coordinate) -> None:
		if height is None:
			raise ValueError("Parameter 'height' is None.")
		elif not isinstance(height, (int, float)):
			ex = TypeError("Parameter 'height' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(height)}'.")
			raise ex

		self._height = height

	height = Height

	@property
	def Depth(self) -> Coordinate:
		"""
		Property to access the depth in z-direction (:attr:`_depth`).

		``depth`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:           The depth in z-direction.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`float` or :class:`int`.
		"""
		return self._depth

	@Depth.setter
	def Depth(self, depth: Coordinate) -> None:
		if depth is None:
			raise ValueError("Parameter 'depth' is None.")
		elif not isinstance(depth, (int, float)):
			ex = TypeError("Parameter 'depth' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(depth)}'.")
			raise ex

		self._depth = depth

	depth = Depth

	def Copy(self) -> Self:
		"""
		Create a new 3D-size as a copy of this 3D-size.

		:returns: Copy of this 3D-size.
		"""
		return self.__class__(self._width, self._height, self._depth)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this 3D-size for :func:`copy.copy`.

		:returns: Copy of this 3D-size.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this 3D-size for :func:`copy.deepcopy`.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this 3D-size.
		"""
		return self.Copy()

	def ToTuple(self) -> tuple[Coordinate, Coordinate, Coordinate]:
		"""
		Convert this 3D-size to a simple 3-element tuple.

		:returns: ``(width, height, depth)`` tuple.
		"""
		return self._width, self._height, self._depth

	def __repr__(self) -> str:
		"""
		Returns the 3D size's string representation.

		:returns: The string representation of the 3D size.
		"""
		return f"Size3D({self._width}, {self._height}, {self._depth})"

	def __str__(self) -> str:
		"""
		Returns the 3D size's string equivalent.

		:returns: The string equivalent of the 3D size.
		"""
		return f"({self._width}, {self._height}, {self._depth})"


@export
class BoundingBox3D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""
	An axis-aligned 3D bounding box.

	A bounding box is a computed value: segments return a new one from their ``BoundingBox`` property on every access.
	Its borders belong to the box.
	"""

	_minX: Coordinate  #: Smallest x-coordinate.
	_minY: Coordinate  #: Smallest y-coordinate.
	_minZ: Coordinate  #: Smallest z-coordinate.
	_maxX: Coordinate  #: Largest x-coordinate.
	_maxY: Coordinate  #: Largest y-coordinate.
	_maxZ: Coordinate  #: Largest z-coordinate.

	def __init__(
		self,
		minX: Coordinate,
		minY: Coordinate,
		minZ: Coordinate,
		maxX: Coordinate,
		maxY: Coordinate,
		maxZ: Coordinate
	) -> None:
		"""
		Initializes a 3-dimensional bounding box from its smallest and largest coordinates.

		:param minX:        Smallest x-coordinate.
		:param minY:        Smallest y-coordinate.
		:param minZ:        Smallest z-coordinate.
		:param maxX:        Largest x-coordinate.
		:param maxY:        Largest y-coordinate.
		:param maxZ:        Largest z-coordinate.
		:raises ValueError: If parameter 'minX' is None.
		:raises TypeError:  If parameter 'minX' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'minY' is None.
		:raises TypeError:  If parameter 'minY' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'minZ' is None.
		:raises TypeError:  If parameter 'minZ' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'maxX' is None.
		:raises TypeError:  If parameter 'maxX' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'maxX' is less than parameter 'minX'.
		:raises ValueError: If parameter 'maxY' is None.
		:raises TypeError:  If parameter 'maxY' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'maxY' is less than parameter 'minY'.
		:raises ValueError: If parameter 'maxZ' is None.
		:raises TypeError:  If parameter 'maxZ' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'maxZ' is less than parameter 'minZ'.
		"""
		for name, value in (
			("minX", minX),
			("minY", minY),
			("minZ", minZ),
			("maxX", maxX),
			("maxY", maxY),
			("maxZ", maxZ)
		):
			if value is None:
				raise ValueError(f"Parameter '{name}' is None.")
			elif not isinstance(value, (int, float)):
				ex = TypeError(f"Parameter '{name}' is not of type 'float' or 'int'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
				raise ex

		if maxX < minX:
			ex = ValueError("Parameter 'maxX' is less than parameter 'minX'.")
			ex.add_note(f"Got minX={minX} and maxX={maxX}.")
			raise ex

		if maxY < minY:
			ex = ValueError("Parameter 'maxY' is less than parameter 'minY'.")
			ex.add_note(f"Got minY={minY} and maxY={maxY}.")
			raise ex

		if maxZ < minZ:
			ex = ValueError("Parameter 'maxZ' is less than parameter 'minZ'.")
			ex.add_note(f"Got minZ={minZ} and maxZ={maxZ}.")
			raise ex

		self._minX = minX
		self._minY = minY
		self._minZ = minZ
		self._maxX = maxX
		self._maxY = maxY
		self._maxZ = maxZ

	@classmethod
	def FromPoints(cls, points: Iterable[Point3D[Coordinate]]) -> Self:
		"""
		Create the smallest bounding box enclosing all given points.

		:param points:      Points to enclose.
		:returns:           Bounding box enclosing all points.
		:raises ValueError: If parameter 'points' is None.
		:raises TypeError:  If parameter 'points' is not iterable.
		:raises ValueError: If an element of parameter 'points' is None.
		:raises TypeError:  If an element of parameter 'points' is not of type :class:`Point3D`.
		:raises ValueError: If parameter 'points' is empty.
		"""
		if points is None:
			raise ValueError("Parameter 'points' is None.")
		elif not isinstance(points, Iterable):
			ex = TypeError("Parameter 'points' is not iterable.")
			ex.add_note(f"Got type '{getFullyQualifiedName(points)}'.")
			raise ex

		iterator = iter(points)
		try:
			point = next(iterator)
		except StopIteration as ex:
			raise ValueError("Parameter 'points' is empty.") from ex

		if point is None:
			raise ValueError("An element of parameter 'points' is None.")
		elif not isinstance(point, Point3D):
			ex = TypeError("An element of parameter 'points' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		minX = maxX = point._x
		minY = maxY = point._y
		minZ = maxZ = point._z

		for point in iterator:
			if point is None:
				raise ValueError("An element of parameter 'points' is None.")
			elif not isinstance(point, Point3D):
				ex = TypeError("An element of parameter 'points' is not of type 'Point3D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
				raise ex

			x = point._x
			y = point._y
			z = point._z
			if x < minX:
				minX = x
			elif x > maxX:
				maxX = x

			if y < minY:
				minY = y
			elif y > maxY:
				maxY = y

			if z < minZ:
				minZ = z
			elif z > maxZ:
				maxZ = z

		return cls(minX, minY, minZ, maxX, maxY, maxZ)

	@readonly
	def MinX(self) -> Coordinate:
		"""
		Read-only property to access the smallest x-coordinate (:attr:`_minX`).

		:returns: The smallest x-coordinate.
		"""
		return self._minX

	@readonly
	def MinY(self) -> Coordinate:
		"""
		Read-only property to access the smallest y-coordinate (:attr:`_minY`).

		:returns: The smallest y-coordinate.
		"""
		return self._minY

	@readonly
	def MinZ(self) -> Coordinate:
		"""
		Read-only property to access the smallest z-coordinate (:attr:`_minZ`).

		:returns: The smallest z-coordinate.
		"""
		return self._minZ

	@readonly
	def MaxX(self) -> Coordinate:
		"""
		Read-only property to access the largest x-coordinate (:attr:`_maxX`).

		:returns: The largest x-coordinate.
		"""
		return self._maxX

	@readonly
	def MaxY(self) -> Coordinate:
		"""
		Read-only property to access the largest y-coordinate (:attr:`_maxY`).

		:returns: The largest y-coordinate.
		"""
		return self._maxY

	@readonly
	def MaxZ(self) -> Coordinate:
		"""
		Read-only property to access the largest z-coordinate (:attr:`_maxZ`).

		:returns: The largest z-coordinate.
		"""
		return self._maxZ

	@readonly
	def Width(self) -> Coordinate:
		"""
		Read-only property to return the bounding box' extent in x-direction.

		:returns: The width in x-direction.
		"""
		return self._maxX - self._minX

	@readonly
	def Height(self) -> Coordinate:
		"""
		Read-only property to return the bounding box' extent in y-direction.

		:returns: The height in y-direction.
		"""
		return self._maxY - self._minY

	@readonly
	def Depth(self) -> Coordinate:
		"""
		Read-only property to return the bounding box' extent in z-direction.

		:returns: The depth in z-direction.
		"""
		return self._maxZ - self._minZ

	@readonly
	def Center(self) -> Point3D[float]:
		"""
		Read-only property to return the bounding box' center as a new 3D-point.

		:returns: The center point.
		"""
		return Point3D((self._minX + self._maxX) / 2, (self._minY + self._maxY) / 2, (self._minZ + self._maxZ) / 2)

	def Union(self, other: BoundingBox3D[Coordinate]) -> BoundingBox3D[Coordinate]:
		"""
		Create the smallest bounding box enclosing this and another bounding box.

		:param other:       The second bounding box.
		:returns:           A new bounding box enclosing both bounding boxes.
		:raises ValueError: If parameter 'other' is None.
		:raises TypeError:  If parameter 'other' is not of type :class:`BoundingBox3D`.
		"""
		if other is None:
			raise ValueError("Parameter 'other' is None.")
		elif not isinstance(other, BoundingBox3D):
			ex = TypeError("Parameter 'other' is not of type 'BoundingBox3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self.__class__(
			min(self._minX, other._minX),
			min(self._minY, other._minY),
			min(self._minZ, other._minZ),
			max(self._maxX, other._maxX),
			max(self._maxY, other._maxY),
			max(self._maxZ, other._maxZ)
		)

	def HasOverlap(self, other: BoundingBox3D[Coordinate]) -> bool:
		"""
		Check if this bounding box and another bounding box overlap.

		Two bounding boxes touching only at a face, an edge or a corner don't overlap, so elements can be aligned next to
		each other without a distance.

		:param other:       The second bounding box.
		:returns:           ``True``, if the inner volumes of both bounding boxes overlap.
		:raises ValueError: If parameter 'other' is None.
		:raises TypeError:  If parameter 'other' is not of type :class:`BoundingBox3D`.
		"""
		if other is None:
			raise ValueError("Parameter 'other' is None.")
		elif not isinstance(other, BoundingBox3D):
			ex = TypeError("Parameter 'other' is not of type 'BoundingBox3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return (
			self._minX < other._maxX and other._minX < self._maxX and
			self._minY < other._maxY and other._minY < self._maxY and
			self._minZ < other._maxZ and other._minZ < self._maxZ
		)

	def ContainsPoint(self, point: Point3D[Coordinate]) -> bool:
		"""
		Check if a point lies within this bounding box.

		A point on a border is contained.

		:param point:       The point to check.
		:returns:           ``True``, if the point lies within the bounding box or on its border.
		:raises ValueError: If parameter 'point' is None.
		:raises TypeError:  If parameter 'point' is not of type :class:`Point3D`.
		"""
		if point is None:
			raise ValueError("Parameter 'point' is None.")
		elif not isinstance(point, Point3D):
			ex = TypeError("Parameter 'point' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		return self._ContainsPoint(point)

	def _ContainsPoint(self, point: Point3D[Coordinate]) -> bool:
		"""
		Check if a point lies within this bounding box, without checking the parameter.

		:param point: The point to check.
		:returns:     ``True``, if the point lies within the bounding box or on its border.
		"""
		return (
			self._minX <= point._x <= self._maxX and
			self._minY <= point._y <= self._maxY and
			self._minZ <= point._z <= self._maxZ
		)

	def __contains__(self, other: Any) -> bool:
		"""
		Check if an element lies within this bounding box (``other in box``).

		:param other:      The element to check. Supported: :class:`Point3D`.
		:returns:          ``True``, if the element lies within the bounding box or on its border.
		:raises TypeError: If the first operand is not of type :class:`Point3D`.
		"""
		if isinstance(other, Point3D):
			return self._ContainsPoint(other)

		ex = TypeError("First operand is not supported by in operator.")
		ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
		ex.add_note("Supported types for first operand: Point3D")
		raise ex

	def __add__(self, other: Any) -> BoundingBox3D[Coordinate]:
		"""
		Adds a 3D-vector to this bounding box and creates a new, shifted bounding box.

		:param other:      A 3D-vector as :class:`Vector3D` or :class:`Offset3D`.
		:returns:          A new bounding box shifted by the 3D-vector.
		:raises TypeError: If parameter 'other' is not of type :class:`BaseVector3D`.
		"""
		if not isinstance(other, BaseVector3D):
			ex = TypeError("Parameter 'other' is not of type 'BaseVector3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self.__class__(
			self._minX + other._xOffset,
			self._minY + other._yOffset,
			self._minZ + other._zOffset,
			self._maxX + other._xOffset,
			self._maxY + other._yOffset,
			self._maxZ + other._zOffset
		)

	def Copy(self) -> Self:
		"""
		Create a new bounding box as a copy of this bounding box.

		:returns: Copy of this bounding box.
		"""
		return self.__class__(self._minX, self._minY, self._minZ, self._maxX, self._maxY, self._maxZ)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this bounding box for :func:`copy.copy`.

		:returns: Copy of this bounding box.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this bounding box for :func:`copy.deepcopy`.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this bounding box.
		"""
		return self.Copy()

	def ToTuple(self) -> tuple[Coordinate, Coordinate, Coordinate, Coordinate, Coordinate, Coordinate]:
		"""
		Convert this bounding box to a simple 6-element tuple.

		:returns: ``(minX, minY, minZ, maxX, maxY, maxZ)`` tuple.
		"""
		return self._minX, self._minY, self._minZ, self._maxX, self._maxY, self._maxZ

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two bounding boxes for equality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if both bounding boxes have the same coordinates.
		:raises TypeError: If the second operand is not of type :class:`BoundingBox3D`.
		"""
		if not isinstance(other, BoundingBox3D):
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: BoundingBox3D")
			raise ex

		return (
			self._minX == other._minX and self._minY == other._minY and self._minZ == other._minZ and
			self._maxX == other._maxX and self._maxY == other._maxY and self._maxZ == other._maxZ
		)

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two bounding boxes for inequality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if the bounding boxes differ in at least one coordinate.
		:raises TypeError: If the second operand is not of type :class:`BoundingBox3D`.
		"""
		if not isinstance(other, BoundingBox3D):
			ex = TypeError("Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: BoundingBox3D")
			raise ex

		return (
			self._minX != other._minX or self._minY != other._minY or self._minZ != other._minZ or
			self._maxX != other._maxX or self._maxY != other._maxY or self._maxZ != other._maxZ
		)

	def __repr__(self) -> str:
		"""
		Returns the bounding box' string representation.

		:returns: The string representation of the bounding box.
		"""
		return f"BoundingBox3D({self._minX}, {self._minY}, {self._minZ}, {self._maxX}, {self._maxY}, {self._maxZ})"

	def __str__(self) -> str:
		"""
		Returns the bounding box' string equivalent.

		:returns: The string equivalent of the bounding box, its corners with the smallest and the largest coordinates.
		"""
		return f"(({self._minX}, {self._minY}, {self._minZ}), ({self._maxX}, {self._maxY}, {self._maxZ}))"


@export
class Plane3D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""
	A 3D plane, which is infinite in all directions within the plane.

	The plane is stored in Hesse normal form: a normal ``(nx, ny, nz)`` of length 1 and the signed distance ``d`` of the
	plane from the origin, so the plane is all points ``(x, y, z)`` with ``nx * x + ny * y + nz * z = d``. The first
	non-zero component of the normal is positive, so a plane has one form only.

	A plane is in absolute coordinates, relative to the origin, so elements of different groups can be mirrored at the
	same plane with :meth:`Element3D.MirrorAt`. A plane is a value: it compares by value and is hashable. Two planes are
	equal, if they have the same normal and distance, whatever class or constructor created them.
	"""

	_normal:   Vector3D[float]  #: The normal of length 1, its first non-zero component is positive.
	_distance: float            #: The signed distance of the plane from the origin, in direction of the normal.

	def __init__(self, normal: BaseVector3D[Coordinate], distance: Coordinate) -> None:
		"""
		Initializes a 3D plane from a normal and a distance, the plane ``nx * x + ny * y + nz * z = distance``.

		A normal of another length than 1 is normalized, and the distance is divided by the normal's length, so the plane
		stays the same. If the first non-zero component of the normal is negative, the normal and the distance are
		negated. A normal of length 1 keeps its values, so the plane with normal ``(1, 0, 0)`` keeps an integer distance.
		Zeros are stored without sign.

		:param normal:      A normal of the plane, perpendicular to it.
		:param distance:    The right-hand side of the plane's equation; for a normal of length 1, the signed distance of
		                    the plane from the origin.
		:raises ValueError: If parameter 'normal' is None.
		:raises TypeError:  If parameter 'normal' is not of type :class:`BaseVector3D`.
		:raises ValueError: If parameter 'normal' is a zero vector. |br|
		                    A plane needs a normal direction.
		:raises ValueError: If parameter 'distance' is None.
		:raises TypeError:  If parameter 'distance' is not of type :class:`float` or :class:`int`.
		"""
		if normal is None:
			raise ValueError("Parameter 'normal' is None.")
		elif not isinstance(normal, BaseVector3D):
			ex = TypeError("Parameter 'normal' is not of type 'BaseVector3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(normal)}'.")
			raise ex
		elif normal._xOffset == 0 and normal._yOffset == 0 and normal._zOffset == 0:
			ex = ValueError("Parameter 'normal' is a zero vector.")
			ex.add_note(f"Got vector {normal}.")
			ex.add_note("A plane needs a normal direction.")
			raise ex

		if distance is None:
			raise ValueError("Parameter 'distance' is None.")
		elif not isinstance(distance, (int, float)):
			ex = TypeError("Parameter 'distance' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(distance)}'.")
			raise ex

		normalX = normal._xOffset
		normalY = normal._yOffset
		normalZ = normal._zOffset
		if (squaredLength := normalX ** 2 + normalY ** 2 + normalZ ** 2) != 1:
			length =   sqrt(squaredLength)
			normalX =  normalX / length
			normalY =  normalY / length
			normalZ =  normalZ / length
			distance = distance / length

		if normalX < 0 or (normalX == 0 and (normalY < 0 or (normalY == 0 and normalZ < 0))):
			normalX =  -normalX
			normalY =  -normalY
			normalZ =  -normalZ
			distance = -distance

		self._normal =   Vector3D(normalX + 0, normalY + 0, normalZ + 0)
		self._distance = distance + 0

	@classmethod
	def FromPoints(
		cls,
		first:  Point3D[Coordinate],
		second: Point3D[Coordinate],
		third:  Point3D[Coordinate]
	) -> Plane3D[float]:
		"""
		Create the plane through three points, which aren't on one line.

		The points are taken in absolute coordinates: a point inside a group is converted. The normal is the cross product
		of the offsets from the first point to the second and to the third point.

		:param first:       A first point of the plane.
		:param second:      A second point of the plane.
		:param third:       A third point of the plane.
		:returns:           A new plane, a :class:`Plane3D`.
		:raises ValueError: If parameter 'first' is None.
		:raises TypeError:  If parameter 'first' is not of type :class:`Point3D`.
		:raises ValueError: If parameter 'second' is None.
		:raises TypeError:  If parameter 'second' is not of type :class:`Point3D`.
		:raises ValueError: If parameter 'third' is None.
		:raises TypeError:  If parameter 'third' is not of type :class:`Point3D`.
		:raises ValueError: If parameters 'first', 'second' and 'third' are on one line. |br|
		                    Three points on one line don't define a plane.
		"""
		for name, point in (
			("first",  first),
			("second", second),
			("third",  third)
		):
			if point is None:
				raise ValueError(f"Parameter '{name}' is None.")
			elif not isinstance(point, Point3D):
				ex = TypeError(f"Parameter '{name}' is not of type 'Point3D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
				raise ex

		start =  first.Absolute
		normal = (second.Absolute - start).VectorProduct(third.Absolute - start)
		if normal._xOffset == 0 and normal._yOffset == 0 and normal._zOffset == 0:
			ex = ValueError("Parameters 'first', 'second' and 'third' are on one line.")
			ex.add_note(f"Got points {first}, {second} and {third}.")
			ex.add_note("Three points on one line don't define a plane.")
			raise ex

		return Plane3D(normal, normal._xOffset * start._x + normal._yOffset * start._y + normal._zOffset * start._z)

	@classmethod
	def FromPointAndSpanningVectors(
		cls,
		point:                Point3D[Coordinate],
		firstSpanningVector:  BaseVector3D[Coordinate],
		secondSpanningVector: BaseVector3D[Coordinate]
	) -> Plane3D[float]:
		"""
		Create the plane through a point, spanned by two vectors.

		The plane is all points ``point + s * firstSpanningVector + t * secondSpanningVector``. The point is taken in
		absolute coordinates: a point inside a group is converted. The normal is the cross product of the spanning vectors.

		:param point:                A point of the plane.
		:param firstSpanningVector:  A first spanning vector.
		:param secondSpanningVector: A second spanning vector.
		:returns:                    A new :class:`Plane3D`.
		:raises ValueError:          If parameter 'point' is None.
		:raises TypeError:           If parameter 'point' is not of type :class:`Point3D`.
		:raises ValueError:          If parameter 'firstSpanningVector' is None.
		:raises TypeError:           If parameter 'firstSpanningVector' is not of type :class:`BaseVector3D`.
		:raises ValueError:          If parameter 'secondSpanningVector' is None.
		:raises TypeError:           If parameter 'secondSpanningVector' is not of type :class:`BaseVector3D`.
		:raises ValueError:          If parameters 'firstSpanningVector' and 'secondSpanningVector' are parallel, or one of
		                             them is a zero vector. |br|
		                             Two parallel vectors don't span a plane.
		"""
		if point is None:
			raise ValueError("Parameter 'point' is None.")
		elif not isinstance(point, Point3D):
			ex = TypeError("Parameter 'point' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		for name, vector in (
			("firstSpanningVector",  firstSpanningVector),
			("secondSpanningVector", secondSpanningVector)
		):
			if vector is None:
				raise ValueError(f"Parameter '{name}' is None.")
			elif not isinstance(vector, BaseVector3D):
				ex = TypeError(f"Parameter '{name}' is not of type 'BaseVector3D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(vector)}'.")
				raise ex

		normal = firstSpanningVector.VectorProduct(secondSpanningVector)
		if normal._xOffset == 0 and normal._yOffset == 0 and normal._zOffset == 0:
			ex = ValueError("Parameters 'firstSpanningVector' and 'secondSpanningVector' are parallel.")
			ex.add_note(f"Got vectors {firstSpanningVector} and {secondSpanningVector}.")
			ex.add_note("Two parallel vectors don't span a plane.")
			raise ex

		absolute = point.Absolute
		return Plane3D(
			normal,
			normal._xOffset * absolute._x + normal._yOffset * absolute._y + normal._zOffset * absolute._z
		)

	@classmethod
	def FromPointAndNormal(cls, point: Point3D[Coordinate], normal: BaseVector3D[Coordinate]) -> Plane3D[float]:
		"""
		Create the plane through a point, perpendicular to a normal.

		The point is taken in absolute coordinates: a point inside a group is converted.

		:param point:       A point of the plane.
		:param normal:      A normal of the plane, perpendicular to it.
		:returns:           A new plane, a :class:`Plane3D`.
		:raises ValueError: If parameter 'point' is None.
		:raises TypeError:  If parameter 'point' is not of type :class:`Point3D`.
		:raises ValueError: If parameter 'normal' is None.
		:raises TypeError:  If parameter 'normal' is not of type :class:`BaseVector3D`.
		:raises ValueError: If parameter 'normal' is a zero vector. |br|
		                    A plane needs a normal direction.
		"""
		if point is None:
			raise ValueError("Parameter 'point' is None.")
		elif not isinstance(point, Point3D):
			ex = TypeError("Parameter 'point' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		if normal is None:
			raise ValueError("Parameter 'normal' is None.")
		elif not isinstance(normal, BaseVector3D):
			ex = TypeError("Parameter 'normal' is not of type 'BaseVector3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(normal)}'.")
			raise ex
		elif normal._xOffset == 0 and normal._yOffset == 0 and normal._zOffset == 0:
			ex = ValueError("Parameter 'normal' is a zero vector.")
			ex.add_note(f"Got vector {normal}.")
			ex.add_note("A plane needs a normal direction.")
			raise ex

		absolute = point.Absolute
		return Plane3D(
			normal,
			normal._xOffset * absolute._x + normal._yOffset * absolute._y + normal._zOffset * absolute._z
		)

	@readonly
	def Normal(self) -> Vector3D[float]:
		"""
		Read-only property to access the normal of the plane (:attr:`_normal`).

		:returns: The normal of length 1, its first non-zero component is positive.
		"""
		return self._normal

	@readonly
	def Distance(self) -> float:
		"""
		Read-only property to access the signed distance of the plane from the origin (:attr:`_distance`).

		:returns: The signed distance, positive in direction of the normal.
		"""
		return self._distance

	def SignedDistance(self, point: Point3D[Coordinate]) -> float:
		"""
		Compute the signed distance of a point from the plane.

		The point is taken in absolute coordinates. The distance is positive on the side the normal points to, negative on
		the other side, and zero for a point on the plane.

		:param point:       The point.
		:returns:           The signed distance ``nx * x + ny * y + nz * z - d``.
		:raises ValueError: If parameter 'point' is None.
		:raises TypeError:  If parameter 'point' is not of type :class:`Point3D`.
		"""
		if point is None:
			raise ValueError("Parameter 'point' is None.")
		elif not isinstance(point, Point3D):
			ex = TypeError("Parameter 'point' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		absolute = point.Absolute
		normal =   self._normal
		return (
			normal._xOffset * absolute._x + normal._yOffset * absolute._y + normal._zOffset * absolute._z - self._distance
		)

	def Project(self, point: Point3D[Coordinate]) -> Point3D[float]:
		"""
		Project a point onto the plane, the foot of the perpendicular from the point to the plane.

		The point is taken in absolute coordinates, and the projection is in absolute coordinates too.

		:param point:       The point to project.
		:returns:           A new 3D-point without owner.
		:raises ValueError: If parameter 'point' is None.
		:raises TypeError:  If parameter 'point' is not of type :class:`Point3D`.
		"""
		if point is None:
			raise ValueError("Parameter 'point' is None.")
		elif not isinstance(point, Point3D):
			ex = TypeError("Parameter 'point' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		absolute = point.Absolute
		normal =   self._normal
		signedDistance = (
			normal._xOffset * absolute._x + normal._yOffset * absolute._y + normal._zOffset * absolute._z - self._distance
		)
		return Point3D(
			absolute._x - signedDistance * normal._xOffset,
			absolute._y - signedDistance * normal._yOffset,
			absolute._z - signedDistance * normal._zOffset
		)

	def Intersects(self, ray: Ray3D[Coordinate]) -> bool:
		"""
		Check if a ray hits the plane.

		A ray starting on the plane hits it, also a ray running within the plane. A ray parallel to the plane, or pointing
		away from it, doesn't.

		:param ray:         The ray.
		:returns:           ``True``, if the ray has a point on the plane.
		:raises ValueError: If parameter 'ray' is None.
		:raises TypeError:  If parameter 'ray' is not of type :class:`Ray3D`.
		"""
		if ray is None:
			raise ValueError("Parameter 'ray' is None.")
		elif not isinstance(ray, Ray3D):
			ex = TypeError("Parameter 'ray' is not of type 'Ray3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(ray)}'.")
			raise ex

		normal =    self._normal
		start =     ray._start
		direction = ray._direction
		startDistance = (
			normal._xOffset * start._x + normal._yOffset * start._y + normal._zOffset * start._z - self._distance
		)
		approach = normal.ScalarProduct(direction)
		return startDistance == 0 or startDistance * approach < 0

	def Intersection(self, ray: Ray3D[Coordinate]) -> Point3D[float]:
		"""
		Compute the point, where a ray hits the plane.

		A ray starting on the plane, also one running within the plane, hits it at its start point.

		:param ray:         The ray.
		:returns:           A new 3D-point without owner, in absolute coordinates.
		:raises ValueError: If parameter 'ray' is None.
		:raises TypeError:  If parameter 'ray' is not of type :class:`Ray3D`.
		:raises ValueError: If parameter 'ray' is parallel to the plane, but doesn't start on it. |br|
		                    Check with :meth:`Intersects` first.
		:raises ValueError: If parameter 'ray' points away from the plane. |br|
		                    Check with :meth:`Intersects` first.
		"""
		if ray is None:
			raise ValueError("Parameter 'ray' is None.")
		elif not isinstance(ray, Ray3D):
			ex = TypeError("Parameter 'ray' is not of type 'Ray3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(ray)}'.")
			raise ex

		normal =    self._normal
		start =     ray._start
		direction = ray._direction
		startDistance = (
			normal._xOffset * start._x + normal._yOffset * start._y + normal._zOffset * start._z - self._distance
		)
		approach = normal.ScalarProduct(direction)
		if startDistance == 0:
			return Point3D(start._x, start._y, start._z)
		elif approach == 0:
			ex = ValueError("Parameter 'ray' is parallel to the plane.")
			ex.add_note(f"Got ray {ray!r} and plane {self!r}.")
			ex.add_note("Check with 'Intersects' first.")
			raise ex
		elif startDistance * approach > 0:
			ex = ValueError("Parameter 'ray' points away from the plane.")
			ex.add_note(f"Got ray {ray!r} and plane {self!r}.")
			ex.add_note("Check with 'Intersects' first.")
			raise ex

		factor = -startDistance / approach
		return Point3D(
			start._x + factor * direction._xOffset,
			start._y + factor * direction._yOffset,
			start._z + factor * direction._zOffset
		)

	def _MirrorElement(self, element: Element3D[Coordinate]) -> None:
		"""
		Mirror an element at this plane (inplace).

		A plane with normal ``(1, 0, 0)``, ``(0, 1, 0)`` or ``(0, 0, 1)`` mirrors an element like a :class:`YZPlane3D`,
		:class:`XZPlane3D` or :class:`XYPlane3D`, so integer coordinates stay integers.

		:param element: The element to mirror.
		"""
		normal = self._normal
		frame =  element.Frame
		if normal._yOffset == 0 and normal._zOffset == 0:
			x = self._distance if frame is None else self._distance - frame.AbsoluteOffset._xOffset
			element._MirrorX(2 * x)
		elif normal._xOffset == 0 and normal._zOffset == 0:
			y = self._distance if frame is None else self._distance - frame.AbsoluteOffset._yOffset
			element._MirrorY(2 * y)
		elif normal._xOffset == 0 and normal._yOffset == 0:
			z = self._distance if frame is None else self._distance - frame.AbsoluteOffset._zOffset
			element._MirrorZ(2 * z)
		else:
			distance = self._distance if frame is None else self._distance - normal.ScalarProduct(frame.AbsoluteOffset)
			element._MirrorAt(normal, distance)

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two planes for equality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if both planes have the same normal and distance.
		:raises TypeError: If the second operand is not of type :class:`Plane3D`.
		"""
		if not isinstance(other, Plane3D):
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Plane3D")
			raise ex

		normal =      self._normal
		otherNormal = other._normal
		return (
			normal._xOffset == otherNormal._xOffset
			and normal._yOffset == otherNormal._yOffset
			and normal._zOffset == otherNormal._zOffset
			and self._distance == other._distance
		)

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two planes for inequality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if the planes differ in normal or distance.
		:raises TypeError: If the second operand is not of type :class:`Plane3D`.
		"""
		if not isinstance(other, Plane3D):
			ex = TypeError("Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Plane3D")
			raise ex

		normal =      self._normal
		otherNormal = other._normal
		return (
			normal._xOffset != otherNormal._xOffset
			or normal._yOffset != otherNormal._yOffset
			or normal._zOffset != otherNormal._zOffset
			or self._distance != other._distance
		)

	def __hash__(self) -> int:
		"""
		Returns a hash of the plane's normal and distance, so equal planes have the same hash.

		:returns: The hash value.
		"""
		normal = self._normal
		return hash((normal._xOffset, normal._yOffset, normal._zOffset, self._distance))

	def __repr__(self) -> str:
		"""
		Returns the plane's string representation.

		:returns: The string representation of the plane, its normal and distance.
		"""
		return f"Plane3D({self._normal}, {self._distance})"

	def __str__(self) -> str:
		"""
		Returns the plane's string equivalent as an equation.

		The plane with normal ``(0.6, 0.0, 0.8)`` and distance ``2.0`` returns ``0.6 * x + 0.0 * y + 0.8 * z = 2.0``.

		:returns: The equation of the plane.
		"""
		normal = self._normal
		ySign =  "-" if normal._yOffset < 0 else "+"
		zSign =  "-" if normal._zOffset < 0 else "+"
		return (
			f"{normal._xOffset} * x {ySign} {abs(normal._yOffset)} * y {zSign} {abs(normal._zOffset)} * z = {self._distance}"
		)


@export
class YZPlane3D(Plane3D[Coordinate], Generic[Coordinate]):
	"""
	A 3D plane parallel to the yz-plane: all its points have the same x-coordinate, the plane ``x = c``.

	Its normal is ``(1, 0, 0)``, and its distance is the x-coordinate.
	"""

	def __init__(self, x: Coordinate) -> None:
		"""
		Initializes a 3D plane parallel to the yz-plane from the x-coordinate all its points have.

		:param x:           The x-coordinate of all points of the plane.
		:raises ValueError: If parameter 'x' is None.
		:raises TypeError:  If parameter 'x' is not of type :class:`float` or :class:`int`.
		"""
		super().__init__(Vector3D(1, 0, 0), 0)

		if x is None:
			raise ValueError("Parameter 'x' is None.")
		elif not isinstance(x, (int, float)):
			ex = TypeError("Parameter 'x' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(x)}'.")
			raise ex

		self._distance = x + 0

	@classmethod
	def FromPoints(
		cls,
		first:  Point3D[Coordinate],
		second: Point3D[Coordinate],
		third:  Point3D[Coordinate]
	) -> Self:
		"""
		Create the plane parallel to the yz-plane through three points with the same x-coordinate.

		The points are taken in absolute coordinates: a point inside a group is converted. The plane keeps the
		x-coordinate as given, so an integer stays an integer.

		:param first:       A first point of the plane.
		:param second:      A second point of the plane.
		:param third:       A third point of the plane.
		:returns:           A new plane parallel to the yz-plane.
		:raises ValueError: If parameter 'first' is None.
		:raises TypeError:  If parameter 'first' is not of type :class:`Point3D`.
		:raises ValueError: If parameter 'second' is None.
		:raises TypeError:  If parameter 'second' is not of type :class:`Point3D`.
		:raises ValueError: If parameter 'third' is None.
		:raises TypeError:  If parameter 'third' is not of type :class:`Point3D`.
		:raises ValueError: If parameters 'first', 'second' and 'third' are on one line. |br|
		                    Three points on one line don't define a plane.
		:raises ValueError: If parameters 'first', 'second' and 'third' have different x-coordinates. |br|
		                    Use :meth:`Plane3D.FromPoints` for a plane in any direction.
		"""
		for name, point in (
			("first",  first),
			("second", second),
			("third",  third)
		):
			if point is None:
				raise ValueError(f"Parameter '{name}' is None.")
			elif not isinstance(point, Point3D):
				ex = TypeError(f"Parameter '{name}' is not of type 'Point3D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
				raise ex

		start =  first.Absolute
		middle = second.Absolute
		end =    third.Absolute
		normal = (middle - start).VectorProduct(end - start)
		if normal._xOffset == 0 and normal._yOffset == 0 and normal._zOffset == 0:
			ex = ValueError("Parameters 'first', 'second' and 'third' are on one line.")
			ex.add_note(f"Got points {first}, {second} and {third}.")
			ex.add_note("Three points on one line don't define a plane.")
			raise ex
		elif start._x != middle._x or start._x != end._x:
			ex = ValueError("Parameters 'first', 'second' and 'third' have different x-coordinates.")
			ex.add_note(f"Got points {first}, {second} and {third}, at {start}, {middle} and {end} in absolute coordinates.")
			ex.add_note("Use 'Plane3D.FromPoints' for a plane in any direction.")
			raise ex

		return cls(start._x)

	@classmethod
	def FromPointAndSpanningVectors(
		cls,
		point:                Point3D[Coordinate],
		firstSpanningVector:  BaseVector3D[Coordinate],
		secondSpanningVector: BaseVector3D[Coordinate]
	) -> Self:
		"""
		Create the plane parallel to the yz-plane through a point, spanned by two vectors parallel to the yz-plane.

		The point is taken in absolute coordinates: a point inside a group is converted. The plane keeps the point's
		x-coordinate as given, so an integer stays an integer.

		:param point:                A point of the plane.
		:param firstSpanningVector:  A first spanning vector, like ``(0, y, z)``.
		:param secondSpanningVector: A second spanning vector, like ``(0, y, z)``.
		:returns:                    A new plane parallel to the yz-plane.
		:raises ValueError:          If parameter 'point' is None.
		:raises TypeError:           If parameter 'point' is not of type :class:`Point3D`.
		:raises ValueError:          If parameter 'firstSpanningVector' is None.
		:raises TypeError:           If parameter 'firstSpanningVector' is not of type :class:`BaseVector3D`.
		:raises ValueError:          If parameter 'secondSpanningVector' is None.
		:raises TypeError:           If parameter 'secondSpanningVector' is not of type :class:`BaseVector3D`.
		:raises ValueError:          If parameters 'firstSpanningVector' and 'secondSpanningVector' are parallel, or one of
		                             them is a zero vector. |br|
		                             Two parallel vectors don't span a plane.
		:raises ValueError:          If parameters 'firstSpanningVector' and 'secondSpanningVector' aren't parallel to the
		                             yz-plane. |br|
		                             Use :meth:`Plane3D.FromPointAndSpanningVectors` for a plane in any direction.
		"""
		if point is None:
			raise ValueError("Parameter 'point' is None.")
		elif not isinstance(point, Point3D):
			ex = TypeError("Parameter 'point' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		for name, vector in (
			("firstSpanningVector",  firstSpanningVector),
			("secondSpanningVector", secondSpanningVector)
		):
			if vector is None:
				raise ValueError(f"Parameter '{name}' is None.")
			elif not isinstance(vector, BaseVector3D):
				ex = TypeError(f"Parameter '{name}' is not of type 'BaseVector3D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(vector)}'.")
				raise ex

		normal = firstSpanningVector.VectorProduct(secondSpanningVector)
		if normal._xOffset == 0 and normal._yOffset == 0 and normal._zOffset == 0:
			ex = ValueError("Parameters 'firstSpanningVector' and 'secondSpanningVector' are parallel.")
			ex.add_note(f"Got vectors {firstSpanningVector} and {secondSpanningVector}.")
			ex.add_note("Two parallel vectors don't span a plane.")
			raise ex
		elif firstSpanningVector._xOffset != 0 or secondSpanningVector._xOffset != 0:
			ex = ValueError("Parameters 'firstSpanningVector' and 'secondSpanningVector' aren't parallel to the yz-plane.")
			ex.add_note(f"Got vectors {firstSpanningVector} and {secondSpanningVector}.")
			ex.add_note("Use 'Plane3D.FromPointAndSpanningVectors' for a plane in any direction.")
			raise ex

		return cls(point.Absolute._x)

	@classmethod
	def FromPointAndNormal(cls, point: Point3D[Coordinate], normal: BaseVector3D[Coordinate]) -> Self:
		"""
		Create the plane parallel to the yz-plane through a point, perpendicular to a normal parallel to the x-axis.

		The point is taken in absolute coordinates: a point inside a group is converted. The plane keeps the point's
		x-coordinate as given, so an integer stays an integer.

		:param point:       A point of the plane.
		:param normal:      A normal of the plane, like ``(1, 0, 0)``.
		:returns:           A new plane parallel to the yz-plane.
		:raises ValueError: If parameter 'point' is None.
		:raises TypeError:  If parameter 'point' is not of type :class:`Point3D`.
		:raises ValueError: If parameter 'normal' is None.
		:raises TypeError:  If parameter 'normal' is not of type :class:`BaseVector3D`.
		:raises ValueError: If parameter 'normal' is a zero vector. |br|
		                    A plane needs a normal direction.
		:raises ValueError: If parameter 'normal' isn't parallel to the x-axis. |br|
		                    Use :meth:`Plane3D.FromPointAndNormal` for a plane in any direction.
		"""
		if point is None:
			raise ValueError("Parameter 'point' is None.")
		elif not isinstance(point, Point3D):
			ex = TypeError("Parameter 'point' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		if normal is None:
			raise ValueError("Parameter 'normal' is None.")
		elif not isinstance(normal, BaseVector3D):
			ex = TypeError("Parameter 'normal' is not of type 'BaseVector3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(normal)}'.")
			raise ex
		elif normal._xOffset == 0 and normal._yOffset == 0 and normal._zOffset == 0:
			ex = ValueError("Parameter 'normal' is a zero vector.")
			ex.add_note(f"Got vector {normal}.")
			ex.add_note("A plane needs a normal direction.")
			raise ex
		elif normal._yOffset != 0 or normal._zOffset != 0:
			ex = ValueError("Parameter 'normal' isn't parallel to the x-axis.")
			ex.add_note(f"Got vector {normal}.")
			ex.add_note("Use 'Plane3D.FromPointAndNormal' for a plane in any direction.")
			raise ex

		return cls(point.Absolute._x)

	@classmethod
	def FromElement(cls, element: Element3D[Coordinate], alignment: Alignment3D) -> Self:
		"""
		Create the plane parallel to the yz-plane through a face or the center of an element's absolute bounding box.

		The x-coordinate of a center is a :class:`float`, as in :attr:`BoundingBox3D.Center`.

		:param element:     The element, whose :attr:`~Element3D.AbsoluteBoundingBox` the plane runs through.
		:param alignment:   The face or center of the bounding box: ``MinX``, ``CenterX`` or ``MaxX``.
		:returns:           A new plane parallel to the yz-plane.
		:raises ValueError: If parameter 'element' is None.
		:raises TypeError:  If parameter 'element' is not of type :class:`Element3D`.
		:raises ValueError: If parameter 'alignment' is None.
		:raises TypeError:  If parameter 'alignment' is not of type :class:`Alignment3D`.
		:raises ValueError: If parameter 'alignment' is not ``Alignment3D.MinX``, ``Alignment3D.CenterX`` or
		                    ``Alignment3D.MaxX``. |br|
		                    Use :meth:`XZPlane3D.FromElement` or :meth:`XYPlane3D.FromElement` for the other alignments.
		"""
		if element is None:
			raise ValueError("Parameter 'element' is None.")
		elif not isinstance(element, Element3D):
			ex = TypeError("Parameter 'element' is not of type 'Element3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
			raise ex

		if alignment is None:
			raise ValueError("Parameter 'alignment' is None.")
		elif not isinstance(alignment, Alignment3D):
			ex = TypeError("Parameter 'alignment' is not of type 'Alignment3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(alignment)}'.")
			raise ex
		elif alignment not in (Alignment3D.MinX, Alignment3D.CenterX, Alignment3D.MaxX):
			ex = ValueError("Parameter 'alignment' is not Alignment3D.MinX, Alignment3D.CenterX or Alignment3D.MaxX.")
			ex.add_note(f"Got value '{alignment}'.")
			ex.add_note("Use 'XZPlane3D.FromElement' or 'XYPlane3D.FromElement' for the other alignments.")
			raise ex

		box = element.AbsoluteBoundingBox
		if alignment is Alignment3D.MinX:
			return cls(box._minX)
		elif alignment is Alignment3D.CenterX:
			return cls((box._minX + box._maxX) / 2)
		else:
			return cls(box._maxX)

	@readonly
	def X(self) -> Coordinate:
		"""
		Read-only property to access the x-coordinate of all points of the plane (:attr:`_distance`).

		:returns: The x-coordinate of the plane.
		"""
		return self._distance

	def __repr__(self) -> str:
		"""
		Returns the plane's string representation.

		:returns: The string representation of the plane.
		"""
		return f"YZPlane3D({self._distance})"

	def __str__(self) -> str:
		"""
		Returns the plane's string equivalent as an equation.

		The plane at 5 returns ``x = 5``.

		:returns: The equation of the plane.
		"""
		return f"x = {self._distance}"


@export
class XZPlane3D(Plane3D[Coordinate], Generic[Coordinate]):
	"""
	A 3D plane parallel to the xz-plane: all its points have the same y-coordinate, the plane ``y = c``.

	Its normal is ``(0, 1, 0)``, and its distance is the y-coordinate.
	"""

	def __init__(self, y: Coordinate) -> None:
		"""
		Initializes a 3D plane parallel to the xz-plane from the y-coordinate all its points have.

		:param y:           The y-coordinate of all points of the plane.
		:raises ValueError: If parameter 'y' is None.
		:raises TypeError:  If parameter 'y' is not of type :class:`float` or :class:`int`.
		"""
		super().__init__(Vector3D(0, 1, 0), 0)

		if y is None:
			raise ValueError("Parameter 'y' is None.")
		elif not isinstance(y, (int, float)):
			ex = TypeError("Parameter 'y' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(y)}'.")
			raise ex

		self._distance = y + 0

	@classmethod
	def FromPoints(
		cls,
		first:  Point3D[Coordinate],
		second: Point3D[Coordinate],
		third:  Point3D[Coordinate]
	) -> Self:
		"""
		Create the plane parallel to the xz-plane through three points with the same y-coordinate.

		The points are taken in absolute coordinates: a point inside a group is converted. The plane keeps the
		y-coordinate as given, so an integer stays an integer.

		:param first:       A first point of the plane.
		:param second:      A second point of the plane.
		:param third:       A third point of the plane.
		:returns:           A new plane parallel to the xz-plane.
		:raises ValueError: If parameter 'first' is None.
		:raises TypeError:  If parameter 'first' is not of type :class:`Point3D`.
		:raises ValueError: If parameter 'second' is None.
		:raises TypeError:  If parameter 'second' is not of type :class:`Point3D`.
		:raises ValueError: If parameter 'third' is None.
		:raises TypeError:  If parameter 'third' is not of type :class:`Point3D`.
		:raises ValueError: If parameters 'first', 'second' and 'third' are on one line. |br|
		                    Three points on one line don't define a plane.
		:raises ValueError: If parameters 'first', 'second' and 'third' have different y-coordinates. |br|
		                    Use :meth:`Plane3D.FromPoints` for a plane in any direction.
		"""
		for name, point in (
			("first",  first),
			("second", second),
			("third",  third)
		):
			if point is None:
				raise ValueError(f"Parameter '{name}' is None.")
			elif not isinstance(point, Point3D):
				ex = TypeError(f"Parameter '{name}' is not of type 'Point3D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
				raise ex

		start =  first.Absolute
		middle = second.Absolute
		end =    third.Absolute
		normal = (middle - start).VectorProduct(end - start)
		if normal._xOffset == 0 and normal._yOffset == 0 and normal._zOffset == 0:
			ex = ValueError("Parameters 'first', 'second' and 'third' are on one line.")
			ex.add_note(f"Got points {first}, {second} and {third}.")
			ex.add_note("Three points on one line don't define a plane.")
			raise ex
		elif start._y != middle._y or start._y != end._y:
			ex = ValueError("Parameters 'first', 'second' and 'third' have different y-coordinates.")
			ex.add_note(f"Got points {first}, {second} and {third}, at {start}, {middle} and {end} in absolute coordinates.")
			ex.add_note("Use 'Plane3D.FromPoints' for a plane in any direction.")
			raise ex

		return cls(start._y)

	@classmethod
	def FromPointAndSpanningVectors(
		cls,
		point:                Point3D[Coordinate],
		firstSpanningVector:  BaseVector3D[Coordinate],
		secondSpanningVector: BaseVector3D[Coordinate]
	) -> Self:
		"""
		Create the plane parallel to the xz-plane through a point, spanned by two vectors parallel to the xz-plane.

		The point is taken in absolute coordinates: a point inside a group is converted. The plane keeps the point's
		y-coordinate as given, so an integer stays an integer.

		:param point:                A point of the plane.
		:param firstSpanningVector:  A first spanning vector, like ``(x, 0, z)``.
		:param secondSpanningVector: A second spanning vector, like ``(x, 0, z)``.
		:returns:                    A new plane parallel to the xz-plane.
		:raises ValueError:          If parameter 'point' is None.
		:raises TypeError:           If parameter 'point' is not of type :class:`Point3D`.
		:raises ValueError:          If parameter 'firstSpanningVector' is None.
		:raises TypeError:           If parameter 'firstSpanningVector' is not of type :class:`BaseVector3D`.
		:raises ValueError:          If parameter 'secondSpanningVector' is None.
		:raises TypeError:           If parameter 'secondSpanningVector' is not of type :class:`BaseVector3D`.
		:raises ValueError:          If parameters 'firstSpanningVector' and 'secondSpanningVector' are parallel, or one of
		                             them is a zero vector. |br|
		                             Two parallel vectors don't span a plane.
		:raises ValueError:          If parameters 'firstSpanningVector' and 'secondSpanningVector' aren't parallel to the
		                             xz-plane. |br|
		                             Use :meth:`Plane3D.FromPointAndSpanningVectors` for a plane in any direction.
		"""
		if point is None:
			raise ValueError("Parameter 'point' is None.")
		elif not isinstance(point, Point3D):
			ex = TypeError("Parameter 'point' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		for name, vector in (
			("firstSpanningVector",  firstSpanningVector),
			("secondSpanningVector", secondSpanningVector)
		):
			if vector is None:
				raise ValueError(f"Parameter '{name}' is None.")
			elif not isinstance(vector, BaseVector3D):
				ex = TypeError(f"Parameter '{name}' is not of type 'BaseVector3D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(vector)}'.")
				raise ex

		normal = firstSpanningVector.VectorProduct(secondSpanningVector)
		if normal._xOffset == 0 and normal._yOffset == 0 and normal._zOffset == 0:
			ex = ValueError("Parameters 'firstSpanningVector' and 'secondSpanningVector' are parallel.")
			ex.add_note(f"Got vectors {firstSpanningVector} and {secondSpanningVector}.")
			ex.add_note("Two parallel vectors don't span a plane.")
			raise ex
		elif firstSpanningVector._yOffset != 0 or secondSpanningVector._yOffset != 0:
			ex = ValueError("Parameters 'firstSpanningVector' and 'secondSpanningVector' aren't parallel to the xz-plane.")
			ex.add_note(f"Got vectors {firstSpanningVector} and {secondSpanningVector}.")
			ex.add_note("Use 'Plane3D.FromPointAndSpanningVectors' for a plane in any direction.")
			raise ex

		return cls(point.Absolute._y)

	@classmethod
	def FromPointAndNormal(cls, point: Point3D[Coordinate], normal: BaseVector3D[Coordinate]) -> Self:
		"""
		Create the plane parallel to the xz-plane through a point, perpendicular to a normal parallel to the y-axis.

		The point is taken in absolute coordinates: a point inside a group is converted. The plane keeps the point's
		y-coordinate as given, so an integer stays an integer.

		:param point:       A point of the plane.
		:param normal:      A normal of the plane, like ``(0, 1, 0)``.
		:returns:           A new plane parallel to the xz-plane.
		:raises ValueError: If parameter 'point' is None.
		:raises TypeError:  If parameter 'point' is not of type :class:`Point3D`.
		:raises ValueError: If parameter 'normal' is None.
		:raises TypeError:  If parameter 'normal' is not of type :class:`BaseVector3D`.
		:raises ValueError: If parameter 'normal' is a zero vector. |br|
		                    A plane needs a normal direction.
		:raises ValueError: If parameter 'normal' isn't parallel to the y-axis. |br|
		                    Use :meth:`Plane3D.FromPointAndNormal` for a plane in any direction.
		"""
		if point is None:
			raise ValueError("Parameter 'point' is None.")
		elif not isinstance(point, Point3D):
			ex = TypeError("Parameter 'point' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		if normal is None:
			raise ValueError("Parameter 'normal' is None.")
		elif not isinstance(normal, BaseVector3D):
			ex = TypeError("Parameter 'normal' is not of type 'BaseVector3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(normal)}'.")
			raise ex
		elif normal._xOffset == 0 and normal._yOffset == 0 and normal._zOffset == 0:
			ex = ValueError("Parameter 'normal' is a zero vector.")
			ex.add_note(f"Got vector {normal}.")
			ex.add_note("A plane needs a normal direction.")
			raise ex
		elif normal._xOffset != 0 or normal._zOffset != 0:
			ex = ValueError("Parameter 'normal' isn't parallel to the y-axis.")
			ex.add_note(f"Got vector {normal}.")
			ex.add_note("Use 'Plane3D.FromPointAndNormal' for a plane in any direction.")
			raise ex

		return cls(point.Absolute._y)

	@classmethod
	def FromElement(cls, element: Element3D[Coordinate], alignment: Alignment3D) -> Self:
		"""
		Create the plane parallel to the xz-plane through a face or the center of an element's absolute bounding box.

		The y-coordinate of a center is a :class:`float`, as in :attr:`BoundingBox3D.Center`.

		:param element:     The element, whose :attr:`~Element3D.AbsoluteBoundingBox` the plane runs through.
		:param alignment:   The face or center of the bounding box: ``MinY``, ``CenterY`` or ``MaxY``.
		:returns:           A new plane parallel to the xz-plane.
		:raises ValueError: If parameter 'element' is None.
		:raises TypeError:  If parameter 'element' is not of type :class:`Element3D`.
		:raises ValueError: If parameter 'alignment' is None.
		:raises TypeError:  If parameter 'alignment' is not of type :class:`Alignment3D`.
		:raises ValueError: If parameter 'alignment' is not ``Alignment3D.MinY``, ``Alignment3D.CenterY`` or
		                    ``Alignment3D.MaxY``. |br|
		                    Use :meth:`YZPlane3D.FromElement` or :meth:`XYPlane3D.FromElement` for the other alignments.
		"""
		if element is None:
			raise ValueError("Parameter 'element' is None.")
		elif not isinstance(element, Element3D):
			ex = TypeError("Parameter 'element' is not of type 'Element3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
			raise ex

		if alignment is None:
			raise ValueError("Parameter 'alignment' is None.")
		elif not isinstance(alignment, Alignment3D):
			ex = TypeError("Parameter 'alignment' is not of type 'Alignment3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(alignment)}'.")
			raise ex
		elif alignment not in (Alignment3D.MinY, Alignment3D.CenterY, Alignment3D.MaxY):
			ex = ValueError("Parameter 'alignment' is not Alignment3D.MinY, Alignment3D.CenterY or Alignment3D.MaxY.")
			ex.add_note(f"Got value '{alignment}'.")
			ex.add_note("Use 'YZPlane3D.FromElement' or 'XYPlane3D.FromElement' for the other alignments.")
			raise ex

		box = element.AbsoluteBoundingBox
		if alignment is Alignment3D.MinY:
			return cls(box._minY)
		elif alignment is Alignment3D.CenterY:
			return cls((box._minY + box._maxY) / 2)
		else:
			return cls(box._maxY)

	@readonly
	def Y(self) -> Coordinate:
		"""
		Read-only property to access the y-coordinate of all points of the plane (:attr:`_distance`).

		:returns: The y-coordinate of the plane.
		"""
		return self._distance

	def __repr__(self) -> str:
		"""
		Returns the plane's string representation.

		:returns: The string representation of the plane.
		"""
		return f"XZPlane3D({self._distance})"

	def __str__(self) -> str:
		"""
		Returns the plane's string equivalent as an equation.

		The plane at 5 returns ``y = 5``.

		:returns: The equation of the plane.
		"""
		return f"y = {self._distance}"


@export
class XYPlane3D(Plane3D[Coordinate], Generic[Coordinate]):
	"""
	A 3D plane parallel to the xy-plane: all its points have the same z-coordinate, the plane ``z = c``.

	Its normal is ``(0, 0, 1)``, and its distance is the z-coordinate.
	"""

	def __init__(self, z: Coordinate) -> None:
		"""
		Initializes a 3D plane parallel to the xy-plane from the z-coordinate all its points have.

		:param z:           The z-coordinate of all points of the plane.
		:raises ValueError: If parameter 'z' is None.
		:raises TypeError:  If parameter 'z' is not of type :class:`float` or :class:`int`.
		"""
		super().__init__(Vector3D(0, 0, 1), 0)

		if z is None:
			raise ValueError("Parameter 'z' is None.")
		elif not isinstance(z, (int, float)):
			ex = TypeError("Parameter 'z' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(z)}'.")
			raise ex

		self._distance = z + 0

	@classmethod
	def FromPoints(
		cls,
		first:  Point3D[Coordinate],
		second: Point3D[Coordinate],
		third:  Point3D[Coordinate]
	) -> Self:
		"""
		Create the plane parallel to the xy-plane through three points with the same z-coordinate.

		The points are taken in absolute coordinates: a point inside a group is converted. The plane keeps the
		z-coordinate as given, so an integer stays an integer.

		:param first:       A first point of the plane.
		:param second:      A second point of the plane.
		:param third:       A third point of the plane.
		:returns:           A new plane parallel to the xy-plane.
		:raises ValueError: If parameter 'first' is None.
		:raises TypeError:  If parameter 'first' is not of type :class:`Point3D`.
		:raises ValueError: If parameter 'second' is None.
		:raises TypeError:  If parameter 'second' is not of type :class:`Point3D`.
		:raises ValueError: If parameter 'third' is None.
		:raises TypeError:  If parameter 'third' is not of type :class:`Point3D`.
		:raises ValueError: If parameters 'first', 'second' and 'third' are on one line. |br|
		                    Three points on one line don't define a plane.
		:raises ValueError: If parameters 'first', 'second' and 'third' have different z-coordinates. |br|
		                    Use :meth:`Plane3D.FromPoints` for a plane in any direction.
		"""
		for name, point in (
			("first",  first),
			("second", second),
			("third",  third)
		):
			if point is None:
				raise ValueError(f"Parameter '{name}' is None.")
			elif not isinstance(point, Point3D):
				ex = TypeError(f"Parameter '{name}' is not of type 'Point3D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
				raise ex

		start =  first.Absolute
		middle = second.Absolute
		end =    third.Absolute
		normal = (middle - start).VectorProduct(end - start)
		if normal._xOffset == 0 and normal._yOffset == 0 and normal._zOffset == 0:
			ex = ValueError("Parameters 'first', 'second' and 'third' are on one line.")
			ex.add_note(f"Got points {first}, {second} and {third}.")
			ex.add_note("Three points on one line don't define a plane.")
			raise ex
		elif start._z != middle._z or start._z != end._z:
			ex = ValueError("Parameters 'first', 'second' and 'third' have different z-coordinates.")
			ex.add_note(f"Got points {first}, {second} and {third}, at {start}, {middle} and {end} in absolute coordinates.")
			ex.add_note("Use 'Plane3D.FromPoints' for a plane in any direction.")
			raise ex

		return cls(start._z)

	@classmethod
	def FromPointAndSpanningVectors(
		cls,
		point:                Point3D[Coordinate],
		firstSpanningVector:  BaseVector3D[Coordinate],
		secondSpanningVector: BaseVector3D[Coordinate]
	) -> Self:
		"""
		Create the plane parallel to the xy-plane through a point, spanned by two vectors parallel to the xy-plane.

		The point is taken in absolute coordinates: a point inside a group is converted. The plane keeps the point's
		z-coordinate as given, so an integer stays an integer.

		:param point:                A point of the plane.
		:param firstSpanningVector:  A first spanning vector, like ``(x, y, 0)``.
		:param secondSpanningVector: A second spanning vector, like ``(x, y, 0)``.
		:returns:                    A new plane parallel to the xy-plane.
		:raises ValueError:          If parameter 'point' is None.
		:raises TypeError:           If parameter 'point' is not of type :class:`Point3D`.
		:raises ValueError:          If parameter 'firstSpanningVector' is None.
		:raises TypeError:           If parameter 'firstSpanningVector' is not of type :class:`BaseVector3D`.
		:raises ValueError:          If parameter 'secondSpanningVector' is None.
		:raises TypeError:           If parameter 'secondSpanningVector' is not of type :class:`BaseVector3D`.
		:raises ValueError:          If parameters 'firstSpanningVector' and 'secondSpanningVector' are parallel, or one of
		                             them is a zero vector. |br|
		                             Two parallel vectors don't span a plane.
		:raises ValueError:          If parameters 'firstSpanningVector' and 'secondSpanningVector' aren't parallel to the
		                             xy-plane. |br|
		                             Use :meth:`Plane3D.FromPointAndSpanningVectors` for a plane in any direction.
		"""
		if point is None:
			raise ValueError("Parameter 'point' is None.")
		elif not isinstance(point, Point3D):
			ex = TypeError("Parameter 'point' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		for name, vector in (
			("firstSpanningVector",  firstSpanningVector),
			("secondSpanningVector", secondSpanningVector)
		):
			if vector is None:
				raise ValueError(f"Parameter '{name}' is None.")
			elif not isinstance(vector, BaseVector3D):
				ex = TypeError(f"Parameter '{name}' is not of type 'BaseVector3D'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(vector)}'.")
				raise ex

		normal = firstSpanningVector.VectorProduct(secondSpanningVector)
		if normal._xOffset == 0 and normal._yOffset == 0 and normal._zOffset == 0:
			ex = ValueError("Parameters 'firstSpanningVector' and 'secondSpanningVector' are parallel.")
			ex.add_note(f"Got vectors {firstSpanningVector} and {secondSpanningVector}.")
			ex.add_note("Two parallel vectors don't span a plane.")
			raise ex
		elif firstSpanningVector._zOffset != 0 or secondSpanningVector._zOffset != 0:
			ex = ValueError("Parameters 'firstSpanningVector' and 'secondSpanningVector' aren't parallel to the xy-plane.")
			ex.add_note(f"Got vectors {firstSpanningVector} and {secondSpanningVector}.")
			ex.add_note("Use 'Plane3D.FromPointAndSpanningVectors' for a plane in any direction.")
			raise ex

		return cls(point.Absolute._z)

	@classmethod
	def FromPointAndNormal(cls, point: Point3D[Coordinate], normal: BaseVector3D[Coordinate]) -> Self:
		"""
		Create the plane parallel to the xy-plane through a point, perpendicular to a normal parallel to the z-axis.

		The point is taken in absolute coordinates: a point inside a group is converted. The plane keeps the point's
		z-coordinate as given, so an integer stays an integer.

		:param point:       A point of the plane.
		:param normal:      A normal of the plane, like ``(0, 0, 1)``.
		:returns:           A new plane parallel to the xy-plane.
		:raises ValueError: If parameter 'point' is None.
		:raises TypeError:  If parameter 'point' is not of type :class:`Point3D`.
		:raises ValueError: If parameter 'normal' is None.
		:raises TypeError:  If parameter 'normal' is not of type :class:`BaseVector3D`.
		:raises ValueError: If parameter 'normal' is a zero vector. |br|
		                    A plane needs a normal direction.
		:raises ValueError: If parameter 'normal' isn't parallel to the z-axis. |br|
		                    Use :meth:`Plane3D.FromPointAndNormal` for a plane in any direction.
		"""
		if point is None:
			raise ValueError("Parameter 'point' is None.")
		elif not isinstance(point, Point3D):
			ex = TypeError("Parameter 'point' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(point)}'.")
			raise ex

		if normal is None:
			raise ValueError("Parameter 'normal' is None.")
		elif not isinstance(normal, BaseVector3D):
			ex = TypeError("Parameter 'normal' is not of type 'BaseVector3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(normal)}'.")
			raise ex
		elif normal._xOffset == 0 and normal._yOffset == 0 and normal._zOffset == 0:
			ex = ValueError("Parameter 'normal' is a zero vector.")
			ex.add_note(f"Got vector {normal}.")
			ex.add_note("A plane needs a normal direction.")
			raise ex
		elif normal._xOffset != 0 or normal._yOffset != 0:
			ex = ValueError("Parameter 'normal' isn't parallel to the z-axis.")
			ex.add_note(f"Got vector {normal}.")
			ex.add_note("Use 'Plane3D.FromPointAndNormal' for a plane in any direction.")
			raise ex

		return cls(point.Absolute._z)

	@classmethod
	def FromElement(cls, element: Element3D[Coordinate], alignment: Alignment3D) -> Self:
		"""
		Create the plane parallel to the xy-plane through a face or the center of an element's absolute bounding box.

		The z-coordinate of a center is a :class:`float`, as in :attr:`BoundingBox3D.Center`.

		:param element:     The element, whose :attr:`~Element3D.AbsoluteBoundingBox` the plane runs through.
		:param alignment:   The face or center of the bounding box: ``MinZ``, ``CenterZ`` or ``MaxZ``.
		:returns:           A new plane parallel to the xy-plane.
		:raises ValueError: If parameter 'element' is None.
		:raises TypeError:  If parameter 'element' is not of type :class:`Element3D`.
		:raises ValueError: If parameter 'alignment' is None.
		:raises TypeError:  If parameter 'alignment' is not of type :class:`Alignment3D`.
		:raises ValueError: If parameter 'alignment' is not ``Alignment3D.MinZ``, ``Alignment3D.CenterZ`` or
		                    ``Alignment3D.MaxZ``. |br|
		                    Use :meth:`YZPlane3D.FromElement` or :meth:`XZPlane3D.FromElement` for the other alignments.
		"""
		if element is None:
			raise ValueError("Parameter 'element' is None.")
		elif not isinstance(element, Element3D):
			ex = TypeError("Parameter 'element' is not of type 'Element3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
			raise ex

		if alignment is None:
			raise ValueError("Parameter 'alignment' is None.")
		elif not isinstance(alignment, Alignment3D):
			ex = TypeError("Parameter 'alignment' is not of type 'Alignment3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(alignment)}'.")
			raise ex
		elif alignment not in (Alignment3D.MinZ, Alignment3D.CenterZ, Alignment3D.MaxZ):
			ex = ValueError("Parameter 'alignment' is not Alignment3D.MinZ, Alignment3D.CenterZ or Alignment3D.MaxZ.")
			ex.add_note(f"Got value '{alignment}'.")
			ex.add_note("Use 'YZPlane3D.FromElement' or 'XZPlane3D.FromElement' for the other alignments.")
			raise ex

		box = element.AbsoluteBoundingBox
		if alignment is Alignment3D.MinZ:
			return cls(box._minZ)
		elif alignment is Alignment3D.CenterZ:
			return cls((box._minZ + box._maxZ) / 2)
		else:
			return cls(box._maxZ)

	@readonly
	def Z(self) -> Coordinate:
		"""
		Read-only property to access the z-coordinate of all points of the plane (:attr:`_distance`).

		:returns: The z-coordinate of the plane.
		"""
		return self._distance

	def __repr__(self) -> str:
		"""
		Returns the plane's string representation.

		:returns: The string representation of the plane.
		"""
		return f"XYPlane3D({self._distance})"

	def __str__(self) -> str:
		"""
		Returns the plane's string equivalent as an equation.

		The plane at 5 returns ``z = 5``.

		:returns: The equation of the plane.
		"""
		return f"z = {self._distance}"


@export
class Ray3D(Generic[Coordinate], metaclass=ExtendedType, slots=True):
	"""
	A 3D ray: a half-line, which starts at a point and is infinite in one direction.

	The ray is in absolute coordinates, relative to the origin. Its start point is a free copy, so it owns no point of an
	element. Two rays are equal, if they start at the same point and their directions point the same way, whatever their
	lengths. A ray is unhashable, as its start point can be changed.
	"""

	_start:     Point3D[Coordinate]   #: The start point of the ray, in absolute coordinates and without owner.
	_direction: Vector3D[Coordinate]  #: The direction of the ray.

	def __init__(self, start: Point3D[Coordinate], direction: BaseVector3D[Coordinate]) -> None:
		"""
		Initializes a 3D ray from its start point and its direction.

		The start point is taken in absolute coordinates (a point inside a group is converted), and the direction is
		copied into a new :class:`Vector3D`.

		:param start:       The start point of the ray.
		:param direction:   The direction of the ray, a 3D-vector or 3D-offset.
		:raises ValueError: If parameter 'start' is None.
		:raises TypeError:  If parameter 'start' is not of type :class:`Point3D`.
		:raises ValueError: If parameter 'direction' is None.
		:raises TypeError:  If parameter 'direction' is not of type :class:`BaseVector3D`.
		:raises ValueError: If parameter 'direction' is a zero vector. |br|
		                    A ray needs a direction.
		"""
		if start is None:
			raise ValueError("Parameter 'start' is None.")
		elif not isinstance(start, Point3D):
			ex = TypeError("Parameter 'start' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(start)}'.")
			raise ex

		if direction is None:
			raise ValueError("Parameter 'direction' is None.")
		elif not isinstance(direction, BaseVector3D):
			ex = TypeError("Parameter 'direction' is not of type 'BaseVector3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(direction)}'.")
			raise ex
		elif direction._xOffset == 0 and direction._yOffset == 0 and direction._zOffset == 0:
			ex = ValueError("Parameter 'direction' is a zero vector.")
			ex.add_note(f"Got vector {direction}.")
			ex.add_note("A ray needs a direction.")
			raise ex

		self._start =     start.Absolute
		self._direction = Vector3D(direction._xOffset, direction._yOffset, direction._zOffset)

	@readonly
	def Start(self) -> Point3D[Coordinate]:
		"""
		Read-only property to access the start point of the ray (:attr:`_start`).

		:returns: The start point, in absolute coordinates and without owner.
		"""
		return self._start

	@readonly
	def Direction(self) -> Vector3D[Coordinate]:
		"""
		Read-only property to access the direction of the ray (:attr:`_direction`).

		:returns: The direction.
		"""
		return self._direction

	def PointAt(self, distance: Coordinate) -> Point3D[float]:
		"""
		Compute the point of the ray at a distance from its start point.

		:param distance:    The distance from the start point along the direction.
		:returns:           A new 3D-point without owner.
		:raises ValueError: If parameter 'distance' is None.
		:raises TypeError:  If parameter 'distance' is not of type :class:`float` or :class:`int`.
		:raises ValueError: If parameter 'distance' is negative. |br|
		                    A point before the start point isn't on the ray.
		"""
		if distance is None:
			raise ValueError("Parameter 'distance' is None.")
		elif not isinstance(distance, (int, float)):
			ex = TypeError("Parameter 'distance' is not of type 'float' or 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(distance)}'.")
			raise ex
		elif distance < 0:
			ex = ValueError("Parameter 'distance' is negative.")
			ex.add_note(f"Got value '{distance}'.")
			ex.add_note("A point before the start point isn't on the ray.")
			raise ex

		start =     self._start
		direction = self._direction
		factor =    distance / sqrt(direction._xOffset ** 2 + direction._yOffset ** 2 + direction._zOffset ** 2)
		return Point3D(
			start._x + direction._xOffset * factor,
			start._y + direction._yOffset * factor,
			start._z + direction._zOffset * factor
		)

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two rays for equality.

		The directions point the same way, if all components of their cross product are zero and their dot product is
		positive. The lengths of the directions don't matter.

		:param other:      Operand to compare against.
		:returns:          ``True``, if both rays have the same start point and their directions point the same way.
		:raises TypeError: If the second operand is not of type :class:`Ray3D`.
		"""
		if not isinstance(other, Ray3D):
			ex = TypeError("Second operand is not supported by == operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Ray3D")
			raise ex

		start =          self._start
		otherStart =     other._start
		direction =      self._direction
		otherDirection = other._direction
		return (
			start._x == otherStart._x
			and start._y == otherStart._y
			and start._z == otherStart._z
			and direction._yOffset * otherDirection._zOffset - direction._zOffset * otherDirection._yOffset == 0
			and direction._zOffset * otherDirection._xOffset - direction._xOffset * otherDirection._zOffset == 0
			and direction._xOffset * otherDirection._yOffset - direction._yOffset * otherDirection._xOffset == 0
			and (
				direction._xOffset * otherDirection._xOffset
				+ direction._yOffset * otherDirection._yOffset
				+ direction._zOffset * otherDirection._zOffset
			) > 0
		)

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two rays for inequality.

		:param other:      Operand to compare against.
		:returns:          ``True``, if the rays differ in start point or their directions point different ways.
		:raises TypeError: If the second operand is not of type :class:`Ray3D`.
		"""
		if not isinstance(other, Ray3D):
			ex = TypeError("Second operand is not supported by != operator.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			ex.add_note("Supported types for second operand: Ray3D")
			raise ex

		start =          self._start
		otherStart =     other._start
		direction =      self._direction
		otherDirection = other._direction
		return (
			start._x != otherStart._x
			or start._y != otherStart._y
			or start._z != otherStart._z
			or direction._yOffset * otherDirection._zOffset - direction._zOffset * otherDirection._yOffset != 0
			or direction._zOffset * otherDirection._xOffset - direction._xOffset * otherDirection._zOffset != 0
			or direction._xOffset * otherDirection._yOffset - direction._yOffset * otherDirection._xOffset != 0
			or (
				direction._xOffset * otherDirection._xOffset
				+ direction._yOffset * otherDirection._yOffset
				+ direction._zOffset * otherDirection._zOffset
			) <= 0
		)

	def __repr__(self) -> str:
		"""
		Returns the ray's string representation.

		:returns: The string representation of the ray, its start point and direction.
		"""
		return f"Ray3D({self._start}, {self._direction})"

	def __str__(self) -> str:
		"""
		Returns the ray's string equivalent as a parametric equation.

		The ray from ``(1, 2)`` in direction ``(3, 4)`` returns ``(1, 2) + t * (3, 4), t >= 0``.

		:returns: The equation of the ray.
		"""
		return f"{self._start} + t * {self._direction}, t >= 0"


@export
@abstractclass
class Segment3D(Element3D[Coordinate], Generic[Coordinate]):
	"""
	An implementation of a 3D cartesian segment.

	A segment owns its start and end point; a group can hold it.
	"""

	_start: Point3D[Coordinate]  #: Start point of a segment.
	_end:   Point3D[Coordinate]  #: End point of a segment.

	def __init__(
		self,
		start:         Point3D[Coordinate],
		end:           Point3D[Coordinate],
		*,
		copyPoints:    bool = True,
		value:         Any = None,
		keyValuePairs: Nullable[Mapping[Hashable, Any]] = None,
		parent:        Nullable[Group3D[Coordinate]] = None
	) -> None:
		"""
		Initializes a 3-dimensional segment.

		:param start:                Start point of the segment.
		:param end:                  End point of the segment.
		:param copyPoints:           Optional, if ``True``, the given points are copied instead of referenced. Default:
		                             ``True``.
		:param value:                Optional, value of the segment. Default: ``None``.
		:param keyValuePairs:        Optional, mapping (dictionary) of key-value-pairs. Default: ``None``.
		:param parent:               Optional, the group the segment is added to. Default: ``None``.
		:raises ValueError:          If parameter 'start' is None.
		:raises TypeError:           If parameter 'start' is not of type :class:`Point3D`.
		:raises AlreadyOwnedError:   If parameter 'start' is owned by another element, while 'copyPoints' is
		                             ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises ValueError:          If parameter 'end' is None.
		:raises TypeError:           If parameter 'end' is not of type :class:`Point3D`.
		:raises DuplicatePointError: If parameter 'end' is the same point as parameter 'start', while 'copyPoints' is
		                             ``False``. |br|
		                             Use ``copyPoints=True`` to copy the points.
		:raises AlreadyOwnedError:   If parameter 'end' is owned by another element, while 'copyPoints' is
		                             ``False``. |br|
		                             Use ``copyPoints=True`` to copy the point.
		:raises ValueError:          If parameter 'copyPoints' is None.
		:raises TypeError:           If parameter 'copyPoints' is not of type :class:`bool`.
		:raises TypeError:           If parameter 'keyValuePairs' is not a mapping.
		:raises TypeError:           If parameter 'parent' is not of type :class:`~pyTooling.Cartesian3D.Groups.Group3D`.
		"""
		super().__init__(value=value, keyValuePairs=keyValuePairs, parent=parent)

		if start is None:
			raise ValueError("Parameter 'start' is None.")
		elif not isinstance(start, Point3D):
			ex = TypeError("Parameter 'start' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(start)}'.")
			raise ex

		if end is None:
			raise ValueError("Parameter 'end' is None.")
		elif not isinstance(end, Point3D):
			ex = TypeError("Parameter 'end' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(end)}'.")
			raise ex

		if copyPoints is None:
			raise ValueError("Parameter 'copyPoints' is None.")
		elif not isinstance(copyPoints, bool):
			ex = TypeError("Parameter 'copyPoints' is not of type 'bool'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(copyPoints)}'.")
			raise ex

		if copyPoints:
			start = start.Copy()
			end =   end.Copy()
		elif end is start:
			ex = DuplicatePointError("Point is given twice.")
			ex.add_note(f"Got point {start}.")
			ex.add_note("Use 'copyPoints=True' to copy the points.")
			raise ex from ValueError("Parameter 'end' is the same point as parameter 'start'.")
		else:
			for name, point in (
				("start", start),
				("end",   end)
			):
				if point._parent is not None:
					ex = AlreadyOwnedError("Point is owned by another element already.")
					ex.add_note(f"Got point {point} owned by {point._parent!r}.")
					ex.add_note("Use 'copyPoints=True' to copy the point.")
					raise ex from ValueError(f"Parameter '{name}' is owned by another element.")

		start._parent = self
		end._parent =   self
		self._start =   start
		self._end =     end

		self.Parent = parent

	@property
	def Start(self) -> Point3D[Coordinate]:
		"""
		Property to access the segment's start point (:attr:`_start`).

		An assigned point is referenced, not copied: the segment takes ownership of it and releases the previous start
		point.

		``start`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:                    Start point of the segment.
		:raises ValueError:          If ``None`` is assigned.
		:raises TypeError:           If an assigned value is not of type :class:`Point3D`.
		:raises DuplicatePointError: If an assigned point is the segment's end point.
		:raises AlreadyOwnedError:   If an assigned point is owned by another element.
		"""
		return self._start

	@Start.setter
	def Start(self, start: Point3D[Coordinate]) -> None:
		if start is None:
			raise ValueError("Parameter 'start' is None.")
		elif not isinstance(start, Point3D):
			ex = TypeError("Parameter 'start' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(start)}'.")
			raise ex
		elif start is self._start:
			return
		elif start is self._end:
			ex = DuplicatePointError("Point is given twice.")
			ex.add_note(f"Got point {start}.")
			raise ex from ValueError("Parameter 'start' is the segment's end point.")
		elif start._parent is not None and start._parent is not self:
			ex = AlreadyOwnedError("Point is owned by another element already.")
			ex.add_note(f"Got point {start} owned by {start._parent!r}.")
			raise ex from ValueError("Parameter 'start' is owned by another element.")

		self._start._parent = None
		start._parent =       self
		self._start =         start

	start = Start

	@property
	def End(self) -> Point3D[Coordinate]:
		"""
		Property to access the segment's end point (:attr:`_end`).

		An assigned point is referenced, not copied: the segment takes ownership of it and releases the previous end
		point.

		``end`` is a deprecated alias of this property; it is removed in v11.0.0.

		:returns:                    End point of the segment.
		:raises ValueError:          If ``None`` is assigned.
		:raises TypeError:           If an assigned value is not of type :class:`Point3D`.
		:raises DuplicatePointError: If an assigned point is the segment's start point.
		:raises AlreadyOwnedError:   If an assigned point is owned by another element.
		"""
		return self._end

	@End.setter
	def End(self, end: Point3D[Coordinate]) -> None:
		if end is None:
			raise ValueError("Parameter 'end' is None.")
		elif not isinstance(end, Point3D):
			ex = TypeError("Parameter 'end' is not of type 'Point3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(end)}'.")
			raise ex
		elif end is self._end:
			return
		elif end is self._start:
			ex = DuplicatePointError("Point is given twice.")
			ex.add_note(f"Got point {end}.")
			raise ex from ValueError("Parameter 'end' is the segment's start point.")
		elif end._parent is not None and end._parent is not self:
			ex = AlreadyOwnedError("Point is owned by another element already.")
			ex.add_note(f"Got point {end} owned by {end._parent!r}.")
			raise ex from ValueError("Parameter 'end' is owned by another element.")

		self._end._parent = None
		end._parent =       self
		self._end =         end

	end = End

	@readonly
	def BoundingBox(self) -> BoundingBox3D[Coordinate]:
		"""
		Read-only property to return the smallest axis-aligned bounding box enclosing the segment's start and end point.

		:returns: A new bounding box.
		"""
		start = self._start
		end =   self._end
		return BoundingBox3D(
			min(start._x, end._x),
			min(start._y, end._y),
			min(start._z, end._z),
			max(start._x, end._x),
			max(start._y, end._y),
			max(start._z, end._z)
		)

	def Move(self, offset: BaseVector3D[Coordinate]) -> None:
		"""
		Move the segment by moving its start and end point (inplace).

		:param offset:      The 3D-vector or 3D-offset to move by.
		:raises ValueError: If parameter 'offset' is None.
		:raises TypeError:  If parameter 'offset' is not of type :class:`BaseVector3D`.
		"""
		if offset is None:
			raise ValueError("Parameter 'offset' is None.")
		elif not isinstance(offset, BaseVector3D):
			ex = TypeError("Parameter 'offset' is not of type 'BaseVector3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(offset)}'.")
			raise ex

		self._start += offset
		self._end +=   offset

	def _MirrorX(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the segment at a plane parallel to the yz-plane by mirroring its start and end point (inplace).

		:param twiceAxis: Twice the x-coordinate of the plane.
		"""
		self._start._x = twiceAxis - self._start._x
		self._end._x =   twiceAxis - self._end._x

	def _MirrorY(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the segment at a plane parallel to the xz-plane by mirroring its start and end point (inplace).

		:param twiceAxis: Twice the y-coordinate of the plane.
		"""
		self._start._y = twiceAxis - self._start._y
		self._end._y =   twiceAxis - self._end._y

	def _MirrorZ(self, twiceAxis: Coordinate) -> None:
		"""
		Mirror the segment at a plane parallel to the xy-plane by mirroring its start and end point (inplace).

		:param twiceAxis: Twice the z-coordinate of the plane.
		"""
		self._start._z = twiceAxis - self._start._z
		self._end._z =   twiceAxis - self._end._z

	def _MirrorAt(self, normal: Vector3D[float], distance: float) -> None:
		"""
		Mirror the segment at a plane by mirroring its start and end point (inplace).

		:param normal:   The normal of the plane, of length 1.
		:param distance: The signed distance of the plane from the frame's origin.
		"""
		self._start._MirrorAt(normal, distance)
		self._end._MirrorAt(normal, distance)

	def Copy(self) -> Self:
		"""
		Create a new 3D-segment as a copy of this 3D-segment.

		The copy holds copies of the start and end point. It references the same :attr:`Value` and holds a shallow copy of
		the key-value-pairs.

		:returns: Copy of this 3D-segment.
		"""
		return self.__class__(self._start, self._end, value=self._value, keyValuePairs=self._dict)

	def __copy__(self) -> Self:
		"""
		Returns a copy of this 3D-segment for :func:`copy.copy`.

		:returns: Copy of this 3D-segment.
		"""
		return self.Copy()

	def __deepcopy__(self, memo: dict[int, Any]) -> Self:
		"""
		Returns a copy of this 3D-segment for :func:`copy.deepcopy`.

		The copy holds copies of the start and end point, and deep copies of the :attr:`Value` and the key-value-pairs.

		:param memo: Dictionary of objects already copied by :func:`copy.deepcopy`.
		:returns:    Copy of this 3D-segment.
		"""
		return self.__class__(
			self._start,
			self._end,
			value=deepcopy(self._value, memo),
			keyValuePairs=deepcopy(self._dict, memo)
		)


@export
class LineSegment3D(Segment3D[Coordinate], Generic[Coordinate]):
	"""An implementation of a 3D cartesian line segment."""

	@readonly
	def Length(self) -> float:
		"""
		Read-only property to return the Euclidean distance between start and end point.

		:returns: Euclidean distance between start and end point
		"""
		start = self._start
		end =   self._end
		return sqrt((end._x - start._x) ** 2 + (end._y - start._y) ** 2 + (end._z - start._z) ** 2)

	def AngleTo(self, other: LineSegment3D[Coordinate]) -> float:
		"""
		Compute the angle between this line segment and another one.

		The angle is the one between both segments' directions, from ``0`` (same direction) to :data:`math.pi` (opposite
		directions).

		:param other:                The second line segment.
		:returns:                    The angle in radians.
		:raises ValueError:          If parameter 'other' is None.
		:raises TypeError:           If parameter 'other' is not of type :class:`LineSegment3D`.
		:raises NotInSameFrameError: If parameter 'other' is in another frame than this line segment.
		:raises ValueError:          If parameter 'other' has length 0.
		:raises ValueError:          If this line segment has length 0.
		"""
		if other is None:
			raise ValueError("Parameter 'other' is None.")
		elif not isinstance(other, LineSegment3D):
			ex = TypeError("Parameter 'other' is not of type 'LineSegment3D'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex
		elif self.Frame is not other.Frame:
			ex = NotInSameFrameError("Line segments are in different frames.")
			ex.add_note(f"Got line segments {self} and {other}.")
			raise ex from ValueError("Parameter 'other' is in another frame.")
		elif other._start._x == other._end._x and other._start._y == other._end._y and other._start._z == other._end._z:
			ex = ValueError("Parameter 'other' has length 0.")
			ex.add_note(f"Got line segment {other}.")
			ex.add_note("Can't determine an angle between two lines if one of the lines has no direction, due to a "
			            "zero-length.")
			raise ex

		if self._start._x == self._end._x and self._start._y == self._end._y and self._start._z == self._end._z:
			ex = ValueError("Line segment has length 0.")
			ex.add_note(f"Got line segment {self}.")
			ex.add_note("Can't determine an angle between two lines if one of the lines has no direction, due to a "
			            "zero-length.")
			raise ex

		vectorA =         self.ToOffset()
		vectorB =         other.ToOffset()
		scalarProductAB = (
			vectorA._xOffset * vectorB._xOffset + vectorA._yOffset * vectorB._yOffset + vectorA._zOffset * vectorB._zOffset
		)
		crossProductX =   vectorA._yOffset * vectorB._zOffset - vectorA._zOffset * vectorB._yOffset
		crossProductY =   vectorA._zOffset * vectorB._xOffset - vectorA._xOffset * vectorB._zOffset
		crossProductZ =   vectorA._xOffset * vectorB._yOffset - vectorA._yOffset * vectorB._xOffset

		return atan2(sqrt(crossProductX ** 2 + crossProductY ** 2 + crossProductZ ** 2), scalarProductAB)

	def ToOffset(self) -> Offset3D[Coordinate]:
		"""
		Convert this 3D line segment to a 3D-offset.

		:returns: 3D-offset as :class:`Offset3D`
		"""
		return self._end - self._start

	def ToVector(self) -> Vector3D[Coordinate]:
		"""
		Convert this 3D line segment to a 3D-vector from its start point to its end point.

		:returns: 3D-vector as :class:`Vector3D`
		"""
		return Vector3D(self._end._x - self._start._x, self._end._y - self._start._y, self._end._z - self._start._z)

	def ToTuple(self) -> tuple[tuple[Coordinate, Coordinate, Coordinate], tuple[Coordinate, Coordinate, Coordinate]]:
		"""
		Convert this 3D line segment to a simple 2-element tuple of 3D-point tuples.

		:returns: ``((x1, y1, z1), (x2, y2, z2))`` tuple.
		"""
		return self._start.ToTuple(), self._end.ToTuple()

	def __repr__(self) -> str:
		"""
		Returns the 3D line segment's string representation.

		:returns: The string representation of the 3D line segment.
		"""
		return f"LineSegment3D({self._start}, {self._end})"

	def __str__(self) -> str:
		"""
		Returns the 3D line segment's string equivalent.

		:returns: The string equivalent of the 3D line segment.
		"""
		return f"({self._start} → {self._end})"

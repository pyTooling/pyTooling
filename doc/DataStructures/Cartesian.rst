.. _STRUCT/Cartesian2D:

2D Cartesian
############

The :mod:`pyTooling.Cartesian2D` package implements points, offsets, sizes and line segments in a 2-dimensional
cartesian coordinate system, plus the four-cornered shapes built from them.

.. seealso::

   :ref:`STRUCT/Cartesian3D`
      |rarr| The same classes with a third axis, and the volumes built from them.

.. #contents:: Table of Contents
   :local:
   :depth: 2

.. rubric:: 2D Cartesian Properties:

* Coordinates as ``int`` or ``float``.
* Every class is generic in its coordinate type, so a grid of integers and a drawing of floats use the same classes.
* A point and an offset are **different types**, which is what makes the arithmetic below unambiguous.

.. _STRUCT/Cartesian2D/Features:

Features
********

* An **integer or a floating-point coordinate system**, chosen per instance - every class is generic in its
  coordinate type, so a grid of integers and a drawing of floats use the same classes.
* **Points and offsets as separate types**, with the arithmetic relating them: a point plus an offset is a point, a
  point minus a point is an offset - in both the copying and the in-place form.
* **Distances measured** - a line segment reports its length and its angle.
* **Shapes placed by their corners**, so a shape is positioned by the points it is built from.
* Shapes validated on construction: :class:`~pyTooling.Cartesian2D.Shapes.Trapezium`,
  :class:`~pyTooling.Cartesian2D.Shapes.Rectangle` and :class:`~pyTooling.Cartesian2D.Shapes.Square`.
* Conversion to plain tuples through ``ToTuple``, for handing coordinates to a library that expects them.


.. _STRUCT/Cartesian2D/MissingFeatures:

Missing Features
================

* Moving a shape as a whole. A point can be shifted, but a shape holds its corners and offers no way to translate
  them together.
* Rotation, scaling and mirroring - a point can be shifted, but not transformed.
* Polygons with a number of corners other than four, and shapes with curved edges.
* Containment and intersection tests (*is this point inside that rectangle?*).
* Area and perimeter of a shape.


.. _STRUCT/Cartesian2D/PlannedFeatures:

Planned Features
================

* An area per shape, and a perimeter derived from its segments.
* The 3-dimensional volumes, which currently exist as empty classes - see :ref:`STRUCT/Cartesian3D/Volumes`.


.. _STRUCT/Cartesian2D/RejectedFeatures:

Out of Scope
============

* A general-purpose geometry or linear-algebra library. These classes exist to give coordinates a **name and a
  type** in the packages using them. |br|
  For doing real geometry have a look at `NumPy <https://numpy.org/>`__ or
  `Shapely <https://shapely.readthedocs.io/>`__.
* Rendering. Nothing here draws anything - ``ToTuple`` hands the numbers to whatever does.
* Coordinate systems other than cartesian - no polar, spherical or geographic coordinates.


.. _STRUCT/Cartesian2D/ByFeature:

By Feature
**********

.. danger::

   Accessing internal fields of a origin, point, offset, ... is strongly not recommended for users, as it might lead to
   a corrupted data structure. If a power-user wants to access these fields, feel free to use them for achieving a
   higher performance, but you got warned 😉.


.. _STRUCT/Cartesian2D/Classes:

Basic Classes
*************

All of them are generic in ``Coordinate``, a type variable bound to :class:`int` or :class:`float`, so the coordinate
type is chosen once and then checked throughout.


.. _STRUCT/Cartesian2D/Point2D:

Point2D
=======

A :class:`~pyTooling.Cartesian2D.Point2D` is a **position**: fields ``x`` and ``y``, and the arithmetic that keeps a
position distinct from a displacement.

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Expression
     - Result
   * - ``point + offset``
     - A new :class:`~pyTooling.Cartesian2D.Point2D`, shifted.
   * - ``point - offset``
     - A new :class:`~pyTooling.Cartesian2D.Point2D`, shifted back.
   * - ``point - point``
     - An :class:`~pyTooling.Cartesian2D.Offset2D` - the displacement between them.
   * - ``point += offset``
     - The **same** point, moved in place.

.. code-block:: Python

   from pyTooling.Cartesian2D import Point2D, Offset2D

   start = Point2D(3, 4)
   moved = start + Offset2D(1, 1)     # Point2D(4, 5)
   delta = moved - start              # Offset2D(1, 1)

An offset may be written as a plain 2-tuple wherever one is accepted. Anything else raises :exc:`TypeError`, with
the offending type in a note.

:meth:`~pyTooling.Cartesian2D.Point2D.Copy` returns an independent point and
:meth:`~pyTooling.Cartesian2D.Point2D.ToTuple` the ``(x, y)`` pair.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Point3D`
      |rarr| Its counterpart, the point with a ``z`` coordinate.


.. _STRUCT/Cartesian2D/Origin2D:

Origin2D
========

An :class:`~pyTooling.Cartesian2D.Origin2D` is a :class:`~pyTooling.Cartesian2D.Point2D` fixed at ``(0, 0)`` - its
constructor takes no coordinates. It exists so a function needing *the* origin can say so in its signature instead
of checking two numbers.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Point2D`
      |rarr| Its base-class, the 2-dimensional point.
   :ref:`STRUCT/Cartesian3D/Origin3D`
      |rarr| Its counterpart, the origin with a ``z`` coordinate.


.. _STRUCT/Cartesian2D/Offset2D:

Offset2D
========

An :class:`~pyTooling.Cartesian2D.Offset2D` is a **displacement**: fields ``xOffset`` and ``yOffset``. Offsets add
and subtract with each other, and negate:

.. code-block:: Python

   right = Offset2D(1, 0)
   left  = -right                     # Offset2D(-1, 0)
   diag  = right + Offset2D(0, 1)     # Offset2D(1, 1)

Unlike a point, an offset compares with ``==`` and ``!=`` - two displacements are equal when their components are.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Offset3D`
      |rarr| Its counterpart, the offset with a ``zOffset``.


.. _STRUCT/Cartesian2D/Size2D:

Size2D
======

A :class:`~pyTooling.Cartesian2D.Size2D` is an **extent**: ``width`` and ``height``. It is deliberately not an
offset - adding a size to a point is meaningless, and keeping the types apart is what prevents it.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Size3D`
      |rarr| Its counterpart, the size with a depth.


.. _STRUCT/Cartesian2D/Segment2D:

Segment2D
=========

A :class:`~pyTooling.Cartesian2D.Segment2D` is a ``start`` and an ``end`` point.

Its constructor **copies both points by default**, so a segment doesn't change when the points it was built from
move later. ``copyPoints=False`` keeps the references instead, which is what
:class:`~pyTooling.Cartesian2D.Shapes.Trapezium` uses to let consecutive edges share a corner.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Segment3D`
      |rarr| Its counterpart, the segment between two 3D points.


.. _STRUCT/Cartesian2D/LineSegment2D:

LineSegment2D
=============

A :class:`~pyTooling.Cartesian2D.LineSegment2D` is a segment understood as a straight line, which is what gives it
measurements:

* :attr:`~pyTooling.Cartesian2D.LineSegment2D.Length` - the Euclidean distance between its ends, a :class:`float`
  even for integer coordinates;
* :meth:`~pyTooling.Cartesian2D.LineSegment2D.AngleTo` - the angle to another line segment;
* :meth:`~pyTooling.Cartesian2D.LineSegment2D.ToOffset` - the segment as the displacement from start to end.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Segment2D`
      |rarr| Its base-class, the 2-dimensional segment.
   :ref:`STRUCT/Cartesian3D/LineSegment3D`
      |rarr| Its counterpart, the line segment in 3D.


.. _STRUCT/Cartesian2D/Shapes:

Shapes
******

The shapes live in :mod:`pyTooling.Cartesian2D.Shapes` and form a chain in which **each class is the one above it
with one more constraint**. The constraint is checked in the constructor, so an object that exists is an object of
that shape.


.. _STRUCT/Cartesian2D/Shape:

Shape
=====

:class:`~pyTooling.Cartesian2D.Shapes.Shape` is the empty base-class of every 2D shape. It carries no fields; it
exists so a function can accept *a shape*.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Volume`
      |rarr| Its counterpart, the base-class of the 3-dimensional volumes.


.. _STRUCT/Cartesian2D/Trapezium:

Trapezium
=========

A :class:`~pyTooling.Cartesian2D.Shapes.Trapezium` is a four-sided polygon, built from four corners given in the
order ``p00``, ``p01``, ``p11``, ``p10`` - around the outline, not across it.

It keeps both views: ``points``, the four corners it copied, and ``segments``, the four
:class:`~pyTooling.Cartesian2D.LineSegment2D` edges between them. The segments are built with ``copyPoints=False``,
so consecutive edges share a corner object and the outline stays closed.

A corner that isn't a :class:`~pyTooling.Cartesian2D.Point2D` raises :exc:`TypeError`.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Shape`
      |rarr| Its base-class, the base-class of the 2-dimensional shapes.


.. _STRUCT/Cartesian2D/Rectangle:

Rectangle
=========

A :class:`~pyTooling.Cartesian2D.Shapes.Rectangle` is a trapezium whose opposite edges are parallel and equal in
length, with 90 |degree| inner angles. The constructor compares the opposite edges' lengths and the angles between
consecutive edges, and raises :exc:`ValueError` when the four corners describe something else.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Trapezium`
      |rarr| Its base-class, the four-cornered shape every other one narrows.
   :ref:`STRUCT/Cartesian3D/Cuboid`
      |rarr| Its counterpart, the volume a rectangle corresponds to.


.. _STRUCT/Cartesian2D/Square:

Square
======

A :class:`~pyTooling.Cartesian2D.Shapes.Square` is a rectangle whose edges are all the same length - one more
comparison, one more :exc:`ValueError`.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Rectangle`
      |rarr| Its base-class, the trapezium with four right angles.
   :ref:`STRUCT/Cartesian3D/Cube`
      |rarr| Its counterpart, the volume a square corresponds to.


.. _STRUCT/Cartesian3D:

3D Cartesian
############

The :mod:`pyTooling.Cartesian3D` package is :mod:`pyTooling.Cartesian2D` with a third axis: the same classes, the
same arithmetic, and a ``z`` coordinate throughout. Everything above applies, so this section names only what
differs.

.. seealso::

   :ref:`STRUCT/Cartesian2D`
      |rarr| The 2-dimensional classes this package extends, where the arithmetic is written out.


.. _STRUCT/Cartesian3D/Classes:

Basic Classes
*************


.. _STRUCT/Cartesian3D/Point3D:

Point3D
=======

A :class:`~pyTooling.Cartesian3D.Point3D` has ``x``, ``y`` and ``z``, and the same arithmetic against an
:class:`~pyTooling.Cartesian3D.Offset3D`. A plain 3-tuple is accepted wherever an offset is.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Point2D`
      |rarr| Its counterpart, the 2-dimensional point.


.. _STRUCT/Cartesian3D/Origin3D:

Origin3D
========

:class:`~pyTooling.Cartesian3D.Origin3D` is a :class:`~pyTooling.Cartesian3D.Point3D` fixed at ``(0, 0, 0)``.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Point3D`
      |rarr| Its base-class, the point with a ``z`` coordinate.
   :ref:`STRUCT/Cartesian2D/Origin2D`
      |rarr| Its counterpart, the 2-dimensional origin.


.. _STRUCT/Cartesian3D/Offset3D:

Offset3D
========

:class:`~pyTooling.Cartesian3D.Offset3D` holds ``xOffset``, ``yOffset`` and ``zOffset``, and negates, adds,
subtracts and compares as its 2D counterpart does.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Offset2D`
      |rarr| Its counterpart, the 2-dimensional offset.


.. _STRUCT/Cartesian3D/Size3D:

Size3D
======

:class:`~pyTooling.Cartesian3D.Size3D` is ``width``, ``height`` and ``depth``.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Size2D`
      |rarr| Its counterpart, the 2-dimensional size.


.. _STRUCT/Cartesian3D/Segment3D:

Segment3D
=========

:class:`~pyTooling.Cartesian3D.Segment3D` is a ``start`` and an ``end`` point, copied on construction unless
``copyPoints=False``.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Segment2D`
      |rarr| Its counterpart, the 2-dimensional segment.


.. _STRUCT/Cartesian3D/LineSegment3D:

LineSegment3D
=============

:class:`~pyTooling.Cartesian3D.LineSegment3D` adds the measurements - length in three dimensions, the angle to
another line segment, and conversion to an offset.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Segment3D`
      |rarr| Its base-class, the segment between two 3D points.
   :ref:`STRUCT/Cartesian2D/LineSegment2D`
      |rarr| Its counterpart, the 2-dimensional line segment.


.. _STRUCT/Cartesian3D/Volumes:

Volumes
*******

.. attention::

   The volumes in :mod:`pyTooling.Cartesian3D.Volumes` are **declared but not implemented**. All three classes are
   empty: no corners, no constructor, no validation. They are not the 3D counterpart of the 2D shapes yet, and are
   listed here because they exist and can be subclassed, not because they can be used.


.. _STRUCT/Cartesian3D/Volume:

Volume
======

:class:`~pyTooling.Cartesian3D.Volumes.Volume` is the empty base-class of every 3D volume, matching
:class:`~pyTooling.Cartesian2D.Shapes.Shape`.

.. seealso::

   :ref:`STRUCT/Cartesian2D/Shape`
      |rarr| Its counterpart, the base-class of the 2-dimensional shapes.


.. _STRUCT/Cartesian3D/Cuboid:

Cuboid
======

:class:`~pyTooling.Cartesian3D.Volumes.Cuboid` is intended as a volume bounded by six rectangles - the counterpart
of :class:`~pyTooling.Cartesian2D.Shapes.Rectangle`.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Volume`
      |rarr| Its base-class, the base-class of the 3-dimensional volumes.
   :ref:`STRUCT/Cartesian2D/Rectangle`
      |rarr| Its counterpart, the trapezium with four right angles.


.. _STRUCT/Cartesian3D/Cube:

Cube
====

:class:`~pyTooling.Cartesian3D.Volumes.Cube` is intended as a cuboid of six equally sized squares - the counterpart
of :class:`~pyTooling.Cartesian2D.Shapes.Square`.

.. seealso::

   :ref:`STRUCT/Cartesian3D/Cuboid`
      |rarr| Its base-class, the volume a rectangle corresponds to.
   :ref:`STRUCT/Cartesian2D/Square`
      |rarr| Its counterpart, the rectangle with four equal sides.
.. _FILESYS:

Filesystem
##########

The :mod:`pyTooling.Filesystem` package provides fast and simple access to directory statistics like file sizes,
accumulated directory sizes, symlinks, hardlinks, etc.


.. _FILESYS/Features:

Features
********

* Scan a directory and its subdirectories for files and create a in-memory filesystem view (directories, files, symbolic
  links, hard links).
* Identify filenames pointing to the same file (a.k.a hard links).
* Compute directory sizes by aggregating file sizes.


.. _FILESYS/MissingFeatures:

Missing Features
================

* tbd


.. _FILESYS/PlannedFeatures:

Planned Features
================

* tbd


.. _FILESYS/RejectedFeatures:

Out of Scope
============

* tbd


.. _FILESYS/ByFeature:

By Feature
**********

.. danger::

   Accessing internal fields of a node is strongly not recommended for users, as it might lead to a corrupted tree data
   structure. If a power-user wants to access these fields, feel free to use them for achieving a higher performance,
   but you got warned 😉.


.. _FILESYS/Root:

Root Reference
==============

Every element of a scanned filesystem - a :class:`~pyTooling.Filesystem.Directory`, a
:class:`~pyTooling.Filesystem.Filename`, a :class:`~pyTooling.Filesystem.SymbolicLink` - knows the
:class:`~pyTooling.Filesystem.Root` it belongs to, through :attr:`~pyTooling.Filesystem.Base.Root`. The root knows
itself, so the reference is never :pycode:`None` within a scan and needs no special case at the top:

.. code-block:: Python

   from pathlib import Path
   from pyTooling.Filesystem import Root

   root = Root(Path("/home/user/project"))

   root.Root is root                        # True

   source = next(root.Subdirectories)
   source.Root is root                      # True
   next(source.RegularFiles).Root is root   # True

The reference exists because the interesting questions are asked of the **root** and answered for the whole scan:
which symbolic links are broken, how many distinct files there are, how much space would be needed without hard
links. An element deep in the tree can reach those answers without being handed the root separately.

.. list-table::
   :header-rows: 1
   :widths: 46 54

   * - On the root
     - Answers
   * - :attr:`~pyTooling.Filesystem.Root.BrokenSymbolicLinks`
     - the links whose target doesn't exist
   * - :attr:`~pyTooling.Filesystem.Root.UnconnectedSymbolicLinks`
     - the links whose target lies outside the scanned tree
   * - :attr:`~pyTooling.Filesystem.Root.TotalUniqueFileCount`
     - distinct file storage objects, hard links counted once
   * - :attr:`~pyTooling.Filesystem.Root.TotalHardLinkCount`
     - directory entries pointing at multiply-linked files

.. attention::

   :attr:`~pyTooling.Filesystem.Base.Root` is writable, and assigning it is how the scan wires an element into its
   tree - not something user code should do. Assigning ``None`` raises :exc:`ValueError` and assigning anything that
   is not a :class:`~pyTooling.Filesystem.Root` raises :exc:`TypeError`, but neither protects a tree from being
   re-parented into an inconsistent state.


.. _FILESYS/Parent:

Parent Reference
================

:attr:`~pyTooling.Filesystem.Element.Parent` is the containing directory, so the tree can be walked **upwards** as
well as downwards. :attr:`~pyTooling.Filesystem.Element.Path` is built from that chain, which is why an element
knows its full path without storing one:

.. code-block:: Python

   source = next(root.Subdirectories)

   source.Parent is root      # True
   source.Name                # 'source'
   source.Path                # PosixPath('/home/user/project/source')

   file = next(source.RegularFiles)
   file.Parent is source      # True

Walking downwards is done with the generators on :class:`~pyTooling.Filesystem.Directory` -
:attr:`~pyTooling.Filesystem.Directory.Subdirectories`, :attr:`~pyTooling.Filesystem.Directory.Files`,
:attr:`~pyTooling.Filesystem.Directory.RegularFiles`, :attr:`~pyTooling.Filesystem.Directory.SymbolicLinks` for one
level, and :meth:`~pyTooling.Filesystem.Directory.IterateDirectories` /
:meth:`~pyTooling.Filesystem.Directory.IterateFiles` for the whole subtree.

.. hint::

   A :class:`~pyTooling.Filesystem.File` is the *storage object* and a :class:`~pyTooling.Filesystem.Filename` is a
   directory entry naming it. That is the distinction hard links are built on: one
   :class:`~pyTooling.Filesystem.File` with several :attr:`~pyTooling.Filesystem.File.Parents`. So an element's
   parent is its directory, while a file's :pycode:`Parents` are the names it is reachable by.


.. _FILESYS/Size:

Size
====

:attr:`~pyTooling.Filesystem.Base.Size` is in bytes, and a directory's size is the sum of everything below it.
:meth:`~pyTooling.Filesystem.Directory.AggregateSizes` computes those sums for the whole tree:

.. code-block:: Python

   root = Root(Path("/home/user/project"))
   root.AggregateSizes()

   root.Size                  # every directory entry, hard links counted each time
   next(root.Subdirectories).Size

**Hard links make "the size of a directory" ambiguous**, so three properties answer three different questions rather
than one of them pretending to be the answer. For a tree of :pycode:`a.txt` (100 bytes), :pycode:`b.txt` (200 bytes),
``c.txt`` (50 bytes), a second directory entry hard-linked to :pycode:`a.txt`, and a symbolic link to :pycode:`b.txt`:

.. list-table::
   :header-rows: 1
   :widths: 34 12 54

   * - Property
     - Value
     - Question it answers
   * - :attr:`~pyTooling.Filesystem.Base.Size`
     - :pycode:`450`
     - How much do the directory entries add up to? The hard link is counted again - ``100 + 200 + 50 + 100``.
   * - :attr:`~pyTooling.Filesystem.Root.Size2`
     - :pycode:`100`
     - How much of that is hard-linked content, counted **once** per file?
   * - :attr:`~pyTooling.Filesystem.Root.Size3`
     - :pycode:`200`
     - How much would the hard-linked content cost on a filesystem **without** hard links? ``100 × 2 entries``.

So ``Size - Size2`` is what hard-linking saves, and the counts alongside them tell the same story in files:
:attr:`~pyTooling.Filesystem.Root.TotalFileCount` is :pycode:`5`,
:attr:`~pyTooling.Filesystem.Root.TotalUniqueFileCount` is :pycode:`3`, and
:attr:`~pyTooling.Filesystem.Root.TotalHardLinkCount` is :pycode:`2`.

.. hint::

   :attr:`~pyTooling.Filesystem.Directory.ScanDuration` and
   :attr:`~pyTooling.Filesystem.Directory.AggregateDuration` report what the two phases cost, measured with
   :class:`~pyTooling.Stopwatch.Stopwatch`. On a large tree the scan dominates, because it is the part that touches
   the filesystem.




.. _FILESYS/Competitors:

Competing Solutions
*******************


.. _FILESYS/Directory-Tree:

Directory Tree
==============

Source: :gh:`Directory Tree <rahulbordoloi/Directory-Tree>`


.. todo:: FILESYS::Directory-Tree write comparison here.

.. rubric:: Disadvantages

* ...

.. rubric:: Standoff

* ...

.. rubric:: Advantages

* ...


.. _FILESYS/folderstats:

folderstats
===========

Source: :gh:`folderstats <njanakiev/folderstats>`


.. todo:: FILESYS::folderstats write comparison here.

.. rubric:: Disadvantages

* ...

.. rubric:: Standoff

* ...

.. rubric:: Advantages

* ...


.. _FILESYS/dutree:

dutree
======

Source: :gh:`dutree <ossobv/dutree>`


.. todo:: FILESYS::dutree write comparison here.

.. rubric:: Disadvantages

* ...

.. rubric:: Standoff

* ...

.. rubric:: Advantages

* ...

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

tbd


.. _FILESYS/Parent:

Parent Reference
================

tbd


.. _FILESYS/Size:

Size
====

tbd




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

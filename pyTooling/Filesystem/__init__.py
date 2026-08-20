# ==================================================================================================================== #
#             _____           _ _               _____ _ _                     _                                        #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  ___(_) | ___  ___ _   _ ___| |_ ___ _ __ ___                         #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |_  | | |/ _ \/ __| | | / __| __/ _ \ '_ ` _ \                        #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_|  _| | | |  __/\__ \ |_| \__ \ ||  __/ | | | | |                       #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|   |_|_|\___||___/\__, |___/\__\___|_| |_| |_|                       #
# |_|    |___/                          |___/                       |___/                                              #
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
An object-oriented file system abstraction for directory, file, symbolic link, ... statistics collection.

.. important::

   This isn't a replacement of :mod:`pathlib` introduced with Python 3.4.

.. seealso::

   :mod:`pyTooling.Filesystem.Docker`
      |rarr| Slicing a scanned filesystem into Docker image layers.
   :mod:`pyTooling.Tree`
      |rarr| The tree data structure a filesystem scope is converted to.
   :mod:`pyTooling.Stopwatch`
      |rarr| The stopwatch measuring how long a scan took.
"""
from os                    import scandir, readlink

from enum                  import Enum
from itertools             import chain
from pathlib               import Path
from typing                import Optional as Nullable, Generic, Generator, TypeVar, Any, Callable, Union
from typing                import Iterator, cast
from pyTooling.Decorators  import readonly, export
from pyTooling.Exceptions  import ToolingException
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Common      import getFullyQualifiedName, zipdicts
from pyTooling.Warning     import WarningCollector, Warning
from pyTooling.Stopwatch   import Stopwatch
from pyTooling.Tree        import Node


__all__ = ["_ParentType"]


_ParentType = TypeVar("_ParentType", bound="Element")
"""The type variable for a parent reference."""


@export
class FilesystemException(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.Filesystem`."""


@export
class PermissionWarning(Warning):
	"""
	Warning emitted when a directory or file couldn't be read while scanning a filesystem.

	The scan continues, so the collected statistics are incomplete by exactly the path this warning carries.
	"""
	_path: Path  #: Path that couldn't be read.

	def __init__(self, path: Path, *args: Any) -> None:
		"""
		Initialize a permission warning for the path that couldn't be read.

		:param path: The path that raised a :exc:`PermissionError`.
		:param args: Positional parameters forwarded to the base-class.
		"""
		super().__init__(*args)
		self._path = path

	@readonly
	def Path(self) -> Path:
		"""
		Read-only property to access the path that couldn't be read (:attr:`_path`).

		:returns: The path that raised a :exc:`PermissionError`.
		"""
		return self._path


@export
class NodeKind(Enum):
	"""
	Node kind for filesystem elements in a :ref:`tree <STRUCT/Tree>`.

	This enumeration is used when converting the filesystem statistics tree to an instance of :mod:`pyTooling.Tree`.
	"""
	Directory =    0  #: Node represents a directory.
	File =         1  #: Node represents a regular file.
	SymbolicLink = 2  #: Node represents a symbolic link.


@export
class Base(metaclass=ExtendedType, slots=True):
	"""
	Base-class for all filesystem elements in :mod:`pyTooling.Filesystem`.

	It implements a size and a reference to the root element of the filesystem.
	"""
	_root:   Nullable["Root"]  #: Reference to the root of the filesystem statistics scope.
	_size:   Nullable[int]     #: Actual or aggregated size of the filesystem element.

	def __init__(
		self,
		size: Nullable[int],
		root: Nullable["Root"]
	) -> None:
		"""
		Initialize the base-class with filesystem element size and root reference.

		:param size:       Optional, size of the element.
		:param root:       Optional reference to the filesystem root element.
		:raises TypeError: If parameter 'size' is not of type integer.
		:raises TypeError: If parameter 'root' is not of type :class:`Root`.
		"""
		if size is not None and not isinstance(size, int):
			ex = TypeError("Parameter 'size' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(size)}'.")
			raise ex

		if root is not None and not isinstance(root, Root):
			ex = TypeError("Parameter 'root' is not of type 'Root'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(root)}'.")
			raise ex

		self._size = size
		self._root = root

	@property
	def Root(self) -> Nullable["Root"]:
		"""
		Property to access the root of the filesystem statistics scope.

		:returns:           Root of the filesystem statistics scope.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`Root`.
		"""
		return self._root

	@Root.setter
	def Root(self, value: "Root") -> None:
		if value is None:
			raise ValueError(f"Parameter 'value' is None.")
		elif not isinstance(value, Root):
			ex = TypeError("Parameter 'value' is not of type 'Root'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

		self._root = value

	@readonly
	def Size(self) -> int:
		"""
		Read-only property to access the element's size in Bytes.

		:returns:                    Size in Bytes.
		:raises FilesystemException: If size is not computed, yet.
		"""
		if self._size is None:
			raise FilesystemException("Size is not computed, yet.")

		return self._size

	# FIXME: @abstractmethod
	def ToTree(self) -> Node:
		"""
		Convert a filesystem element to a node in :mod:`pyTooling.Tree`.

		The node's :attr:`~pyTooling.Tree.Node.Value` field contains a reference to the filesystem element. Additional data
		will be stored in the node's key-value store.

		:returns:                    A tree's node referencing this filesystem element.
		"""
		raise NotImplementedError()


@export
class Element(Base, Generic[_ParentType]):
	"""
	Base-class for all named elements within a filesystem.

	It adds a name, parent reference and list of symbolic-link sources.

	.. hint::

	   Symbolic link sources are reverse references describing which symbolic links point to this element.
	"""
	_name:        str                   #: Name of the filesystem element.
	_parent:      _ParentType           #: Reference to the filesystem element's parent (:class:`Directory`)
	_linkSources: list["SymbolicLink"]  #: A list of symbolic links pointing to this filesystem element.

	def __init__(
		self,
		name:   str,
		size:   Nullable[int] = None,
		parent: Nullable[_ParentType] = None
	) -> None:
		"""
		Initialize the element base-class with name, size and parent reference.

		:param name:        Name of the element.
		:param size:        Optional, size of the element.
		:param parent:      Optional, parent reference.
		:raises ValueError: If parameter 'name' is None.
		:raises TypeError:  If parameter 'parent' is not of type :class:`Directory`.
		"""
		if name is None:
			raise ValueError(f"Parameter 'name' is None.")
		elif not isinstance(name, str):
			ex = TypeError("Parameter 'name' is not of type 'str'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(name)}'.")
			raise ex

		self._name =   name

		if parent is None:
			super().__init__(size, None)
			self._parent = None
		else:
			if not isinstance(parent, Directory):
				ex = TypeError("Parameter 'parent' is not of type 'Directory'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
				raise ex

			super().__init__(size, parent._root)
			self._parent = parent

		self._linkSources = []

	@property
	def Parent(self) -> _ParentType:
		"""
		Property to access the element's parent.

		:returns:           Parent element.
		:raises ValueError: If ``None`` is assigned.
		:raises TypeError:  If an assigned value is not of type :class:`Directory`.
		"""
		return self._parent

	@Parent.setter
	def Parent(self, value: _ParentType) -> None:
		if value is None:
			raise ValueError(f"Parameter 'value' is None.")
		elif not isinstance(value, Directory):
			ex = TypeError("Parameter 'value' is not of type 'Directory'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(value)}'.")
			raise ex

		self._parent = value

		if value._root is not None:
			self._root = value._root

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the element's name.

		:returns: Element name.
		"""
		return self._name

	@readonly
	def Path(self) -> Path:
		"""
		Read-only property to access the element's path.

		:returns:                    Path of the element.
		"""
		raise NotImplementedError(f"Property 'Path' is abstract.")

	@readonly
	def LinkSources(self) -> list["SymbolicLink"]:
		"""
		Read-only property to access the symbolic links pointing to this element (:attr:`_linkSources`).

		:returns: List of symbolic links targeting this element.
		"""
		return self._linkSources

	def AddLinkSources(self, source: "SymbolicLink") -> None:
		"""
		Add a link source of a symbolic link to the named element (reverse reference).

		:param source:     The referenced symbolic link.
		:raises TypeError: If parameter 'source' is not of type :class:`SymbolicLink`.
		"""
		if not isinstance(source, SymbolicLink):
			ex = TypeError("Parameter 'source' is not of type 'SymbolicLink'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(source)}'.")
			raise ex

		source._isConnected =  True
		source._isBroken =     False
		source._isOutOfRange = False
		self._linkSources.append(source)


@export
class Directory(Element["Directory"]):
	"""
	A **directory** represents a directory in the filesystem, which contains subdirectories, regular files and symbolic links.

	While scanning for subelements, the directory is populated with elements. Every file object added, gets registered in
	the filesystems :class:`Root` for deduplication. In case a file identifier already exists, the found filename will
	reference the same file objects. In turn, the file objects has then references to multiple filenames (parents). This
	allows to detect :term:`hardlinks <hardlink>`.

	The time needed for scanning the directory and its subelements is provided via :data:`ScanDuration`.

	After scnaning the directory for subelements, certain directory properties get aggregated. The time needed for
	aggregation is provided via :data:`AggregateDuration`.
	"""

	_path:              Nullable[Path]             #: Cached :class:`~pathlib.Path` object of this directory.
	_subdirectories:    dict[str, "Directory"]     #: Dictionary containing name-:class:`Directory` pairs.
	_files:             dict[str, "Filename"]      #: Dictionary containing name-:class:`Filename` pairs.
	_symbolicLinks:     dict[str, "SymbolicLink"]  #: Dictionary containing name-:class:`SymbolicLink` pairs.
	_filesSize:         int                        #: Aggregated size of all direct files.
	_collapsed:         bool                       #: True, if this directory was collapsed. It contains no subelements.
	_scanDuration:      Nullable[float]            #: Duration for scanning the directory and all its subelements.
	_aggregateDuration: Nullable[float]            #: Duration for aggregating all subelements.

	def __init__(
		self,
		name:                  str,
		collectSubdirectories: bool = False,
		parent:                Nullable["Directory"] = None
	) -> None:
		"""
		Initialize the directory with name and parent reference.

		:param name:                  Name of the element.
		:param collectSubdirectories: Optional, if ``True``, collect subdirectory statistics.
		:param parent:                Optional, parent reference.
		"""
		super().__init__(name, None, parent)

		self._path =              None
		self._subdirectories =    {}
		self._files =             {}
		self._symbolicLinks =     {}
		self._filesSize =         0
		self._collapsed =         False
		self._scanDuration =      None
		self._aggregateDuration = None

		if parent is not None:
			parent._subdirectories[name] = self

			if parent._root is not None:
				self._root = parent._root

		if collectSubdirectories:
			self.CollectSubdirectories()

	def CollectSubdirectories(self) -> None:
		"""
		Helper method for scanning subdirectories and aggregating found element sizes therein.
		"""
		self.ScanSubdirectories()
		self.AggregateSizes()

	def ScanSubdirectories(self) -> None:
		"""
		Helper method for scanning subdirectories (recursively) and building a
		:class:`Directory`-:class:`Filename`-:class:`File` object tree.

		If a file refers to the same filesystem internal unique ID, a hardlink (two or more filenames) to the same file
		storage object is assumed.

		A directory that can't be read is reported as a :class:`PermissionWarning` and skipped, so the scan continues and
		the collected statistics are incomplete by exactly that path.

		:raises FilesystemException: If this directory isn't attached to a :class:`Root`, which owns the ID table.
		:raises FilesystemException: If the directory contains an element that is neither a directory, a file nor a
		                             symbolic link.
		"""
		if (root := self._root) is None:
			raise FilesystemException(f"Directory '{self._name}' is not attached to a filesystem root.")

		with Stopwatch() as sw1:
			try:
				items = scandir(directoryPath := self.Path)
			except PermissionError as ex:
				return WarningCollector.Raise(PermissionWarning(self.Path), ex)

			for dirEntry in items:
				if dirEntry.is_dir(follow_symlinks=False):
					_ = Directory(dirEntry.name, collectSubdirectories=True, parent=self)
				elif dirEntry.is_file(follow_symlinks=False):
					id = dirEntry.inode()
					if id in root._ids:
						file = root._ids[id]

						_ = Filename(dirEntry.name, file=file, parent=self)
					else:
						s = dirEntry.stat(follow_symlinks=False)
						filename = Filename(dirEntry.name, parent=self)
						file = File(id, s.st_size, parent=filename)

						root._ids[id] = file
				elif dirEntry.is_symlink():
					target = Path(readlink(directoryPath / dirEntry.name))
					_ = SymbolicLink(dirEntry.name, target, parent=self)
				else:
					raise FilesystemException(f"Unknown directory element.")

		self._scanDuration = sw1.Duration

	def ResolveSymbolicLinks(self) -> None:
		"""
		Resolve the symbolic links of this directory and of every directory below it.

		A link whose target lies inside the scanned tree is connected to that element; a target that doesn't exist
		registers the link as broken, and a target outside the scanned tree registers it as unconnected.
		"""
		for dir in self._subdirectories.values():
			dir.ResolveSymbolicLinks()

		for link in self._symbolicLinks.values():
			if link._target.is_absolute():
				# todo: resolve path and check if target is in range, otherwise add to out-of-range list
				pass
			else:
				target = self
				for elem in link._target.parts:
					if elem == ".":
						continue
					elif elem == "..":
						if (target := target._parent) is None:
							self._root.RegisterUnconnectedSymbolicLink(link)
							break

						continue

					try:
						target = target._subdirectories[elem]
						continue
					except KeyError:
						pass

					try:
						target = target._files[elem]
						continue
					except KeyError:
						pass

					try:
						target = target._symbolicLinks[elem]
						continue
					except KeyError:
						self._root.RegisterBrokenSymbolicLink(link)
						break
				else:
					target.AddLinkSources(link)

	def AggregateSizes(self) -> set["File"]:
		"""
		Compute the aggregated size of this directory and of every directory below it.

		A file is counted once, even when several filenames (hardlinks) refer to it, which is why the already counted
		files are returned and handed up the recursion.

		:returns: The set of file objects counted in this subtree.
		"""
		with Stopwatch() as sw2:
			aggregatedFiles = set()

			self._size = 0
			self._filesSize = 0
			for dir in self._subdirectories.values():
				aggregatedFiles |= dir.AggregateSizes()
				self._size += dir._size

			for filename in self._files.values():
				if (file := filename._file) not in aggregatedFiles:
					self._filesSize += file._size
					aggregatedFiles.add(file)

			self._size += self._filesSize

		self._aggregateDuration = sw2.Duration

		return aggregatedFiles

	@Element.Root.setter
	def Root(self, value: "Root") -> None:
		Element.Root.fset(self, value)

		for subdir in self._subdirectories.values():
			subdir.Root = value

		for file in self._files.values():
			file.Root = value

		for link in self._symbolicLinks.values():
			link.Root = value

	@Element.Parent.setter
	def Parent(self, value: _ParentType) -> None:
		Element.Parent.fset(self, value)

		value._subdirectories[self._name] = self

		if isinstance(value, Root):
			self.Root = value

	@readonly
	def Count(self) -> int:
		"""
		Read-only property to return the number of elements in a directory.

		:returns: Number of files plus subdirectories.
		"""
		return len(self._subdirectories) + len(self._files) + len(self._symbolicLinks)

	@readonly
	def FileCount(self) -> int:
		"""
		Read-only property to return the number of files in a directory.

		.. hint::

		   Files include regular files and symbolic links.

		:returns: Number of files.
		"""
		return len(self._files) + len(self._symbolicLinks)

	@readonly
	def RegularFileCount(self) -> int:
		"""
		Read-only property to return the number of regular files in a directory.

		:returns: Number of regular files.
		"""
		return len(self._files)

	@readonly
	def SymbolicLinkCount(self) -> int:
		"""
		Read-only property to return the number of symbolic links in a directory.

		:returns: Number of symbolic links.
		"""
		return len(self._symbolicLinks)

	@readonly
	def SubdirectoryCount(self) -> int:
		"""
		Read-only property to return the number of subdirectories in a directory.

		:returns: Number of subdirectories.
		"""
		return len(self._subdirectories)

	@readonly
	def TotalFileCount(self) -> int:
		"""
		Read-only property to return the total number of files in all child hierarchy levels (recursively).

		.. hint::

		   Files include regular files and symbolic links.

		:returns: Total number of files.
		"""
		return sum(d.TotalFileCount for d in self._subdirectories.values()) + len(self._files) + len(self._symbolicLinks)

	@readonly
	def TotalRegularFileCount(self) -> int:
		"""
		Read-only property to return the total number of regular files in all child hierarchy levels (recursively).

		:returns: Total number of regular files.
		"""
		return sum(d.TotalRegularFileCount for d in self._subdirectories.values()) + len(self._files)

	@readonly
	def TotalSymbolicLinkCount(self) -> int:
		"""
		Read-only property to return the total number of symbolic links in all child hierarchy levels (recursively).

		:returns: Total number of symbolic links.
		"""
		return sum(d.TotalSymbolicLinkCount for d in self._subdirectories.values()) + len(self._symbolicLinks)

	@readonly
	def TotalSubdirectoryCount(self) -> int:
		"""
		Read-only property to return the total number of subdirectories in all child hierarchy levels (recursively).

		:returns: Total number of subdirectories.
		"""
		return len(self._subdirectories) + sum(d.TotalSubdirectoryCount for d in self._subdirectories.values())

	@readonly
	def Subdirectories(self) -> Generator["Directory", None, None]:
		"""
		Iterate all direct subdirectories of the directory.

		:returns: A generator to iterate all direct subdirectories.
		"""
		return (d for d in self._subdirectories.values())

	@readonly
	def Files(self) -> Generator["Filename | SymbolicLink", None, None]:
		"""
		Iterate all direct files of the directory.

		.. hint::

		   Files include regular files and symbolic links.

		:returns: A generator to iterate all direct files.
		"""
		return (f for f in chain(self._files.values(), self._symbolicLinks.values()))

	@readonly
	def RegularFiles(self) -> Generator["Filename", None, None]:
		"""
		Iterate all direct regular files of the directory.

		:returns: A generator to iterate all direct regular files.
		"""
		return (f for f in self._files.values())

	@readonly
	def SymbolicLinks(self) -> Generator["SymbolicLink", None, None]:
		"""
		Iterate all direct symbolic links of the directory.

		:returns: A generator to iterate all direct symbolic links.
		"""
		return (l for l in self._symbolicLinks.values())

	@readonly
	def Path(self) -> Path:
		"""
		Read-only property to access the equivalent Path instance for accessing the represented directory.

		:returns:                    Path to the directory.
		:raises FilesystemException: If no parent is set.
		"""
		if self._path is not None:
			return self._path

		if self._parent is None:
			raise FilesystemException(f"No parent or root set for directory.")

		self._path = self._parent.Path / self._name
		return self._path

	@readonly
	def ScanDuration(self) -> float:
		"""
		Read-only property to access the time needed to scan a directory structure including all subelements (recursively).

		:returns:                    The scan duration in seconds.
		:raises FilesystemException: If the directory was not scanned.
		"""
		if self._scanDuration is None:
			raise FilesystemException(f"Directory was not scanned, yet.")

		return self._scanDuration

	@readonly
	def AggregateDuration(self) -> float:
		"""
		Read-only property to access the time needed to aggregate the directory's and subelement's properties (recursively).

		:returns:                    The aggregation duration in seconds.
		:raises FilesystemException: If the directory properties were not aggregated.
		"""
		if self._scanDuration is None:
			raise FilesystemException(f"Directory properties were not aggregated, yet.")

		return self._aggregateDuration

	def __hash__(self) -> int:
		"""
		Compute a hash for this filesystem element based on its identity.

		Two elements with the same name in different directories are different elements, so the hash is derived from the
		object's identity and not from its name.

		:returns: Hash of this filesystem element.
		"""
		return hash(id(self))

	def IterateDirectories(self) -> Generator["Directory", None, None]:
		"""
		A generator to iterate all subdirectories below this directory in pre-order.

		A parent directory is yielded before its children.

		:returns: A generator to iterate all subdirectories below this directory.
		"""
		# pre-order
		for directory in self._subdirectories.values():
			yield directory
			yield from directory.IterateDirectories()

	def IterateFiles(self) -> Generator[Element, None, None]:
		"""
		A generator to iterate all files and symbolic links below this directory in post-order.

		The elements of the subdirectories are yielded before this directory's own.

		:returns: A generator to iterate all files and symbolic links below this directory.
		"""
		# post-order
		for directory in self._subdirectories.values():
			yield from directory.IterateFiles()

		yield from self._files.values()
		yield from self._symbolicLinks.values()

	def Copy(self, parent: Nullable["Directory"] = None) -> "Directory":
		"""
		Copy the directory structure including all subelements and link it to the given parent.

		.. hint::

		   Statistics like aggregated directory size are copied too. |br|
		   There is no rescan or repeated aggregation needed.

		:param parent: Optional, the parent element of the copied directory.
		:returns:      A deep copy of the directory structure.
		"""
		dir = Directory(self._name, parent=parent)
		dir._size = self._size

		for subdir in self._subdirectories.values():
			subdir.Copy(dir)

		for file in self._files.values():
			file.Copy(dir)

		for link in self._symbolicLinks.values():
			link.Copy(dir)

		return dir

	def Collapse(self, func: Callable[["Directory"], bool]) -> bool:
		"""
		Collapse this directory's subtree where the given predicate accepts it.

		A directory is collapsed when it has no subdirectories left - or all of them collapsed - and the predicate
		accepts it. Collapsing discards the directory's elements, so only its aggregated numbers remain.

		:param func: Predicate deciding whether a directory may be collapsed.
		:returns:    ``True``, if this directory was collapsed.
		"""
		# if len(self._subdirectories) == 0 or all(subdir.Collapse(func) for subdir in self._subdirectories.values()):
		if len(self._subdirectories) == 0:
			if func(self):
				# print(f"collapse 1 {self.Path}")
				self._collapsed = True
				self._subdirectories.clear()
				self._files.clear()
				self._symbolicLinks.clear()

				return True
			else:
				return False

		# if all(subdir.Collapse(func) for subdir in self._subdirectories.values())
		collapsible = True
		for subdir in self._subdirectories.values():
			result = subdir.Collapse(func)
			collapsible = collapsible and result

		if collapsible:
			# print(f"collapse 2 {self.Path}")
			self._collapsed = True
			self._subdirectories.clear()
			self._files.clear()
			self._symbolicLinks.clear()

			return True
		else:
			return False

	def ToTree(self, format: Nullable[Callable[[Node], str]] = None) -> Node:
		"""
		Convert the directory to a :class:`~pyTooling.Tree.Node`.

		The node's :attr:`~pyTooling.Tree.Node.Value` field contains a reference to the directory. Additional data is
		attached to the node's key-value store:

		``kind``
		  The node's kind. See :class:`NodeKind`.
		``size``
		  The directory's aggregated size.

		:param format: Optional, a user defined formatting function for tree nodes.
		:returns:      A tree node representing this directory.
		"""
		if format is None:
			def format(node: Node) -> str:
				"""
				Nested function rendering a tree node as one line.

				:param node: The tree node to render.
				:returns:    The node's size in MiB, followed by its name.
				"""
				element = cast(Element[Any], node._value)     # the node was created with this element as its value
				return f"{node['size'] * 1e-6:7.1f} MiB {element.Name}"

		directoryNode: Node[Any, Any, Any, Any] = Node(
			value=self,
			keyValuePairs={
				"kind": NodeKind.File,
				"size": self._size
			},
			format=format
		)
		directoryNode.AddChildren(
			e.ToTree(format) for e in chain(self._subdirectories.values())  #, self._files.values(), self._symbolicLinks.values())
		)

		return directoryNode

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two Directory instances for equality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both directories and all its subelements are equal.
		:raises TypeError: If parameter ``other`` is not of type :class:`Directory`.
		"""
		if not isinstance(other, Directory):
			ex = TypeError("Parameter 'other' is not of type Directory.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		if not all(dir1 == dir2 for _, dir1, dir2 in zipdicts(self._subdirectories, other._subdirectories)):
			return False

		if not all(file1 == file2 for _, file1, file2 in zipdicts(self._files, other._files)):
			return False

		if not all(link1 == link2 for _, link1, link2 in zipdicts(self._symbolicLinks, other._symbolicLinks)):
			return False

		return True

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two Directory instances for inequality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both directories and all its subelements are unequal.
		:raises TypeError: If parameter ``other`` is not of type :class:`Directory`.
		"""
		return not self.__eq__(other)

	def __repr__(self) -> str:
		"""
		Return a detailed string representation of this directory.

		:returns: The directory's full path, prefixed by its kind.
		"""
		return f"Directory: {self.Path}"

	def __str__(self) -> str:
		"""
		Return a string representation of this filesystem element.

		:returns: The element's name, without any path.
		"""
		return self._name


@export
class Filename(Element[Directory]):
	"""
	Represents a filename in the filesystem, but not the file storage object (:class:`File`).

	.. hint::

	   Filename and file storage are represented by two classes, which allows multiple names (hard links) per file storage
	   object.
	"""
	_file: Nullable["File"]  #: The file this filename refers to; ``None`` until the filename is linked.

	def __init__(
		self,
		name:   str,
		file:   Nullable["File"] = None,
		parent: Nullable[Directory] = None
	) -> None:
		"""
		Initialize the filename with name, file (storage) object and parent reference.

		:param name:       Name of the file.
		:param file:       Optional, file (storage) object.
		:param parent:     Optional, parent reference.
		:raises TypeError: If parameter 'file' is not of type :class:`File`.
		"""
		super().__init__(name, None, parent)

		if file is None:
			self._file = None
		else:
			if not isinstance(file, File):
				ex = TypeError("Parameter 'file' is not of type 'File'.")
				ex.add_note(f"Got type '{getFullyQualifiedName(file)}'.")
				raise ex

			self._file = file
			file._parents.append(self)

		if parent is not None:
			parent._files[name] = self

			if parent._root is not None:
				self._root = parent._root

	@Element.Root.setter
	def Root(self, value: "Root") -> None:
		Element.Root.fset(self, value)

		if self._file is not None:
			self._file.Root = value

	@Element.Parent.setter
	def Parent(self, value: _ParentType) -> None:
		Element.Parent.fset(self, value)

		value._files[self._name] = self

		if isinstance(value, Root):
			self.Root = value

	@readonly
	def File(self) -> Nullable["File"]:
		"""
		Read-only property to access the file this filename is linked to (:attr:`_file`).

		:returns: The linked file, or ``None`` if the filename isn't linked yet.
		"""
		return self._file

	@readonly
	def Size(self) -> int:
		"""
		Read-only property to access the size of the linked file.

		:returns:                 Size of the linked file in bytes.
		:raises ToolingException: If the filename isn't linked to a file object.
		"""
		if self._file is None:
			raise ToolingException(f"Filename isn't linked to a File object.")

		return self._file._size

	@readonly
	def Path(self) -> Path:
		"""
		Read-only property to return the filename's absolute path.

		The path is computed from the parent directory's path and the filename.

		:returns:                 Absolute path of the file.
		:raises ToolingException: If the filename has no parent object.
		"""
		if self._parent is None:
			raise ToolingException(f"Filename has no parent object.")

		return self._parent.Path / self._name

	def __hash__(self) -> int:
		"""
		Compute a hash for this filesystem element based on its identity.

		Two elements with the same name in different directories are different elements, so the hash is derived from the
		object's identity and not from its name.

		:returns: Hash of this filesystem element.
		"""
		return hash(id(self))

	def Copy(self, parent: Directory) -> "Filename":
		"""
		Copy this filename into another filesystem statistics scope.

		The file object behind the filename is copied only once per scope: a filename referring to a file that was
		already copied - a hardlink - is connected to the existing copy.

		:param parent: Optional, the directory in the target scope the copy is registered at.
		:returns:      The copied filename.
		"""
		fileID = self._file._id

		if fileID in parent._root._ids:
			file = parent._root._ids[fileID]
		else:
			fileSize = self._file._size
			file = File(fileID, fileSize)

			parent._root._ids[fileID] = file

		return Filename(self._name, file, parent=parent)

	def ToTree(self) -> Node:
		"""
		Convert this filename to a node of a :mod:`pyTooling.Tree`.

		:returns: A tree node carrying this filename, its kind and its size.
		"""
		def format(node: Node) -> str:
			"""
			Nested function rendering a tree node as one line.

			:param node: The tree node to render.
			:returns:    The node's size in MiB, followed by its name.
			"""
			return f"{node['size'] * 1e-6:7.1f} MiB {node._value.Name}"

		fileNode: Node[Any, Any, Any, Any] = Node(
			value=self,
			keyValuePairs={
				"kind": NodeKind.File,
				"size": self._size
			},
			format=format
		)

		return fileNode

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two Filename instances for equality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both filenames are equal.
		:raises TypeError: If parameter ``other`` is not of type :class:`Filename`.
		"""
		if not isinstance(other, Filename):
			ex = TypeError("Parameter 'other' is not of type 'Filename'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._name == other._name and self.Size == other.Size

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two Filename instances for inequality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both filenames are unequal.
		:raises TypeError: If parameter ``other`` is not of type :class:`Filename`.
		"""
		if not isinstance(other, Filename):
			ex = TypeError("Parameter 'other' is not of type 'Filename'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._name != other._name or self.Size != other.Size

	def __repr__(self) -> str:
		"""
		Return a detailed string representation of this filename.

		:returns: The file's full path, prefixed by its kind.
		"""
		return f"File: {self.Path}"

	def __str__(self) -> str:
		"""
		Return a string representation of this filesystem element.

		:returns: The element's name, without any path.
		"""
		return self._name


@export
class SymbolicLink(Element[Directory]):
	"""
	A symbolic link in the filesystem statistics scope.

	After the scan, the link is resolved: it is either connected to an element of the scanned tree, broken (the target
	doesn't exist), or out of range (the target lies outside the scanned tree).
	"""
	_target:       Path            #: Path the symbolic link points to.
	_isConnected:  bool            #: ``True``, if the link target was resolved to an element of the scanned tree.
	_isBroken:     Nullable[bool]  #: ``True``, if the link target doesn't exist; ``None`` until resolved.
	_isOutOfRange: Nullable[bool]  #: ``True``, if the link target lies outside the scanned tree; ``None`` until resolved.

	def __init__(
		self,
		name:   str,
		target: Path,
		parent: Nullable[Directory]
	) -> None:
		"""
		Initialize a symbolic link, which is registered at its parent directory.

		The link is unresolved at first: :meth:`Root.ResolveSymbolicLinks` decides afterwards whether it is connected,
		broken or out of range.

		:param name:        Name of the symbolic link.
		:param target:      Path the symbolic link points to.
		:param parent:      Optional, parent directory of the symbolic link.
		:raises ValueError: If parameter 'target' is None.
		:raises TypeError:  If parameter 'target' is not of type :class:`~pathlib.Path`.
		"""
		super().__init__(name, None, parent)

		if target is None:
			raise ValueError(f"Parameter 'target' is None.")
		elif not isinstance(target, Path):
			ex = TypeError("Parameter 'target' is not of type 'Path'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(target)}'.")
			raise ex

		self._target =       target
		self._isConnected =  False
		self._isBroken =     None
		self._isOutOfRange = None

		if parent is not None:
			parent._symbolicLinks[name] = self

			if parent._root is not None:
				self._root = parent._root

	@readonly
	def Path(self) -> Path:
		"""
		Read-only property to return the symbolic link's path.

		The path is computed from the parent directory's path and the link's name.

		:returns: Path of the symbolic link.
		"""
		return self._parent.Path / self._name

	@readonly
	def Target(self) -> Path:
		"""
		Read-only property to access the path this symbolic link points to (:attr:`_target`).

		:returns: Target path of the symbolic link.
		"""
		return self._target

	@readonly
	def IsConnected(self) -> bool:
		"""
		Check if the symbolic link was resolved to an element within the scanned filesystem (:attr:`_isConnected`).

		:returns: ``True``, if the link's target was found and connected.
		"""
		return self._isConnected

	@readonly
	def IsBroken(self) -> Nullable[bool]:
		"""
		Check if the symbolic link points to a non-existing target (:attr:`_isBroken`).

		:returns: ``True``, if the target doesn't exist. ``None``, if the link wasn't resolved yet.
		"""
		return self._isBroken

	@readonly
	def IsOutOfRange(self) -> Nullable[bool]:
		"""
		Check if the symbolic link points outside the scanned filesystem (:attr:`_isOutOfRange`).

		:returns: ``True``, if the target lies outside the scanned root. ``None``, if the link wasn't resolved yet.
		"""
		return self._isOutOfRange

	def __hash__(self) -> int:
		"""
		Compute a hash for this filesystem element based on its identity.

		Two elements with the same name in different directories are different elements, so the hash is derived from the
		object's identity and not from its name.

		:returns: Hash of this filesystem element.
		"""
		return hash(id(self))

	def Copy(self, parent: Directory) -> "SymbolicLink":
		"""
		Copy this symbolic link into another filesystem statistics scope.

		:param parent: Optional, the directory in the target scope the copy is registered at.
		:returns:      The copied symbolic link, unresolved.
		"""
		return SymbolicLink(self._name, self._target, parent=parent)

	def ToTree(self) -> Node:
		"""
		Convert this symbolic link to a node of a :mod:`pyTooling.Tree`.

		:returns: A tree node carrying this symbolic link, its kind and its size.
		"""
		def format(node: Node) -> str:
			"""
			Nested function rendering a tree node as one line.

			:param node: The tree node to render.
			:returns:    The node's size in MiB, followed by its name.
			"""
			return f"{node['size'] * 1e-6:7.1f} MiB {node._value.Name}"

		symbolicLinkNode: Node[Any, Any, Any, Any] = Node(
			value=self,
			keyValuePairs={
				"kind": NodeKind.SymbolicLink,
				"size": self._size
			},
			format=format
		)

		return symbolicLinkNode

	def __eq__(self, other: Any) -> bool:
		"""
		Compare two SymbolicLink instances for equality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both symbolic links are equal.
		:raises TypeError: If parameter ``other`` is not of type :class:`SymbolicLink`.
		"""
		if not isinstance(other, SymbolicLink):
			ex = TypeError("Parameter 'other' is not of type 'SymbolicLink'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._name == other._name and self._target == other._target

	def __ne__(self, other: Any) -> bool:
		"""
		Compare two SymbolicLink instances for inequality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both symbolic links are unequal.
		:raises TypeError: If parameter ``other`` is not of type :class:`SymbolicLink`.
		"""
		if not isinstance(other, SymbolicLink):
			ex = TypeError("Parameter 'other' is not of type 'SymbolicLink'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._name != other._name or self._target != other._target

	def __repr__(self) -> str:
		"""
		Return a detailed string representation of this symbolic link.

		:returns: The link's full path and the path it points to.
		"""
		return f"SymLink: {self.Path} -> {self._target}"

	def __str__(self) -> str:
		"""
		Return a string representation of this filesystem element.

		:returns: The element's name, without any path.
		"""
		return self._name


@export
class Root(Directory):
	"""
	A **Root** represents the root-directory in the filesystem, which contains subdirectories, regular files and symbolic links.
	"""
	_ids:                      dict[int, "File"]   #: Dictionary of file identifier - file objects pairs found while scanning the directory structure.
	_brokenSymbolicLinks:      list[SymbolicLink]  #: Broken symbolic links (target doesn't exist).
	_unconnectedSymbolicLinks: list[SymbolicLink]  #: Symbolic links which couldn't be connected to their target (out of scope).

	def __init__(
		self,
		rootDirectory:         Path,
		collectSubdirectories: bool = True
	) -> None:
		"""
		Initialize a filesystem statistics scope for the given directory.

		Unless ``collectSubdirectories`` is disabled, the whole tree is scanned and its symbolic links are resolved right
		away, so the root is usable as soon as it exists.

		:param rootDirectory:         Directory to collect the statistics for.
		:param collectSubdirectories: Optional, if ``True``, scan the tree and resolve its symbolic links immediately.
		:raises ValueError:           If parameter 'rootDirectory' is None.
		:raises TypeError:            If parameter 'rootDirectory' is not of type :class:`~pathlib.Path`.
		:raises ToolingException:     If the given path doesn't exist.
		"""
		if rootDirectory is None:
			raise ValueError(f"Parameter 'rootDirectory' is None.")
		elif not isinstance(rootDirectory, Path):
			raise TypeError(f"Parameter 'rootDirectory' is not of type 'Path'.")
		elif not rootDirectory.exists():
			raise ToolingException(f"Path '{rootDirectory}' doesn't exist.") from FileNotFoundError(rootDirectory)

		self._ids =                      {}
		self._brokenSymbolicLinks =      []
		self._unconnectedSymbolicLinks = []

		super().__init__(rootDirectory.name)
		self._root = self
		self._path = rootDirectory

		if collectSubdirectories:
			self.CollectSubdirectories()
			self.ResolveSymbolicLinks()

	@readonly
	def Path(self) -> Path:
		"""
		Read-only property to access the path of the filesystem statistics root.

		:returns: Path to the root of the filesystem statistics root directory.
		"""
		return self._path

	@readonly
	def BrokenSymbolicLinks(self) -> list[SymbolicLink]:
		"""
		Read-only property to access all symbolic links with a non-existing target (:attr:`_brokenSymbolicLinks`).

		:returns: List of broken symbolic links.
		"""
		return self._brokenSymbolicLinks

	@readonly
	def UnconnectedSymbolicLinks(self) -> list[SymbolicLink]:
		"""
		Read-only property to access all symbolic links that couldn't be resolved within the scanned filesystem (:attr:`_unconnectedSymbolicLinks`).

		:returns: List of unconnected symbolic links.
		"""
		return self._unconnectedSymbolicLinks

	@readonly
	def TotalHardLinkCount(self) -> int:
		"""
		Read-only property to return the accumulated number of hardlinks to multiply-linked files.

		Every file storage object referenced by more than one directory entry contributes its number of
		directory entries.

		:returns: Sum of directory entries over all hardlinked files.
		"""
		return sum(l for f in self._ids.values() if (l := len(f._parents)) > 1)

	@readonly
	def TotalHardLinkCount2(self) -> int:
		"""
		Read-only property to return the number of file storage objects that are hardlinked.

		In contrast to :attr:`TotalHardLinkCount`, every hardlinked file contributes ``1``, regardless of how
		many directory entries reference it.

		:returns: Number of files referenced by more than one directory entry.
		"""
		return sum(1 for f in self._ids.values() if len(f._parents) > 1)

	@readonly
	def TotalHardLinkCount3(self) -> int:
		"""
		Read-only property to return the number of file storage objects that are **not** hardlinked.

		.. attention::

		   Despite the name, this counts files referenced by exactly *one* directory entry.

		:returns: Number of files referenced by exactly one directory entry.
		"""
		return sum(1 for f in self._ids.values() if len(f._parents) == 1)

	@readonly
	def Size2(self) -> int:
		"""
		Read-only property to return the accumulated size of all hardlinked files, counted once each.

		:returns: Sum of sizes over all files referenced by more than one directory entry.
		"""
		return sum(f._size for f in self._ids.values() if len(f._parents) > 1)

	@readonly
	def Size3(self) -> int:
		"""
		Read-only property to return the accumulated size of all hardlinked files, counted per directory entry.

		In contrast to :attr:`Size2`, a file's size is multiplied by the number of directory entries
		referencing it, so it reflects the size a filesystem without hardlink support would need.

		:returns: Sum of sizes over all hardlinked files, weighted by their number of directory entries.
		"""
		return sum(f._size * len(f._parents) for f in self._ids.values() if len(f._parents) > 1)

	@readonly
	def TotalUniqueFileCount(self) -> int:
		"""
		Read-only property to return the number of distinct file storage objects, counting hardlinks to the same content once.

		:returns: Number of unique files.
		"""
		return len(self._ids)

	def RegisterBrokenSymbolicLink(self, symLink: SymbolicLink) -> None:
		"""
		Mark a symbolic link as broken and collect it at the root.

		:param symLink: The symbolic link whose target doesn't exist.
		"""
		symLink._isBroken = True
		self._brokenSymbolicLinks.append(symLink)

	def RegisterUnconnectedSymbolicLink(self, symLink: SymbolicLink) -> None:
		"""
		Mark a symbolic link as out of range and collect it at the root.

		:param symLink: The symbolic link whose target lies outside the scanned tree.
		"""
		symLink._isOutOfRange = True
		self._unconnectedSymbolicLinks.append(symLink)

	def Copy(self) -> "Root":
		"""
		Copy the directory structure including all subelements and link it to the given parent.

		The duration for the deep copy process is provided in :attr:`ScanDuration`

		.. hint::

		   Statistics like aggregated directory size are copied too. |br|
		   There is no rescan or repeated aggregation needed.

		:returns: A deep copy of the directory structure.
		"""
		with Stopwatch() as sw:
			root = Root(self._path, False)
			root._size = self._size

			for subdir in self._subdirectories.values():
				subdir.Copy(root)

			for file in self._files.values():
				file.Copy(root)

			for link in self._symbolicLinks.values():
				link.Copy(root)

		root._scanDuration = sw.Duration
		root._aggregateDuration = 0.0

		return root

	def __repr__(self) -> str:
		"""
		Return a detailed string representation of this filesystem root.

		:returns: The root's path and the number of directories, regular files and symbolic links below it.
		"""
		return f"Root: {self.Path} (dirs: {self.TotalSubdirectoryCount}, files: {self.TotalRegularFileCount}, symlinks: {self.TotalSymbolicLinkCount})"

	def __str__(self) -> str:
		"""
		Return a string representation of this filesystem element.

		:returns: The element's name, without any path.
		"""
		return self._name


@export
class File(Base):
	"""
	A **File** represents a file storage object in the filesystem, which is accessible by one or more :class:`Filename` objects.

	Each file has an internal id, which is associated to a unique ID within the host's filesystem.
	"""
	_id:      int             #: Unique (host internal) file object ID)
	_parents: list[Filename]  #: List of reverse references to :class:`Filename` objects.

	def __init__(
		self,
		id:     int,
		size:   int,
		parent: Nullable[Filename] = None
	) -> None:
		"""
		Initialize the File storage object with an ID, size and parent reference.

		:param id:          Unique ID of the file object.
		:param size:        Optional, size of the file object.
		:param parent:      Optional, parent reference.
		:raises ValueError: If parameter 'id' is None.
		:raises TypeError:  If parameter 'parent' is not of type :class:`Filename`.
		"""
		if id is None:
			raise ValueError(f"Parameter 'id' is None.")
		elif not isinstance(id, int):
			ex = TypeError("Parameter 'id' is not of type 'int'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(id)}'.")
			raise ex

		self._id = id

		if parent is None:
			super().__init__(size, None)
			self._parents = []
		elif isinstance(parent, Filename):
			super().__init__(size, parent._root)
			self._parents = [parent]
			parent._file = self
		else:
			ex = TypeError("Parameter 'parent' is not of type 'Filename'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(parent)}'.")
			raise ex

	@readonly
	def ID(self) -> int:
		"""
		Read-only property to access the file object's unique identifier.

		:returns: Unique file object identifier.
		"""
		return self._id

	@readonly
	def Parents(self) -> list[Filename]:
		"""
		Read-only property to access the list of filenames using the same file storage object.

		.. hint::

		   This allows to check if a file object has multiple filenames a.k.a hardlinks.

		:returns: List of filenames for the file storage object.
		"""
		return self._parents

	def AddParent(self, filename: Filename) -> None:
		"""
		Add another parent reference to a :class:`Filename`.

		:param filename:          Reference to a filename object.
		:raises ValueError:       If parameter 'filename' is None.
		:raises TypeError:        If parameter 'filename' is not of type :class:`Filename`.
		:raises ToolingException: If the filename already references another file object.
		"""
		if filename is None:
			raise ValueError(f"Parameter 'filename' is None.")
		elif not isinstance(filename, Filename):
			ex = TypeError("Parameter 'filename' is not of type 'Filename'.")
			ex.add_note(f"Got type '{getFullyQualifiedName(filename)}'.")
			raise ex
		elif filename._file is not None:
			raise ToolingException(f"Filename is already referencing an other file object ({filename._file._id}).")

		self._parents.append(filename)
		filename._file = self

		if filename._root is not None:
			self._root = filename._root

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
# Copyright 2025-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
"""
from os                    import scandir, readlink
from sys                   import version_info

from enum                  import Enum
from itertools             import chain
from pathlib               import Path
from typing                import Optional as Nullable, Dict, Generic, Generator, TypeVar, List, Any, Callable, Union

try:
	from pyTooling.Decorators  import readonly, export
	from pyTooling.Exceptions  import ToolingException
	from pyTooling.MetaClasses import ExtendedType, abstractmethod
	from pyTooling.Common      import getFullyQualifiedName, zipdicts
	from pyTooling.Stopwatch   import Stopwatch
	from pyTooling.Tree        import Node
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.Filesystem] Could not import from 'pyTooling.*'!")

	try:
		from pyTooling.Decorators  import readonly, export
		from pyTooling.Exceptions  import ToolingException
		from pyTooling.MetaClasses import ExtendedType, abstractmethod
		from pyTooling.Common      import getFullyQualifiedName
		from pyTooling.Stopwatch   import Stopwatch
		from pyTooling.Tree        import Node
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.Filesystem] Could not import directly!")
		raise ex


_ParentType = TypeVar("_ParentType", bound="Element")


@export
class FilesystemException(ToolingException):
	"""Base-exception of all exceptions raised by :mod:`pyTooling.Filesystem`."""


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
	_root:   Nullable["Root"]  #: Reference to the root of the filesystem statistics scope.
	_size:   Nullable[int]     #: Actual or aggregated size of the filesystem element.

	def __init__(
		self,
		root: Nullable["Root"],
		size: Nullable[int],
	) -> None:
		self._root = root
		self._size = size

	@property
	def Root(self) -> Nullable["Root"]:
		"""
		Property to access the root of the filesystem statistics scope.

		:returns: Root of the filesystem statistics scope.
		"""
		return self._root

	@Root.setter
	def Root(self, value: "Root") -> None:
		self._root = value

	@readonly
	def Size(self) -> int:
		"""
		Read-only property to access the elements size in Bytes.

		:returns:                    Size in Bytes.
		:raises FilesystemException: If size is not computed, yet.
		"""
		if self._size is None:
			raise FilesystemException("Size is not computed, yet.")

		return self._size

	# @abstractmethod
	def ToTree(self) -> Node:
		pass


@export
class Element(Base, Generic[_ParentType]):
	_name:        str                   #: Name of the filesystem element.
	_parent:      _ParentType           #: Reference to the filesystem element's parent (:class:`Directory`)
	_linkSources: List["SymbolicLink"]  #: A list of symbolic links pointing to this filesystem element.

	def __init__(
		self,
		name: str,
		size: Nullable[int] = None,
		parent: Nullable[_ParentType] = None
	) -> None:
		root = None # if parent is None else parent._root

		super().__init__(root, size)

		self._parent = parent
		self._name = name
		self._linkSources = []

	@property
	def Parent(self) -> _ParentType:
		return self._parent

	@Parent.setter
	def Parent(self, value: _ParentType) -> None:
		self._parent = value

		if value._root is not None:
			self._root = value._root

	@readonly
	def Name(self) -> str:
		"""
		Read-only property to access the elements name.

		:returns: Element name.
		"""
		return self._name

	@readonly
	def Path(self) -> Path:
		raise NotImplemented(f"Property 'Path' is abstract.")

	def AddLinkSources(self, source: "SymbolicLink") -> None:
		self._linkSources.append(source)


@export
class Directory(Element["Directory"]):
	"""
	A **directory** represents a directory in the filesystem contains subdirectories, regular files and symbolic links.

	While scanning for subelements, the directory is populated with elements. Every file object added, gets registered in
	the filesystems :class:`Root` for deduplication. In case a file identifier already exists, the found filename will
	reference the same file objects. In turn, the file objects has then references to multiple filenames (parents). This
	allows to detect :term:`hardlinks <hardlink>`.

	The time needed for scanning the directory and its subelements is provided via :data:`ScanDuration`.

	After scnaning the directory for subelements, certain directory properties get aggregated. The time needed for
	aggregation is provided via :data:`AggregateDuration`.
	"""

	_path:              Nullable[Path]             #: Cached :class:`~pathlib.Path` object of this directory.
	_subdirectories:    Dict[str, "Directory"]     #: Dictionary containing name-:class:`Directory` pairs.
	_files:             Dict[str, "Filename"]      #: Dictionary containing name-:class:`Filename` pairs.
	_symbolicLinks:     Dict[str, "SymbolicLink"]  #: Dictionary containing name-:class:`SymbolicLink` pairs.
	_collapsed:         bool                       #: True, if this directory was collapsed. It contains no subelements.
	_scanDuration:      Nullable[float]            #: Duration for scanning the directory and all its subelements.
	_aggregateDuration: Nullable[float]            #: Duration for aggregating all subelements.

	def __init__(
		self,
		name:                  str,
		collectSubdirectories: bool = False,
		parent:                Nullable["Directory"] = None
	) -> None:
		super().__init__(name, None, parent)

		self._path = None
		self._subdirectories = {}
		self._files = {}
		self._symbolicLinks = {}
		self._collapsed = False
		self._scanDuration = None
		self._aggregateDuration = None

		if parent is not None:
			parent._subdirectories[name] = self

			if parent._root is not None:
				self._root = parent._root

		if collectSubdirectories:
			self._collectSubdirectories()

	def _collectSubdirectories(self) -> None:
		with Stopwatch() as sw1:
			self._scanSubdirectories()

		with Stopwatch() as sw2:
			self._aggregateSizes()

		self._scanDuration = sw1.Duration
		self._aggregateDuration = sw2.Duration

	def _scanSubdirectories(self) -> None:
		try:
			items = scandir(directoryPath := self.Path)
		except PermissionError as ex:
			return

		for dirEntry in items:
			if dirEntry.is_dir(follow_symlinks=False):
				subdirectory = Directory(dirEntry.name, collectSubdirectories=True, parent=self)
			elif dirEntry.is_file(follow_symlinks=False):
				id = dirEntry.inode()
				if id in self._root._ids:
					file = self._root._ids[id]

					hardLink = Filename(dirEntry.name, file=file, parent=self)
				else:
					s = dirEntry.stat(follow_symlinks=False)
					filename = Filename(dirEntry.name, parent=self)
					file = File(id, s.st_size, parent=filename)

					self._root._ids[id] = file
			elif dirEntry.is_symlink():
				target = Path(readlink(directoryPath / dirEntry.name))
				symlink = SymbolicLink(dirEntry.name, target, parent=self)
			else:
				raise FilesystemException(f"Unknown directory element.")

	def _connectSymbolicLinks(self) -> None:
		for dir in self._subdirectories.values():
			dir._connectSymbolicLinks()

		for link in self._symbolicLinks.values():
			if link._target.is_absolute():
				pass
			else:
				target = self
				for elem in link._target.parts:
					if elem == ".":
						continue
					elif elem == "..":
						target = target._parent
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
						pass

				target.AddLinkSources(link)

	def _aggregateSizes(self) -> None:
		self._size = (
			sum(dir._size for dir in self._subdirectories.values()) +
			sum(file._file._size for file in self._files.values())
		)

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
		Read-only property to access the number of elements in a directory.

		:returns: Number of files plus subdirectories.
		"""
		return len(self._subdirectories) + len(self._files) + len(self._symbolicLinks)

	@readonly
	def FileCount(self) -> int:
		"""
		Read-only property to access the number of files in a directory.

		.. hint::

		   Files include regular files and symbolic links.

		:returns: Number of files.
		"""
		return len(self._files) + len(self._symbolicLinks)

	@readonly
	def RegularFileCount(self) -> int:
		"""
		Read-only property to access the number of regular files in a directory.

		:returns: Number of regular files.
		"""
		return len(self._files)

	@readonly
	def SymbolicLinkCount(self) -> int:
		"""
		Read-only property to access the number of symbolic links in a directory.

		:returns: Number of symbolic links.
		"""
		return len(self._symbolicLinks)

	@readonly
	def SubdirectoryCount(self) -> int:
		"""
		Read-only property to access the number of subdirectories in a directory.

		:returns: Number of subdirectories.
		"""
		return len(self._subdirectories)

	@readonly
	def TotalFileCount(self) -> int:
		"""
		Read-only property to access the total number of files in all child hierarchy levels (recursively).

		.. hint::

		   Files include regular files and symbolic links.

		:returns: Total number of files.
		"""
		return sum(d.TotalFileCount for d in self._subdirectories.values()) + len(self._files) + len(self._symbolicLinks)

	@readonly
	def TotalRegularFileCount(self) -> int:
		"""
		Read-only property to access the total number of regular files in all child hierarchy levels (recursively).

		:returns: Total number of regular files.
		"""
		return sum(d.TotalRegularFileCount for d in self._subdirectories.values()) + len(self._files)

	@readonly
	def TotalSymbolicLinkCount(self) -> int:
		"""
		Read-only property to access the total number of symbolic links in all child hierarchy levels (recursively).

		:returns: Total number of symbolic links.
		"""
		return sum(d.TotalSymbolicLinkCount for d in self._subdirectories.values()) + len(self._symbolicLinks)

	@readonly
	def TotalSubdirectoryCount(self) -> int:
		"""
		Read-only property to access the total number of subdirectories in all child hierarchy levels (recursively).

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
	def Files(self) -> Generator[Union["Filename", "SymbolicLink"], None, None]:
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

	def Copy(self, parent: Nullable["Directory"] = None) -> "Directory":
		"""
		Copy the directory structure including all subelements and link it to the given parent.

		.. hint::

		   Statistics like aggregated directory size are copied too. |br|
		   There is no rescan or repeated aggregation needed.

		:param parent: The parent element of the copied directory.
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

		:param format: A user defined formatting function for tree nodes.
		:returns:      A tree node representing this directory.
		"""
		if format is None:
			def format(node: Node) -> str:
				return f"{node['size'] * 1e-6:7.1f} MiB {node._value.Name}"

		directoryNode = Node(
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

	def __eq__(self, other) -> bool:
		"""
		Compare two Directory instances for equality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both directories and all its subelements are equal.
		:raises TypeError: If parameter ``other`` is not of type :class:`Directory`.
		"""
		if not isinstance(other, Directory):
			ex = TypeError("Parameter 'other' is not of type Directory.")
			if version_info >= (3, 11):  # pragma: no cover
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
		return f"Directory: {self.Path}"

	def __str__(self) -> str:
		return self._name


@export
class Filename(Element[Directory]):
	_file: Nullable["File"]

	def __init__(
		self,
		name: str,
		file: Nullable["File"] = None,
		parent: Nullable[Directory] = None
	) -> None:
		super().__init__(name, None, parent)

		if file is None:
			self._file = None
		else:
			self._file = file
			file._parents.append(self)

		if parent is not None:
			parent._files[name] = self

			if parent._root is not None:
				self._root = parent._root

	@Element.Root.setter
	def Root(self, value: "Root") -> None:
		self._root = value

		if self._file is not None:
			self._file._root = value

	@Element.Parent.setter
	def Parent(self, value: _ParentType) -> None:
		Element.Parent.fset(self, value)

		value._files[self._name] = self

		if isinstance(value, Root):
			self.Root = value

	@readonly
	def File(self) -> Nullable["File"]:
		return self._file

	@readonly
	def Size(self) -> int:
		if self._file is None:
			raise ToolingException(f"Filename isn't linked to a File object.")

		return self._file._size

	@readonly
	def Path(self) -> Path:
		if self._parent is None:
			raise ToolingException(f"Filename has no parent object.")

		return self._parent.Path / self._name

	def Copy(self, parent: Directory) -> "Filename":
		fileID = self._file._id

		if fileID in parent._root._ids:
			file = parent._root._ids[fileID]
		else:
			fileSize = self._file._size
			file = File(fileID, fileSize)

			parent._root._ids[fileID] = file

		return Filename(self._name, file, parent=parent)

	def ToTree(self) -> Node:
		def format(node: Node) -> str:
			return f"{node['size'] * 1e-6:7.1f} MiB {node._value.Name}"

		fileNode = Node(
			value=self,
			keyValuePairs={
				"kind": NodeKind.File,
				"size": self._size
			},
			format=format
		)

		return fileNode

	def __eq__(self, other) -> bool:
		"""
		Compare two Filename instances for equality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both filenames are equal.
		:raises TypeError: If parameter ``other`` is not of type :class:`Filename`.
		"""
		if not isinstance(other, Filename):
			ex = TypeError("Parameter 'other' is not of type Filename.")
			if version_info >= (3, 11):  # pragma: no cover
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
			ex = TypeError("Parameter 'other' is not of type Filename.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._name != other._name or self.Size != other.Size

	def __repr__(self) -> str:
		return f"File: {self.Path}"

	def __str__(self) -> str:
		return self._name


@export
class SymbolicLink(Element[Directory]):
	_target: Path

	def __init__(
		self,
		name:   str,
		target: Path,
		parent: Nullable[Directory]
	) -> None:
		super().__init__(name, None, parent)

		self._target = target

		if parent is not None:
			parent._symbolicLinks[name] = self

			if parent._root is not None:
				self._root = parent._root

	@readonly
	def Path(self) -> Path:
		return self._parent.Path / self._name

	@readonly
	def Target(self) -> Path:
		return self._target

	def Copy(self, parent: Directory) -> "SymbolicLink":
		return SymbolicLink(self._name, self._target, parent=parent)

	def ToTree(self) -> Node:
		def format(node: Node) -> str:
			return f"{node['size'] * 1e-6:7.1f} MiB {node._value.Name}"

		symbolicLinkNode = Node(
			value=self,
			keyValuePairs={
				"kind": NodeKind.SymbolicLink,
				"size": self._size
			},
			format=format
		)

		return symbolicLinkNode

	def __eq__(self, other) -> bool:
		"""
		Compare two SymbolicLink instances for equality.

		:param other:      Parameter to compare against.
		:returns:          ``True``, if both symbolic links are equal.
		:raises TypeError: If parameter ``other`` is not of type :class:`SymbolicLink`.
		"""
		if not isinstance(other, SymbolicLink):
			ex = TypeError("Parameter 'other' is not of type SymbolicLink.")
			if version_info >= (3, 11):  # pragma: no cover
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
			ex = TypeError("Parameter 'other' is not of type SymbolicLink.")
			if version_info >= (3, 11):  # pragma: no cover
				ex.add_note(f"Got type '{getFullyQualifiedName(other)}'.")
			raise ex

		return self._name != other._name or self._target != other._target

	def __repr__(self) -> str:
		return f"SymLink: {self.Path} -> {self._target}"

	def __str__(self) -> str:
		return self._name


@export
class Root(Directory):
	_ids:  Dict[int, "File"]   #: Dictionary of file identifier - file objects pairs found while scanning the directory structure.

	def __init__(
		self,
		rootDirectory:         Path,
		collectSubdirectories: bool = True
	) -> None:
		if rootDirectory is None:
			raise ValueError(f"Parameter 'path' is None.")
		elif not isinstance(rootDirectory, Path):
			raise TypeError(f"Parameter 'path' is not of type Path.")
		elif not rootDirectory.exists():
			raise ToolingException(f"Path '{rootDirectory}' doesn't exist.") from FileNotFoundError(rootDirectory)

		self._ids = {}

		super().__init__(rootDirectory.name)
		self._root = self
		self._path = rootDirectory

		if collectSubdirectories:
			self._collectSubdirectories()
			self._connectSymbolicLinks()

	@readonly
	def TotalHardLinkCount(self) -> int:
		return sum(l for f in self._ids.values() if (l := len(f._parents)) > 1)

	@readonly
	def TotalHardLinkCount2(self) -> int:
		return sum(1 for f in self._ids.values() if len(f._parents) > 1)

	@readonly
	def TotalHardLinkCount3(self) -> int:
		return sum(1 for f in self._ids.values() if len(f._parents) == 1)

	@readonly
	def Size2(self) -> int:
		return sum(f._size for f in self._ids.values() if len(f._parents) > 1)

	@readonly
	def Size3(self) -> int:
		return sum(f._size * len(f._parents) for f in self._ids.values() if len(f._parents) > 1)

	@readonly
	def TotalUniqueFileCount(self) -> int:
		return len(self._ids)

	@readonly
	def Path(self) -> Path:
		"""
		Read-only property to access the path of the filesystem statistics root.

		:returns: Path to the root of the filesystem statistics root directory.
		"""
		return self._path

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
		return f"Root: {self.Path} (dirs: {self.TotalSubdirectoryCount}, files: {self.TotalRegularFileCount}, symlinks: {self.TotalSymbolicLinkCount})"

	def __str__(self) -> str:
		return self._name


@export
class File(Base):
	_id: int
	_parents: List[Filename]

	def __init__(
		self,
		id: int,
		size: int,
		parent: Nullable[Filename] = None
	) -> None:
		self._id = id
		if parent is None:
			super().__init__(None, size)
			self._parents = []
		else:
			super().__init__(parent._root, size)
			self._parents = [parent]
			parent._file = self

	@readonly
	def ID(self) -> int:
		"""
		Read-only property to access the file object's unique identifier.

		:returns: Unique file object identifier.
		"""
		return self._id

	@readonly
	def Parents(self) -> List[Filename]:
		"""
		Read-only property to access the list of filenames using the file object.

		.. hint::

		   This allows to check if a file object has multiple filenames a.k.a hardlinks.

		:returns: List of filenames for the file object.
		"""
		return self._parents

	def AddParent(self, file: Filename) -> None:
		if file._file is not None:
			raise ToolingException(f"Filename is already referencing an other file object ({file._file._id}).")

		self._parents.append(file)
		file._file = self

		if file._root is not None:
			self._root = file._root

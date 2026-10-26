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
Unit tests for :mod:`pyTooling.Filesystem`: scanning a directory tree and the statistics collected for it.
"""
from datetime              import timedelta
from gc                    import collect as gc_collect, disable as gc_disable, enable as gc_enable, \
                                  get_objects as gc_get_objects, isenabled as gc_isenabled
from os                    import DirEntry, link, scandir, symlink
from pathlib               import Path
from sys                   import platform as sys_platform
from tempfile              import TemporaryDirectory
from typing                import Iterator, get_args, get_type_hints
from unittest.mock         import patch

from pytest                import mark

from pyTooling.Exceptions  import ToolingException
from pyTooling.Common      import count
from pyTooling.Filesystem  import Base, Root, Directory, Element, Filename, File, SymbolicLink, FilesystemError, \
                                  NodeKind, PermissionWarning
from pyTooling.MetaClasses import AbstractClassError
from pyTooling.Platform    import CurrentPlatform
from pyTooling.Warning     import WarningCollector
from pyTooling.Testing     import Testcase

if sys_platform != "win32":
	from os                  import geteuid


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(Testcase):
	def test_Root(self) -> None:
		rootPath = Path("tests/data")
		root = Root(rootPath, collectSubdirectories=False)

		self.assertIs(root, root.Root)
		self.assertIsNone(root.Parent)
		self.assertEqual("data", root.Name)
		self.assertEqual(0, count(root.Subdirectories))
		self.assertEqual(0, count(root.Files))
		self.assertEqual(0, root.TotalSubdirectoryCount)
		self.assertEqual(0, root.TotalFileCount)

	def test_Directory(self) -> None:
		directory = Directory("directory")

		self.assertIsNone(directory.Root)
		self.assertIsNone(directory.Parent)
		self.assertEqual("directory", directory.Name)
		self.assertEqual(0, count(directory.Subdirectories))
		self.assertEqual(0, count(directory.Files))
		self.assertEqual(0, directory.TotalSubdirectoryCount)
		self.assertEqual(0, directory.TotalFileCount)

	def test_Directory_Root(self) -> None:
		rootPath = Path("tests/data")
		root = Root(rootPath, collectSubdirectories=False)
		directory = Directory("directory", parent=root)

		self.assertIs(root, root.Root)
		self.assertIsNone(root.Parent)
		self.assertEqual("data", root.Name)
		self.assertEqual(1, count(root.Subdirectories))
		self.assertEqual(0, count(root.Files))
		self.assertEqual(1, root.TotalSubdirectoryCount)
		self.assertEqual(0, root.TotalFileCount)

		self.assertIs(root, directory.Root)
		self.assertIs(root, directory.Parent)
		self.assertEqual("directory", directory.Name)
		self.assertEqual(0, count(directory.Subdirectories))
		self.assertEqual(0, count(directory.Files))
		self.assertEqual(0, directory.TotalSubdirectoryCount)
		self.assertEqual(0, directory.TotalFileCount)

	def test_Filename(self) -> None:
		filename = Filename("filename")

		self.assertIsNone(filename.Root)
		self.assertIsNone(filename.Parent)
		self.assertEqual("filename", filename.Name)
		self.assertIsNone(filename.File)
		with self.assertRaises(ToolingException):
			_ = filename.Size

	def test_Filename_Directory(self) -> None:
		directory = Directory("directory")
		filename = Filename("filename", parent=directory)

		self.assertIsNone(directory.Root)
		self.assertIsNone(directory.Parent)
		self.assertEqual("directory", directory.Name)
		self.assertEqual(0, count(directory.Subdirectories))
		self.assertEqual(1, count(directory.Files))
		self.assertEqual(1, count(directory.IterateFiles()))
		self.assertEqual(0, directory.TotalSubdirectoryCount)
		self.assertEqual(1, directory.TotalFileCount)

		self.assertIsNone(filename.Root)
		self.assertIs(directory, filename.Parent)
		self.assertEqual("filename", filename.Name)
		self.assertIsNone(filename.File)
		with self.assertRaises(ToolingException):
			_ = filename.Size

	def test_File(self) -> None:
		file = File(1, 1024)

		self.assertIsNone(file.Root)
		self.assertEqual(0, len(file.Parents))
		self.assertEqual(1, file.ID)
		self.assertEqual(1024, file.Size)

	def test_File_Filename(self) -> None:
		filename = Filename("filename")
		file = File(2, 2048, parent=filename)

		self.assertIsNone(filename.Root)
		self.assertIsNone(filename.Parent)
		self.assertEqual(2048, filename.Size)

		self.assertIsNone(file.Root)
		self.assertEqual(1, len(file.Parents))
		self.assertListEqual(file.Parents, [filename])
		self.assertEqual(2, file.ID)
		self.assertEqual(2048, file.Size)

	def test_TopDown(self) -> None:
		rootPath = Path("tests/data")
		root = Root(rootPath, collectSubdirectories=False)
		directory = Directory("directory", parent=root)
		filename = Filename("filename", parent=directory)
		file = File(2, 2048, parent=filename)

		self.assertIs(root, root.Root)
		self.assertIsNone(root.Parent)
		self.assertEqual("data", root.Name)
		self.assertEqual(1, count(root.Subdirectories))
		self.assertEqual(0, count(root.Files))
		self.assertEqual(1, count(root.IterateFiles()))
		self.assertEqual(1, root.TotalSubdirectoryCount)
		self.assertEqual(1, root.TotalFileCount)

		self.assertIs(root, directory.Root)
		self.assertIs(root, directory.Parent)
		self.assertEqual("directory", directory.Name)
		self.assertEqual(0, count(directory.Subdirectories))
		self.assertEqual(1, count(directory.Files))
		self.assertEqual(1, count(directory.IterateFiles()))
		self.assertEqual(0, directory.TotalSubdirectoryCount)
		self.assertEqual(1, directory.TotalFileCount)

		self.assertIs(root, filename.Root)
		self.assertIs(directory, filename.Parent)
		self.assertEqual(2048, filename.Size)

		self.assertIs(root, file.Root)
		self.assertEqual(1, len(file.Parents))
		self.assertListEqual(file.Parents, [filename])
		self.assertEqual(2, file.ID)
		self.assertEqual(2048, file.Size)

	def test_BottomUp_ChainUp(self) -> None:
		rootPath = Path("tests/data")

		file = File(2, 2048)
		filename = Filename("filename")
		directory = Directory("directory")
		root = Root(rootPath, collectSubdirectories=False)

		file.AddParent(filename)
		filename.Parent = directory
		directory.Parent = root

		self.assertIs(root, root.Root)
		self.assertIsNone(root.Parent)
		self.assertEqual("data", root.Name)
		self.assertEqual(1, count(root.Subdirectories))
		self.assertEqual(0, count(root.Files))
		self.assertEqual(1, count(root.IterateFiles()))
		self.assertEqual(1, root.TotalSubdirectoryCount)
		self.assertEqual(1, root.TotalFileCount)

		self.assertIs(root, directory.Root)
		self.assertIs(root, directory.Parent)
		self.assertEqual("directory", directory.Name)
		self.assertEqual(0, count(directory.Subdirectories))
		self.assertEqual(1, count(directory.Files))
		self.assertEqual(1, count(directory.IterateFiles()))
		self.assertEqual(0, directory.TotalSubdirectoryCount)
		self.assertEqual(1, directory.TotalFileCount)

		self.assertIs(root, filename.Root)
		self.assertIs(directory, filename.Parent)
		self.assertEqual(2048, filename.Size)

		self.assertIs(root, file.Root)
		self.assertEqual(1, len(file.Parents))
		self.assertListEqual(file.Parents, [filename])
		self.assertEqual(2, file.ID)
		self.assertEqual(2048, file.Size)

	def test_BottomUp_ChainDown(self) -> None:
		rootPath = Path("tests/data")

		file = File(2, 2048)
		filename = Filename("filename")
		directory = Directory("directory")
		root = Root(rootPath, collectSubdirectories=False)

		directory.Parent = root
		filename.Parent = directory
		file.AddParent(filename)

		self.assertIs(root, root.Root)
		self.assertIsNone(root.Parent)
		self.assertEqual("data", root.Name)
		self.assertEqual(1, count(root.Subdirectories))
		self.assertEqual(0, count(root.Files))
		self.assertEqual(1, count(root.IterateFiles()))
		self.assertEqual(1, root.TotalSubdirectoryCount)
		self.assertEqual(1, root.TotalFileCount)

		self.assertIs(root, directory.Root)
		self.assertIs(root, directory.Parent)
		self.assertEqual("directory", directory.Name)
		self.assertEqual(0, count(directory.Subdirectories))
		self.assertEqual(1, count(directory.Files))
		self.assertEqual(1, count(directory.IterateFiles()))
		self.assertEqual(0, directory.TotalSubdirectoryCount)
		self.assertEqual(1, directory.TotalFileCount)

		self.assertIs(root, filename.Root)
		self.assertIs(directory, filename.Parent)
		self.assertEqual(2048, filename.Size)

		self.assertIs(root, file.Root)
		self.assertEqual(1, len(file.Parents))
		self.assertListEqual(file.Parents, [filename])
		self.assertEqual(2, file.ID)
		self.assertEqual(2048, file.Size)


class AbstractMembers(Testcase):
	"""``Base`` declares ``ToTree`` and ``Element`` declares ``Path`` abstract; every concrete class implements them."""

	def test_Base(self) -> None:
		"""A ``Base`` can't be instantiated, as its ``ToTree`` is abstract."""
		with self.assertRaises(AbstractClassError) as context:
			Base(None, None)

		self.assertIn("ToTree", str(context.exception))

	def test_BaseWithoutToTree(self) -> None:
		"""A derived class without its own ``ToTree`` stays abstract."""
		class Incomplete(Base):
			pass

		with self.assertRaises(AbstractClassError):
			Incomplete(None, None)

	def test_Element(self) -> None:
		"""An ``Element`` can't be instantiated, as its ``Path`` is abstract."""
		with self.assertRaises(AbstractClassError) as context:
			Element("element")

		self.assertIn("Path", str(context.exception))

	def test_ElementWithoutPath(self) -> None:
		"""A derived element without its own ``Path`` stays abstract."""
		class Incomplete(Element[Directory]):
			pass

		with self.assertRaises(AbstractClassError):
			Incomplete("incomplete")

	def test_ConcreteElements(self) -> None:
		"""Directory, file name and the root implement ``Path``; ``File`` is no ``Element``."""
		root = Root(Path("tests/data"), collectSubdirectories=False)
		directory = Directory("dir", parent=root)
		filename = Filename("file.txt", parent=directory)

		self.assertEqual(Path("tests/data"), root.Path)
		self.assertEqual(Path("tests/data/dir"), directory.Path)
		self.assertEqual(Path("tests/data/dir/file.txt"), filename.Path)
		self.assertIsInstance(File(1, 1024), File)


class Conversion(Testcase):
	"""Converting filesystem elements to nodes of a :mod:`pyTooling.Tree`."""

	def test_FileToTree(self) -> None:
		"""A file storage object becomes a node with its kind and size, referencing the file object."""
		file = File(7, 2_000_000)
		node = file.ToTree()

		self.assertIs(file, node.Value)
		self.assertEqual(NodeKind.File, node["kind"])
		self.assertEqual(2_000_000, node["size"])
		self.assertEqual("    2.0 MiB file object 7\n", node.Render())

	def test_HardLinkedFileToTree(self) -> None:
		"""Every call creates a new node; the filenames of a hard-linked file stay reachable through the value."""
		file = File(3, 1024)
		file.AddParent(Filename("a.txt"))
		file.AddParent(Filename("b.txt"))

		first = file.ToTree()
		second = file.ToTree()

		self.assertIsNot(first, second)
		self.assertEqual(2, len(first.Value.Parents))

	def test_DirectoryToTree(self) -> None:
		"""A directory node is of kind directory; its subdirectories, files and symbolic links are its children."""
		root = Root(Path("tests/data"), collectSubdirectories=False)
		directory = Directory("dir", parent=root)
		subdirectory = Directory("sub", parent=directory)
		filename = Filename("file.txt", parent=directory)
		File(5, 1024, parent=filename)
		link = SymbolicLink("link", Path("file.txt"), parent=directory)

		node = directory.ToTree(format=lambda n: n.Value.Name)

		self.assertIs(directory, node.Value)
		self.assertEqual(NodeKind.Directory, node["kind"])
		self.assertEqual([subdirectory, filename, link], [child.Value for child in node.GetChildren()])
		self.assertEqual(
			[NodeKind.Directory, NodeKind.File, NodeKind.SymbolicLink],
			[child["kind"] for child in node.GetChildren()]
		)

	def test_DirectoryToTreeFormat(self) -> None:
		"""A user defined format renders every node of the directory's tree."""
		root = Root(Path("tests/data"), collectSubdirectories=False)
		directory = Directory("dir", parent=root)
		Filename("file.txt", parent=directory)
		SymbolicLink("link", Path("file.txt"), parent=directory)

		lines = directory.ToTree(format=lambda n: f"<{n.Value.Name}>").Render().splitlines()

		self.assertEqual(3, len(lines))
		self.assertTrue(all(line.endswith(">") for line in lines))
		self.assertIn("<dir>", lines[0])


class Scanning(Testcase):
	"""Scanning a real directory tree - the path that reads the filesystem and fills the inode table."""

	def test_ScanRealDirectory(self) -> None:
		"""A scan walks the directory and counts what it found."""
		root = Root(Path("tests/data"), collectSubdirectories=True)

		self.assertGreater(root.TotalFileCount, 0)
		self.assertGreater(root.TotalSubdirectoryCount, 0)
		self.assertEqual(root.TotalFileCount, root.TotalRegularFileCount + root.TotalSymbolicLinkCount)

	def test_ScanNeedsARoot(self) -> None:
		"""A directory that is not attached to a root has no inode table to fill."""
		directory = Directory("detached")

		with self.assertRaises(FilesystemError) as context:
			directory.ScanSubdirectories()

		self.assertIn("not attached to a filesystem root", str(context.exception))



	def test_Durations(self) -> None:
		"""Scanning and aggregating measure their durations as timedeltas."""
		root = Root(Path("tests/data"))

		self.assertIsInstance(root.ScanDuration, timedelta)
		self.assertIsInstance(root.AggregateDuration, timedelta)


def _createTree(directory: Path) -> None:
	"""
	Create a directory tree: files in two levels, a hard link and - except on Windows - a symbolic link.

	:param directory: The (empty) directory to fill.
	"""
	(directory / "a" / "b").mkdir(parents=True)
	(directory / "x.txt").write_text("x")
	(directory / "a" / "y.txt").write_text("yy")
	(directory / "a" / "b" / "z.txt").write_text("zzz")
	link(directory / "x.txt", directory / "a" / "h.txt")
	if sys_platform != "win32":
		symlink("y.txt", directory / "a" / "l")


def _filesystemObjectCount() -> int:
	"""
	Count the filesystem elements the garbage collector tracks.

	:returns: The number of tracked :class:`~pyTooling.Filesystem.Base` instances.
	"""
	return sum(1 for obj in gc_get_objects() if isinstance(obj, Base))


class Deletion(Testcase):
	"""Deleting a root disconnects all elements of the scanned tree from each other."""

	_directory: Path

	def setUp(self) -> None:
		super().setUp()

		self._directory = Path(self.enterContext(TemporaryDirectory()))
		_createTree(self._directory)

	def test_Delete(self) -> None:
		root = Root(self._directory)
		directories = list(root.IterateDirectories())
		elements = list(root.IterateFiles())
		filenames = [element for element in elements if isinstance(element, Filename)]
		files = [filename.File for filename in filenames]

		root.Delete()

		self.assertIsNone(root.Root)
		self.assertEqual(0, root.Count)
		self.assertEqual(0, root.TotalFileCount)
		self.assertEqual(0, root.TotalUniqueFileCount)
		for directory in directories:
			self.assertIsNone(directory.Root)
			self.assertIsNone(directory.Parent)
			self.assertEqual(0, directory.Count)

		for element in elements:
			self.assertIsNone(element.Root)
			self.assertIsNone(element.Parent)
			self.assertEqual(0, len(element.LinkSources))

		for filename in filenames:
			self.assertIsNone(filename.File)

		for file in files:
			self.assertIsNone(file.Root)
			self.assertEqual(0, len(file.Parents))

	def test_Delete_Collapsed(self) -> None:
		"""The elements a collapse removed from their directories are disconnected too."""
		root = Root(self._directory)
		subdirectory = next(next(root.Subdirectories).Subdirectories)
		filename = next(subdirectory.RegularFiles)
		file = filename.File

		root.Collapse(lambda directory: True)
		root.Delete()

		self.assertIsNone(subdirectory.Parent)
		self.assertIsNone(filename.Parent)
		self.assertIsNone(filename.File)
		self.assertEqual(0, len(file.Parents))

	@mark.skipif(CurrentPlatform.IsPyPy, reason="PyPy doesn't count references.")
	def test_ReferenceCounting(self) -> None:
		"""Without the cyclic garbage collector, a deleted tree is freed as soon as the last reference is dropped."""
		gc_collect()
		wasEnabled = gc_isenabled()
		gc_disable()
		try:
			before = _filesystemObjectCount()
			root = Root(self._directory)
			self.assertGreater(_filesystemObjectCount(), before)

			root.Delete()
			del root

			self.assertEqual(before, _filesystemObjectCount())
		finally:
			if wasEnabled:
				gc_enable()

	@mark.skipif(CurrentPlatform.IsPyPy, reason="PyPy doesn't count references.")
	def test_ReferenceCounting_WithoutDelete(self) -> None:
		"""Without the cyclic garbage collector, a tree, which wasn't deleted, stays in memory: it has reference cycles."""
		gc_collect()
		wasEnabled = gc_isenabled()
		gc_disable()
		try:
			before = _filesystemObjectCount()
			root = Root(self._directory)
			del root

			self.assertGreater(_filesystemObjectCount(), before)
		finally:
			if wasEnabled:
				gc_enable()
			gc_collect()


class PermissionDenied(Testcase):
	"""A directory that can't be read is skipped and reported as a :exc:`~pyTooling.Filesystem.PermissionWarning`."""

	_root:   Path
	_locked: Path

	def setUp(self) -> None:
		super().setUp()

		self._root =   Path(self.enterContext(TemporaryDirectory()))
		self._locked = self._root / "locked"

		(self._root / "readable").mkdir()
		(self._root / "readable" / "file.txt").write_text("content")
		self._locked.mkdir()

		if sys_platform == "win32" or geteuid() == 0:
			locked = self._locked

			def denyLocked(path: Path) -> Iterator[DirEntry]:
				if path == locked:
					raise PermissionError(13, "Permission denied", str(path))

				return scandir(path)

			self.enterContext(patch("pyTooling.Filesystem.scandir", denyLocked))
		else:
			self._locked.chmod(0o000)
			self.addCleanup(self._locked.chmod, 0o700)

	def test_Scan_Uncollected(self) -> None:
		"""Without a collector, the warning is dropped and the scan continues."""
		root = Root(self._root)

		self.assertEqual(2, root.TotalSubdirectoryCount)
		self.assertEqual(1, root.TotalFileCount)

	def test_Scan_Collected(self) -> None:
		"""With a collector, the warning carries the directory that couldn't be read, and the scan continues."""
		with WarningCollector() as warnings:
			root = Root(self._root)

		self.assertEqual(1, len(warnings))
		warning = warnings[0]
		self.assertIsInstance(warning, PermissionWarning)
		self.assertEqual(f"Directory '{self._locked}' can't be read.", str(warning))
		self.assertIsInstance(warning.Directory, Directory)
		self.assertEqual(self._locked, warning.Directory.Path)
		self.assertIsInstance(warning.__cause__, PermissionError)
		self.assertEqual(2, root.TotalSubdirectoryCount)
		self.assertEqual(1, root.TotalFileCount)

	def test_MessageOnly(self) -> None:
		with self.assertRaises(TypeError) as context:
			_ = PermissionWarning("Directory can't be read.")

		self.assertIn("'directory'", str(context.exception))


@mark.skipif(sys_platform == "win32", reason="Creating a symbolic link needs a privilege on Windows.")
class SymbolicLinkResolution(Testcase):
	"""A relative link target is followed through other links, as the operating system resolves it."""

	_root: Path

	def setUp(self) -> None:
		super().setUp()

		self._root = Path(self.enterContext(TemporaryDirectory())) / "root"
		(self._root / "dir" / "inner").mkdir(parents=True)
		(self._root / "dir" / "f.txt").write_text("f")
		(self._root / "file.txt").write_text("file")

	def _Link(self, root: Root, name: str) -> SymbolicLink:
		return next(link for link in root.SymbolicLinks if link.Name == name)

	def _Directory(self, root: Root, name: str) -> Directory:
		return next(directory for directory in root.Subdirectories if directory.Name == name)

	def test_Chain(self) -> None:
		"""A link to a link is connected to that link, which is connected to its own target."""
		symlink("dir", self._root / "b")
		symlink("b", self._root / "a")
		root = Root(self._root)

		self.assertTrue(self._Link(root, "a").IsConnected)
		self.assertIn(self._Link(root, "a"), self._Link(root, "b").LinkSources)
		self.assertIn(self._Link(root, "b"), self._Directory(root, "dir").LinkSources)

	def test_ThroughLink(self) -> None:
		"""A link in the middle of the target's path is replaced by its own target."""
		symlink("dir", self._root / "dirlink")
		symlink("dirlink/f.txt", self._root / "a")
		root = Root(self._root)
		file = next(file for file in self._Directory(root, "dir").RegularFiles if file.Name == "f.txt")

		self.assertTrue(self._Link(root, "a").IsConnected)
		self.assertIn(self._Link(root, "a"), file.LinkSources)
		self.assertEqual([], root.BrokenSymbolicLinks)

	def test_ThroughLink_Parent(self) -> None:
		"""A '..' after a followed link leaves the link's target, not the link's own directory."""
		symlink("dir/inner", self._root / "innerlink")
		symlink("innerlink/../f.txt", self._root / "a")
		root = Root(self._root)
		file = next(file for file in self._Directory(root, "dir").RegularFiles if file.Name == "f.txt")

		self.assertIn(self._Link(root, "a"), file.LinkSources)

	def test_ThroughFile(self) -> None:
		"""A regular file in the middle of the target's path makes the link broken."""
		symlink("file.txt/x", self._root / "a")
		root = Root(self._root)

		self.assertTrue(self._Link(root, "a").IsBroken)
		self.assertFalse(self._Link(root, "a").IsConnected)
		self.assertEqual([self._Link(root, "a")], root.BrokenSymbolicLinks)

	def test_Cycle(self) -> None:
		"""A path through a cycle of links is broken; the link closing the cycle is connected to the other link."""
		symlink("b/x", self._root / "a")
		symlink("a", self._root / "b")
		root = Root(self._root)

		self.assertTrue(self._Link(root, "a").IsBroken)
		self.assertEqual([self._Link(root, "a")], root.BrokenSymbolicLinks)
		self.assertIn(self._Link(root, "b"), self._Link(root, "a").LinkSources)

	def test_Dangling(self) -> None:
		"""A target nothing in the tree is named like is broken."""
		symlink("missing", self._root / "a")
		root = Root(self._root)

		self.assertTrue(self._Link(root, "a").IsBroken)
		self.assertEqual([self._Link(root, "a")], root.BrokenSymbolicLinks)

	def test_OutsideRoot(self) -> None:
		"""A target above the root is outside the scanned tree."""
		symlink("../outside", self._root / "a")
		root = Root(self._root)

		self.assertTrue(self._Link(root, "a").IsOutOfRange)
		self.assertEqual([self._Link(root, "a")], root.UnconnectedSymbolicLinks)

	def test_ThroughAbsoluteLink(self) -> None:
		"""A path through a link with an absolute target can't be followed inside the tree."""
		symlink(self._root / "dir", self._root / "absolute")
		symlink("absolute/f.txt", self._root / "a")
		root = Root(self._root)

		self.assertTrue(self._Link(root, "a").IsOutOfRange)
		self.assertEqual([self._Link(root, "a")], root.UnconnectedSymbolicLinks)


class TypeHints(Testcase):
	def test_PropertyNamedLikeAClass(self) -> None:
		"""A field's annotation names the class, although the class body has a property of that name."""
		import pyTooling.Filesystem

		self.assertIs(Root, get_args(get_type_hints(Base, vars(pyTooling.Filesystem))["_root"])[0])
		self.assertIs(Path, get_args(get_type_hints(Directory, vars(pyTooling.Filesystem))["_path"])[0])
		self.assertIs(File, get_args(get_type_hints(Filename, vars(pyTooling.Filesystem))["_file"])[0])
		self.assertIs(Path, get_type_hints(SymbolicLink, vars(pyTooling.Filesystem))["_target"])

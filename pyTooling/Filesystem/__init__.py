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
"""An object-oriented file system abstraction."""
from os import listdir, stat, lstat
from stat import S_ISDIR, S_ISREG, S_ISLNK

from enum import Enum
from itertools import chain
from pathlib import Path
from typing import Optional as Nullable, Dict, Generic, Generator, TypeVar

from pyTooling.Decorators import readonly
from pyTooling.MetaClasses import abstractmethod
from pyTooling.Stopwatch import Stopwatch
from pyTooling.Tree import Node


_ParentType = TypeVar("_ParentType", bound="Element")


class NodeKind(Enum):
	Directory = 0
	File = 1
	SymbolicLink = 2
	HardLink = 3


class Element(Generic[_ParentType]):
	_root:   "Root"
	_parent: _ParentType
	_path:   Path
	_size:   Nullable[int]

	def __init__(self, path: Path, size: Nullable[int], parent: Nullable[_ParentType] = None) -> None:
		# if not path.exists():
		# 	raise FileNotFoundError(path)

		if parent is None:
			self._root = self
		else:
			self._root = parent._root

		self._parent = parent
		self._path = path
		self._size = size

	@readonly
	def Root(self) -> "Root":
		return self._root

	@readonly
	def Parent(self) -> _ParentType:
		return self._parent

	@readonly
	def Name(self) -> str:
		return self._path.name

	@readonly
	def Path(self) -> Path:
		return self._path

	@readonly
	def Size(self) -> int:
		if self._size is None:
			raise Exception(f"Directory not counted.")
		return self._size

	@abstractmethod
	def ToTree(self) -> Node:
		pass


class Directory(Element["Directory"]):
	_subdirectories: Dict[str, "Directory"]
	_files:          Dict[str, "File"]
	_symbolicLinks:  Dict[str, "SymbolicLink"]
	_scanDuration:   Nullable[float]

	_hardlinks:      int

	def __init__(
		self,
		path: Path,
		scanSubdirectories: bool = False,
		parent: Nullable["Directory"] = None
	) -> None:
		super().__init__(path, None, parent)

		self._subdirectories = {}
		self._files = {}
		self._hardlinks = 0

		if scanSubdirectories:
			with Stopwatch() as sw:
				self._scan()

			self._scanDuration = sw.Duration

			with Stopwatch() as sw:
				self._aggregate()

			self._aggregateDuration = sw.Duration
		else:
			self._scanDuration = None
			self._aggregateDuration = None

	def _scan(self) -> None:
		for name in listdir(self._path):
			s = lstat(self._path / name)
			mode = s.st_mode
			if S_ISDIR(mode):
				self._subdirectories[name] = Directory(self._path / name, scanSubdirectories=True, parent=self)
			elif S_ISLNK(mode):
				print(f"SymLink: {name}")
			elif S_ISREG(mode):
				id = s.st_ino
				if id in self._root._ids:
					self._hardlinks += 1
					# print(f"HardLink: {name}")
				else:
					file = File(self._path / name, id, s.st_size, parent=self)
					self._files[name] = file
					self._root._ids[id] = file
			else:
				print(f"Unknown file type")

	def _aggregate(self) -> None:
		self._size = (
			sum(dir._size for dir in self._subdirectories.values()) +
			sum(file._size for file in self._files.values())
		)

	@readonly
	def Count(self) -> int:
		return len(self._files) + len(self._subdirectories)

	@readonly
	def FileCount(self) -> int:
		return len(self._files)

	@readonly
	def SubdirectoryCount(self) -> int:
		return len(self._subdirectories)

	@readonly
	def TotalFileCount(self) -> int:
		return len(self._files) + sum(d.TotalFileCount for d in self._subdirectories.values())

	@readonly
	def TotalSubdirectoryCount(self) -> int:
		return 1 + sum(d.TotalSubdirectoryCount for d in self._subdirectories.values())

	@readonly
	def TotalHardLinkCount(self) -> int:
		return sum(d.TotalHardLinkCount for d in self._subdirectories.values()) + self._hardlinks

	@readonly
	def Subdirectories(self) -> Generator["Directory", None, None]:
		return (d for d in self._subdirectories.values())

	def ToTree(self) -> Node:
		def format(node: Node) -> str:
			return f"{node["size"] * 1e-6:7.1f} MiB {node._value.Name}"

		directoryNode = Node(
			value=self,
			keyValuePairs={
				"kind": NodeKind.File,
				"size": self._size
			},
			format=format
		)
		directoryNode.AddChildren(
			d.ToTree() for d in chain(self._subdirectories.values(), self._files.values())
		)

		return directoryNode


class File(Element[Directory]):
	_id: int

	def __init__(self, path: Path, id: int, size: int, parent: Directory) -> None:
		super().__init__(path, size, parent)
		self._id = id

	def ToTree(self) -> Node:
		def format(node: Node) -> str:
			return f"{node["size"] * 1e-6:7.1f} MiB {node._value.Name}"

		fileNode = Node(
			value=self,
			keyValuePairs={
				"kind": NodeKind.File,
				"size": self._size
			},
			format=format
		)

		return fileNode


class SymbolicLink(Element[Directory]):
	def __init__(self, path: Path, parent: Directory) -> None:
		super().__init__(path, 0, parent)

	def ToTree(self) -> Node:
		def format(node: Node) -> str:
			return f"{node["size"] * 1e-6:7.1f} MiB {node._value.Name}"

		symbolicLinkNode = Node(
			value=self,
			keyValuePairs={
				"kind": NodeKind.SymbolicLink,
				"size": self._size
			},
			format=format
		)

		return symbolicLinkNode


class Root(Directory):
	_ids: Dict[int, File]

	def __init__(
		self,
		path: Path,
		scanSubdirectories: bool = False
	) -> None:
		self._ids = {}

		super().__init__(path, scanSubdirectories, None)

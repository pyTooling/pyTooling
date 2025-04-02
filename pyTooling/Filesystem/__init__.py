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
from os import listdir, stat
from stat import S_ISDIR

from enum import Enum
from itertools import chain
from pathlib import Path
from typing import Optional as Nullable, Dict, Generic, Generator, TypeVar

from pyTooling.Common import firstElement
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
	_parent: _ParentType
	_path:   Path
	_size:   Nullable[int]

	def __init__(self, path: Path, size: Nullable[int], parent: Nullable[_ParentType] = None) -> None:
		# if not path.exists():
		# 	raise FileNotFoundError(path)

		self._parent = parent
		self._path = path
		self._size = size

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
	_subdirectories: Dict[Path, "Directory"]
	_files:          Dict[Path, "File"]

	def __init__(
		self,
		path: Path,
		parent: Nullable["Directory"] = None
	) -> None:
		super().__init__(path, None, parent)

		self._subdirectories = {}
		self._files = {}

	def _scan(self) -> None:
		for name in listdir(self._path):
			s = stat(self._path / name)
			if S_ISDIR(s.st_mode):
				print(f"dir:  {name}")

				self._subdirectories[name] = Directory(name, self)
			else:
				print(f"file: {name}")

				self._files[name] = File(name, s.st_ino, s.st_size, self)


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
	def SubDirectoryCount(self) -> int:
		return len(self._subdirectories)

	@readonly
	def TotalFileCount(self) -> int:
		return len(self._files) + sum(d.TotalFileCount for d in self._subdirectories.values())

	@readonly
	def TotalSubDirectoryCount(self) -> int:
		return 1 + sum(d.TotalSubDirectoryCount for d in self._subdirectories.values())

	@readonly
	def SubDirectories(self) -> Generator["Directory", None, None]:
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

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
from pathlib               import Path
from typing                import Optional as Nullable, List, Set

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Filesystem  import Root, Element, Directory, Filename, SymbolicLink, FilesystemException
from pyTooling.Stopwatch   import Stopwatch


@export
class Layer(metaclass=ExtendedType):
	_parent:        Nullable["LayerCake"]     #: Reference to the parent layer cake.
	_previousLayer: Nullable["Layer"]         #: Reference to the previous layer.
	_nextLayer:     Nullable["Layer"]         #: Reference to the next layer

	_files:         List[Element[Directory]]  #: List of files in this layer.
	_size:          int                       #: Aggregated size of all contained files for this layer.

	def __init__(self, parent: Nullable["LayerCake"] = None, previousLayer: Nullable["Layer"] = None) -> None:
		if parent is not None:
			parent._layers.append(self)
		self._parent =        parent
		self._previousLayer = previousLayer
		self._nextLayer =     None
		if previousLayer is not None:
			previousLayer._nextLayer = self

		self._files = []
		self._size =  0

	@readonly
	def Parent(self) -> Nullable["LayerCake"]:
		return self._parent

	@readonly
	def PreviousLayer(self) -> Nullable["Layer"]:
		return self._previousLayer

	@readonly
	def NextLayer(self) -> Nullable["Layer"]:
		return self._nextLayer

	@readonly
	def Files(self) -> List[Element[Directory]]:
		return self._files

	@readonly
	def FileCount(self) -> int:
		return len(self._files)

	@readonly
	def Size(self) -> int:
		return self._size

	def AddFile(self, element: Element) -> Set[Filename]:
		usedFiles = set()
		if isinstance(element, Filename):
			for filename in element.File.Parents:
				self._files.append(filename)
				usedFiles.add(filename)
		elif isinstance(element, SymbolicLink):
			self._files.append(element)
			usedFiles.add(element)
		else:
			ex = TypeError(f"Parameter 'element' is not a filename nor symbolic link.")
			ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
			raise ex

		self._size += 0 if isinstance(element, SymbolicLink) else element.Size

		return usedFiles

	def WriteLayerFile(self, path: Path, relative: bool = True) -> None:
		rootDirectory = self._parent._root._path

		if relative:
			def format(file: Path) -> str:
				return f"{file.relative_to(rootDirectory).as_posix()}\n"
		else:
			def format(file: Path) -> str:
				return f"{file.as_posix()}\n"

		with path.open("w", encoding="utf-8") as f:
			for file in self._files:
				f.write(format(file.Path))


@export
class LayerCake(metaclass=ExtendedType):
	_root:            Nullable[Root]   #: Reference to the filesystem root.
	_layers:          List[Layer]      #: List of Docker image layers.
	_slicingDuration: Nullable[float]  #: Duration for sorting files by size and assigning them to Docker image layers.

	def __init__(self, root: Root) -> None:
		self._root =   root
		self._layers = []

	@readonly
	def Root(self) -> Root:
		return self._root

	@readonly
	def Layers(self) -> List[Layer]:
		return self._layers

	@readonly
	def LayerCount(self) -> int:
		return len(self._layers)

	@readonly
	def TotalFileCount(self) -> int:
		return sum(layer.FileCount for layer in self._layers)

	@readonly
	def SlicingDuration(self) -> float:
		"""
		Read-only property to access the time needed to slice the filesystem structure into docker layers.

		:returns:                    The slicing duration in seconds.
		:raises FilesystemException: If the filesystem was not sliced into layers.
		"""
		if self._slicingDuration is None:
			raise FilesystemException(f"Filesystem was not sliced, yet.")

		return self._slicingDuration

	def CreateDockerLayers(
		self,
		minLayerSize: int,
		maxLayerSize: int,
		layerSizeGradient: int
	) -> List[Layer]:
		self._layers.append(layer := Layer(self))

		collectedFiles = set()
		targetLayerSize = maxLayerSize

		def sizeOf(file: Element[Directory]) -> int:
			return 0 if isinstance(file, SymbolicLink) else file.Size

		with Stopwatch() as sw:
			iterator = iter(sorted(self._root.IterateFiles(), key=sizeOf, reverse=True))
			firstFile = next(iterator)
			collectedFiles |= layer.AddFile(firstFile)

			for file in iterator:
				if file in collectedFiles:
					continue

				if layer._size + sizeOf(file) <= targetLayerSize:
					collectedFiles |= layer.AddFile(file)
				else:
					self._layers.append(layer := Layer(self, layer))
					collectedFiles |= layer.AddFile(file)

					if (size := targetLayerSize - layerSizeGradient) >= minLayerSize:
						targetLayerSize = size

		self._slicingDuration = sw.Duration

	def WriteLayerFiles(self, directory: Path, relative: bool = True) -> None:
		for i, layer in enumerate(self._layers, start=1):
			layer.WriteLayerFile(directory / f"layer_{i}.files", relative)

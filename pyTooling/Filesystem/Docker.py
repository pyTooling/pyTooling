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
Slice a filesystem tree into Docker image layers.

A :class:`~pyTooling.Filesystem.Docker.LayerCake` distributes the files of a
:class:`~pyTooling.Filesystem.Root` over layers - largest file first, each layer filled up to a target size that
shrinks from layer to layer - and writes one file list per layer, ready to be turned into image layers.
"""
from __future__            import annotations

from pathlib               import Path
from typing                import Optional as Nullable

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Filesystem  import Root, Element, Directory, Filename, SymbolicLink, FilesystemError
from pyTooling.Stopwatch   import Stopwatch


@export
class Layer(metaclass=ExtendedType):
	"""
	One layer of a Docker image: the files assigned to it, and its neighboring layers in the layer cake.

	A layer knows its aggregated size, so the slicing algorithm can stop filling it when the target size is reached.
	"""
	_parent:        Nullable[LayerCake]       #: Reference to the parent layer cake.
	_previousLayer: Nullable[Layer]           #: Reference to the previous layer.
	_nextLayer:     Nullable[Layer]           #: Reference to the next layer

	_files:         list[Element[Directory]]  #: List of files in this layer.
	_size:          int                       #: Aggregated size of all contained files for this layer.

	def __init__(self, parent: Nullable[LayerCake] = None, previousLayer: Nullable[Layer] = None) -> None:
		"""
		Initialize an empty layer, which appends itself to the layer cake it belongs to.

		:param parent:        Optional, layer cake this layer is part of.
		:param previousLayer: Optional, layer below this one, which is linked to this layer in both directions.
		"""
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
	def Parent(self) -> Nullable[LayerCake]:
		"""
		Read-only property to access the layer cake this layer belongs to (:attr:`_parent`).

		:returns: The layer cake this layer belongs to, or ``None`` if the layer isn't part of one.
		"""
		return self._parent

	@readonly
	def PreviousLayer(self) -> Nullable[Layer]:
		"""
		Read-only property to access the layer below this one (:attr:`_previousLayer`).

		:returns: The previous layer, or ``None`` if this is the bottom layer.
		"""
		return self._previousLayer

	@readonly
	def NextLayer(self) -> Nullable[Layer]:
		"""
		Read-only property to access the layer above this one (:attr:`_nextLayer`).

		:returns: The next layer, or ``None`` if this is the top layer.
		"""
		return self._nextLayer

	@readonly
	def Files(self) -> list[Element[Directory]]:
		"""
		Read-only property to access the files contributed by this layer (:attr:`_files`).

		:returns: List of files in this layer.
		"""
		return self._files

	@readonly
	def FileCount(self) -> int:
		"""
		Read-only property to return the number of files in this layer.

		:returns: Number of files.
		"""
		return len(self._files)

	@readonly
	def Size(self) -> int:
		"""
		Read-only property to access the accumulated size of all files in this layer (:attr:`_size`).

		:returns: Size of the layer in bytes.
		"""
		return self._size

	def AddFile(self, element: Element) -> set[Filename]:
		"""
		Add a filename or symbolic link to this layer.

		For a filename, every other filename of the same file object is added too, because hardlinks have to end up in
		the same image layer.

		:param element:    The filename or symbolic link to add.
		:returns:          The set of elements that were added, so the caller can skip them.
		:raises TypeError: If parameter 'element' is neither a filename nor a symbolic link.
		"""
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
		"""
		Write the layer's files as one file list.

		:param path:     Path of the file list to write.
		:param relative: Optional, if ``True``, the paths are written relative to the filesystem root.
		"""
		rootDirectory = self._parent._root._path

		if relative:
			def format(file: Path) -> str:
				"""
				Nested function rendering a file's path relative to the filesystem root.

				:param file: The path to render.
				:returns:    The relative path in POSIX notation, terminated by a newline.
				"""
				return f"{file.relative_to(rootDirectory).as_posix()}\n"
		else:
			def format(file: Path) -> str:
				"""
				Nested function rendering a file's path as it is.

				:param file: The path to render.
				:returns:    The absolute path in POSIX notation, terminated by a newline.
				"""
				return f"{file.as_posix()}\n"

		with path.open("w", encoding="utf-8") as f:
			for file in self._files:
				f.write(format(file.Path))


@export
class LayerCake(metaclass=ExtendedType):
	"""
	A stack of Docker image layers computed from a filesystem tree.

	:meth:`CreateDockerLayers` distributes the files of a :class:`~pyTooling.Filesystem.Root` over layers - largest file
	first, each layer filled up to a target size that shrinks by a gradient from layer to layer - and collects the
	directories no layer covers.
	"""
	_root:             Nullable[Root]   #: Reference to the filesystem root.
	_layers:           list[Layer]      #: List of Docker image layers.
	_emptyDirectories: list[Directory]  #: List of empty directories (not covered by layers).
	_slicingDuration:  Nullable[float]  #: Duration for sorting files by size and assigning them to Docker image layers.

	def __init__(self, root: Root) -> None:
		"""
		Initialize an empty layer cake for the given filesystem tree.

		:param root: Root of the filesystem statistics scope to slice into layers.
		"""
		self._root =             root
		self._layers =           []
		self._emptyDirectories = []

	@readonly
	def Root(self) -> Root:
		"""
		Read-only property to access the root directory of the merged layers (:attr:`_root`).

		:returns: Root directory of the layer cake.
		"""
		return self._root

	@readonly
	def Layers(self) -> list[Layer]:
		"""
		Read-only property to access all layers, bottom-most first (:attr:`_layers`).

		:returns: List of layers.
		"""
		return self._layers

	@readonly
	def LayerCount(self) -> int:
		"""
		Read-only property to return the number of layers.

		:returns: Number of layers.
		"""
		return len(self._layers)

	@readonly
	def TotalFileCount(self) -> int:
		"""
		Read-only property to return the number of files across all layers.

		:returns: Sum of all layers' file counts.
		"""
		return sum(layer.FileCount for layer in self._layers)

	@readonly
	def EmptyDirectories(self) -> list[Directory]:
		"""
		Read-only property to access the directories that contain no files (:attr:`_emptyDirectories`).

		:returns: List of empty directories.
		"""
		return self._emptyDirectories

	@readonly
	def EmptyDirectoryCount(self) -> int:
		"""
		Read-only property to return the number of empty directories.

		:returns: Number of empty directories.
		"""
		return len(self._emptyDirectories)

	@readonly
	def SlicingDuration(self) -> float:
		"""
		Read-only property to access the time needed to slice the filesystem structure into docker layers.

		:returns:                    The slicing duration in seconds.
		:raises FilesystemError: If the filesystem was not sliced into layers.
		"""
		if self._slicingDuration is None:
			raise FilesystemError(f"Filesystem was not sliced, yet.")

		return self._slicingDuration

	def CreateDockerLayers(self, minLayerSize: int, maxLayerSize: int, layerSizeGradient: int) -> None:
		"""
		Distribute the filesystem's files over image layers and collect the directories no layer covers.

		The layers are filled largest file first. Each layer is filled up to a target size, which shrinks by
		``layerSizeGradient`` from layer to layer until ``minLayerSize`` is reached.

		:param minLayerSize:      Smallest target size a layer is filled to.
		:param maxLayerSize:      Target size of the first layer.
		:param layerSizeGradient: Amount the target size shrinks by from layer to layer.
		"""
		with Stopwatch() as sw:
			self._SliceFilesystemIntoLayers(minLayerSize, maxLayerSize, layerSizeGradient)
			self._CollectEmptDirectories()

		self._slicingDuration = sw.Duration

	def _SliceFilesystemIntoLayers(self, minLayerSize: int, maxLayerSize: int, layerSizeGradient: int) -> None:
		"""
		Distribute the filesystem's files over image layers, largest file first.

		:param minLayerSize:      Smallest target size a layer is filled to.
		:param maxLayerSize:      Target size of the first layer.
		:param layerSizeGradient: Amount the target size shrinks by from layer to layer.
		"""
		# greedy algorithm
		layer = Layer(self)

		def sizeOf(file: Element[Directory]) -> int:
			"""
			Nested function used as sort key.

			A symbolic link occupies no space of its own, so it is counted as zero and ends up last.

			:param file: The filesystem element to measure.
			:returns:    Size of the element in bytes.
			"""
			return 0 if isinstance(file, SymbolicLink) else file.Size

		collectedFiles = set()
		targetLayerSize = maxLayerSize
		iterator = iter(sorted(self._root.IterateFiles(), key=sizeOf, reverse=True))
		firstFile = next(iterator)
		collectedFiles |= layer.AddFile(firstFile)

		for file in iterator:
			if file in collectedFiles:
				continue

			if layer._size + sizeOf(file) <= targetLayerSize:
				collectedFiles |= layer.AddFile(file)
			else:
				layer = Layer(self, layer)
				collectedFiles |= layer.AddFile(file)

				if (size := targetLayerSize - layerSizeGradient) >= minLayerSize:
					targetLayerSize = size

	def _CollectEmptDirectories(self) -> None:
		"""
		Collect the directories that contain neither files nor subdirectories, so no layer covers them.
		"""
		for directory in self._root.IterateDirectories():
			if directory.SubdirectoryCount == 0 and directory.FileCount == 0:
				self._emptyDirectories.append(directory)

	def WriteLayerFiles(self, directory: Path, fileNamePattern: str = "layer_{layerID}.files", relative: bool = True) -> None:
		"""
		Write one file list per layer.

		:param directory:       Directory the file lists are written to.
		:param fileNamePattern: Optional, pattern of the file names, with ``{layerID}`` replaced by the layer's number.
		:param relative:        Optional, if ``True``, the paths are written relative to the filesystem root.
		"""
		for i, layer in enumerate(self._layers, start=1):
			layer.WriteLayerFile(directory / fileNamePattern.format(layerID=i), relative)

	def WriteEmptyDirectoryFile(self, directory: Path, fileNamePattern: str = "empty_directories.files", relative: bool = True) -> None:
		"""
		Write the empty directories as one file list, so an image build can recreate them.

		:param directory:       Directory the file list is written to.
		:param fileNamePattern: Optional, name of the file list to write.
		:param relative:        Optional, if ``True``, the paths are written relative to the filesystem root.
		"""
		rootDirectory = self._root._path

		if relative:
			def format(file: Path) -> str:
				"""
				Nested function rendering a directory's path relative to the filesystem root.

				:param file: The path to render.
				:returns:    The relative path in POSIX notation, terminated by a newline.
				"""
				return f"{file.relative_to(rootDirectory).as_posix()}\n"
		else:
			def format(file: Path) -> str:
				"""
				Nested function rendering a directory's path as it is.

				:param file: The path to render.
				:returns:    The absolute path in POSIX notation, terminated by a newline.
				"""
				return f"{file.as_posix()}\n"

		with (directory / fileNamePattern).open("w", encoding="utf-8") as f:
			for directory in self._emptyDirectories:
				f.write(format(directory.Path))

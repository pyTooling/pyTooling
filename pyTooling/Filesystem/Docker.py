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
from typing                import Optional as Nullable, List, Set

from pyTooling.Decorators  import readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Common      import getFullyQualifiedName
from pyTooling.Filesystem  import Root, Element, Directory, Filename, SymbolicLink


class Layer(metaclass=ExtendedType):
	_parent:        "LayerCake"
	_previousLayer: Nullable["Layer"]
	_nextLayer:     Nullable["Layer"]

	_elements:      List[Element[Directory]]
	_size:          int

	def __init__(self, parent: "LayerCake", previousLayer: Nullable["Layer"] = None) -> None:
		self._parent =        parent
		self._previousLayer = previousLayer
		self._nextLayer =     None
		if previousLayer is not None:
			previousLayer._nextLayer = self

		self._elements =      []
		self._size =          0

	@readonly
	def Parent(self) -> "LayerCake":
		return self._parent

	@readonly
	def PreviousLayer(self) -> "Layer":
		return self._previousLayer

	@readonly
	def NextLayer(self) -> "Layer":
		return self._nextLayer

	@readonly
	def Elements(self) -> List[Element[Directory]]:
		return self._elements

	@readonly
	def Size(self) -> int:
		return self._size

	def AddFile(self, element: Element) -> Set[Filename]:
		usedFiles = set()
		if isinstance(element, Filename):
			for filename in element.File.Parents:
				self._elements.append(filename)
				usedFiles.add(filename)
		elif isinstance(element, SymbolicLink):
			self._elements.append(element)
			usedFiles.add(element)
		else:
			ex = TypeError(f"Parameter 'element' is not a filename nor symbolic link.")
			ex.add_note(f"Got type '{getFullyQualifiedName(element)}'.")
			raise ex

		self._size += element.Size

		return usedFiles


class LayerCake(metaclass=ExtendedType):
	_root:   Nullable[Root]
	_layers: List[Layer]

	def __init__(self, root: Root) -> None:
		self._root =   root
		self._layers = []

	@readonly
	def Root(self) -> Root:
		return self._root

	@readonly
	def Layers(self) -> List[Layer]:
		return self._layers

	def CreateDockerLayers(self, minLayerSize: int, maxLayerSize: int, layerSizeGradient: int) -> List[Layer]:
		expectedLayerSize = maxLayerSize
		collectedFiles = set()
		self._layers.append(layer := Layer(self))
		for file in self._root.IterateFiles():
			if file in collectedFiles:
				continue

			if layer._size + file.Size <= expectedLayerSize:
				collectedFiles |= layer.AddFile(file)
			else:
				self._layers.append(layer := Layer(self, layer))

				if (size := expectedLayerSize - layerSizeGradient) >= minLayerSize:
					expectedLayerSize = size

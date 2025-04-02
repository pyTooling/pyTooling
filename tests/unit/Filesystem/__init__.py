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
"""Unit tests for pyTooling.Tree."""
from pathlib import Path

from typing   import Any, Optional as Nullable, List, Tuple, Dict
from unittest import TestCase

from pyTooling.Exceptions import ToolingException
from pyTooling.Common     import count
from pyTooling.Filesystem import Root, Directory, Filename, File


if __name__ == "__main__":  # pragma: no cover
	print("ERROR: you called a testcase declaration file as an executable module.")
	print("Use: 'python -m unittest <testcase module>'")
	exit(1)


class Instantiation(TestCase):
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
		self.assertEqual(1, root.TotalSubdirectoryCount)
		self.assertEqual(1, root.TotalFileCount)

		self.assertIs(root, directory.Root)
		self.assertIs(root, directory.Parent)
		self.assertEqual("directory", directory.Name)
		self.assertEqual(0, count(directory.Subdirectories))
		self.assertEqual(1, count(directory.Files))
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
		self.assertEqual(1, root.TotalSubdirectoryCount)
		self.assertEqual(1, root.TotalFileCount)

		self.assertIs(root, directory.Root)
		self.assertIs(root, directory.Parent)
		self.assertEqual("directory", directory.Name)
		self.assertEqual(0, count(directory.Subdirectories))
		self.assertEqual(1, count(directory.Files))
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
		self.assertEqual(1, root.TotalSubdirectoryCount)
		self.assertEqual(1, root.TotalFileCount)

		self.assertIs(root, directory.Root)
		self.assertIs(root, directory.Parent)
		self.assertEqual("directory", directory.Name)
		self.assertEqual(0, count(directory.Subdirectories))
		self.assertEqual(1, count(directory.Files))
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

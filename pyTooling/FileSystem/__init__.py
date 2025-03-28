from enum import Enum
from itertools import chain
from pathlib import Path
from re import compile as re_compile
from typing import Optional as Nullable, Dict, Generic, Generator, TypeVar

from pyTooling.Common import firstElement
from pyTooling.Decorators import readonly
from pyTooling.MetaClasses import abstractmethod
from pyTooling.Stopwatch import Stopwatch
from pyTooling.Tree import Node

_ParentType = TypeVar("_ParentType", bound="Element")

_DU_LINEPATTERN = re_compile(r"\s*(\d+)\s+.*?")
_IEC_SIZES = {
	"":  2 **  0,
	"K": 2 ** 10,
	"M": 2 ** 20,
	"G": 2 ** 30,
	"T": 2 ** 40,
}

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
		if not path.exists():
			raise FileNotFoundError(path)

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
		size: Nullable[int] = None,
		collectData: int = 0,
		parent: Nullable["Directory"] = None
	) -> None:
		super().__init__(path, size, parent)

		self._subdirectories = {}
		self._files = {}

		s = 0 if size is None else size
		print(".", end="")
		# print(f"Directory {path} ({s/_IEC_SIZES["M"]:.1f} >= {collectData/_IEC_SIZES["M"]:.1f} MiB)", end="")
		if size is None or size >= collectData:
			# print(" collect")
			self._collectData(collectData)
			self._aggregate()
		# else:
			# print(" skip")

	def _collectData(self, collectData: int) -> None:
		for element in self._path.iterdir():  # type: Path
			# print(f"  {element}", end="")
			if element.is_dir():
				du = DiskUsage()
				du[du.FlagBlockSize] = 1
				du[du.FlagSummary] = True
				# du[du.FlagHumanReadable] = True
				du[du.ArgPath] = element.as_posix()
				du.StartProcess()

				result = [l for l in du.GetLineReader()]
				match = _DU_LINEPATTERN.match(firstElement(result))
				if match is None:
					raise Exception(f"Unable to parse output from du: {firstElement(result)}")

				size = int(match[1].replace(",", ".")) # * _IEC_SIZES[match[3]]
				# print(f"  {size/_IEC_SIZES["M"]:.1f} MiB")
				directory = Directory(element, size, collectData=collectData, parent=self)
				self._subdirectories[element] = directory
			elif element.is_file():
				# print("  file")
				stat = element.stat()
				file = File(element, stat.st_size, self)
				self._files[element] = file

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
	def __init__(self, path: Path, size: int, parent: Directory) -> None:
		super().__init__(path, size, parent)

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

#
#
# def main(vivadoPath: Path, outputPath: Path) -> None:
# 	if not vivadoPath.exists():
# 		print(f"Vivado path '{vivadoPath}' doesn't exist.")
# 		return
#
# 	if not outputPath.exists() or not outputPath.is_dir() :
# 		print(f"Output path '{outputPath}' doesn't exist or is not a directory.")
# 		return
#
# 	maxItemSize =       1*2**30
# 	maxImageLayerSize = 3*2**30
#
# 	print(f"Collecting data (this may take several minutes) ...")
# 	with Stopwatch() as sw:
# 		root = Directory(vivadoPath, collectData=maxItemSize)
# 	print()
# 	print(f"Time:        {sw.Duration:.3f} s")
# 	print(f"Total files: {root.TotalFileCount}")
# 	print(f"Total dirs:  {root.TotalSubDirectoryCount}")
# 	# print(f"Root: {root.Size/_IEC_SIZES["M"]:.1f} MiB for {vivadoPath.as_posix()}")
# 	# for dir in root.SubDirectories:  # type: Directory
# 	# 	print(f"      {dir.Size/_IEC_SIZES["M"]:7.1f} MiB  {dir.Path}")
#
# 	with Stopwatch() as sw:
# 		tree: Node[None, Element[Directory], str, Any] = root.ToTree()
# 	print(f"Time:        {sw.Duration:.3f} s")
# 	# print(tree.Render())
#
# 	items: List[Element[Directory]] = []
# 	totalSize = 0
# 	for node in tree.IterateLeafs():
# 		items.append(node.Value)
# 		totalSize += node.Value.Size
#
# 	print(f"Total size:  {totalSize/_IEC_SIZES["M"]:.1f} MiB ({len(items)})")
#
# 	with Stopwatch() as sw:
# 		sortedList = sorted(items, key=lambda e: e.Size, reverse=True)
# 	print(f"Sort Time:   {sw.Duration:.3f} s")
#
# 	index = 0
# 	imageLayers = {index: []}
# 	imageLayerSize = 0
# 	# print(f"Bucket {index} max={maxImageLayerSize/_IEC_SIZES["M"]:.1f} MiB:")
# 	for item in sortedList:
# 		if imageLayerSize + item.Size > maxImageLayerSize:
# 			# print(f"  Bucket size: {imageLayerSize/_IEC_SIZES["M"]:.1f} MiB")
# 			imageLayers[str(index)] = imageLayerSize
#
# 			maxImageLayerSize -= 2**26
#
# 			imageLayerSize = 0
# 			index += 1
# 			imageLayers[index] = []
# 			# print(f"Bucket {index} max={maxImageLayerSize/_IEC_SIZES["M"]:.1f} MiB:")
#
# 		imageLayers[index].append(item)
# 		imageLayerSize += item.Size
#
# 		# print(f"  {item.Size/_IEC_SIZES["M"]:7.1f} MiB {item.Path}")
#
# 	# print(f"  Bucket size: {imageLayerSize/_IEC_SIZES["M"]:.1f} MiB")
# 	imageLayers[str(index)] = imageLayerSize
#
# 	imageLayerCount = index + 1
# 	print(f"Docker Layers: {imageLayerCount}")
# 	# for i in range(imageLayerCount):
# 	for i in range(imageLayerCount - 1, -1, -1):
# 		layerFile = outputPath / f"layer_{i}.list"
# 		print(f"{i:2} {imageLayers[str(i)]/_IEC_SIZES["M"]:7.1f} MiB  {len(imageLayers[i]):4}  {layerFile}")
#
# 		with layerFile.open("w", encoding="utf-8") as f:
# 			for e in imageLayers[i]:
# 				relPath = e.Path.relative_to(vivadoPath)
# 				f.write(f"{relPath.as_posix()}\n")
#
# if __name__ == '__main__':
# 	scriptPath = Path(__file__)
# 	main(Path(argv[1]), scriptPath.parent)

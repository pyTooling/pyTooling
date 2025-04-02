from pathlib import Path

from pyTooling.Filesystem import Root


def main() -> None:
	rootPath = Path("C:\\Xilinx\\Vivado\\2023.1")

	dir = Root(rootPath, scanSubdirectories=True)

	print()
	print(f"Scan duration:          {dir._scanDuration:.3f} sec")
	print(f"Aggregation duration:   {dir._aggregateDuration*1e3:6.3f} ms")
	print(f"TotalSubdirectoryCount: {dir.TotalSubdirectoryCount:6}")
	print(f"TotalFileCount:         {dir.TotalFileCount:6}")
	print(f"TotalHardLinkCount:     {dir.TotalHardLinkCount:6}")
	print(f"Total size:             {dir.Size/2**30:.3f} GiB")


if __name__ == '__main__':
	main()

from pathlib import Path

from pyTooling.Filesystem import Directory


def main() -> None:
	rootPath = Path("C:\\Xilinx\\Vivado\\2023.1\\bin")

	dir = Directory(rootPath)
	dir._scan()


if __name__ == '__main__':
	main()

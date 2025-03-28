from typing import Any

from pyTooling.Decorators import export

from pyTooling.CLIAbstraction import Executable, CLIArgument
from pyTooling.CLIAbstraction.Flag import ShortFlag
from pyTooling.CLIAbstraction.ValuedFlag import LongValuedFlag
from pyTooling.CLIAbstraction.Argument import StringArgument


@export
class DiskUsage(Executable):
	def __new__(cls, *args: Any, **kwargs: Any):
		cls._executableNames = {
			"Darwin":  "du",
			"FreeBSD": "du",
			"Linux":   "du",
			"Windows": "du.exe"
		}
		return super().__new__(cls)

	@CLIArgument()
	class FlagSummary(ShortFlag, name="s"): ...

	@CLIArgument()
	class FlagBlockSize(LongValuedFlag, name="block-size"): ...

	@CLIArgument()
	class FlagHumanReadable(ShortFlag, name="h"): ...

	@CLIArgument()
	class ArgPath(StringArgument): ...

# Total --total
# Summary --summary
# Bytes --bytes

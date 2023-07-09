

from pyTooling.Decorators import export
from .. import Attribute


#@abstract
@export
class ArgParseAttribute(Attribute):
	"""
	Base-class for all attributes to describe a :mod:`argparse`-base command line
	argument parser.
	"""

# String
# StringList
# Path
# PathList
# Delimiter
# ValuedFlag --option=value
# ValuedFlagList --option=foo --option=bar
# OptionalValued --option --option=foo
# ValuedTuple

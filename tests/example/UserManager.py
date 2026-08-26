# ==================================================================================================================== #
#             _____           _ _                                                                                      #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _                                                                          #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` |                                                                         #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |                                                                         #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, |                                                                         #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2026-2026 Patrick Lehmann - Bötzingen, Germany                                                             #
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
A user manager, with its command line described declaratively by :mod:`pyTooling.Attributes.ArgParse`.

The commands, their options and the methods handling them are the same declaration: a handler is a method, and
what it accepts on the command line is written above it. Compare with :file:`OldStyle.py`, which builds the same
command line with :mod:`argparse` directly.
"""
from pyTooling.Attributes.ArgParse            import ArgParseHelperMixin, CommandHandler, DefaultHandler
from pyTooling.Attributes.ArgParse.Argument   import StringArgument
from pyTooling.Attributes.ArgParse.Flag       import LongFlag
from pyTooling.Attributes.ArgParse.ValuedFlag import LongValuedFlag


class UserManager(ArgParseHelperMixin):
	"""Manage the users of a system."""

	def __init__(self) -> None:
		super().__init__(prog="UserManager.py", description="Manage the users of a system.")

	@DefaultHandler()
	@LongFlag("--verbose", dest="verbose", help="Print verbose messages.")
	def HandleDefault(self, args) -> None:
		"""Handle the program being called without a command."""
		print(f"Called without a command. (verbose={args.verbose})")
		self.MainParser.print_help()

	@CommandHandler("create", help="Create a new user.")
	@StringArgument(dest="username", metaName="username", help="Name of the user to create.")
	@LongValuedFlag("--quota", dest="quota", help="Disk quota of the new user.")
	def HandleCreate(self, args) -> None:
		"""Handle the 'create' command."""
		print(f"Creating user '{args.username}' with a quota of {args.quota}.")

	@CommandHandler("delete", help="Delete a user.")
	@StringArgument(dest="username", metaName="username", help="Name of the user to delete.")
	def HandleDelete(self, args) -> None:
		"""Handle the 'delete' command."""
		print(f"Deleting user '{args.username}'.")

	@CommandHandler("list", help="List all users.")
	def HandleList(self, args) -> None:
		"""Handle the 'list' command."""
		print("Listing all users.")


def main() -> None:
	"""Parse the command line and route it to the handler that declared it."""
	program = UserManager()
	program.Run()


if __name__ == "__main__":
	main()

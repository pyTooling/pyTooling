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
The same user manager as :file:`UserManager.py`, built with :mod:`argparse` directly.

Every command appears twice - once where the parser is built, and once where it is dispatched - and nothing ties
the two together but a string. That separation is what :mod:`pyTooling.Attributes.ArgParse` removes.
"""
from argparse import ArgumentParser


def HandleDefault(args) -> None:
	"""Handle the program being called without a command."""
	print(f"Called without a command. (verbose={args.verbose})")


def HandleCreate(args) -> None:
	"""Handle the 'create' command."""
	print(f"Creating user '{args.username}' with a quota of {args.quota}.")


def HandleDelete(args) -> None:
	"""Handle the 'delete' command."""
	print(f"Deleting user '{args.username}'.")


def HandleList(args) -> None:
	"""Handle the 'list' command."""
	print("Listing all users.")


def main() -> None:
	"""Build the parser, parse the command line, and dispatch to the matching handler."""
	mainParser = ArgumentParser(prog="OldStyle.py", description="Manage the users of a system.")
	mainParser.add_argument("--verbose", dest="verbose", action="store_true", help="Print verbose messages.")
	subParsers = mainParser.add_subparsers(dest="command", help="sub-command help")

	createParser = subParsers.add_parser("create", help="Create a new user.")
	createParser.add_argument(dest="username", metavar="username", help="Name of the user to create.")
	createParser.add_argument("--quota", dest="quota", help="Disk quota of the new user.")

	deleteParser = subParsers.add_parser("delete", help="Delete a user.")
	deleteParser.add_argument(dest="username", metavar="username", help="Name of the user to delete.")

	subParsers.add_parser("list", help="List all users.")

	args = mainParser.parse_args()

	# the dispatch table repeats every command name a third time
	handlers = {
		None:     HandleDefault,
		"create": HandleCreate,
		"delete": HandleDelete,
		"list":   HandleList,
	}
	handlers[args.command](args)


if __name__ == "__main__":
	main()

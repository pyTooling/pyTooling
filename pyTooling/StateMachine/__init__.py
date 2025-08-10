# ==================================================================================================================== #
#             _____           _ _               ____  _        _       __  __            _     _                       #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|| |_ __ _| |_ ___|  \/  | __ _  ___| |__ (_)_ __   ___            #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | \___ \| __/ _` | __/ _ \ |\/| |/ _` |/ __| '_ \| | '_ \ / _ \           #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_ ___) | || (_| | ||  __/ |  | | (_| | (__| | | | | | | |  __/           #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/ \__\__,_|\__\___|_|  |_|\__,_|\___|_| |_|_|_| |_|\___|           #
# |_|    |___/                          |___/                                                                          #
# ==================================================================================================================== #
# Authors:                                                                                                             #
#   Patrick Lehmann                                                                                                    #
#                                                                                                                      #
# License:                                                                                                             #
# ==================================================================================================================== #
# Copyright 2017-2025 Patrick Lehmann - Bötzingen, Germany                                                             #
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
This packages provides a data structure to describe statemachines.

.. hint:: See :ref:`high-level help <STRUCT/StateMachine>` for explanations and usage examples.
"""
from typing import List

try:
	from pyTooling.Decorators  import export, readonly
	from pyTooling.MetaClasses import ExtendedType
except (ImportError, ModuleNotFoundError):  # pragma: no cover
	print("[pyTooling.StateMachine] Could not import from 'pyTooling.*'!")

	try:
		from Decorators          import export, readonly
		from MetaClasses         import ExtendedType, mixin
	except (ImportError, ModuleNotFoundError) as ex:  # pragma: no cover
		print("[pyTooling.StateMachine] Could not import directly!")
		raise ex


@export
class Base(metaclass=ExtendedType, slots=True):
	pass


@export
class Transition(Base):
	"""
	Represents a transition (edge) in a statemachine diagram (directed graph).
	"""
	_source:      "State"  #: Source state.
	_destination: "State"  #: Destination state.

	def __init__(self, source: "State", destination: "State") -> None:
		"""
		Initializes a transition.

		:param source:      Source state of a transition.
		:param destination: Destination state of a transition.
		"""
		self._source = source
		self._destination = destination


@export
class State(Base):
	"""
	Represents a state (node/vertex) in a statemachine diagram (directed graph).
	"""
	_inboundTransitions:  List[Transition]  #: List of inbound transitions.
	_outboundTransitions: List[Transition]  #: List of outbound transitions.

	def __init__(self) -> None:
		"""
		Initializes a state.

		"""
		self._inboundTransitions = []
		self._outboundTransitions = []


@export
class StateMachine(Base):
	"""
	Represents a statemachine (graph) in a statemachine diagram (directed graph).
	"""
	_states:       List[State]
	_initialState: State

	def __init__(self, initialState: State) -> None:
		"""
		Initializes a (finite) state machine (FSM).

		:param initialState: The initialize state of the FSM.
		"""
		self._states = []
		self._initialState = initialState

	def AddState(self, state: State) -> None:
		"""
		Add a state to the state machine.

		:param state: State to add.
		"""
		if state not in self._states:    # TODO: use a set to check for double added states?
			self._states.append(state)
		else:
			raise ValueError(f"State '{state}' was already added to this statemachine.")

	@readonly
	def States(self) -> List[State]:
		"""
		Read-only property to access the list of states.

		:returns:                    List of states.
		"""
		return self._states

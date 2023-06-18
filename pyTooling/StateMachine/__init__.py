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
# Copyright 2017-2023 Patrick Lehmann - Bötzingen, Germany                                                             #
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

from pyTooling.Decorators import export
from pyTooling.MetaClasses import ExtendedType


@export
class Base(metaclass=ExtendedType, slots=True):
	pass


@export
class Transition(Base):
	"""
	Represents a transition (edge) in a statemachine diagram (directed graph).
	"""
	_source:      "State"
	_destination: "State"

	def __init__(self, source: "State", destination: "State"):
		self._source = source
		self._destination = destination


@export
class State(Base):
	"""
	Represents a state (node/vertex) in a statemachine diagram (directed graph).
	"""
	_inboundTransitions:  List[Transition]
	_outboundTransitions: List[Transition]

	def __init__(self):
		self._inboundTransitions = []
		self._outboundTransitions = []


@export
class StateMachine(Base):
	"""
	Represents a statemachine (graph) in a statemachine diagram (directed graph).
	"""
	_states:       List[State]
	_initialState: State

	def __init__(self, initialState: State):
		self._states = []
		self._initialState = initialState

	def AddState(self, state: State):
		if state not in self._states:    # TODO: use a set to check for double added states?
			self._states.append(state)
		else:
			raise ValueError(f"State '{state}' was already added to this statemachine.")

	@property
	def States(self) -> List[State]:
		return self._states

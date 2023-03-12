from typing import Any, Dict, List

from pyTooling.Decorators import export


# TODO: sub-statemachine
# TODO: history

@export
class Transition:
	_lastState: 'State'
	_nextState: 'State'


@export
class State:
	_fsm:                'FiniteStateMachine'
	_ingressTransitions: List[Transition]
	_egressTransitions:  List[Transition]


@export
class StartState(State):
	pass


@export
class FiniteStateMachine:
	_states: Dict[Any, State]

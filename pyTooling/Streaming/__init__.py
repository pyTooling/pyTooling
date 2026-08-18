# ==================================================================================================================== #
#             _____           _ _               ____  _                            _                                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  / ___|| |_ _ __ ___  __ _ _ __ ___ (_)_ __   __ _                       #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | \___ \| __| '__/ _ \/ _` | '_ ` _ \| | '_ \ / _` |                      #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_ ___) | |_| | |  __/ (_| | | | | | | | | | | (_| |                      #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)____/ \__|_|  \___|\__,_|_| |_| |_|_|_| |_|\__, |                      #
# |_|    |___/                          |___/                                              |___/                       #
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
Helpers to stream items from a producer thread to a consumer through a thread-safe queue.

A queue becomes an iterator, so neither side polls: the producer hands items over and the consumer iterates them until
the producer signals the end.
"""
from collections import deque
from queue       import Queue as ThreadSafeQueue, Full
from threading   import Event
from typing      import Optional as Nullable, Iterator, TypeVar

from pyTooling.Decorators import export

__all__ = ["QueueReader", "StreamItem"]

QueueItem =  TypeVar("QueueItem")
StreamItem = TypeVar("StreamItem")


# TODO: does it need a real timeout and/or maxTries?
# TODO: it should return of sucessful or aborted
@export
def BlockingPut(queue: ThreadSafeQueue[QueueItem], item: QueueItem, stopEvent: Event, retryTimeout: float = 0.1) -> bool:
	"""
	Puts an item into a bounded queue, but re-checks ``stopEvent`` on every timeout instead of blocking forever.

	This is what prevents a dead/failed consumer from deadlocking its producer when the queue is full.
	"""
	while not stopEvent.is_set():
		try:
			queue.put(item, timeout=retryTimeout)
			return True
		except Full:
			continue

	return False


# TODO: maybe later: implement a predicate, max items and stop marker
@export
def QueueReader(queue: ThreadSafeQueue[Nullable[QueueItem]]) -> Iterator[QueueItem]:
	"""
	Adapts a queue to a blocking iterator.

	``None`` is used as the end-of-stream marker.

	:param queue: The queue to read from.
	:returns:     An iterator over the items from the queue.
	"""
	while True:
		if (item := queue.get()) is None:
			return

		yield item


@export
def Delay(stream: Iterator[QueueItem], delay: int = 1) -> Iterator[QueueItem]:
	"""
	Holds each item back for ``delay`` further items before releasing it.
	"""
	buffer: deque[QueueItem] = deque()

	for line in stream:
		buffer.append(line)
		if len(buffer) > delay:
			yield buffer.popleft()

	while buffer:
		yield buffer.popleft()

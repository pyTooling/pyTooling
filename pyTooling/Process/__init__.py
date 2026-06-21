# ==================================================================================================================== #
#             _____           _ _               ____                                                                   #
#  _ __  _   |_   _|__   ___ | (_)_ __   __ _  |  _ \ _ __ ___   ___ ___  ___ ___                                      #
# | '_ \| | | || |/ _ \ / _ \| | | '_ \ / _` | | |_) | '__/ _ \ / __/ _ \/ __/ __|                                     #
# | |_) | |_| || | (_) | (_) | | | | | | (_| |_|  __/| | | (_) | (_|  __/\__ \__ \                                     #
# | .__/ \__, ||_|\___/ \___/|_|_|_| |_|\__, (_)_|   |_|  \___/ \___\___||___/___/                                     #
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

from ctypes              import Structure, c_void_p, c_size_t, c_int, c_int32, c_uint64
from os                  import getpid, strerror
from pathlib             import Path
from typing import ClassVar, Any

from pyTooling.Decorators  import export, readonly
from pyTooling.MetaClasses import ExtendedType
from pyTooling.Platform    import PlatformException, CurrentPlatform

if CurrentPlatform.IsNativeWindows or CurrentPlatform.IsMSYS2Environment:
	from ctypes          import WinDLL
	from ctypes.wintypes import HANDLE, BOOL, DWORD


@export
class MemoryInfo(metaclass=ExtendedType, slots=True):
	_ResidentMemory: int  #: Resident Set Size (VmRSS)  – physical pages currently mapped. Memory usage in bytes.
	_VirtualMemory:  int  #: Virtual Memory Size (VmS) – total virtual address space used. Memory usage in bytes.

	def __init__(self, residentMemory: int, virtualMemory: int) -> None:
		"""
		Initializes the memory info object with **Resident Set Size** and **Virtual Memory Size**.

		:param residentMemory: Resident Memory Size (VmRSS) in bytes.
		:param virtualMemory:  Virtual Memory Size (VmS) in bytes.
		"""
		self._ResidentMemory = residentMemory
		self._VirtualMemory =  virtualMemory

	@readonly
	def ResidentMemory(self) -> int:
		"""
		Read-only property to access the **Resident Set Size** (used physical memory).

		:returns: Resident Set Size (VmRSS) in bytes.
		"""
		return self._ResidentMemory

	@readonly
	def VirtualMemory(self) -> int:
		"""
		Read-only property to access the **Virtual Memory Size** (used virtual memory).

		:returns: Virtual Memory Size (VmS) in bytes.
		"""
		return self._VirtualMemory

	def __str__(self) -> str:
		return f"Physical Memory (VmRSS): {self.ResidentMemory / 2**20:.3f} MiB / Virtual Memory (VmS): {self.VirtualMemory / 2**20:.3f}  MiB"


@export
class ProcessInformation(metaclass=ExtendedType, slots=True):
	if CurrentPlatform.IsNativeWindows or CurrentPlatform.IsMSYS2Environment:
		_psapi:         WinDLL
		_kernel32:      WinDLL
		_processHandle: Any
	elif CurrentPlatform.IsNativeLinux:
		_processStatusFile: ClassVar[Path] = Path(f"/proc/self/statm")

	if CurrentPlatform.IsNativeWindows or CurrentPlatform.IsMSYS2Environment:
		def __init__(self) -> None:
			self._psapi =    WinDLL("psapi", use_last_error=True)
			self._kernel32 = WinDLL("kernel32", use_last_error=True)

			self._kernel32.GetCurrentProcess.restype = HANDLE
			self._kernel32.GetCurrentProcess.argtypes = []

			self._processHandle = self._kernel32.GetCurrentProcess()
	else:
		def __init__(self) -> None:
			pass

	if CurrentPlatform.IsNativeLinux:
		from os import sysconf
		_pageSize: ClassVar[int] = sysconf("SC_PAGESIZE")

		def GetMemoryUsage(self) -> MemoryInfo:
			"""
			Get the memory usage of this Python process on a Linux system.

			Read the `/proc/self/statm` memory statistic file (space separated) for the current process:

			[0] size
					VmSize (total virtual address space)
			[1] resident
					VmRSS - Virtual memory Resident Set Size (pages currently resident in RAM) = used physical memory
			[2] shared
					shared pages (mapped from files)
			[3] text
					code segment pages
			[4] lib
					unused (always 0 since Linux 2.6)
			[5] data
					data + stack pages
			[6] dt
					dirty pages (always 0 since Linux 2.6)

			``SC_PAGESIZE`` is typically 4096 bytes, but can be 16kiB (ARM64) or 64kiB (PowerPC/RHEL9+). :func:`os.sysconf`
			reads it from the aux vector — no syscall overhead.

			:returns: Physical memory usage (VmRSS) in bytes.
			"""

			try:
				with self._processStatusFile.open("rb") as f:
					fields = f.read().split()
			except FileNotFoundError as ex:
				raise PlatformException(f"Can't open '{self._processStatusFile}' to extract the process' physical memory usage.") from ex

			vms = int(fields[0]) * self._pageSize  #: VmSize
			rss = int(fields[1]) * self._pageSize  #: VmRSS

			return MemoryInfo(rss, vms)

	elif CurrentPlatform.IsNativeMacOS:
		class _ProcTaskInfo(Structure):
			"""
			``struct proc_taskinfo`` from ``<sys/proc_info.h>``
			"""
			_fields_ = [
				("pti_virtual_size", c_uint64),
				("pti_resident_size", c_uint64),
				("pti_total_user", c_uint64),
				("pti_total_system", c_uint64),
				("pti_threads_user", c_uint64),
				("pti_threads_system", c_uint64),
				("pti_policy", c_int32),
				("pti_faults", c_int32),
				("pti_pageins", c_int32),
				("pti_cow_faults", c_int32),
				("pti_messages_sent", c_int32),
				("pti_messages_received", c_int32),
				("pti_syscalls_mach", c_int32),
				("pti_syscalls_unix", c_int32),
				("pti_csw", c_int32),
				("pti_threadnum", c_int32),
				("pti_numrunning", c_int32),
				("pti_priority", c_int32),
			]

		def GetMemoryUsage(self) -> MemoryInfo:
			"""
			Call libproc.proc_pidinfo(PROC_PIDTASKINFO) – the same route psutil takes.

			struct proc_taskinfo  (<sys/proc_info.h>):
					pti_virtual_size   uint64  – virtual address space in bytes
					pti_resident_size  uint64  – resident (physical) memory in bytes
					… 16 further fields (timing, policy, fault/syscall counters)

			proc_pidinfo() returns the number of bytes written; ≤ 0 means error
			(errno is set).  PROC_PIDTASKINFO = 4.
			"""
			from ctypes import CDLL, byref, sizeof, get_errno
			from ctypes.util import find_library

			PROC_PIDTASKINFO = 4

			_libproc_path = find_library("proc")  # or "/usr/lib/libproc.dylib"
			_libproc = CDLL(_libproc_path, use_errno=True)
			_libproc.proc_pidinfo.restype = c_int
			_libproc.proc_pidinfo.argtypes = [
				c_int,     # pid
				c_int,     # flavor
				c_uint64,  # arg  (unused for PROC_PIDTASKINFO)
				c_void_p,  # buffer
				c_int,     # buffersize
			]

			taskInfo = self._ProcTaskInfo()
			ret = _libproc.proc_pidinfo(getpid(), PROC_PIDTASKINFO, 0, byref(taskInfo), sizeof(taskInfo))
			if ret <= 0:
				err = get_errno()
				raise PlatformException(f"Failed to get current process' information.") from OSError(err, strerror(err), "proc_pidinfo")

			return MemoryInfo(taskInfo.pti_resident_size, taskInfo.pti_virtual_size)

	elif CurrentPlatform.IsNativeWindows or CurrentPlatform.IsMSYS2Environment:
		class _ProcessMemoryCounters(Structure):
			from ctypes.wintypes import DWORD

			_fields_ = [
				("cb", DWORD),
				("PageFaultCount", DWORD),
				("PeakWorkingSetSize", c_size_t),
				("WorkingSetSize", c_size_t),
				("QuotaPeakPagedPoolUsage", c_size_t),
				("QuotaPagedPoolUsage", c_size_t),
				("QuotaPeakNonPagedPoolUsage", c_size_t),
				("QuotaNonPagedPoolUsage", c_size_t),
				("PagefileUsage", c_size_t),
				("PeakPagefileUsage", c_size_t),
			]

			del DWORD

		def GetMemoryUsage(self) -> MemoryInfo:
			"""
			Call psapi.GetProcessMemoryInfo() with a PROCESS_MEMORY_COUNTERS struct.

			WorkingSetSize  – physical pages currently mapped  → RSS
			PagefileUsage   – private committed bytes          → VMS  (= "Private Bytes"
												in Task Manager; mirrors psutil's vms on Windows)

			GetCurrentProcess() returns a pseudo-handle (-1) requiring no CloseHandle.
			use_last_error=True routes SetLastError / GetLastError through ctypes so
			WinError() picks up the correct code without a race.
			"""

			from ctypes import WinDLL, WinError, POINTER, sizeof, byref, get_last_error

			self._psapi.GetProcessMemoryInfo.restype = BOOL
			self._psapi.GetProcessMemoryInfo.argtypes = [HANDLE, POINTER(self._ProcessMemoryCounters), DWORD]

			processMemoryCounters = self._ProcessMemoryCounters()
			processMemoryCounters.cb = sizeof(processMemoryCounters)

			if not self._psapi.GetProcessMemoryInfo(self._processHandle, byref(processMemoryCounters), processMemoryCounters.cb):
				raise WinError(get_last_error())

			return MemoryInfo(processMemoryCounters.WorkingSetSize, processMemoryCounters.PagefileUsage)

	else:
		raise PlatformException(f"Unsupported platform: '{CurrentPlatform}'.")

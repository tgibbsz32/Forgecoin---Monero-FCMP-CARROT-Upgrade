"""Bounded persistent native-worker adapter for synthetic research only.

No runtime compilation, daemon, miner, credits or payouts. Caller supplies a
trusted executable implementing randomx_worker.cpp's tagged line protocol.
One request at a time; errors discard the worker and are never retried silently.
"""
from pathlib import Path
import queue
import re
import subprocess
import threading
from .native_randomx_adapter import NativeRandomXError


class PersistentRandomXAdapter:
    def __init__(self, executable, timeout=10, *, arguments=()):
        path = Path(executable).resolve(strict=True)
        if not path.is_file() or type(timeout) not in (int, float) or not 0 < timeout <= 60:
            raise NativeRandomXError("invalid worker or timeout")
        if not isinstance(arguments, (tuple, list)) or any(not isinstance(a, str) for a in arguments):
            raise NativeRandomXError("invalid worker arguments")
        self.command = [str(path), *arguments]
        self.timeout = timeout
        self.process = None
        self.requests = 0
        self.starts = 0
        self.lock = threading.Lock()
        self.closed = False
        self.broken = False

    def _discard(self):
        process, self.process = self.process, None
        if process is None:
            return
        try:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=2)
        except (OSError, subprocess.TimeoutExpired):
            self.broken = True
            raise NativeRandomXError("worker cleanup failed; adapter disabled")
        return process

    @staticmethod
    def _close_pipes(process):
        for handle in (process.stdin, process.stdout):
            if handle:
                handle.close()

    def close(self):
        with self.lock:
            self.closed = True
            process = self._discard()
            if process:
                self._close_pipes(process)

    def __call__(self, seed, blob):
        if not isinstance(seed, bytes) or len(seed) != 32:
            raise NativeRandomXError("seed must be 32 bytes")
        if not isinstance(blob, bytes) or not 1 <= len(blob) <= 262144:
            raise NativeRandomXError("invalid hashing blob size")
        if not self.lock.acquire(blocking=False):
            raise NativeRandomXError("native worker busy")
        thread = None
        try:
            if self.closed or self.broken:
                raise NativeRandomXError("native adapter unavailable")
            if self.process is not None and (self.requests >= 64 or self.process.poll() is not None):
                old = self._discard()
                self._close_pipes(old)
            if self.process is None:
                self.process = subprocess.Popen(self.command, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                self.requests = 0
                self.starts += 1
            self.requests += 1
            tag = self.requests
            process = self.process
            frame = f"{tag} {seed.hex()} {blob.hex()}\n".encode("ascii")
            output = queue.Queue(maxsize=1)

            def exchange():
                try:
                    # Raw pipes can short-write; keep all blocking I/O inside
                    # the timed exchange thread, including a stalled stdin.
                    view = memoryview(frame)
                    while view:
                        written = process.stdin.write(view)
                        if not written:
                            raise OSError("worker pipe closed")
                        view = view[written:]
                    process.stdin.flush()
                    output.put(process.stdout.readline(96))
                except (OSError, ValueError):
                    output.put(None)

            thread = threading.Thread(target=exchange, daemon=True)
            thread.start()
            try:
                line = output.get(timeout=self.timeout)
            except queue.Empty as error:
                raise NativeRandomXError("native worker timeout") from error
            thread.join(timeout=1)
            if thread.is_alive() or not isinstance(line, bytes) or not re.fullmatch(
                    str(tag).encode() + rb" [0-9a-f]{64}\r?\n", line):
                raise NativeRandomXError("invalid native worker response")
            return bytes.fromhex(line.decode().split()[1])
        except (OSError, NativeRandomXError) as error:
            old = self._discard()
            if thread:
                thread.join(timeout=2)
                if thread.is_alive():
                    self.broken = True
            if old and not (thread and thread.is_alive()):
                self._close_pipes(old)
            raise NativeRandomXError("native worker request failed") from error
        finally:
            self.lock.release()

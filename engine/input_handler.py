"""Threaded non-blocking keyboard input using msvcrt on Windows."""

from __future__ import annotations

import queue
import threading

import msvcrt


# Two-byte arrow key codes: msvcrt returns 0xe0 followed by one of these.
_ARROW_MAP: dict[int, str] = {
    72: "up",     # H
    80: "down",   # P
    75: "left",   # K
    77: "right",  # M
}

# Special single-byte keys
_SPECIAL_MAP: dict[int, str] = {
    13: "enter",
    27: "escape",
    8:  "backspace",
    9:  "tab",
    32: "space",
}


class InputHandler:
    """Polls the keyboard on a background daemon thread and queues key names.

    Call ``get_key()`` from the main thread to consume the next key press
    without blocking.  Returns ``None`` when no key is available.
    """

    def __init__(self) -> None:
        self._queue: queue.Queue[str] = queue.Queue()
        self._running = False
        self._thread: threading.Thread | None = None

    # -- public API ----------------------------------------------------------

    def start(self) -> None:
        """Spawn the background reader thread (daemon, so it dies with the process)."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._input_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Signal the reader thread to exit."""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=0.5)
            self._thread = None

    def get_key(self) -> str | None:
        """Return the next queued key name, or ``None`` if the queue is empty."""
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    # -- internal ------------------------------------------------------------

    def _input_loop(self) -> None:
        """Continuously poll msvcrt for key presses.

        Handles the two-byte sequences Windows sends for arrow keys
        (0xe0 prefix followed by scan code) as well as ordinary
        single-byte key presses.
        """
        while self._running:
            if not msvcrt.kbhit():
                # Tiny sleep to avoid busy-waiting at 100% CPU.
                import time
                time.sleep(0.01)
                continue

            raw = msvcrt.getch()
            code = raw[0] if isinstance(raw, bytes) else ord(raw)

            # Two-byte sequence: 0x00 or 0xe0 prefix → read second byte
            if code in (0x00, 0xE0):
                if not self._running:
                    break
                raw2 = msvcrt.getch()
                code2 = raw2[0] if isinstance(raw2, bytes) else ord(raw2)
                key_name = _ARROW_MAP.get(code2)
                if key_name:
                    self._queue.put(key_name)
                # Unknown extended key — silently drop it.
                continue

            # Named specials
            if code in _SPECIAL_MAP:
                self._queue.put(_SPECIAL_MAP[code])
                continue

            # Printable character → lowercase string
            try:
                char = chr(code)
                if char.isprintable():
                    self._queue.put(char.lower())
            except (ValueError, OverflowError):
                pass  # unprintable / out of range — ignore

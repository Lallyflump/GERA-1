"""Small fail-closed helpers for bounded local input files."""

from __future__ import annotations

import os
from pathlib import Path
import stat


class BoundedFileError(OSError):
    """A local input could not be read within the configured boundary."""

    def __init__(self, code: str):
        super().__init__(code)
        self.code = code


def read_bounded_regular_file(
    path: str | Path, *, maximum_bytes: int
) -> bytes:
    """Read one regular, non-symlink file once and enforce a byte limit."""

    selected = Path(path)
    try:
        if selected.is_symlink():
            raise BoundedFileError("unsafe_file")
    except BoundedFileError:
        raise
    except OSError as exc:
        raise BoundedFileError("unreadable_file") from exc

    flags = os.O_RDONLY
    if hasattr(os, "O_CLOEXEC"):
        flags |= os.O_CLOEXEC
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW

    try:
        descriptor = os.open(selected, flags)
    except FileNotFoundError as exc:
        raise BoundedFileError("missing_file") from exc
    except OSError as exc:
        if selected.is_symlink():
            raise BoundedFileError("unsafe_file") from exc
        raise BoundedFileError("unreadable_file") from exc

    try:
        details = os.fstat(descriptor)
        if not stat.S_ISREG(details.st_mode):
            raise BoundedFileError("unsafe_file")
        if details.st_size > maximum_bytes:
            raise BoundedFileError("file_too_large")

        chunks: list[bytes] = []
        remaining = maximum_bytes + 1
        while remaining:
            chunk = os.read(descriptor, min(65_536, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        payload = b"".join(chunks)
        if len(payload) > maximum_bytes:
            raise BoundedFileError("file_too_large")
        return payload
    except BoundedFileError:
        raise
    except OSError as exc:
        raise BoundedFileError("unreadable_file") from exc
    finally:
        os.close(descriptor)

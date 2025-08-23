import platform
from pathlib import Path
from typing import Protocol, cast

from cffi import FFI

__all__ = ["build_ffi_and_lib"]


EXTENSION = {"Darwin": ".dylib", "Linux": ".so", "Windows": ".dll"}[platform.system()]
HERE = Path(__file__).parent


class LibEbur128(Protocol):
    def ebur128_init(self, channels: int, samplerate: int, mode: int): ...
    def ebur128_destroy(self, state_ptr): ...
    def ebur128_add_frames_float(self, state, frames, frames_size: int) -> int: ...
    def ebur128_add_frames_double(self, state, frames, frames_size: int) -> int: ...
    def ebur128_true_peak(self, state, channel, out_ptr) -> int: ...
    def ebur128_loudness_global(self, state, out_ptr) -> int: ...


def build_ffi_and_lib() -> tuple[FFI, LibEbur128]:
    header_path = HERE / "include" / "ebur128.h"
    library_path = HERE / "lib" / f"libebur128{EXTENSION}"

    ffi = FFI()
    contents = header_path.read_text()
    contents = "".join([ln for ln in contents.split() if not ln.startswith("#")])
    ffi.cdef(contents)

    lib = ffi.dlopen(str(library_path))
    return ffi, cast(LibEbur128, lib)

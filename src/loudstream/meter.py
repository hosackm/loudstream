import math
from enum import Enum
from pathlib import Path
from typing import IO

from soundfile import SoundFile


from loudstream._ffi import build_ffi_and_lib
from loudstream.source import make_audio_source

__all__ = ["Meter"]


class Mode(Enum):
    MOMENTARY = 1 << 0
    LOUDNESS_SHORT_TERM = 1 << 1 | MOMENTARY
    GLOBAL_AND_RELATIVE = 1 << 2 | MOMENTARY
    LOUDNESS_RANGE = 1 << 3 | LOUDNESS_SHORT_TERM
    SAMPLE_PEAK = 1 << 4 | MOMENTARY
    TRUE_PEAK = 1 << 5 | MOMENTARY | SAMPLE_PEAK
    HISTOGRAM = 1 << 6


class Meter:
    def __init__(self):
        self.ffi, self.lib = build_ffi_and_lib()

    def measure(
        self,
        source: str | Path | IO[bytes] | SoundFile,
        framesize: int = 4096,
        as_double: bool = False,
    ) -> tuple[float, float]:
        """
        Measure the loudness and true peak level of an audio file.

        This function reads the given audio file in blocks and computes:
          - Integrated loudness in LUFS (per ITU-R BS.1770 / EBU R128).
          - True peak level in dBTP, accounting for inter-sample peaks.

        Parameters
        ----------
        source : str | Path | IO[bytes] | SoundFile
            The filename, filepath, file object, or soundfile to read from.
        framesize : int, optional
            Number of frames per block to process during streaming analysis.
            Larger values are more efficient, smaller values reduce memory footprint.
            Default is 4096.
        double : bool, optional
            If True, perform calculations using 64-bit floats for higher precision.
            Default is False.

        Returns
        -------
        tuple[float, float]
            A tuple `(loudness_lufs, true_peak_dbtp)` where:
              - `loudness_lufs` is the integrated loudness of the file in LUFS.
              - `true_peak_dbtp` is the maximum true peak level in dBTP.

        Notes
        -----
        - The integrated loudness follows the gating and filtering defined in
          ITU-R BS.1770 / EBU R128.
        - True peak detection may oversample internally to capture inter-sample peaks.
        """
        audio_source = make_audio_source(source)
        mode = Mode.GLOBAL_AND_RELATIVE.value | Mode.TRUE_PEAK.value
        st = self.lib.ebur128_init(audio_source.channels, audio_source.samplerate, mode)
        if not st:
            raise RuntimeError("Failed to initialize ebur128_state")

        try:
            for frames in audio_source.read_frames(
                framesize=framesize, as_double=as_double
            ):
                if len(frames) == 0:
                    break

                if as_double:
                    c_frames = self.ffi.cast("double *", frames.ctypes.data)
                    res = self.lib.ebur128_add_frames_double(
                        st, c_frames, frames.shape[0]
                    )
                else:
                    c_frames = self.ffi.cast("float *", frames.ctypes.data)
                    res = self.lib.ebur128_add_frames_float(
                        st, c_frames, frames.shape[0]
                    )

                if res != 0:
                    raise RuntimeError("Failed to add frames")

            out_loudness = self.ffi.new("double*")
            res = self.lib.ebur128_loudness_global(st, out_loudness)
            if res != 0:
                raise RuntimeError("Failed to compute loudness")

            true_peak = -math.inf
            out_true_peak = self.ffi.new("double*")
            for i in range(audio_source.channels):
                res = self.lib.ebur128_true_peak(st, i, out_true_peak)
                if res != 0:
                    raise RuntimeError("Failed to compute loudness")
                true_peak = max(true_peak, out_true_peak[0])

            return out_loudness[0], 20.0 * math.log10(true_peak)
        finally:
            self.lib.ebur128_destroy(self.ffi.new("ebur128_state**", st))

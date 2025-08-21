import math
from pathlib import Path
from typing import IO

import soundfile as sf

from loudstream.source import make_audio_source
from loudstream.meter import Meter


def normalize(
    input: str | Path | IO[bytes] | sf.SoundFile,
    output_path: str | Path,
    target_loudness: float,
    target_peak: float,
    framesize: int = 2048,
) -> None:
    lufs, dbtp = Meter().measure(input)
    gain_factor = compute_gain_factor(lufs, target_loudness, dbtp, target_peak)

    input_source = make_audio_source(input)

    with sf.SoundFile(
        output_path,
        "w",
        samplerate=input_source.samplerate,
        channels=input_source.channels,
        format=input_source.format,
    ) as fout:
        for frames in input_source.read_frames(framesize=framesize):
            if len(frames) == 0:
                break
            fout.write(frames * gain_factor)


def compute_gain_factor(loudness_measured, loudness_target, peak_measured, peak_target):
    """
    Compute a safe linear gain factor for loudness normalization
    that respects both the loudness target and the true peak ceiling.

    Args:
        loudness_measured (float): measured integrated loudness [LUFS]
        loudness_target   (float): desired loudness target [LUFS]
        peak_measured     (float): measured true peak [dBTP]
        peak_target       (float): desired peak ceiling [dBTP]

    Returns:
        float: linear gain factor
    """
    gain_loudness_db = loudness_target - loudness_measured
    gain_peak_db = peak_target - peak_measured
    gain_final_db = min(gain_loudness_db, gain_peak_db)
    return math.pow(10.0, gain_final_db / 20.0)


__all__ = ["compute_gain_factor", "normalize"]

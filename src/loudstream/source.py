from pathlib import Path
from typing import Protocol, IO, Iterator

import numpy as np
import soundfile as sf


__all__ = [
    "AudioSource",
    "FileObjectSource",
    "PathSource",
    "SoundFileSource",
    "make_audio_source",
]


class AudioSource(Protocol):
    """A streaming audio source that yields numpy frames."""

    channels: int
    format: str
    samplerate: int

    def read_frames(
        self,
        framesize: int = 1024,
        as_double: bool = False,
    ) -> Iterator[np.ndarray]:
        """Yield frames of shape (n_channels, n_samples)."""
        ...


def make_audio_source(obj: str | Path | IO[bytes] | sf.SoundFile) -> AudioSource:
    if isinstance(obj, sf.SoundFile):
        return SoundFileSource(obj)
    elif isinstance(obj, (str, Path)):
        return PathSource(obj)
    elif hasattr(obj, "read"):
        return FileObjectSource(obj)
    else:
        raise TypeError(f"Unsupported source type {type(obj)}")


class SoundFileSource:
    def __init__(self, file: sf.SoundFile):
        self.file = file
        self.channels = file.channels
        self.format = file.format
        self.samplerate = file.samplerate

    def read_frames(
        self,
        framesize: int = 1024,
        as_double: bool = False,
    ) -> Iterator[np.ndarray]:
        while True:
            dtype = "float64" if as_double else "float32"
            data = self.file.read(framesize, dtype=dtype, always_2d=True)
            if len(data) == 0:
                break

            yield data


class PathSource(SoundFileSource):
    def __init__(self, path: str | Path):
        self.file = sf.SoundFile(str(path))
        super().__init__(self.file)


class FileObjectSource(SoundFileSource):
    def __init__(self, file_obj):
        if "rb" not in file_obj.mode:
            raise Exception("File must be opened in 'rb' binary mode.")
        self.file = sf.SoundFile(file_obj)
        super().__init__(self.file)

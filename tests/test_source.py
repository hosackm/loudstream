import pytest
import soundfile as sf

from loudstream import make_audio_source


def test_source_creation_filepath_str(signal_directory):
    filepath = str(signal_directory / "1770-2_Comp_23LKFS_2000Hz_2ch.wav")
    source = make_audio_source(filepath)
    assert source

    assert next(source.read_frames()).shape == (1024, 2)


def test_source_creation_filepath(signal_directory):
    filepath = signal_directory / "1770-2_Comp_23LKFS_2000Hz_2ch.wav"
    source = make_audio_source(filepath)
    assert next(source.read_frames()).shape == (1024, 2)


def test_source_creation_fileobj(signal_directory):
    filepath = signal_directory / "1770-2_Comp_23LKFS_2000Hz_2ch.wav"
    with open(filepath, "rb") as fobj:
        source = make_audio_source(fobj)
        assert next(source.read_frames()).shape == (1024, 2)


def test_source_creation_soundfile(signal_directory):
    filepath = signal_directory / "1770-2_Comp_23LKFS_2000Hz_2ch.wav"
    with sf.SoundFile(filepath) as f:
        source = make_audio_source(f)
        assert next(source.read_frames()).shape == (1024, 2)


def test_source_creation_invalid_type_fails():
    invalids = (42, "hello", {"A": 1}, [9, 8, 7], 1900.0)
    with pytest.raises(TypeError):
        make_audio_source(invalids)


def test_source_fileobj_must_be_opened_with_rb(signal_directory):
    filepath = signal_directory / "1770-2_Comp_23LKFS_2000Hz_2ch.wav"
    with open(filepath) as fobj:
        with pytest.raises(Exception):
            make_audio_source(fobj)

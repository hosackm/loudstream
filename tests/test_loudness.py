from pathlib import Path
from random import randint
from tempfile import TemporaryDirectory

import pytest

from loudstream import Meter, normalize

# https://en.wikipedia.org/wiki/EBU_R_128?utm_source=chatgpt.com#Normalisation
COMPLIANCE_THRESHOLD = 0.5


def is_close(actual, target, threshold=COMPLIANCE_THRESHOLD):
    return target - threshold <= actual <= target + threshold


@pytest.mark.parametrize("double", [True, False])
@pytest.mark.parametrize(
    "input_path,expected_loudness,expected_peak",
    [
        ("1770-2_Comp_23LKFS_10000Hz_2ch.wav", -23, -25.5),
        ("1770-2_Comp_23LKFS_2000Hz_2ch.wav", -23, -25.5),
        ("1770-2_Comp_23LKFS_1000Hz_2ch.wav", -23, -23),
        ("1770-2_Comp_23LKFS_500Hz_2ch.wav", -23, -22.3),
        ("1770-2_Comp_23LKFS_100Hz_2ch.wav", -23, -21),
        ("1770-2_Comp_23LKFS_25Hz_2ch.wav", -23, -11.9),
        ("1770-2_Comp_24LKFS_10000Hz_2ch.wav", -24, -27),
        ("1770-2_Comp_24LKFS_2000Hz_2ch.wav", -24, -26.5),
        ("1770-2_Comp_24LKFS_1000Hz_2ch.wav", -24, -24),
        ("1770-2_Comp_24LKFS_100Hz_2ch.wav", -24, -22.3),
        ("1770-2_Comp_24LKFS_500Hz_2ch.wav", -24, -23.3),
        ("1770-2_Comp_24LKFS_25Hz_2ch.wav", -24, -12.9),
        ("1770-2_Conf_Mono_Voice+Music-23LKFS.wav", -23, -4.7),
        ("1770-2_Conf_Mono_Voice+Music-24LKFS.wav", -24, -5.7),
        ("1770-2_Conf_Stereo_VinL+R-23LKFS.wav", -23, -7.9),
        ("1770-2_Conf_Stereo_VinL+R-24LKFS.wav", -24, -8.9),
    ],
)
def test_measure(
    signal_directory, input_path, expected_loudness, expected_peak, double
):
    loudness, tp = Meter().measure(signal_directory / input_path, as_double=double)
    assert is_close(tp, expected_peak)
    assert is_close(loudness, expected_loudness)


@pytest.mark.parametrize(
    "input_path,loudness",
    [
        ("1770-2_Comp_23LKFS_10000Hz_2ch.wav", -23),
        ("1770-2_Comp_23LKFS_2000Hz_2ch.wav", -23),
        ("1770-2_Comp_23LKFS_1000Hz_2ch.wav", -23),
        ("1770-2_Comp_23LKFS_500Hz_2ch.wav", -23),
        ("1770-2_Comp_23LKFS_100Hz_2ch.wav", -23),
        ("1770-2_Comp_23LKFS_25Hz_2ch.wav", -23),
        ("1770-2_Comp_24LKFS_10000Hz_2ch.wav", -24),
        ("1770-2_Comp_24LKFS_2000Hz_2ch.wav", -24),
        ("1770-2_Comp_24LKFS_1000Hz_2ch.wav", -24),
        ("1770-2_Comp_24LKFS_100Hz_2ch.wav", -24),
        ("1770-2_Comp_24LKFS_500Hz_2ch.wav", -24),
        ("1770-2_Comp_24LKFS_25Hz_2ch.wav", -24),
        ("1770-2_Conf_Mono_Voice+Music-23LKFS.wav", -23),
        ("1770-2_Conf_Mono_Voice+Music-24LKFS.wav", -23),
        ("1770-2_Conf_Stereo_VinL+R-23LKFS.wav", -23),
        ("1770-2_Conf_Stereo_VinL+R-24LKFS.wav", -24),
    ],
)
def test_normalize(signal_directory, input_path, loudness):
    input_path = signal_directory / input_path

    with TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test.wav"

        deviation_dbtp = 5
        tld = randint(loudness - deviation_dbtp, loudness + deviation_dbtp)
        normalize(input_path, output_path, tld, -1)

        ld, pk = Meter().measure(str(output_path))
        assert is_close(ld, tld)
        assert pk < -1

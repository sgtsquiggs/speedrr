import pytest

from helpers.bit_convert import bit_conv, bit_convertion_dict


@pytest.mark.parametrize(
    "value,src,dst,expected",
    [
        (1, "Mbit", "Mbit", 1.0),
        (1, "B", "bit", 8.0),
        (1, "bit", "B", 0.125),
        (1, "Kbit", "bit", 1000.0),
        (1, "Kibit", "bit", 1024.0),
        (1, "MB", "Mbit", 8.0),
        (400, "Mbit", "B", 50000000.0),
        (1, "Mbit", "B", 125000.0),
    ],
)
def test_known_conversions(value, src, dst, expected):
    assert bit_conv(value, src, dst) == expected


@pytest.mark.parametrize(
    "acronym,full_name",
    [
        ("B", "byte"),
        ("Kbit", "kilobit"),
        ("Kibit", "kibibit"),
        ("KB", "kilobyte"),
        ("KiB", "kibibyte"),
        ("Mbit", "megabit"),
        ("Mibit", "mebibit"),
        ("MB", "megabyte"),
        ("MiB", "mebibyte"),
        ("Gbit", "gigabit"),
        ("Gibit", "gibibit"),
        ("GB", "gigabyte"),
        ("GiB", "gibibyte"),
    ],
)
def test_acronym_and_full_name_agree(acronym, full_name):
    assert bit_conv(1, acronym, "bit") == bit_conv(1, full_name, "bit")


def test_every_unit_round_trips_through_bit():
    for unit in bit_convertion_dict:
        assert bit_conv(bit_conv(1024, unit, "bit"), "bit", unit) == 1024.0


def test_rounds_to_three_decimal_places_and_can_underflow_to_zero():
    # 1 bit expressed in GB is 1.25e-10, which round(_, 3) flattens to 0.0.
    # Callers that must not hit zero are responsible for flooring; see
    # qBittorrentClient.set_upload_speed, which wraps this in max(1, ...).
    assert bit_conv(1, "bit", "GB") == 0.0


def test_unknown_unit_raises_keyerror():
    with pytest.raises(KeyError):
        bit_conv(1, "furlongs", "bit")

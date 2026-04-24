from my_functions import is_even, reverse_string, power


def test_is_even():
    assert is_even(256) is True


def test_reverse_string():
    assert reverse_string("hello") == "olleh"


def test_power():
    assert power(2, 3) == 8
"""Tests for the calculator module."""

import pytest

from calculator import add, divide, multiply, subtract


def test_add():
    assert add(2, 3) == 5
    assert add(-1, 1) == 0
    assert add(2.5, 0.5) == 3.0


def test_subtract():
    assert subtract(5, 3) == 2
    assert subtract(0, 4) == -4
    assert subtract(2.5, 0.5) == 2.0


def test_multiply():
    assert multiply(3, 4) == 12
    assert multiply(-2, 5) == -10
    assert multiply(0, 7) == 0


def test_divide():
    assert divide(10, 2) == 5
    assert divide(-9, 3) == -3
    assert divide(1, 4) == 0.25


def test_divide_by_zero():
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(1, 0)

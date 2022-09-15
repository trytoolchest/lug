import functools

import numpy as np
import pytest

from lug.lug import get_modules_to_register


def func_that_uses_numpy_and_lug():
    return np.euler_gamma


def decorator(func):
    @functools.wraps(func)
    def inner(*args, **kwargs):
        modules_to_register = get_modules_to_register(func)
        module_names = sorted([module.__name__ for module in modules_to_register])
        assert module_names == ["_pytest.assertion.rewrite", "numpy", "pytest"]
        return func(*args, **kwargs)
    return inner


@pytest.mark.unit
def test_module_registration():
    wrapped_func = decorator(func_that_uses_numpy_and_lug)
    wrapped_func()


import functools

import idna
import pytest


def func_that_uses_idna():
    return idna.encode('ドメイン.テスト')


def decoy_function_with_unpicklable_library():
    """This doesn't actually run – it's a decoy function to make sure import pickling is appropriately scoped"""
    import lug
    lug.lug.unpatch_system_calls(func_that_uses_idna)


def lug_simulating_decorator(func):
    from lug.lug import get_modules_to_register

    @functools.wraps(func)
    def inner(*args, **kwargs):
        modules_to_register = get_modules_to_register(func)
        module_names = sorted([module.__name__ for module in modules_to_register])
        assert module_names == [
            '_pytest.assertion.rewrite',
            'idna',
            'test_module_registration',
        ]
        return func(*args, **kwargs)
    return inner


@pytest.mark.unit
def test_module_registration():
    wrapped_func = lug_simulating_decorator(func_that_uses_idna)
    assert wrapped_func() == b'xn--eckwd4c7c.xn--zckzah'


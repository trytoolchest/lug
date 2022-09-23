import idna
import pytest

from .test_module_detection import lug_simulating_decorator


def func_that_uses_idna():
    return idna.encode('ドメイン.テスト')


def decoy_function_with_unpicklable_library():
    """This doesn't actually run – it's a decoy function to make sure import detection is appropriately scoped"""
    import docker
    return docker


@pytest.mark.unit
def test_module_detection_simple():
    wrapped_func = lug_simulating_decorator(
        func=func_that_uses_idna,
        assert_module_names=[
            '_pytest.assertion.rewrite',
            'idna',
            'test_module_registration.test_module_detection',
            'test_module_registration.test_simple_package'
        ]
    )
    assert wrapped_func() == b'xn--eckwd4c7c.xn--zckzah'

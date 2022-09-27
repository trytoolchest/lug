import pytest
import six

from .test_module_detection import lug_simulating_decorator


def func_that_uses_six():
    return six


@pytest.mark.unit
def test_module_detection_module_dependency():
    wrapped_func = lug_simulating_decorator(
        func=func_that_uses_six,
        assert_module_names=[
            '_pytest.assertion.rewrite',
            'six',
            'test_module_registration.test_module_detection',
            'test_module_registration.test_package_with_dependency'
        ],
    )
    assert wrapped_func() == six

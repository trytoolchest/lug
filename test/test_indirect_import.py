"""Tests importing a patched call from a relative module, different than the lug-decorated function"""
import pytest

import lug
from test.base import base_test_decorator, BASE_TEST_IMAGE
# The below imports should be kept as relative imports for testing
from .test_os_system.indirect_import_helper_system import patched_system_subfunction
from .test_os_system.indirect_import_helper_os_system import patched_os_system_subfunction
from .test_subprocess_popen.indirect_import_helper_popen import patched_popen_subfunction
from .test_subprocess_popen.indirect_import_helper_subprocess_popen \
    import patched_subprocess_popen_subfunction
from .test_subprocess_run.indirect_import_helper_run import patched_run_subfunction
from .test_subprocess_run.indirect_import_helper_subprocess_run \
    import patched_subprocess_run_subfunction


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_system_indirect_import(number, **kwargs):
    patched_system_subfunction()
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_os_system_indirect_import(number, **kwargs):
    patched_os_system_subfunction()
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_popen_indirect_import(number, **kwargs):
    patched_popen_subfunction()
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_subprocess_popen_indirect_import(number, **kwargs):
    patched_subprocess_popen_subfunction()
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_run_indirect_import(number, **kwargs):
    patched_run_subfunction()
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_subprocess_run_indirect_import(number, **kwargs):
    patched_subprocess_run_subfunction()
    return number

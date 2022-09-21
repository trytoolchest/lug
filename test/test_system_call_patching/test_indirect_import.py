"""Tests importing a patched call from a relative module, different than the lug-decorated function"""
import pytest

import lug
from .base import BASE_TEST_IMAGE
# The below imports should be kept as relative imports for testing
from .test_relative_import_patching.subprocess_run import subprocess_run


@pytest.mark.unit
@lug.run(image=BASE_TEST_IMAGE)
def test_subprocess_run_indirect_import():
    result = subprocess_run()
    assert result == "Hello, Linux!\n"

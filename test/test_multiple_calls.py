"""Tests multiple calls to os.system and subprocess.run"""
import os
import subprocess
from subprocess import Popen

import pytest

import lug
from test.base import base_test_decorator, BASE_TEST_IMAGE


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_multiple_calls(number, **kwargs):
    return_code_1 = os.system("echo one")
    proc_2 = subprocess.run("echo two", shell=True)
    proc_3 = subprocess.Popen("echo three", shell=True)
    proc_4 = Popen("echo four", shell=True)
    assert return_code_1 == 0
    assert proc_2.returncode == 0
    assert proc_3.wait() == 0
    assert proc_4.wait() == 0
    return number

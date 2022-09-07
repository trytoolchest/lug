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
    os.system("echo one")
    subprocess.run("echo two", shell=True)
    subprocess.Popen("echo three", shell=True)
    Popen("echo four", shell=True)
    return number

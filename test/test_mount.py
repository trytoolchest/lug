"""Tests mounting from paths other than the cwd"""
import os
import shutil

import pytest

import lug
from test.base import BASE_TEST_IMAGE


@lug.run(image=BASE_TEST_IMAGE, mount="./temp_test_lug_mount")
def function_with_different_mount(number):
    command = "echo hello world > /lug/output.txt"
    os.system(command)
    return number


@pytest.mark.unit_io
def test_mount_subfolder():
    number = 4
    temp_dir = "./temp_test_lug_mount"
    os.makedirs(temp_dir, exist_ok=True)
    return_value = function_with_different_mount(number)
    assert return_value == number
    with open(f"{temp_dir}/output.txt", "r") as outfile:
        assert outfile.read() == "hello world\n"  # echo piping ends with a newline
    shutil.rmtree(temp_dir)

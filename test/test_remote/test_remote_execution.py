import os
import subprocess

import pathlib
import pytest

import lug
from test.base import BASE_TEST_IMAGE, remote_test_decorator
from test.multiple_imports_helper import multiply_some_constants

THIS_FILE_PATH = pathlib.Path(__file__).parent.resolve()


@pytest.mark.integration
@remote_test_decorator(expected_value="Hello, world!")
@lug.run(image=BASE_TEST_IMAGE, remote=True, remote_inputs=[os.path.join(THIS_FILE_PATH, "test_input.txt")],
         remote_output_directory="./temp_test_output", remote_instance_type="compute-2", volume_size=16)
def test_remote_execution():
    result = subprocess.run("cat ./input/test_input.txt", text=True, capture_output=True, shell=True)
    return result.stdout


@pytest.mark.integration
@remote_test_decorator(expected_value="7")
@lug.run(image=BASE_TEST_IMAGE, remote=True, remote_inputs=[os.path.join(THIS_FILE_PATH, "test_input.txt")],
         remote_output_directory="./temp_test_output", remote_instance_type="compute-2", volume_size=16)
def test_remote_execution_with_imports():
    """Tests importing multiple module dependencies, including non-built-ins and ones located in other files."""
    # This function uses imports of `numpy` (non-built-in) from a helper module.
    result = subprocess.run(f"expr {multiply_some_constants(4)}", text=True, capture_output=True, shell=True)
    return result.stdout

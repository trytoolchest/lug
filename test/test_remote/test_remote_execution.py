import os
import subprocess

import pathlib
import pytest

import lug
import toolchest_client as tc
from test.base import BASE_TEST_IMAGE, remote_test_decorator
from test.test_remote.remote_import_helper import encode_an_example_string

THIS_FILE_PATH = pathlib.Path(__file__).parent.resolve()


@pytest.mark.integration
@remote_test_decorator(expected_value="Hello, world!")
@lug.run(image=BASE_TEST_IMAGE, remote=True, remote_inputs=[os.path.join(THIS_FILE_PATH, "test_input.txt")],
         remote_output_directory="./temp_test_output", remote_instance_type="compute-2", volume_size=16)
def test_remote_execution():
    result = subprocess.run("cat ./input/test_input.txt", text=True, capture_output=True, shell=True)
    return result.stdout


@lug.run(image=BASE_TEST_IMAGE, remote=True, remote_inputs=[os.path.join(THIS_FILE_PATH, "test_input.txt")],
         remote_output_directory="./temp_test_output", remote_instance_type="compute-2", volume_size=16)
def test_remote_execution_with_imports():
    """Tests importing multiple module dependencies, including non-built-ins and ones located in other files."""
    # This function uses imports of `idna` (non-built-in) from a helper module.
    result = subprocess.run(f"echo {encode_an_example_string()}", text=True, capture_output=True, shell=True)
    return result.stdout


@pytest.mark.integration
def test_remote_call_sans_pytest_decorator():
    results = test_remote_execution_with_imports()
    assert results == 'bxn--eckwd4c7c.xn--zckzah\n'


@lug.run(image=BASE_TEST_IMAGE, remote=True, remote_inputs=[os.path.join(THIS_FILE_PATH, "test_input.txt")],
         remote_output_directory="./temp_test_output", remote_instance_type="compute-2", volume_size=16)
def test_remote_execution_with_toolchest_lugged():
    result = tc.test(
        inputs="./input/test_input.txt",
        output_path="./output/",
    )
    return result


@pytest.mark.integration
def test_remote_execution_with_toolchest():
    results = test_remote_execution_with_imports()
    print(results)
    with open(os.path.join('temp_test_output', 'test_output.txt')) as file:
        content = file.readlines()
        assert content == "success"

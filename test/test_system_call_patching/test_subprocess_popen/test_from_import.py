import random
from subprocess import Popen
import time
from time import sleep

import pytest

import lug
from ..base import BASE_TEST_IMAGE, SLEEP_TIME, base_test_decorator, error_test_decorator, io_test_decorator
from ..multiple_imports_helper import function_that_uses_imported_modules


@pytest.mark.unit
@error_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_expected_error():
    """Tests lug behavior on return value + error propagation
    when an error is hit within the function body"""
    result = Popen("exit 1", shell=True)
    if result.returncode != 0:
        raise RuntimeError("Nonzero exit code (expected)")


@pytest.mark.unit_io
@io_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_concatenate_text_io(input_basename, output_basename, number, text="a", **kwargs):
    """Tests behavior with input and output files (mounted at /lug)"""
    Popen(f"echo '{text}' > added.txt; cat /lug/{input_basename} added.txt > /lug/{output_basename}", shell=True)
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_multiple_imports(number, **kwargs):
    """Tests importing multiple module dependencies, including non-built-ins and ones located in other files."""
    # This function uses imports of `random` from this module
    # and `math` + `idna` (non-built-in) from a helper module.
    example_number, example_string = function_that_uses_imported_modules(number)
    Popen(f"expr {random.getrandbits(1)} + {example_number}; echo {example_string}", shell=True)
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_sleep_cmd(number, **kwargs):
    Popen(f"sleep {SLEEP_TIME}; echo $PATH", shell=True)
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_from_time_sleep_script(number, **kwargs):
    sleep(SLEEP_TIME)
    Popen("echo $PATH", shell=True)
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_sleep_script(number, **kwargs):
    time.sleep(SLEEP_TIME)
    Popen("echo $PATH", shell=True)
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_subfunction(number, **kwargs):
    """Tests behavior with a sub-function not directly decorated with lug"""
    run_value = Popen("echo $PATH", shell=True)
    print("return code:", run_value.wait())
    print("run_value.args:", run_value.args)
    print("before subfunction")
    subfunction(**kwargs)
    return number


def subfunction(name='World'):
    print(f"{name}!")


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_without_shell(number, **kwargs):
    """Tests behavior when shell=True is not specified and a list is passed in as args."""
    run_value = Popen(["/bin/ls", "-l"])
    print("return code:", run_value.wait())
    return number

import os
import random
import time
from time import sleep

import pytest

import lug
from test.base import BASE_TEST_IMAGE, SLEEP_TIME, base_test_decorator, \
    error_test_decorator, io_test_decorator
from test.multiple_imports_helper import function_that_uses_imported_modules


@pytest.mark.unit
@error_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_expected_error():
    """Tests lug behavior on return value + error propagation
    when an error is hit within the function body"""
    return_code = os.system("exit 1")
    if return_code != 0:
        raise RuntimeError("Nonzero exit code (expected)")


@pytest.mark.unit_io
@io_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_concatenate_text_io(input_basename, output_basename, number, text="a", **kwargs):
    """Tests behavior with input and output files (mounted at /lug)"""
    os.system(f"echo '{text}' > added.txt; cat /lug/{input_basename} added.txt > /lug/{output_basename}")
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_multiple_imports(number, **kwargs):
    """Tests importing multiple module dependencies, including non-built-ins and ones located in other files."""
    # This function uses imports of `random` from this module
    # and `math` + `idna` (non-built-in) from a helper module.
    example_number, example_string = function_that_uses_imported_modules(number)
    os.system(f"expr {random.getrandbits(1)} + {example_number}; echo {example_string}")
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_sleep_cmd(number, **kwargs):
    os.system(f"sleep {SLEEP_TIME}; echo $PATH")
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_from_time_sleep_script(number, **kwargs):
    sleep(SLEEP_TIME)
    os.system("echo $PATH")
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_sleep_script(number, **kwargs):
    time.sleep(SLEEP_TIME)
    os.system("echo $PATH")
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_subfunction(number, **kwargs):
    """Tests behavior with a sub-function not directly decorated with lug"""
    run_value = os.system("echo $PATH")
    print("return code:", run_value)
    print("before subfunction")
    subfunction(**kwargs)
    return number


def subfunction(name='World'):
    print(f"{name}!")

import random
import subprocess
import time
from time import sleep

import pytest

import lug
from test.base import BASE_TEST_IMAGE, SLEEP_TIME, base_test_decorator, \
    error_test_decorator, io_test_decorator
from test.multiple_imports_helper import multiply_some_constants


@pytest.mark.unit
@error_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_expected_error():
    """Tests lug behavior on return value + error propagation
    when an error is hit within the function body"""
    proc = subprocess.run("exit 1", shell=True)
    assert proc.returncode == 1
    try:
        proc.check_returncode()
    except subprocess.CalledProcessError:
        raise RuntimeError("Nonzero exit code (expected)")


@pytest.mark.unit_io
@io_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_concatenate_text_io(input_basename, output_basename, number, text="a", **kwargs):
    """Tests behavior with input and output files (mounted at /lug)"""
    proc = subprocess.run(f"echo '{text}' > added.txt; cat /lug/{input_basename} added.txt > /lug/{output_basename}",
                          shell=True)
    assert proc.returncode == 0
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_multiple_imports(number, **kwargs):
    """Tests importing multiple module dependencies, including non-built-ins and ones located in other files."""
    # This function uses imports of `random` from this module
    # and `math` + `numpy` (non-built-in) from a helper module.
    proc = subprocess.run(f"expr {random.getrandbits(1)} + {multiply_some_constants(number)}", shell=True)
    assert proc.returncode == 0
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_sleep_cmd(number, **kwargs):
    proc = subprocess.run(f"sleep {SLEEP_TIME}; echo $PATH", shell=True)
    assert proc.returncode == 0
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_from_time_sleep_script(number, **kwargs):
    sleep(SLEEP_TIME)
    proc = subprocess.run("echo $PATH", shell=True)
    assert proc.returncode == 0
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_sleep_script(number, **kwargs):
    time.sleep(SLEEP_TIME)
    proc = subprocess.run("echo $PATH", shell=True)
    assert proc.returncode == 0
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_subfunction(number, **kwargs):
    """Tests behavior with a sub-function not directly decorated with lug"""
    proc = subprocess.run("echo $PATH", shell=True)
    assert proc.returncode == 0
    print("proc.args:", proc.args)
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
    proc = subprocess.run(["/bin/ls", "-l"])
    assert proc.returncode == 0
    return number


@pytest.mark.unit
@base_test_decorator
@lug.run(image=BASE_TEST_IMAGE)
def test_check_output_redirects(number, **kwargs):
    """Tests behavior when shell=True is not specified and a list is passed in as args."""
    proc = subprocess.run(["ls", "/"], capture_output=True, text=True)
    assert proc.stdout == "bin\ndev\netc\nhome\nlib\nlug\nmedia\nmnt\nopt\nproc\n" \
                          "root\nrun\nsbin\nsrv\nsys\ntmp\nusr\nvar\n"
    return number

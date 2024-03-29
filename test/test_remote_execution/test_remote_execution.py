import os
import subprocess
import pathlib
import pytest

import lug
from .remote_import_helper import encode_an_example_string

THIS_FILE_PATH = pathlib.Path(__file__).parent.resolve()
BASE_TEST_IMAGE = "alpine:3.16.2"


@lug.run(image=BASE_TEST_IMAGE, remote=True)
def standard_remote_execution():
    result = subprocess.run('echo "Hello, `uname`!"', text=True, capture_output=True, shell=True)
    return result.stdout


def test_standard_remote_execution():
    results = standard_remote_execution()
    assert results == 'Hello, Linux!\n'


@lug.run(image=BASE_TEST_IMAGE, remote=True, remote_inputs=[os.path.join(THIS_FILE_PATH, "test_input.txt")],
         remote_output_directory="./temp_test_output", remote_instance_type="compute-2", volume_size=16,
         serialize_dependencies=True)
def remote_execution_with_imports():
    """Tests importing multiple module dependencies, including non-built-ins and ones located in other files."""
    # This function uses imports of `idna` (non-built-in) from a helper module.
    result = subprocess.run(f"echo {encode_an_example_string()}", text=True, capture_output=True, shell=True)
    return result.stdout


@pytest.mark.integration
def test_remote_call_sans_pytest_decorator():
    results = remote_execution_with_imports()
    assert results == 'bxn--eckwd4c7c.xn--zckzah\n'


@lug.docker_sidecar(sidecar_image="python:bullseye", cloud=True)
def docker_sidecar_shell():
    return lug.sidecar_shell('echo "Hello, `cat /etc/os-release`!"')


@pytest.mark.integration
def test_docker_sidecar_shell():
    result = docker_sidecar_shell()
    assert "Debian GNU/Linux 11 (bullseye)" in result.stdout


def run_hybrid_in_cloud_wrapper(provider):
    @lug.hybrid(cloud=True, provider=provider)
    def run_hybrid_in_cloud():
        return subprocess.run('echo "Hello, `cat /etc/os-release`!"', text=True, capture_output=True, shell=True)
    return run_hybrid_in_cloud


def run_hybrid_locally_wrapper(provider):
    @lug.hybrid(cloud=False, provider=provider)
    def run_hybrid_locally():
        return subprocess.run('echo "Hello, `cat /etc/os-release`!"', text=True, capture_output=True, shell=True)
    return run_hybrid_locally


@pytest.mark.integration
@pytest.mark.parametrize("provider", ["aws", "tce"])
def test_hybrid_execution(provider):
    parametrized_local = run_hybrid_locally_wrapper(provider)
    local_result = parametrized_local()
    assert "Debian GNU/Linux 11 (bullseye)" not in local_result.stdout
    assert local_result.returncode == 0
    parametrized_cloud = run_hybrid_in_cloud_wrapper(provider)
    cloud_result = parametrized_cloud()
    assert "Debian GNU/Linux 11 (bullseye)" in cloud_result.stdout

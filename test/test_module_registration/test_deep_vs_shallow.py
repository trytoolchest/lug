import docker
import pytest

from .test_module_detection import lug_simulating_decorator


def func_that_uses_docker():
    return docker


@pytest.mark.unit
def test_module_detection_docker_shallow():
    wrapped_func = lug_simulating_decorator(
        func=func_that_uses_docker,
        assert_module_names=[
            '_pytest.assertion.rewrite',
            'docker',
            'test_module_registration.test_deep_vs_shallow',
            'test_module_registration.test_module_detection'
        ],
        modules_to_skip=frozenset({"pytest", "lug", "cloudpickle"}),  # exclude docker from skip list
    )
    assert wrapped_func() == docker


@pytest.mark.unit
def test_module_detection_docker_deep():
    wrapped_func = lug_simulating_decorator(
        func=func_that_uses_docker,
        assert_module_names=[
            '_pytest.assertion.rewrite',
            'docker',
            'docker.api',
            'docker.constants',
            'docker.context',
            'docker.context.config',
            'docker.errors',
            'docker.tls',
            'docker.transport.basehttpadapter',
            'docker.types',
            'docker.utils.config',
            'http.client',
            'importlib.metadata',
            'json.decoder',
            'lug.module_detection',
            'packaging.version',
            'posixpath',
            'requests',
            'requests.adapters',
            'requests.exceptions',
            'test_module_registration.test_deep_vs_shallow',
            'test_module_registration.test_module_detection',
            'urllib.parse',
            'urllib3',
            'websocket'
        ],
        deep=True,
        modules_to_skip=frozenset({"pytest", "lug", "cloudpickle"})  # exclude docker from skip list
    )
    assert wrapped_func() == docker

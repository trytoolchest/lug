import functools


def lug_simulating_decorator(
        func,
        assert_module_names,
        deep=False,
        modules_to_skip=frozenset({"pytest", "lug", "cloudpickle", "docker", "toolchest_client"})
):
    from lug.module_detection import get_modules_to_register

    @functools.wraps(func)
    def inner(*args, **kwargs):
        modules_to_register = get_modules_to_register(func, deep=deep, modules_to_skip=modules_to_skip)
        module_names = sorted([module.__name__ for module in modules_to_register])
        assert module_names == assert_module_names
        return func(*args, **kwargs)

    return inner

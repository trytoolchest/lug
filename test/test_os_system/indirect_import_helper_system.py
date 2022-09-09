from os import system


def patched_system_subfunction():
    return_code = system("echo hello world")
    assert return_code == 0

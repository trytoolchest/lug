import os


def patched_os_system_subfunction():
    return_code = os.system("echo hello world")
    assert return_code == 0

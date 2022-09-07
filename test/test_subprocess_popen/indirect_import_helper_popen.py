from subprocess import Popen


def patched_popen_subfunction():
    Popen("echo hello world", shell=True)

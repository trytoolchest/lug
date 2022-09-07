from os import system


def patched_system_subfunction():
    system("echo hello world")

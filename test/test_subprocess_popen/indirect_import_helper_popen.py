from subprocess import Popen


def patched_popen_subfunction():
    proc = Popen("echo hello world", shell=True)
    assert proc.wait() == 0

import subprocess


def patched_subprocess_popen_subfunction():
    proc = subprocess.Popen("echo hello world", shell=True)
    assert proc.wait() == 0

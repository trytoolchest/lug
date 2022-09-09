import subprocess


def patched_subprocess_run_subfunction():
    proc = subprocess.run("echo hello world", shell=True)
    assert proc.returncode == 0

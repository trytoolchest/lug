from subprocess import run


def patched_run_subfunction():
    proc = run("echo hello world", shell=True)
    assert proc.returncode == 0

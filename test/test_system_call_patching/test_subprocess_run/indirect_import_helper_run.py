from subprocess import run


def patched_run_subfunction():
    run("echo hello world", shell=True)

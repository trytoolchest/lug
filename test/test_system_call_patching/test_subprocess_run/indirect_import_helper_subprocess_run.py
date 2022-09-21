import subprocess


def patched_subprocess_run_subfunction():
    subprocess.run("echo hello world", shell=True)

import subprocess


def patched_subprocess_popen_subfunction():
    subprocess.Popen("echo hello world", shell=True)

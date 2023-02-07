import subprocess


def sidecar_shell(command, **kwargs):
    """
    This function is redirected to the Lug sidecar container. The first arg must remain the shell command.
    """
    result = subprocess.run(
        command,
        text=True,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        **kwargs,
    )
    return result

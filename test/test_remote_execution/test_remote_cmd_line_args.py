import argparse
import lug
import subprocess

import pytest


@lug.run(
    image="alpine:3.16.2",
    remote=True,
    command_line_args=["--value-to-print", "Hello"],
)
def say_hello():
    parser = argparse.ArgumentParser()
    parser.add_argument("--value-to-print",
                        dest="value_to_print")

    result = subprocess.run(f"echo {parser.parse_args().value_to_print}", capture_output=True, text=True, shell=True)
    return result.stdout


@pytest.mark.integration
def test_remote_call_with_cmd_line_args():
    result_stdout = say_hello()
    assert result_stdout == "Hello\n"  # newline added by shell after echo call

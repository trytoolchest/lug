"""Single source for constants and decorator functions throughout the test suite."""
import functools
from os.path import basename
import tempfile

BASE_TEST_IMAGE = "ncbi/blast"
SLEEP_TIME = 5


def base_test_decorator(func):
    # Tests whether a number passed into the function is returned,
    # indicating that the function was executed successfully via lug.
    def wrapper():
        number = 4
        result = func(number, name="Bob")
        print(f"Result: {result}. Is {number}? {result == number}")
        assert result == number
    return wrapper


def remote_test_decorator(expected_value=None):
    def decorator_remote(func):
        @functools.wraps(func)
        # Tests whether a test file generated on a remote docker container
        # is successfully transferred to the client.
        def inner():
            result = func()
            print(f"Result: {result}")
            assert result == expected_value
        return inner
    return decorator_remote


def io_test_decorator(concatenate_text_func):
    # Tests whether inputs and outputs are correctly processed
    # in a text concatenation test via lug.
    def wrapper():
        number = 4
        input_file = tempfile.NamedTemporaryFile(mode='w', dir='.')
        output_file = tempfile.NamedTemporaryFile(mode='w+', dir='.')
        input_file.write("(this is the original text)")
        input_file.flush()  # necessary for original text to be written + readable

        result = concatenate_text_func(
            f"{basename(input_file.name)}",
            f"{basename(output_file.name)}",
            number,
            text="[this text is concatenated]",
            name="Bob"
        )
        print(f"Result: {result}. Is {number}? {result == number}")
        assert result == number
        assert output_file.read() == "(this is the original text)[this text is concatenated]\n"  # cat adds a newline
    return wrapper


def error_test_decorator(func):
    # Tests whether an error in a lug-decorated function
    # is properly propagated to the invoker.
    def wrapper():
        try:
            func()
            assert False
        except RuntimeError:
            assert True
    return wrapper

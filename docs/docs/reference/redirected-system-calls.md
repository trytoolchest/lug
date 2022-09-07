# Redirected system calls

## How Lug detects and redirects functions

Lug finds calls to supported functions and re-routes them to the Docker container. It digs three layers deep, starting 
with the decorated function and including all references up to three steps away.

This means that a call to `subproccess.run` in the Lug-decorated function would be redirected, and so would a 
`subprocess.run` call that happens in a function called by the Lug-decorated function. The same call that happens after 
chain of five function calls would not be re-routed, unless it shares the same reference.

For example, both of these `subprocess.run` calls run in the Docker container even though only `hello_world` is 
decorated:

```python
import lug
import subprocess

def my_name_is():
    result = subprocess.run('echo "My name is `uname`."', capture_output=True, text=True, shell=True)
    return result.stdout

@lug.run(image="alpine:3.16.2")
def hello_world():
    result = subprocess.run('echo "Hello, `uname`!"', capture_output=True, text=True, shell=True)
    return result.stdout + my_name_is()

print(hello_world())
```

Running from macOS with a Linux Docker image prints:
```
Hello, Linux!
My name is Linux.
```

## Supported functions

### `os.system`

The single string argument to `os.system` is redirected to the Docker container.

The `docker_shell_location` argument is ignored.

### `subprocess.Popen`

The entire `subprocess.Popen` call is redirected to the Docker container.

The `docker_shell_location` argument is only used if `shell=True` is not set.

Functionality is nearly identical to executing locally – you can even call `.wait()` after spawning a new process.

### `subprocess.run`

The entire `subprocess.run` call is redirected to the Docker container.

The `docker_shell_location` argument is only used if `shell=True` is not set.

### Any function that uses any of the above calls under the hood is supported

## Unsupported functions

### Direct calls to any system call, below the `subprocess.Popen` layer

A direct C `system` call that's executed without going through `os.system`, `subprocess.run`, or 
`subprocess.Popen` would not be redirected to the Docker container.
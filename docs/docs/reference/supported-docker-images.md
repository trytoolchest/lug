# Supported Docker images

## What is supported?

### Images that have interactive shell support

Lug assumes that a shell is supported at `/bin/sh`. If you want to use a different type of shell, like `/bin/bash`, you 
can set it using the `docker_shell_location` Lug argument:

```python
@lug.run(image="alpine:3.16.2", docker_shell_location="/bin/bash")
def hello_world():
    result = subprocess.run('asdf "Hello, `uname`!"', capture_output=True, text=True, shell=True)
    return result.stdout

print(hello_world())
```

### Docker images that don't have Python

You don't need Python on your Docker image with Lug! Lug handles your Python code independently of the Docker container 
you set.

### Posix file systems (macOS, most Linux distros)

Some functionality will work on other systems, but everything is tested using Linux and macOS.

## What isn't supported?

- Docker images that don't have the ability to open a shell
- Running your Lug-decorated Python function inside the Docker container
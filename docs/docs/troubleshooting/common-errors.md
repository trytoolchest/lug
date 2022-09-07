# Common errors

## Docker isn't installed or running

### What it looks like:

```
docker.errors.DockerException: Error while fetching server API version: ('Connection aborted.', FileNotFoundError(2, 'No such file or directory'))
```

### How to solve it:

Install and start Docker Engine: https://docs.docker.com/engine/install/

## `subprocess.run` can't find your command

### What it looks like:

```
FileNotFoundError: [Errno 2] No such file or directory: 'docker exec lug-c8eef2d5-adcd-4263-bf67-061b7ea56f68 /bin/sh -c \'echo "Hello, `uname`!"\''
```

```
(no output, when you're expecting output)
```

### How to solve it:

- If you're using `subprocess.run`, try setting using the `shell=True` argument. This sets a shell location and accepts 
string commands as input, just like a terminal.  
- Make sure that the command exists in the Docker image, and if it's not in the `$PATH` use an absolute reference path.

## It runs slowly

### What it looks like:

The command runs slower than expected (e.g. 2x longer than before), after factoring in Docker container start time.

### How to solve it:

Docker runs Linux containers in a VM on non-Linux machines. If you're using macOS, for example, Lug will run slower 
than if you're on Linux.

You can get more speed by running remotely with `remote=True` – under the hood, this uses a Linux machine.

Without running remotely, this can't be solved without changing operating systems. If a Docker replacement comes along 
that executes across different architectures with no VM, this could be solved!
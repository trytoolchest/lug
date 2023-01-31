# Using files

## Using files locally with Docker images

When running a function with Lug locally, the Python function's file access doesn't change. You can skip this section!

If you're using a sidecar Docker container, Lug mounts your system's file system at `/lug` inside the container.

By default, Lug mounts the current working directory to `/lug`. You can change this with the `mount` parameter.

!!! tip "Lug's `mount` is a Docker mount point"

    Lug's `mount` is a Docker mount point. This means that Docker must have permission to access the mount point. Some 
    environments, like Docker Desktop on macOS, require explicitly adding permissions for non-user files – even if 
    you're running as `root`.

This snippet grants mounts the root directory, but then uses a relative path to access a file one directory above the 
current working directory:

```python
import lug

@lug.docker_sidecar(image="alpine:3.16.2", mount="/")
def list_root():
    result = lug.sidecar_shell("ls /lug/")
    return result.stdout
    
print(list_root())
```

You'll see the output of `ls` on your root directory.

### Using absolute file paths

To use absolute paths in Lug, you'll need:

- to add a `/lug` prefix to the absolute path
- a mount point that contains the path you're referencing

```python
import lug
import os

@lug.docker_sidecar(sidecar_image="alpine:3.16.2", mount="/")
def cat_file(absolute_path):
    result = lug.sidecar_shell(f"cat /lug{absolute_path}")
    return result.stdout

absolute_path = os.path.abspath("test.txt")
with open(absolute_path, 'w') as f:
    f.write('Hello, world!')

print(cat_file(absolute_path))
```

If everything is working, you'll see `Hello, world!` printed.

## Using files remotely

To use remote files, you'll need to set up input and output file handling.

### Input files

All input files are passed to the Lug` remote_inputs` argument. They're accessible at `./input/` on the remote instance.


### Output files

All output files need to be written to `./output` on the remote instance. Set the `remote_output_directory` argument to 
a directory where Lug will transfer all the output files.

`remote_inputs` and `remote_output_directory` can be local files or S3 URIs.

###

```python
import lug
import os
import subprocess

@lug.hybrid(
    image="alpine:3.16.2",
    remote_inputs=["./my_input/"],
    remote_output_directory="./my_output/",
    remote=True,
    toolchest_key="KEY",
)
def hello_world():
    result = subprocess.run(f"cat ./input/test.txt > ./output/test2.txt", text=True, capture_output=True, shell=True)
    return result.stdout

os.makedirs("./my_input", exist_ok=True)
file_path = "./my_input/test.txt"
with open(file_path, 'w') as f:
    f.write('Hello, world!')

print(hello_world())
```

`./my_output/` now has a named `test.txt` with the contents "Hello, world!"

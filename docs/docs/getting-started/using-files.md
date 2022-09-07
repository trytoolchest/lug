# Using files

!!! warning "Lug is not a security boundary"

    We strongly recommend only running trusted code in trusted containers with Lug. It is possible to break out of 
    Lug's virtualization layer.

## Using files locally

When running a function with Lug locally, the Python function's file access does not change. The container – or, in 
other words, calls to `subprocess.run`, `subprocess.Popen`, and `os.system` – is limited to files in Lug's `mount` 
argument.

`mount` defaults to the current working directory, but you can pass a new mount point to grant greater access.

!!! tip "Lug's `mount` is a Docker mount point"

    Lug's `mount` is a Docker mount point. This means that Docker must have permission to access the mount point. Some 
    environments, like Docker Desktop on macOS, require explicitly adding permissions for non-user files – even if 
    you're running as `root`.

This grants full root directory access to Lug, but then uses a relative path to access a file one directory above the 
current working directory:

```python
import lug
import subprocess

@lug.run(image="alpine:3.16.2", mount="/")
def hello_world(file_path):
    result = subprocess.run(f"echo {file_path}", text=True, capture_output=True, shell=True)
    return result.stdout

file_path = "../test.txt"
with open(file_path, 'w') as f:
    f.write('Hello, world!')
    
print(hello_world(file_path))
```

You'll see `Hello, world!` printed.

### Absolute paths

To use absolute paths in Lug, you'll need:

- to add a `/lug` prefix to the absolute path
- a mount point that contains the path you're referencing

```python
import lug
import os
import subprocess

@lug.run(image="alpine:3.16.2", mount="/")
def hello_world(file_path):
    result = subprocess.run(f"cat /lug{file_path}", text=True, capture_output=True, shell=True)
    return result.stdout


file_path = os.path.abspath("test.txt")
with open(file_path, 'w') as f:
    f.write('Hello, world!')

print(hello_world(file_path))
```

You'll still see `Hello, world!` printed.

## Using files remotely

With remote execution, there are two new ways to access files:

1. You need to pass all input files to the Lug` remote_inputs` argument. They're accessible at `./input/`.

2. You need to set the Lug `remote_output_directory` argument to a directory, which will contain all files written to 
`./output/`.

You can pass local or S3 files to `remote_inputs`, and `remote_output_directory` can be local or on S3.

```python
import lug
import os
import subprocess

@lug.run(
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

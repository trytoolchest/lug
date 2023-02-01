# Using files

## Accessing files locally

When running a function with Lug locally, the Python function's file access doesn't change. If you aren't using 
Docker Sidecar, you can skip this section!

If you are running a Docker Sidecar function locally, the access to your system's file system is a bit different. The 
files in your system can be accessed inside the Docker container through the `/lug` directory. You can change the root 
directory that's attached to the container with the `mount` parameter.

Here's an example that accesses the root directory of the host file system from inside the Docker container:

```python
import lug

@lug.docker_sidecar(image="alpine:3.16.2", mount="/")
def list_root():
    result = lug.sidecar_shell("ls /lug/")
    return result.stdout
    
print(list_root())
```

In this example, the function `list_root` uses the `lug.sidecar_shell` function to execute the `ls` command inside the 
Docker container and returns the output. The `mount` parameter is set to `/`, so the root directory of the host's file 
system is mounted at `/lug` inside the Docker container.

!!! tip "Lug's `mount` is a Docker mount point"

    Lug's `mount` is a Docker mount point. This means that Docker must have permission to access the mount point. Some 
    environments, like Docker Desktop on macOS, require explicitly adding permissions for non-user files – even if 
    you're running as `root`.

### Accessing files with absolute paths

When using absolute paths in Lug, there are two things to keep in mind:

1. Add a `/lug` prefix to the absolute path inside the Docker container
2. The mount point set in the Docker sidecar should contain the path being referenced

Here's an example that accesses a file created on the host system from within the Docker container using an absolute 
path:

```python
import lug
import os

def create_file(absolute_path):
    with open(absolute_path, 'w') as f:
        f.write('Hello, world!')

@lug.docker_sidecar(sidecar_image="alpine:3.16.2", mount="/")
def cat_file(absolute_path):
    result = lug.sidecar_shell(f"cat /lug{absolute_path}")
    return result.stdout
    
absolute_path = os.path.abspath("test.txt")
create_file(absolute_path)
print(cat_file(absolute_path))
```

It will print `Hello, world!` if everything is set up correctly.

## Accessing files in cloud runs

To access files in remote runs, you need to set up input and output file handling.

### Input files

You can pass input files to a Lug function by using the `remote_inputs` argument. The input files are accessible at 
`./input/` on the remote instance.

### Output files

To access output files, you need to specify a directory for the output files using the `remote_output_directory` 
argument. The output files need to be written to `./output` on the remote instance.

Both `remote_intputs` and `remote_output_directory` can be local paths or S3 URIs.

### Example usage

Here's an example that shows how to use remote files with a Lug Docker Sidecar:


```python
import lug
import os

@lug.docker_sidecar(
    sidecar_image="alpine:3.16.2",
    remote_inputs=["./my_input/"],
    remote_output_directory="./my_output/",
    cloud=True,
    key="YOUR_KEY_HERE",
)
def hello_world():
    result = lug.sidecar_shell("cat ./input/one.txt > ./output/two.txt")
    return result.stdout

os.makedirs("./my_input", exist_ok=True)
file_path = "./my_input/one.txt"
with open(file_path, 'w') as f:
    f.write('Hello, world!')

hello_world()
```

The `./my_output/` now has a file named `two.txt` with the contents "Hello, world!"

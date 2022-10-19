# Running Lug remotely

## Running Lug in the Toolchest cloud

### Get a Toolchest API key

1. [Sign up for a Toolchest account](https://www.trytoolchest.com/)

### Add `remote=True` and your Toolchest key:

```python
import lug
import subprocess

@lug.run(image="alpine:3.16.2", remote=True, toolchest_key="YOUR_KEY")
def hello_world():
    result = subprocess.run('echo "Hello, `uname`!"', capture_output=True, text=True, shell=True)
    return result.stdout

print(hello_world())
```

That's it! There's about a minute of overhead, but once it's finished you'll once again see `Hello, Linux!`

### If needed, add more vCPUs, RAM, GPUs, and disk

By default, Lug runs remotely with 2 vCPUs, 4 GB of RAM, and 8 GB of disk.

To add more disk, use the `volume_size` argument. To add more vCPUs or RAM, use the `instance_type` argument.

Here's what it looks like to run with 48 vCPUs, 96 GB of RAM, and 512 GB of disk space:

```python
import lug
import subprocess

@lug.run(
    image="alpine:3.16.2",
    remote=True,
    toolchest_key="YOUR_KEY",
    volume_size=512,
    instance_type="compute-48",
)
def hello_world():
    result = subprocess.run('echo "Hello, `uname`!"', capture_output=True, text=True, shell=True)
    return result.stdout

print(hello_world())
```

See the Toolchest docs for a full list of [instance types](todo) and 
[pricing](https://docs.trytoolchest.com/docs/pricing).

### Command-line arguments
To pass in command-line arguments to your remotely executing script, use the `command_line_arguments` argument. 

This can be either a list or a single string of space-separated args. 
```python
import argparse
import lug
import subprocess

@lug.run(
    image="alpine:3.16.2",
    remote=True,
    toolchest_key="YOUR_KEY",
    command_line_args=["--value-to-print", "Hello"],
)
def say_hello():
    parser = argparse.ArgumentParser()
    parser.add_argument("--value-to-print",
                        dest="value_to_print")
    
    result = subprocess.run(f"echo {parser.parse_args().value_to_print}", capture_output=True, text=True, shell=True)
    return result.stdout

print(say_hello())
```

## Running Lug in AWS, Azure, GCP, or on-prem

You can run Lug on any machine, but automated cloud offloading isn't supported yet outside of Toolchest. PRs are welcome!


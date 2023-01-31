# Create a Docker Sidecar Function

Lug Docker Sidecar functions are Lug Hybrid functions with an extra benefit: they attach a running Docker container to 
your function. This is particularly useful for programs with very specific requirements function best in their own 
separate container.

## Creating a Docker Sidecar function locally

To create a Docker Sidecar Function, add the `@lug.docker_sidecar` decorator with `sidecar_image` set to the Docker 
image you want to use. Once that's set, you can use the `lug.sidecar_shell()` function to execute shell commands inside 
the container.

Here's an example that attaches a sidecar image for a bioinformatics package, and executes a simple command:

```python
import lug

@lug.docker_sidecar(sidecar_image='biocontainers/bowtie2:v2.4.1_cv1')
def run_bowtie2():
    result = lug.sidecar_shell("bowtie2 --version ")
    return result.stdout

print(run_bowtie2())
```

`lug.sidecar_shell()` calls a modified Python `subprocess.run` under the hood, so you expect common return values and 
attributes – like `.stdout` in the example above. You can also pass the same arguments to `lug.sidecar_shell` that you 
would to `subprocess.run` if needed.

### Running in the cloud

Just like with Hybrid functions, you can run a Docker Sidecar function in the cloud by adding `cloud=True` and setting 
your Toolchest key:

```python
import lug

@lug.docker_sidecar(
    sidecar_image='biocontainers/bowtie2:v2.4.1_cv1',
    cloud=True,
    key="YOUR_KEY_HERE"
)
def run_bowtie2():
    result = lug.sidecar_shell("bowtie2 --version ")
    return result.stdout

print(run_bowtie2())
```

You can also add more power or use a different provider, 
[just like you can with Hybrid functions](running-lug-remotely.md#run-your-hybrid-function-in-the-cloud).

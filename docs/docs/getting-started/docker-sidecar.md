# Create a Docker Sidecar Function

Lug Docker Sidecar functions are like regular Lug Hybrid functions, but with an added bonus: they run a Docker 
container alongside your function. This is helpful for programs that work best in their own separate container and that 
you execute via shell.

## Running locally

To create a Docker Sidecar function, use the `@lug.docker_sidecar` decorator and specify the Docker image you want to 
use with the `sidecar_image` argument. Then, you can use the `lug.sidecar_shell` function to run shell commands inside 
the container.

Here's an example that shows how to use a bioinformatics package in a sidecar container:

```python
import lug

@lug.docker_sidecar(sidecar_image='biocontainers/bowtie2:v2.4.1_cv1')
def run_bowtie2():
    result = lug.sidecar_shell("bowtie2 --version ")
    return result.stdout

print(run_bowtie2())
```

`lug.sidecar_shell()` is similar to the Python `subprocess.run` function, so you can expect similar return values and 
attributes – like `result.stdout` in the example above. You can also pass the same arguments to `lug.sidecar_shell` 
that you would to `subprocess.run`.

### Running in the cloud

Running a Docker Sidecar function in the cloud is exactly the same as running a Hybrid function in the cloud: you just 
need to add the `cloud=True` argument and set your Toolchest key:

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

You can also grant more power to your function or use a different cloud provider, 
[following the same steps as with Hybrid functions](running-lug-remotely.md#run-your-hybrid-function-in-the-cloud).

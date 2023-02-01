# Lug

<p align="center">
    <a href="https://pypi.python.org/pypi/lug/" alt="PyPI version">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/lug?labelColor=212121&color=304FFE"></a>
    <a href="https://github.com/trytoolchest/lug/" alt="Build">
        <img src="https://img.shields.io/circleci/build/gh/trytoolchest/lug/main?label=build&token=3eb013dde86ed79996a768ab325cd30ea3a1c993&labelColor=212121&color=304FFE" /></a>
</p>

**Lug** is an open source package that allows you to move the execution of specific Python functions to different 
environments on each call. This means that instead of deploying a function permanently to a specific environment 
(e.g. your local computer or a cloud-based server), you can choose where you want to run the function at the time of 
execution. This flexibility allows you to optimize your resource consumption and cost for the needs of the specific 
function.

Lug is particularly useful for computational science, where researchers and scientists often have programs that are 
challenging to install and run. Lug automatically detects and packages pip-installed dependencies and local modules, 
and you can even attach a sidecar Docker image for the command-line programs that need their own image – making it 
simple to debug and scale your code.

Check out the full docs at [lug.dev](https://lug.dev)

## Highlights

- 📦 Automatic dependency detection and propagation
- 🐳 Attach function-scoped sidecar Docker images
- ☁️ Execute on your computer, the cloud, or on your own servers


## Prerequisites

- macOS or Linux
- [Docker Engine](https://docs.docker.com/engine/install/), if you're using Lug Docker Sidecar functions

## Install

[Install Docker Engine and the CLI](https://docs.docker.com/engine/install/), if you don't have it.

### With pip:

`pip install lug`

## Get started 

There are two ways to use Lug:

1. Creating a Lug Hybrid function that executes on your computer or in the cloud.
2. Creating a Lug Docker Sidecar function, which is the same as a Lug Hybrid function but with a function-scoped Docker 
image.

On this readme, we'll just create a short Lug Hybrid function, but there's more detail in the [docs](https://lug.dev).

### Quick start:

Let's create a simple Python function that tells us how many CPUs our system has:

```python
import lug
import multiprocessing

@lug.hybrid(cloud=False)
def num_cpus():
    return multiprocessing.cpu_count()

print(num_cpus())
```

This function will execute locally and print the number of CPUs on the system. To run on the cloud, first [generate a 
Toolchest API key](https://dash.trytoolchest.com/) and set `key` to your Toolchest API key and `cloud=True`:

```python
import lug
import multiprocessing

@lug.hybrid(cloud=True, key="YOUR_KEY_HERE")
def num_cpus():
    return multiprocessing.cpu_count()

print(num_cpus())
```

This function will execute on the cloud and print the number of CPUs on the cloud-based server.

For more detail, check out the docs at [lug.dev](https://lug.dev)

## Open-source roadmap

- [x] Run a Python function in a local container
- [x] Maintain Python major.version in function and in container
- [x] Serialize and deserialize Python function and Python dependencies
- [x] `os.system()`, `subprocess.run()`, and `subprocess.Popen()` redirect to a user-specified container
- [x] Local files passed to as input go to `./input/` in remote Docker container
- [x] Remote files written to `./output/` in the container are written to local output Path
- [x] Runs locally
- [x] Run in the cloud with [Toolchest](https://github.com/trytoolchest/toolchest-client-python)
- [x] Stream live `stdout` during remote cloud execution
- [x] `pip`-based environment propagation
- [ ] `conda`-based environment propagation (help needed)

## License

Lug is licensed under the Apache License 2.0
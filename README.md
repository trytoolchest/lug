# Lug

<p align="center">
    <a href="https://pypi.python.org/pypi/lug/" alt="PyPI version">
        <img alt="PyPI" src="https://img.shields.io/pypi/v/lug?labelColor=212121&color=304FFE"></a>
    <a href="https://github.com/trytoolchest/lug/" alt="Build">
        <img src="https://img.shields.io/circleci/build/gh/trytoolchest/lug/main?label=build&token=3eb013dde86ed79996a768ab325cd30ea3a1c993&labelColor=212121&color=304FFE" /></a>
    <a href="https://discord.gg/zgeJ9Pss" alt="Discord">
        <img src="https://img.shields.io/discord/1016544715128176721?labelColor=212121&color=304FFE&label=discord" /></a>
</p>

**Lug** is an open source package that redirects Python calls to `subprocess.run`, `subprocess.Popen`, and `os.system` into 
any Docker container. This makes these system-level Python calls behave the same way on different machines, without 
requiring any changes to the Docker container.

Lug also packages the Python function and Docker container, so you can easily run both in the cloud via Lug if needed. 
This lets you give more computing power to the functions that need it.
## Highlights

- 📦 `subprocess.run`, `subprocess.Popen`, and `os.system` run in your container – for the dependencies you can't 
install with pip
- 🐍 Use containers as-is, no need to add your Python version
- ☁️ Run on your computer or in the cloud

## Why use Lug?

Some software – especially in bioinformatics and machine learning – can't be installed with `pip install`. Conda works 
in some cases, but for others a Docker container is the best solution. Lug makes the Docker container easier to work 
with from Python.

The same software is usually resource intensive. Lug can run on your computer, or it can automatically run the Python 
function and Docker container in the cloud with [Toolchest](https://docs.trytoolchest.com/docs/pricing).

## Prerequisites

- macOS or Linux (supporting `POSIX_SPAWN`)
- [Docker Engine](https://docs.docker.com/engine/install/) and the Docker CLI

## Install

[Install Docker Engine and the CLI](https://docs.docker.com/engine/install/), if you don't have it.

### With pip:

`pip install lug`

### With Poetry:

`poetry add lug`

## Get started 

### Run a Python function locally in a Docker image

Everything but the `subprocess.run` below runs as-is, with the `echo` command running in the Docker image:

```python
import lug
import subprocess

@lug.run(image="alpine:3.16.2")
def hello_world():
    result = subprocess.run('echo "Hello, `uname`!"', capture_output=True, text=True, shell=True)
    return result.stdout

print(hello_world())
```

That's it! After it finishes, you'll see `Hello, Linux!`.


## Docs

Full docs are at [lug.dev](https://lug.dev)

## Open-source roadmap

- [x] Run a Python function in a local container
- [x] Maintain Python major.version in function and in container
- [x] Serialize and deserialize Python function and Python dependencies
- [x] `os.system()`, `subprocess.run()`, and `subprocess.Popen()` redirect to a user-specified container
- [x] Local files passed to as input go to `./input/` in remote Docker container
- [x] Remote files written to `./output/` in the container are written to local output Path
- [x] Runs locally
- [x] Run in the cloud with [Toolchest](https://github.com/trytoolchest/toolchest-client-python)
- [ ] Stream live `stdout` during remote execution
- [ ] `pip`-based environment propagation (help needed)
- [ ] `conda`-based environment propagation (help needed)
- [ ] Run in the cloud with AWS (help needed)
- [ ] Run in the cloud with GCP (help needed)

## License

Lug is licensed under the Apache License 2.0
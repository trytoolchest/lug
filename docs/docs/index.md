# Lug

If you're ready to start building, head straight to [Installation](getting-started/installation.md) or 
[Adding Lug to a Function](getting-started/create-a-hybrid-function.md).

## What does Lug do?

Lug is a tool that allows you to move the execution of specific Python functions to different environments on each call. 
This means that instead of deploying a function permanently to a specific environment (e.g. your local computer or a 
cloud-based server), you can choose where you want to run the function at the time of execution. This flexibility 
allows you to optimize your resource consumption and cost for the needs of the specific function.

Lug is particularly useful for computational science, where researchers and scientists often have programs that are 
challenging to install and run. Lug automatically detects and packages pip-installed dependencies and local modules, 
and you can even attach a sidecar Docker image for the command-line programs that need their own image – making it 
simple to debug and scale your code.

## What isn't Lug good at (yet)?

- Short-running functions – there's a startup time (1-5 minutes) for each cloud run
- Hosting for reference databases / models / etc (try [Toolchest](https://trytoolchest.com) for that if you're in bio)
- TensorFlow

## Why Lug?

- It's one line of code
- You don't need to statically define your dependencies
- Lug is open source (Apache 2.0)

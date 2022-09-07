# Lug

If you're ready to start building, head straight to [Installation](getting-started/installation.md) or 
[Adding Lug to a Function](getting-started/adding-lug-to-a-function.md).

## What does Lug do?

Lug redirects calls to `subprocess.run`, `subprocess.Popen`, and `os.system` to any Docker container. This makes these 
system-level calls behave the same way on different machines.

Lug also packages the Python function and Docker container, so you can run it on the cloud if needed. This lets you give
more computing power to the functions that need it.

## Who should use Lug?

If you:

- have a dependency that you can't install with `pip`
- are already invoking Docker images from your Python function
- want an easy way to get more computing power for a function

then you should try Lug!

## What doesn't Lug solve?

- Speeding up short-running functions (e.g. <1 min)
- Hosting for reference databases / models / etc (although you can pass these files as input)
- Building Docker containers for you

## Why Lug?

- You don't need to add Python – or any new dependencies – to your Docker container
- You can run Lug on your computer or in the cloud
- Lug is open source (Apache 2.0)

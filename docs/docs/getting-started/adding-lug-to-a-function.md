# Adding Lug to a function

## Running Lug on your computer

Add the `@lug.run` decorator with a Docker image:

```python
import lug
import subprocess

@lug.run(image="alpine:3.16.2")
def hello_world():
    result = subprocess.run('echo "Hello, `uname`!"', capture_output=True, text=True, shell=True)
    return result.stdout

print(hello_world())
```

That's it! If it works, you'll see `Hello, Linux!`.
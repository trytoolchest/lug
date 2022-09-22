# Dependencies and Lug

## Python dependencies

When Lug runs locally, it uses the local Python environment. When Lug runs remotely, Lug transfers a portion of the 
local Python environment to the cloud.

By default, Lug doesn't include any dependencies outside the immediate scope of your function. That means imported 
modules are not sent to the cloud by default. If you do need to include imported modules or other dependencies to a Lug 
call, you can use the `serialize_dependencies` argument.

For example:

```python
import idna
import lug

@lug.run(image="alpine:3.16.2", remote=True, serialize_dependencies=True)
def encode_string():
    return idna.encode('ドメイン.テスト')

print(encode_string())
```

Serializing dependencies uses [cloudpickle](https://github.com/cloudpipe/cloudpickle) under the hood, the same package 
used in packages like Apache Spark. That also means Lug faces the same limitations as cloudpickle: many popular
packages like `numpy`, `tensorflow`, and `pytorch` aren't serializable with cloudpickle.

To keep the scope of dependencies in a lugged function small, try keeping the function scope to the minimal amount of 
code needed to execute your containerized command.


## Container dependencies

Anything that Lug re-routes to your container – like a `subprocess.run` call – uses the environment of your custom 
Docker image.

To add dependencies to your container, just modify the container!
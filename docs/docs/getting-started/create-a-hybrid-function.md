# Create a Hybrid Function

With Lug, you can easily create hybrid functions that can run both locally and in the cloud. First, let's create a 
simple Python function that tells us how many CPUs our system has. We'll use the `multiprocessing` library to do this:

```python
import multiprocessing

def num_cpus():
    return multiprocessing.cpu_count()

print(num_cpus())
```

This function will print the number of CPUs on the system. On my laptop, that number is "10".

Now, let's make this function a "hybrid function" using Lug. To do this, we'll import the Lug library and add the 
`@lug.hybrid()` decorator to the function:
```python
import lug
import multiprocessing

@lug.hybrid(cloud=False)
def num_cpus():
    return multiprocessing.cpu_count()

print(num_cpus())
```

This will give us the same output as before, since we are still running the function on our local system. However, by 
using the `@lug.hybrid()` decorator, we have now made our function "hybrid" and it can easily move it to the cloud if 
we wish to do so in the future.
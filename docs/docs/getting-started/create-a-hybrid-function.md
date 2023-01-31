# Running Hybrid Functions in the Cloud

## Get an API key

To run a function in the cloud using Lug, you will need to get an API key from Toolchest. Here's how:

1. First, [sign up for a free Toolchest account](https://dash.trytoolchest.com/).
2. Log in and navigate to the API Keys section.
3. Click on "Generate New Key" to create a new API key.
4. Once you have the key, you can use the Toolchest app to monitor your runs, execute in the cloud, or connect your own 
on-prem servers.

Note: Lug uses Toolchest for cloud execution, so an API key from Toolchest is required to use Lug's cloud functionality.

## Run your hybrid function in the cloud

To run your hybrid function on the cloud, set the `cloud` parameter to `True`. You'll also need to set your Toolchest 
API key in the `key` parameter.

Here's an example of how to use the `@lug.hybrid` decorator to run a `num_cpus` function on the cloud:

```python
import lug
import multiprocessing

@lug.hybrid(cloud=True, key="YOUR_KEY_HERE")
def num_cpus():
    return multiprocessing.cpu_count()

print(num_cpus())
```

This will run the `num_cpus` function on the cloud using the smallest available instance (2 CPUs) by default. Once the 
execution is finished, you will see the number of CPUs returned as the result. By default, Lug uses AWS as the cloud 
provider.

### Adding more power

If you want to give the function more resources, you can specify a different instance type when you decorate the 
function. For example, if you want to grant 48 CPUs, you can set the instance type to "compute-48":

```python
import lug
import multiprocessing

@lug.hybrid(cloud=True, key="YOUR_KEY_HERE", instance_type="compute-48")
def num_cpus():
    return multiprocessing.cpu_count()

print(num_cpus())
```

This will run the function on an instance with 96 CPUs. You can use any of the cloud-generic 
[available Toolchest instance types](https://docs.trytoolchest.com/toolchest-hosted-cloud/instance-types/) by replacing 
"compute-96" with the desired instance type.

### Running on another cloud

You can also run your function on another cloud provider – or your on-prem servers – as long as it's connected to your 
Toolchest account. By default, every account has access to the lower-cost queued Toolchest Cloud Extension (TCE), so 
we'll use it for this example.

To run your Lug functions in TCE, simply set the `provider` argument to "tce" in the `@lug.hybrid` function call.

```python
import lug
import multiprocessing

@lug.hybrid(
    cloud=True,
    key="YOUR_KEY_HERE",
    instance_type="compute-48",
    provider="tce", # add this line
)
def num_cpus():
    return multiprocessing.cpu_count()

print(num_cpus())
```

This allows for easy switching between different environments and providers, making it easy to scale your computation 
while utilizing specialized or lower-cost infrastructure.

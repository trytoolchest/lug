import base64
import functools
import glob

from docker.errors import DockerException, APIError
from importlib_metadata import packages_distributions, version
import inspect
import os
import shutil
import signal
import sys
import threading
import types
import uuid

import cloudpickle
import docker
import tempfile

from .containers import DockerContainer
from .module_detection import get_modules_to_register
from .shell import sidecar_shell


def patch_system_call(user_docker_container_name=None, original_function=None, pass_kwargs=True,
                      docker_shell_location=None):
    """
    Patch os.system, subprocess.run, subprocess.Popen, and Lug sidecar_shell
    Note: docker_shell_location refers to the shell in the *user* docker container
    """

    def run(*args, **kwargs):
        """Lug-replaced function."""
        docker_exec_args = [
            "docker",
            "exec",
            f"{user_docker_container_name}",
        ]
        using_shell = kwargs.get("shell") or original_function.__name__ in ["system", "sidecar_shell"]
        if using_shell:
            docker_exec_args.append(docker_shell_location)

        if type(args[0]) is list:
            original_list_args = args[0]
            docker_exec_args += original_list_args
            return original_function(docker_exec_args, *args[1:], **kwargs)
        else:
            # NOTE: args[0] (the user command argument) can only be a string if using_shell is True.
            stringified_docker_command = ' '.join(docker_exec_args)
            user_command = args[0].replace("'", r"'\''")  # sanitizes single quotes within sh command
            new_args = stringified_docker_command + " -c '" + user_command + "'"
            if pass_kwargs:
                return original_function(new_args, **kwargs)
            return original_function(new_args)

    run.is_lug_function = True
    run.lug_original_function = original_function
    return run


def find_and_replace_function(member, unique_docstring, replace_with, patched_functions, depth=0, max_depth=3):
    if depth > max_depth:
        return
    if type(member) in [str, type(None)]:
        return
    elif type(member) == dict:
        for name, sub_attribute in member.copy().items():  # The dict can change size, so make a copy for iteration
            if name == "__builtins__":
                continue
            this_one = find_and_replace_function(
                member=sub_attribute,
                unique_docstring=unique_docstring,
                replace_with=replace_with,
                patched_functions=patched_functions,
                depth=depth + 1,
                max_depth=max_depth,
            )
            if this_one:
                patched_functions.append({
                    "member": member,
                    "attribute_name": name,
                    "original_value": replace_with.lug_original_function,
                    "is_dictionary": True,
                })
                member[name] = replace_with
                return False
    elif isinstance(member, types.ModuleType):
        # import subprocess -> subprocess is a module
        # import os -> os is a module
        try:
            members = inspect.getmembers(member)
        # For some members, inspect.getmembers returns "TypeError: '_ClassNamespace' object is not iterable"
        except (ModuleNotFoundError, TypeError):
            return
        for name, sub_member in members:
            if name == "__builtins__":
                continue
            this_one = find_and_replace_function(
                member=sub_member,
                unique_docstring=unique_docstring,
                replace_with=replace_with,
                patched_functions=patched_functions,
                depth=depth + 1,
                max_depth=max_depth,
            )
            if this_one:
                patched_functions.append({
                    "member": member,
                    "attribute_name": name,
                    "original_value": getattr(member, name),
                    "is_dictionary": False,
                })
                setattr(member, name, replace_with)
                return False
        return False
    else:
        try:
            if hasattr(member, "__doc__") and member.__doc__ and unique_docstring in member.__doc__:
                return True
            elif isinstance(member, types.FunctionType):
                # Explore the globals of any imported function
                find_and_replace_function(
                    member=member.__globals__,
                    unique_docstring=unique_docstring,
                    replace_with=replace_with,
                    patched_functions=patched_functions,
                    depth=depth + 1,
                    max_depth=5,  # If we're exploring a function globals, increase max depth to five
                )
                return False
        except (TypeError, ModuleNotFoundError):
            return False
        return False


def patch_system_calls(func, user_docker_container_name, docker_shell_location, redirect_shell):
    patched_functions = []

    # Create a patched lug.sidecar_shell
    new_sidecar_shell = patch_system_call(
        user_docker_container_name=user_docker_container_name,
        original_function=sidecar_shell,
        docker_shell_location=docker_shell_location,
    )
    find_and_replace_function(
        member=func.__globals__,
        unique_docstring="This function is redirected to the Lug sidecar container.",
        replace_with=new_sidecar_shell,
        patched_functions=patched_functions,
    )

    if redirect_shell:
        # Create a new subprocess.Popen
        import subprocess
        new_subprocess_popen = patch_system_call(
            user_docker_container_name=user_docker_container_name,
            original_function=subprocess.Popen,
            docker_shell_location=docker_shell_location,
        )
        find_and_replace_function(
            member=func.__globals__,
            unique_docstring="Execute a child program in a new process.",
            replace_with=new_subprocess_popen,
            patched_functions=patched_functions,
        )
        # Create a new subprocess.run
        new_subprocess_run = patch_system_call(
            user_docker_container_name=user_docker_container_name,
            original_function=subprocess.run,
            docker_shell_location=docker_shell_location,
        )
        if not hasattr(subprocess.Popen, "is_lug_function"):
            find_and_replace_function(
                member=func.__globals__,
                unique_docstring="Run command with arguments and return a CompletedProcess instance",
                replace_with=new_subprocess_run,
                patched_functions=patched_functions,
            )
        # Create a new os.system
        import os
        new_os_system = patch_system_call(
            user_docker_container_name=user_docker_container_name,
            original_function=os.system,
            pass_kwargs=False,
            docker_shell_location=docker_shell_location,
        )
        find_and_replace_function(
            member=func.__globals__,
            unique_docstring="Execute the command in a subshell",
            replace_with=new_os_system,
            patched_functions=patched_functions,
        )

    return patched_functions


def unpatch_system_calls(patched_functions):
    for patched_function_info in patched_functions:
        if patched_function_info["is_dictionary"]:
            attribute = patched_function_info["attribute_name"]
            patched_function_info["member"][attribute] = patched_function_info["original_value"]
        else:
            setattr(
                patched_function_info["member"],
                patched_function_info["attribute_name"],
                patched_function_info["original_value"],
            )


def can_be_pickled(module):
    # The module must be referenced inside the function to actually test if it can be pickled
    dummy_function_using_module = lambda x: module.__name__
    try:
        cloudpickle.register_pickle_by_value(module)
        cloudpickle.dumps(dummy_function_using_module)
        return True
    except Exception:
        return False
    finally:
        cloudpickle.unregister_pickle_by_value(module)


def find_module_transferability(modules):
    children_to_ignore = set()
    copyable_packages = set()
    uncopyable_packages = set()
    uncopyable_pip_names = dict()  # package_name: version # todo: filter out packages that can't be installed with pip
    packages_distribution = packages_distributions()
    # Split pickleable and unpickleable packages
    for module in modules:
        if not module.__spec__:
            continue

        picklable = can_be_pickled(module)

        # Find physical location of module source
        parent = module.__spec__.name.rpartition(".")[0]
        child = None
        if parent:
            child = module
            module = sys.modules[parent]
        submodule_search_locations = module.__spec__.submodule_search_locations
        loader_members = inspect.getmembers(module.__spec__.loader)
        loader_keys = [loader[0] for loader in loader_members]
        loader_path = None
        if "path" in loader_keys:
            loader_path = module.__spec__.loader.path
        # todo: handle multiple submodule search locations
        primary_location = (submodule_search_locations and submodule_search_locations[0]) or loader_path

        has_so_files = False
        if primary_location:
            adjusted_primary_location = os.path.dirname(primary_location) if primary_location.endswith(".py") \
                else primary_location

            # Check if the package contains any CPython compiled files (e.g. numpy, scipy, etc)
            has_so_files = glob.glob(f"{adjusted_primary_location}/*.so") \
                + glob.glob(f"{adjusted_primary_location}/**/*.so", recursive=True)
            picklable = False

        if not picklable:
            try:
                pip_names = packages_distribution[module.__name__]
                for pip_name in pip_names:
                    # Drop local version identifiers (e.g. "+cu117" in "torch==1.13.1+cu117")
                    if hasattr(module, "__version__"):
                        # Some packages, like sklearn, don't support version()
                        public_version = module.__version__.split("+")[0]
                    else:
                        public_version = version(module.__name__)
                    uncopyable_pip_names[pip_name] = public_version
                uncopyable_packages.add(module.__name__)
                # Make sure we know not to copy the child if present (e.g. lug and lug.run)
                if child:
                    uncopyable_packages.add(child.__name__)
                    children_to_ignore.add(child)
            except KeyError:
                if not has_so_files:
                    # Add to packages that need to be manually copied
                    copyable_packages.add(primary_location)
                    children_to_ignore.add(child)
                else:
                    raise ModuleNotFoundError(f"'{module.__name__}' distribution info not found on this machine.")
            continue

    # Prune copyable packages that are a subdirectory of another package
    # I'm assuming the copyable_packages set will be tiny; optimizing for clarity rather than performance
    for package_a in copyable_packages.copy():
        for package_b in copyable_packages:
            if package_a == package_b:
                continue
            # Assuming all absolute paths, no symlinks. If not, we should use proper parent finding.
            is_child = package_a.startswith(package_b) and len(package_a.split(package_b)) > 1
            if is_child:
                copyable_packages.remove(package_a)
                break

    return uncopyable_packages, uncopyable_pip_names, copyable_packages, children_to_ignore


def env_requirements_to_string(pip_packages):
    requirements_string = ""
    for name, package_version in pip_packages.items():
        requirements_string += f"{name}=={package_version} "
    return requirements_string


def create_python_script(func, args, kwargs, temp_input, user_docker, docker_shell_location, serialize_dependencies,
                         internal_dir, redirect_shell):
    output_uuid = uuid.uuid4()
    with open(temp_input.name, 'w') as fp:
        copyable_packages = []
        pip_packages_string = ''
        links = []
        if serialize_dependencies:
            modules_to_register = get_modules_to_register(func)
            uncopyable_packages, uncopyable_pip_names, copyable_packages, children_to_ignore = \
                find_module_transferability(modules_to_register)
            pip_packages_string = env_requirements_to_string(uncopyable_pip_names)
            pickle_packages = set(filter(
                lambda mod: mod.__name__ not in copyable_packages and mod.__name__ not in uncopyable_packages,
                modules_to_register,
            ))
            pickle_packages -= children_to_ignore
            internal_dir_basename = os.path.basename(internal_dir)
            for module_location_to_include in copyable_packages:
                #  todo: handle conflicts for package directory names
                local_path_with_internal_dir = os.path.join(
                    internal_dir_basename,
                    os.path.basename(module_location_to_include)
                )
                abs_path_with_internal_dir = os.path.join(internal_dir, os.path.basename(module_location_to_include))
                if not os.path.exists(abs_path_with_internal_dir):
                    shutil.copytree(module_location_to_include, abs_path_with_internal_dir)
                links.append((module_location_to_include, f"./input/{local_path_with_internal_dir}"))
            for module in pickle_packages:
                cloudpickle.register_pickle_by_value(module)
        else:
            cloudpickle.register_pickle_by_value(sys.modules[__name__])
        pickled_func = cloudpickle.dumps(func)
        encoded_func = base64.encodebytes(pickled_func)
        pickled_patch = cloudpickle.dumps(patch_system_calls)
        encoded_pickled_patch = base64.encodebytes(pickled_patch)
        pickled_args = cloudpickle.dumps(args)
        encoded_args = base64.encodebytes(pickled_args)
        pickled_kwargs = cloudpickle.dumps(kwargs)
        encoded_kwargs = base64.encodebytes(pickled_kwargs)
        if serialize_dependencies:
            for module in pickle_packages:
                cloudpickle.unregister_pickle_by_value(module)
        else:
            cloudpickle.unregister_pickle_by_value(sys.modules[__name__])
        container_name = user_docker.container_name if user_docker else None

        fp.write("import base64\n")
        fp.write("import cloudpickle\n")
        fp.write("import os\n")
        fp.write("import sys\n")
        fp.write(f"for dir in {list(copyable_packages)}:\n")  # Make directories
        fp.write("\tos.makedirs(os.path.dirname(dir), exist_ok=True)\n")
        fp.write("\tsys.path.insert(0, os.path.dirname(dir))\n")
        fp.write(f"for link in {links}:\n")  # ln all paths
        fp.write("\tif not os.path.exists(link[0]):\n")
        fp.write("\t\tos.symlink(os.path.join(os.getcwd(), link[1]), link[0])\n")
        fp.write(f"func = cloudpickle.loads(base64.decodebytes({encoded_func}))\n")
        fp.write(f"patch_system_calls = cloudpickle.loads(base64.decodebytes({encoded_pickled_patch}))\n")
        fp.write(f"args = cloudpickle.loads(base64.decodebytes({encoded_args}))\n")
        fp.write(f"kwargs = cloudpickle.loads(base64.decodebytes({encoded_kwargs}))\n")
        fp.write(f"patch_system_calls(func, '{container_name}', '{docker_shell_location}', {redirect_shell})\n")
        fp.write("result = func(*args, **kwargs)\n")
        fp.write(f"with open(f'./output/encoded_output_{output_uuid}', 'wb') as file:\n")
        fp.write("\tfile.write(base64.encodebytes(cloudpickle.dumps(result)))\n")
    return output_uuid, pip_packages_string


def parse_toolchest_run(output_path, output_uuid):
    encoded_output_path = f'{output_path}/encoded_output_{output_uuid}'
    if os.path.exists(encoded_output_path):
        with open(encoded_output_path, 'rb') as file:
            encoded_result = file.read().replace(b'\n', b'')
            if encoded_result:
                result = cloudpickle.loads(base64.decodebytes(encoded_result))
            else:
                result = None
        os.remove(encoded_output_path)
    return result


def execute_remote(func, args, kwargs, toolchest_key, remote_output_directory, tmp_dir, image, remote_inputs,
                   user_docker, remote_instance_type, volume_size, python_version, docker_shell_location,
                   serialize_dependencies, command_line_args, streaming_enabled, redirect_shell, provider):
    # We're deploying Lug via Toolchest, but the user code deployed by Lug could include a different version of the
    # client. It's a late import inside this function to avoid being picked up by the Lug dependency transfer.
    import toolchest_client

    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    # Create a .lug-uuid4()/ directory for Lug module propagation
    lug_internal_dir = os.path.join(tmp_dir, f".lug-{uuid.uuid4()}")
    os.mkdir(lug_internal_dir)

    temp_input = tempfile.NamedTemporaryFile(dir=tmp_dir)
    temp_directory = None
    output_uuid, pip_packages_string = create_python_script(
        func=func,
        args=args,
        kwargs=kwargs,
        temp_input=temp_input,
        user_docker=user_docker,
        docker_shell_location=docker_shell_location,
        serialize_dependencies=serialize_dependencies,
        internal_dir=lug_internal_dir,
        redirect_shell=redirect_shell,
    )
    try:
        if toolchest_key:
            toolchest_client.set_key(toolchest_key)
        if remote_output_directory is None:
            temp_directory = tempfile.TemporaryDirectory(dir=tmp_dir)
        output_directory = remote_output_directory or temp_directory.name
        if isinstance(command_line_args, list):
            command_line_args = " ".join(command_line_args)
        if not remote_inputs:
            remote_inputs = []
        elif type(remote_inputs) is str:
            remote_inputs = [remote_inputs]
        remote_inputs.append(lug_internal_dir)
        container_name = user_docker.container_name if user_docker else None
        remote_run = toolchest_client.lug(
            custom_docker_image_id=image,
            tool_version=python_version,
            inputs=remote_inputs,
            output_path=output_directory,
            script=temp_input.name,
            container_name=container_name,
            docker_shell_location=docker_shell_location,
            tool_args=command_line_args,
            instance_type=remote_instance_type,
            volume_size=volume_size,
            streaming_enabled=streaming_enabled,
            compress_inputs=True,
            pip_dependencies=pip_packages_string,
            retain_base_directory=True,
            provider=provider,
        )
        status_response = remote_run.get_status(return_error=True)
        status = status_response['status']
        if status == 'failed':
            raise ValueError(f"Remote execution failed due to: {status_response['error_message']}")
        result = parse_toolchest_run(output_directory, output_uuid)
        return result
    finally:
        if temp_directory is not None:
            temp_directory.cleanup()
        if temp_input is not None:
            temp_input.close()


def execute_local(mount, client, user_docker, func, args, kwargs, docker_shell_location, redirect_shell):
    # todo: make sure the docker containers don't exit shortly after spawn, propagate errors
    mount = os.path.realpath(mount)
    patched_functions = None
    if user_docker:
        # Run user container
        user_docker.container = client.containers.run(
            image=user_docker.image_name_and_tag,
            volumes=[f'{mount}:/lug'],
            detach=True,
            stdin_open=True,
            name=user_docker.container_name,
            command=docker_shell_location,
            working_dir="/lug",
        )
        if threading.current_thread() is threading.main_thread() and not sys.platform.startswith('win'):
            # Only supports Unix signals
            signal.signal(signal.SIGABRT, user_docker.signal_kill_handler)
            signal.signal(signal.SIGHUP, user_docker.signal_kill_handler)
            signal.signal(signal.SIGSEGV, user_docker.signal_kill_handler)
            signal.signal(signal.SIGTERM, user_docker.signal_kill_handler)
        patched_functions = patch_system_calls(func, user_docker.container_name, docker_shell_location, redirect_shell)
    try:
        result = func(*args, **kwargs)
    finally:
        if patched_functions:
            unpatch_system_calls(patched_functions)
    return result


def run(image=None, mount=os.getcwd(), tmp_dir=tempfile.gettempdir(), docker_shell_location="/bin/sh", remote=False,
        remote_inputs=None, remote_output_directory=None, toolchest_key=None, remote_instance_type=None,
        volume_size=None, serialize_dependencies=True, command_line_args="", streaming_enabled=True,
        redirect_shell=True, provider="aws"):
    def decorator_lug(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            # Find current Python version
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            supported_versions = ["3.8", "3.9", "3.10", "3.11"]
            if python_version not in supported_versions:
                raise ValueError(f"Python version {python_version} is not supported. PRs welcome!")
            user_docker = None
            try:
                if remote:
                    user_docker = DockerContainer(
                        docker_client=None,
                        image_name_and_tag=image,
                    )
                    result = execute_remote(
                        func=func,
                        args=args,
                        kwargs=kwargs,
                        image=image,
                        remote_inputs=remote_inputs,
                        toolchest_key=toolchest_key,
                        remote_output_directory=remote_output_directory,
                        tmp_dir=tmp_dir,
                        user_docker=user_docker,
                        remote_instance_type=remote_instance_type,
                        volume_size=volume_size,
                        python_version=python_version,
                        docker_shell_location=docker_shell_location,
                        serialize_dependencies=serialize_dependencies,
                        command_line_args=command_line_args,
                        streaming_enabled=streaming_enabled,
                        redirect_shell=image is not None and redirect_shell,
                        provider=provider,
                    )
                else:
                    client, user_docker = None, None
                    if image:
                        try:
                            client = docker.from_env()
                        except (APIError, DockerException):
                            raise EnvironmentError(
                                'Unable to connect to Docker. Make sure you have Docker installed and that it is '
                                'currently running.'
                            )
                        # Get or pull the user Docker image from local/remote
                        user_docker = DockerContainer(
                            docker_client=client,
                            image_name_and_tag=image,
                        )
                        user_docker.load_image(remote=remote)
                    result = execute_local(
                        func=func,
                        args=args,
                        kwargs=kwargs,
                        mount=mount,
                        client=client,
                        user_docker=user_docker,
                        docker_shell_location=docker_shell_location,
                        redirect_shell=image is not None and redirect_shell,
                    )
            finally:
                if user_docker is not None and user_docker.container is not None:
                    user_docker.container.reload()
                    if user_docker.container.status == "running":
                        user_docker.container.stop()
                    user_docker.container.remove()
            return result

        return inner

    return decorator_lug


def hybrid(cloud=False, key=None, instance_type=None, **kwargs):
    return run(
        image=None,
        serialize_dependencies=True,
        remote=cloud,
        redirect_shell=False,
        toolchest_key=key,
        remote_instance_type=instance_type,
        **kwargs
    )


def docker_sidecar(sidecar_image, cloud=False, extract_modules=True, key=None, instance_type=None, **kwargs):
    return run(
        image=sidecar_image,
        serialize_dependencies=extract_modules,
        remote=cloud,
        redirect_shell=False,
        toolchest_key=key,
        remote_instance_type=instance_type,
        **kwargs
    )

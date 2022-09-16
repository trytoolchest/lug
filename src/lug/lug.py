import base64
import functools
import inspect
import os
import signal
import sys
import threading
import types
import uuid

import cloudpickle
import docker
import tempfile
import toolchest_client

from .containers import DockerContainer


def patch_system_call(user_docker_container_name=None, original_function=None, pass_kwargs=True,
                      docker_shell_location=None):
    """
    Patch os.system, subprocess.run, or subprocess.Popen
    """

    def run(*args, **kwargs):
        """Lug-replaced function."""
        docker_exec_args = [
            "docker",
            "exec",
            f"{user_docker_container_name}",
        ]
        if type(args[0]) is list:
            # subprocess.run or subprocess.Popen without shell
            original_list_args = args[0]
            docker_exec_args += original_list_args
            return original_function(docker_exec_args, *args[1:], **kwargs)
        else:
            additional_docker_exec_args = [
                docker_shell_location,
                "-c",
                "'"
            ]
            stringified_docker_command = ' '.join(docker_exec_args + additional_docker_exec_args)
            user_command = args[0].replace("'", r"'\''")  # sanitizes single quotes within sh command
            new_args = stringified_docker_command + user_command + "'"
        if pass_kwargs:
            return original_function(new_args, **kwargs)
        return original_function(new_args)
    run.is_lug_function = True
    run.lug_original_function = original_function
    return run


def find_and_replace_function(member, unique_docstring, replace_with, depth=0, unpatch=False):
    if depth > 3:
        return
    if type(member) in [str, type(None)]:
        return
    elif type(member) == dict:
        for name, sub_attribute in member.items():
            if name == "__builtins__":
                continue
            this_one = find_and_replace_function(sub_attribute, unique_docstring, replace_with, depth + 1, unpatch)
            if this_one:
                if unpatch:
                    member[name] = member[name].lug_original_function
                else:
                    member[name] = replace_with
                return False
    elif isinstance(member, types.ModuleType):
        # import subprocess -> subprocess is a module
        # import os -> os is a module
        try:
            members = inspect.getmembers(member)
        except ModuleNotFoundError:
            return
        for name, sub_member in members:
            if name == "__builtins__":
                continue
            this_one = find_and_replace_function(sub_member, unique_docstring, replace_with, depth + 1, unpatch)
            if this_one:
                if unpatch:
                    patched_function = getattr(member, name)
                    setattr(member, name, patched_function.lug_original_function)
                else:
                    setattr(member, name, replace_with)
                return False
        return False
    else:
        # Base case; catches:
        # os.system (a "builtin_function_or_method")
        # subprocess.run (a "function")
        try:
            if unpatch:
                if hasattr(member, "lug_original_function"):
                    return True
            elif hasattr(member, "__doc__") and unique_docstring in member.__doc__:
                return True
        except (TypeError, ModuleNotFoundError):
            return False
        return False


def patch_system_calls(func, user_docker_container_name, docker_shell_location):
    # Create a new subprocess.run
    import subprocess
    new_subprocess_run = patch_system_call(
        user_docker_container_name=user_docker_container_name,
        original_function=subprocess.run,
        docker_shell_location=docker_shell_location,
    )
    # Create a new subprocess.Popen
    new_subprocess_popen = patch_system_call(
        user_docker_container_name=user_docker_container_name,
        original_function=subprocess.Popen,
        docker_shell_location=docker_shell_location,
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
        unique_docstring="Execute a child program in a new process.",
        replace_with=new_subprocess_popen
    )
    if not hasattr(subprocess.Popen, "is_lug_function"):
        find_and_replace_function(
            member=func.__globals__,
            unique_docstring="Run command with arguments and return a CompletedProcess instance",
            replace_with=new_subprocess_run
        )
    find_and_replace_function(
        member=func.__globals__,
        unique_docstring="Execute the command in a subshell",
        replace_with=new_os_system
    )


def unpatch_system_calls(func):
    find_and_replace_function(
        member=func.__globals__,
        unique_docstring=None,
        replace_with=None,
        unpatch=True
    )


def get_modules_to_register(func):
    modules_to_register = []
    # Skip test and internal unpicklable Lug modules
    modules_to_skip = {
        "pytest",
        "lug",
        "cloudpickle",
        # "toolchest_client",
        "docker"
    }
    search_for_modules_to_register(
        member=func,
        modules_to_register=modules_to_register,
        discovered_module_names=modules_to_skip,
    )
    return modules_to_register


def search_for_modules_to_register(member, modules_to_register, discovered_module_names, depth=0):
    """Recursively search for modules to register."""
    if depth > 3:
        return
    is_module = isinstance(member, types.ModuleType)
    is_function = isinstance(member, types.FunctionType)
    if is_function:
        for global_var in member.__globals__.values():
            search_for_modules_to_register(
                member=global_var,
                modules_to_register=modules_to_register,
                discovered_module_names=discovered_module_names,
                depth=depth + 1
            )
        function_parent_module = inspect.getmodule(member)
        search_for_modules_to_register(
            member=function_parent_module,
            modules_to_register=modules_to_register,
            discovered_module_names=discovered_module_names,
            depth=depth + 1
        )
    elif is_module:
        module_name = getattr(member, "__name__")
        if module_name in discovered_module_names:
            return
        else:
            discovered_module_names.add(module_name)
        is_builtin_module = module_name in sys.builtin_module_names
        is_stdlib_module = module_name in sys.stdlib_module_names
        if not is_builtin_module and not is_stdlib_module:
            modules_to_register.append(member)
        if hasattr(member, "__globals__"):
            for global_var in member.__globals__.values():
                search_for_modules_to_register(
                    member=global_var,
                    modules_to_register=modules_to_register,
                    discovered_module_names=discovered_module_names,
                    depth=depth + 1,
                )


def create_python_script(func, args, kwargs, temp_input, user_docker, docker_shell_location):
    output_uuid = uuid.uuid4()
    with open(temp_input.name, 'w') as fp:
        modules_to_register = get_modules_to_register(func)
        for module in modules_to_register:
            print("registering apparent module", module)
            cloudpickle.register_pickle_by_value(module)
        pickled_func = cloudpickle.dumps(func)
        encoded_func = base64.encodebytes(pickled_func)
        pickled_patch = cloudpickle.dumps(patch_system_calls)
        encoded_pickled_patch = base64.encodebytes(pickled_patch)
        pickled_args = cloudpickle.dumps(args)
        encoded_args = base64.encodebytes(pickled_args)
        pickled_kwargs = cloudpickle.dumps(kwargs)
        encoded_kwargs = base64.encodebytes(pickled_kwargs)
        for module in modules_to_register:
            cloudpickle.unregister_pickle_by_value(module)
        fp.write("import base64\n")
        fp.write("import cloudpickle\n")
        fp.write(f"func = cloudpickle.loads(base64.decodebytes({encoded_func}))\n")
        fp.write(f"patch_system_calls = cloudpickle.loads(base64.decodebytes({encoded_pickled_patch}))\n")
        fp.write(f"args = cloudpickle.loads(base64.decodebytes({encoded_args}))\n")
        fp.write(f"kwargs = cloudpickle.loads(base64.decodebytes({encoded_kwargs}))\n")
        fp.write(f"patch_system_calls(func, '{user_docker.container_name}', '{docker_shell_location}')\n")
        fp.write("print('Starting execution')\n")
        fp.write("result = func(*args, **kwargs)\n")
        fp.write(f"with open(f'./output/encoded_output_{output_uuid}', 'wb') as file:\n")
        fp.write("\tfile.write(base64.encodebytes(cloudpickle.dumps(result)))\n")
    return output_uuid


def parse_toolchest_run(output_path, output_uuid):
    encoded_output_path = f'{output_path}/encoded_output_{output_uuid}'
    if os.path.exists(encoded_output_path):
        with open(encoded_output_path, 'rb') as file:
            encoded_result = file.readline()
            if encoded_result:
                result = cloudpickle.loads(base64.decodebytes(encoded_result))
            else:
                result = None
        os.remove(encoded_output_path)
    return result


def execute_remote(func, args, kwargs, toolchest_key, remote_output_directory, tmp_dir, image, remote_inputs,
                   user_docker, remote_instance_type, volume_size, python_version, docker_shell_location):
    if not os.path.exists(tmp_dir):
        os.mkdir(tmp_dir)
    temp_input = tempfile.NamedTemporaryFile(dir=tmp_dir)
    temp_directory = None
    output_uuid = create_python_script(func, args, kwargs, temp_input, user_docker, docker_shell_location)
    try:
        if toolchest_key:
            toolchest_client.set_key(toolchest_key)
        if remote_output_directory is None:
            temp_directory = tempfile.TemporaryDirectory(dir=tmp_dir)
        output_directory = remote_output_directory or temp_directory.name
        remote_run = toolchest_client.lug(
            custom_docker_image_id=image,
            tool_version=python_version,
            inputs=remote_inputs,
            output_path=output_directory,
            script=temp_input.name,
            tool_args=user_docker.container_name,
            instance_type=remote_instance_type,
            volume_size=volume_size,
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


def execute_local(mount, client, user_docker, func, args, kwargs, docker_shell_location):
    # todo: make sure the docker containers don't exit shortly after spawn, propagate errors
    mount = os.path.realpath(mount)
    # Run user container
    user_docker.container = client.containers.run(
        image=user_docker.image_name_and_tag,
        volumes=[f'{mount}:/lug'],
        detach=True,
        stdin_open=True,
        name=user_docker.container_name
    )
    if threading.current_thread() is threading.main_thread() and not sys.platform.startswith('win'):
        # Only supports Unix signals
        signal.signal(signal.SIGABRT, user_docker.signal_kill_handler)
        signal.signal(signal.SIGHUP, user_docker.signal_kill_handler)
        signal.signal(signal.SIGSEGV, user_docker.signal_kill_handler)
        signal.signal(signal.SIGTERM, user_docker.signal_kill_handler)
    patch_system_calls(func, user_docker.container_name, docker_shell_location)
    result = func(*args, **kwargs)
    return result


def run(image, mount=os.getcwd(), tmp_dir=os.getcwd(), docker_shell_location="/bin/sh", remote=False,
        remote_inputs=None, remote_output_directory=None, toolchest_key=None, remote_instance_type=None,
        volume_size=None):
    def decorator_lug(func):
        @functools.wraps(func)
        def inner(*args, **kwargs):
            client = docker.from_env()

            # Get or pull the user Docker image from local/remote
            user_docker = DockerContainer(
                docker_client=client,
                image_name_and_tag=image,
            )
            user_docker.load_image()

            # Find current Python version
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            supported_versions = ["3.7", "3.8", "3.9", "3.10", "3.11"]
            if python_version not in supported_versions:
                raise ValueError(f"Python version {python_version} is not supported. PRs welcome!")

            try:
                if remote:
                    result = execute_remote(func=func, args=args, kwargs=kwargs,
                                            image=image, remote_inputs=remote_inputs, toolchest_key=toolchest_key,
                                            remote_output_directory=remote_output_directory, tmp_dir=tmp_dir,
                                            user_docker=user_docker, remote_instance_type=remote_instance_type,
                                            volume_size=volume_size, python_version=python_version,
                                            docker_shell_location=docker_shell_location)
                else:
                    result = execute_local(func=func, args=args, kwargs=kwargs,
                                           mount=mount, client=client, user_docker=user_docker,
                                           docker_shell_location=docker_shell_location)
            finally:
                if user_docker is not None and user_docker.container is not None:
                    user_docker.container.reload()
                    if user_docker.container.status == "running":
                        user_docker.container.stop()
                    user_docker.container.remove()
                if not remote:
                    unpatch_system_calls(func)
            return result
        return inner
    return decorator_lug

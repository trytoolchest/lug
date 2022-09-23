import ast
import glob
import inspect
import sys
import types
import os

from .constants import STDLIB_MODULE_NAMES


def parse_ast_for_file(python_file_path):
    opened_file = open(python_file_path).read()
    parsed_ast = ast.parse(opened_file)
    return [node for node in ast.walk(parsed_ast)]


def get_registered_module_imports(modules_to_register, modules_to_skip):
    """
    Perform a deep search for module dependencies, by parsing the AST and looking for all imports.

    All imports in the module are parsed, even if they aren't used. Practically, this means we're catching
    more dependencies than needed within a module.

    Modules that this function finds are not searched for _their_ dependencies. For a truly deep search, this would need
    to be modified to search through found modules and their dependencies.

    Only modules that are already loaded within `sys.modules` of the Lugged function are registered for pickling.
    """
    # Find all sys level registered modules that aren't builtins
    filtered_sys_modules = []
    for module_name, module_value in sys.modules.items():
        is_builtin_module = module_name in sys.builtin_module_names
        is_stdlib_module = module_name in STDLIB_MODULE_NAMES
        if not (is_builtin_module or is_stdlib_module):
            filtered_sys_modules.append(module_name)

    # Find all imported modules within dependencies
    deep_modules = set()
    for module in modules_to_register:
        all_ast_nodes = []

        # Some modules are single-file modules, or otherwise don't have a root directory
        if not hasattr(module, "__path__"):
            # We're not supporting modules that have neither a directory or file at their root
            if not hasattr(module, "__file__"):
                continue
            # If the module only has one file, we only need to parse that file
            all_ast_nodes = parse_ast_for_file(
                python_file_path=getattr(module, "__file__")
            )
        else:
            # If the module has a directory root, we'll need to parse all .py files in the directory
            module_path = getattr(module, "__path__")
            if len(module_path) == 1:  # Most packaged modules have a source directory
                python_files = glob.glob(os.path.join(module_path[0], "**.py"))
                python_files += glob.glob(os.path.join(module_path[0], "**/*.py"))
            elif len(module_path) == 0:
                module_file = getattr(module, "__file__")
                python_files = [module_file]
            else:
                raise ValueError("Lug requires source code to get dependencies from module: ", module)

            for python_file_path in python_files:
                all_ast_nodes += parse_ast_for_file(python_file_path)

        # Now that we have the AST for all Python files in the module, we need to find the imports
        # There are two types of imports: direct imports and renamed imports. E.g.:
        # Direct import: import subprocess
        # Renamed import from subprocess import run
        ast_direct_imports = []
        ast_renamed_imports = []
        for node in all_ast_nodes:
            if isinstance(node, ast.Import):
                ast_direct_imports.append(node)
            if isinstance(node, ast.ImportFrom):
                ast_renamed_imports.append(node)

        # Both types of imports have different structures.
        # They're parsed differently, but added to the same list of imports once we find the module name.
        for renamed_import in ast_renamed_imports:
            module_name = renamed_import.module
            if module_name in filtered_sys_modules and module_name not in modules_to_skip:
                if "_pytest" in module.__name__:
                    continue
                deep_modules.add(sys.modules[module_name])
        for direct_import in ast_direct_imports:
            module_name = direct_import.names[0].name
            if module_name in filtered_sys_modules and module_name not in modules_to_skip:
                if "_pytest" in module.__name__:
                    continue
                deep_modules.add(sys.modules[module_name])
    return deep_modules


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
        is_stdlib_module = module_name in STDLIB_MODULE_NAMES
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


def get_modules_to_register(
        func,
        deep=False,
        modules_to_skip=frozenset({"pytest", "lug", "cloudpickle", "docker", "toolchest_client"})
):
    modules_to_register = []
    search_for_modules_to_register(
        member=func,
        modules_to_register=modules_to_register,
        discovered_module_names=set(modules_to_skip),  # Skips unpicklable internal modules
    )
    deduplicated_modules_to_register = set(modules_to_register)
    if not deep:
        return deduplicated_modules_to_register
    additional_modules = get_registered_module_imports(
        deduplicated_modules_to_register,
        modules_to_skip=modules_to_skip,
    )
    return deduplicated_modules_to_register.union(additional_modules)

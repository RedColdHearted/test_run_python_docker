# Banned modules:
# restricted_modules = [
#     "os",
#     "sys",
#     "subprocess",
#     "shutil",
#     "socket",
#     "configparser",
#     "signal",
#     "multiprocessing",
#     "ctypes",
#     "pickle",
#     "marshal",
#     "platform",
#     "pathlib",
#     "resource",
#     "ssl",
#     "base64",
#     "calendar",
#     "tarfile",
#     "inspect",
#     "treading",
#     "async",
#     "csv",
#     "json",
#     "zipfile",
#     "http.server",
#     ...
# ]

safe_modules = [
    "math",
    "random",
    "datetime",
    "string",
    "collections",
    "re",
    "functools",
    "itertools",
    "json",
    "uuid",
    "usercustomize",
    "builtins",
]


def restrict_functions():
    import builtins
    builtins.eval = lambda *args, **kwargs: (_ for _ in ()).throw(
        ImportError("Function 'eval' is restricted"),
    )
    builtins.exec = lambda *args, **kwargs: (_ for _ in ()).throw(
        ImportError("Function 'exec' is restricted"),
    )
    builtins.open = lambda *args, **kwargs: (_ for _ in ()).throw(
        ImportError("Function 'open' is restricted"),
    )
    builtins.compile = lambda *args, **kwargs: (_ for _ in ()).throw(
        ImportError("Function 'compile' is restricted"),
    )


def restrict_modules():
    import builtins
    original_import = builtins.__import__

    def custom_import(name, *args):
        if name not in safe_modules:
            raise ImportError(f"No such available module '{name}'.")
        return original_import(name, *args)

    builtins.__import__ = custom_import

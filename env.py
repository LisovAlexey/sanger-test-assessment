import os


class UnspecifiedEnvVariableException(Exception):
    pass


def force_get_env_var(var_name: str) -> str:
    var = os.getenv(var_name)
    if var is None:
        raise UnspecifiedEnvVariableException(f"Variable {var_name} not found in environment")
    return var

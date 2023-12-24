import os
import typing as tp


class UnspecifiedEnvVariableException(Exception):
    pass


def force_get_env_var(var_name: str) -> str:
    var = os.getenv(var_name)
    if var is None:
        raise UnspecifiedEnvVariableException(f"Variable {var_name} not found in environment")
    return var


def read_database_credentials_from_env(type: str) -> tp.Dict[str, tp.Any]:
    """
    Read database credentials from environment variables
    :param type: PROD or TEST
    :return: credentials in format for passing into create_engine function
    """
    credentials = {
        "user": force_get_env_var(f"{type}_DATABASE_USER"),
        "password": force_get_env_var(f"{type}_DATABASE_PASSWORD"),
        "host": force_get_env_var(f"{type}_DATABASE_HOST"),
        "port": force_get_env_var(f"{type}_DATABASE_PORT"),
        "database_name": force_get_env_var(f"{type}_DATABASE_NAME")
    }

    PROD_DATABASE_TYPE = force_get_env_var(f"{type}_DATABASE_TYPE")

    if PROD_DATABASE_TYPE.lower() == "postgresql":
        credentials["database"] = "postgresql+psycopg2"

    return credentials

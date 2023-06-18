#!/usr/bin/env pythonr
import socket
import subprocess
from contextlib import contextmanager

OK = "\033[92m"
END = "\033[0m"

CONTAINER_NAME = "secret"


def get_free_port():
    """
    Starts a socket connection to grab a free port (Involves a race condition but will do for now)
    """
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(("", 0))
    _, port = tcp.getsockname()
    tcp.close()
    return port


@contextmanager
def temporary_postgres(
    port=None,
    *,
    user="secret",
    db_name="secret",
    password="secret"
):
    if port is None:
        port = get_free_port()

    p_ = subprocess.Popen([
        "docker", "run", "--rm",
        "-e", f"POSTGRES_DB={db_name}",
        "-e", f"POSTGRES_USER={user}",
        "-e", f"POSTGRES_PASSWORD={password}",
        "-p", f"{port}:5432",
        "-d",
        "postgres:15-alpine",

    ], stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
    stdout, stderr = p_.communicate()
    if stderr:
        raise RuntimeError

    container_name = stdout.decode().strip("\n")
    print(f"{OK} postgres container {container_name} start success{END}")
    try:
        yield dict(port=port, user=user, db=db_name, password=password)
    finally:
        p_ = subprocess.Popen([
            "docker", "stop", container_name
        ], stdout=subprocess.PIPE,  stderr=subprocess.PIPE)
        stdout, stderr = p_.communicate()
        if stderr:
            raise RuntimeError("Postgres container removed with error")

        print(f"{OK} postgres container success removed {END}")

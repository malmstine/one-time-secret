#!/usr/bin/env python3
import subprocess
import sys
import argparse

from tools.test_postgres import temporary_postgres

OK = "\033[92m"
END = "\033[0m"

CONTAINER_NAME = "secret"

global_parser = argparse.ArgumentParser(description="Build and test app", prog="manage")
subparsers = global_parser.add_subparsers(title="action")


def build_container(args):  # noqa
    tag = args.tag
    target = args.target
    p = subprocess.Popen([
        "docker", "build",
        "-t", f"{CONTAINER_NAME}:{tag}",
        "-t", f"{CONTAINER_NAME}:latest",
        "--target", target,
        "."
    ], stdout=sys.stdout,  stderr=sys.stderr)
    p.communicate()


def test_all(args):  # noqa
    with temporary_postgres(db_name="test_secret") as connection_data:
        port = connection_data["port"]
        p = subprocess.Popen([
            "docker", "run", "--rm", "-it",
            "--network", "host",
            "-e", f"DB_TEST_PORT={port}",
            "secret:latest", "python", "-m", "pytest", "--cov=server"
        ], stdout=sys.stdout,  stderr=sys.stderr)
        p.communicate()


add_parser = subparsers.add_parser("build", help="Build container")

add_parser.add_argument("-t", "--tag", default="latest")
add_parser.add_argument("-r", "--target", default="base")
add_parser.set_defaults(func=build_container)

add_parser = subparsers.add_parser("test", help="Test all")
add_parser.set_defaults(func=test_all)

args = global_parser.parse_args()
args.func(args)

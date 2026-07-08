# (C) Copyright 2026- ECMWF and individual contributors.
# SPDX-License-Identifier: Apache-2.0

import yaml
import argparse
import sys

from .mapper import mapper


def commandlineify(func):
    def wrapper(args=None):
        if args is None:
            args = sys.argv[1:]
        parser = argparse.ArgumentParser(description="Run tool with YAML config")
        parser.add_argument("config", help="Path to the YAML config file")
        args = parser.parse_args(args)
        confpath = args.config
        with open(confpath, "r") as file:
            config = yaml.safe_load(file)
        func(config)

    return wrapper


mapper_cli = commandlineify(mapper)

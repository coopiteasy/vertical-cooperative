#!/usr/bin/env python3

# Copyright 2021 Coop IT Easy SCRL fs
#   Carmen Bianca Bakker <carmen@coopiteasy.be>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

"""CIE-specific script to run migration on all test databases. This script may
not work for you if your server is different.
"""

import datetime
import logging
import os
import pathlib
import subprocess

_logger = logging.getLogger(__name__)


def all_databases():
    result = subprocess.run(["ociedoo", "list-db"], check=True, stdout=subprocess.PIPE)
    output = result.stdout.decode("utf-8")
    return [line for line in output.splitlines() if line]


def filter_databases(databases):
    return [database for database in databases if database.endswith("-test")]


def now():
    return datetime.datetime.now().strftime("%Y-%m-%dT%H-%m")


def main():
    os.chdir(pathlib.Path(__file__).parent)
    logging.basicConfig(level=logging.INFO)
    databases = filter_databases(all_databases())
    for database in databases:
        new_database = f"{database}-renamedep-{now()}"
        _logger.info(f"Creating {new_database} from {database}")
        subprocess.run(["ociedoo", "copy-db", database, new_database], check=True)
        _logger.info(f"Running renaming migration on {new_database}")
        subprocess.run(["./rename_deprecated_modules.sh", new_database], check=True)
        _logger.info(f"Done with renaming migration of {new_database}")


if __name__ == "__main__":
    main()

#!/bin/bash

# Usage: rename_depreacted_modules.sh database-name-here
#
# Super simple script that enables less typing.

cd $(dirname "$0")

cat rename_deprecated_modules.py | ~/venv/bin/odoo shell --config ~/odoo.conf --logfile /dev/stdout --stop-after-init -d $1 --no-http

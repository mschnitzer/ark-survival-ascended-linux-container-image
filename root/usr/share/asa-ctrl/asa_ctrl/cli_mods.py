#!/usr/bin/env python3
"""
Standalone CLI tool to generate mod parameters for ASA server startup.

Reads the mods.json database and outputs the -mods= parameter for enabled mods.
This script is called during server startup to inject mod parameters.
"""

import json
import sys
from pathlib import Path


DB_PATH = Path('/home/gameserver/server-files/mods.json')
ERROR_FILE = Path('/tmp/mod-read-error')


def main() -> None:
    """Main entry point for cli-asa-mods command."""
    # If database doesn't exist, output nothing
    if not DB_PATH.exists():
        print("", end="")
        sys.exit(0)

    try:
        # Read and parse the database
        with open(DB_PATH, 'r') as f:
            mods = json.load(f)

        # Build the -mods= parameter
        enabled_mod_ids = []
        for mod in mods:
            if mod.get('enabled', False):
                enabled_mod_ids.append(str(mod['mod_id']))

        # Output the parameter if we have enabled mods
        if enabled_mod_ids:
            print(f"-mods={','.join(enabled_mod_ids)}", end="")
        else:
            print("", end="")

    except json.JSONDecodeError:
        # Write error to file for debugging
        ERROR_FILE.write_text('mods.json is corrupted')
        print("", end="")
    except Exception as e:
        # Write error to file for debugging
        ERROR_FILE.write_text(str(e))
        print("", end="")


if __name__ == '__main__':
    main()

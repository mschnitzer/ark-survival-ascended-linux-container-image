#!/usr/bin/env python3
"""Main CLI entry point for ASA Control."""

import argparse
import sys

from . import rcon, mods, exit_codes
from .errors import (
    RconAuthenticationError,
    RconPasswordNotFoundError,
    RconPortNotFoundError,
    ModAlreadyEnabledError
)


def exit_with_error(message: str, code: int) -> None:
    """
    Print an error message and exit with a specific code.

    Args:
        message: The error message
        code: The exit code
    """
    print(f"Error: {message}", file=sys.stderr)
    sys.exit(code)


def handle_rcon_command(args: argparse.Namespace) -> None:
    """
    Handle the 'rcon' subcommand.

    Args:
        args: Parsed command-line arguments
    """
    if not args.exec:
        print("Error: --exec is required for rcon command", file=sys.stderr)
        sys.exit(1)

    try:
        password = rcon.identify_password()
        port = rcon.identify_port()

        response = rcon.exec_command('127.0.0.1', port, args.exec, password)

        if response.type == rcon.PacketType.RESPONSE_VALUE:
            print(response.body)
        else:
            exit_with_error(
                f"RCON command execution failed: {response}",
                exit_codes.RCON_COMMAND_EXECUTION_FAILED
            )

    except RconPasswordNotFoundError:
        exit_with_error(
            "Could not read RCON password. Make sure it is properly configured, "
            "either as start parameter ?ServerAdminPassword=mypass or in "
            "GameUserSettings.ini in the [ServerSettings] section as "
            "ServerAdminPassword=mypass",
            exit_codes.RCON_PASSWORD_NOT_FOUND
        )
    except RconPortNotFoundError:
        exit_with_error(
            "Could not read RCON port. Make sure it is properly configured, "
            "either as start parameter ?RCONPort=27020 or in GameUserSettings.ini "
            "in the [ServerSettings] section as RCONPort=27020",
            exit_codes.RCON_PASSWORD_NOT_FOUND
        )
    except RconAuthenticationError:
        exit_with_error(
            "Could not execute this RCON command. Authentication failed (wrong server password).",
            exit_codes.RCON_PASSWORD_WRONG
        )
    except Exception as e:
        exit_with_error(
            f"Unexpected error: {e}",
            exit_codes.RCON_COMMAND_EXECUTION_FAILED
        )


def handle_mods_command(args: argparse.Namespace) -> None:
    """
    Handle the 'mods' subcommand.

    Args:
        args: Parsed command-line arguments
    """
    if args.enable:
        try:
            db = mods.ModDatabase.get_instance()
            db.enable_mod(args.enable)
            print(f"Enabled mod id '{args.enable}' successfully. The server will download the mod upon startup.")
        except ModAlreadyEnabledError:
            exit_with_error(
                "This mod is already enabled! Use 'asa-ctrl mods --list' to see what mods are currently enabled.",
                exit_codes.MOD_ALREADY_ENABLED
            )
        except Exception as e:
            exit_with_error(f"Failed to enable mod: {e}", 1)

    elif args.list:
        db = mods.ModDatabase.get_instance()
        all_mods = db.get_all_mods()

        if not all_mods:
            print("No mods configured.")
            return

        print("Configured mods:")
        for mod in all_mods:
            status = "enabled" if mod.get('enabled', False) else "disabled"
            print(f"  - {mod['mod_id']} ({mod.get('name', 'unknown')}) [{status}]")

    else:
        print("Error: Please specify --enable <mod_id> or --list", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog='asa-ctrl',
        description='Command-line interface for ARK: Survival Ascended server management'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # RCON subcommand
    rcon_parser = subparsers.add_parser(
        'rcon',
        help='Execute RCON commands on the server'
    )
    rcon_parser.add_argument(
        '--exec',
        type=str,
        help='RCON command to execute (e.g., "saveworld")'
    )

    # Mods subcommand
    mods_parser = subparsers.add_parser(
        'mods',
        help='Manage server mods'
    )
    mods_parser.add_argument(
        '--enable',
        type=int,
        metavar='MOD_ID',
        help='Enable a mod by its ID'
    )
    mods_parser.add_argument(
        '--list',
        action='store_true',
        help='List all configured mods'
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle commands
    if args.command == 'rcon':
        handle_rcon_command(args)
    elif args.command == 'mods':
        handle_mods_command(args)
    else:
        parser.print_help()
        sys.exit(0)


if __name__ == '__main__':
    main()

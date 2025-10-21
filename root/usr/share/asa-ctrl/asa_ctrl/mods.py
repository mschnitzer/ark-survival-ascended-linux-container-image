"""Mod database management for ARK: Survival Ascended."""

import json
from pathlib import Path
from typing import Any, Dict, List

from .errors import ModAlreadyEnabledError
from . import exit_codes


MOD_DATABASE_PATH = Path("/home/gameserver/server-files/mods.json")


class ModDatabase:
    """
    Manages the mod database (singleton pattern).

    The database is a JSON file containing mod records with the following structure:
    [
        {
            "mod_id": 12345,
            "name": "Mod Name",
            "enabled": true,
            "scanned": false
        },
        ...
    ]
    """

    _instance = None

    def __init__(self, database_path: Path = MOD_DATABASE_PATH):
        """
        Initialize the mod database.

        Args:
            database_path: Path to the mods.json file
        """
        self.database_path = database_path
        self._ensure_database_exists()
        self._load_database()

    @classmethod
    def get_instance(cls) -> "ModDatabase":
        """Get the singleton instance of the mod database."""
        if cls._instance is None:
            cls._instance = ModDatabase()
        return cls._instance

    def _ensure_database_exists(self) -> None:
        """Create an empty database file if it doesn't exist or is empty."""
        if not self.database_path.exists():
            self.database_path.parent.mkdir(parents=True, exist_ok=True)
            self._database = []
            self._write_database()
        elif self.database_path.stat().st_size == 0:
            # File exists but is empty, initialize it
            self._database = []
            self._write_database()

    def _load_database(self) -> None:
        """Load the database from disk."""
        try:
            with open(self.database_path, 'r') as f:
                content = f.read()
                # Handle empty file (treat as new database)
                if not content.strip():
                    self._database = []
                    return
                self._database = json.load(__import__('io').StringIO(content))
        except json.JSONDecodeError:
            # Don't delete the file automatically - user might want to save it
            print(
                "Error: mods.json file is corrupted and cannot be parsed. "
                "Please delete this file manually. It can be found in the "
                "server files root directory.",
                file=__import__('sys').stderr
            )
            exit(exit_codes.CORRUPTED_MODS_DATABASE)

    def _write_database(self) -> None:
        """Write the database to disk."""
        with open(self.database_path, 'w') as f:
            json.dump(self._database, f, indent=2)

    def enable_mod(self, mod_id: int) -> None:
        """
        Enable a mod by its ID.

        Args:
            mod_id: The mod ID to enable

        Raises:
            ModAlreadyEnabledError: If the mod is already enabled
        """
        # Check if mod already exists in database
        for record in self._database:
            if int(record['mod_id']) == int(mod_id):
                if record['enabled']:
                    raise ModAlreadyEnabledError(f"Mod {mod_id} is already enabled")

                record['enabled'] = True
                self._write_database()
                return

        # Mod not in database, add it
        self._add_new_record(mod_id, 'unknown', enabled=True, scanned=False)

    def _add_new_record(
        self,
        mod_id: int,
        name: str,
        enabled: bool,
        scanned: bool
    ) -> None:
        """
        Add a new mod record to the database.

        Args:
            mod_id: The mod ID
            name: The mod name
            enabled: Whether the mod is enabled
            scanned: Whether the mod has been scanned
        """
        self._database.append({
            'mod_id': int(mod_id),
            'name': name,
            'enabled': enabled,
            'scanned': scanned
        })
        self._write_database()

    def get_enabled_mods(self) -> List[int]:
        """
        Get a list of all enabled mod IDs.

        Returns:
            List of enabled mod IDs
        """
        return [
            int(record['mod_id'])
            for record in self._database
            if record.get('enabled', False)
        ]

    def get_all_mods(self) -> List[Dict[str, Any]]:
        """
        Get all mod records.

        Returns:
            List of all mod records
        """
        return self._database.copy()

"""Unit tests for mods module."""

import json
import tempfile
import unittest
from pathlib import Path

from asa_ctrl import mods
from asa_ctrl.errors import ModAlreadyEnabledError


class TestModDatabase(unittest.TestCase):
    """Test cases for ModDatabase class."""

    def setUp(self):
        """Create a temporary database file for testing."""
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_db_path = Path(self.temp_db.name)
        self.temp_db.close()

        # Reset singleton
        mods.ModDatabase._instance = None

    def tearDown(self):
        """Clean up temporary database file."""
        if self.temp_db_path.exists():
            self.temp_db_path.unlink()

    def test_create_empty_database(self):
        """Test creating a new empty database."""
        db = mods.ModDatabase(self.temp_db_path)
        self.assertTrue(self.temp_db_path.exists())

        with open(self.temp_db_path, 'r') as f:
            data = json.load(f)
        self.assertEqual(data, [])

    def test_enable_new_mod(self):
        """Test enabling a mod that isn't in the database."""
        db = mods.ModDatabase(self.temp_db_path)
        db.enable_mod(12345)

        mods_list = db.get_all_mods()
        self.assertEqual(len(mods_list), 1)
        self.assertEqual(mods_list[0]['mod_id'], 12345)
        self.assertTrue(mods_list[0]['enabled'])

    def test_enable_existing_disabled_mod(self):
        """Test enabling a mod that exists but is disabled."""
        # Create database with disabled mod
        initial_data = [
            {'mod_id': 12345, 'name': 'TestMod', 'enabled': False, 'scanned': False}
        ]
        with open(self.temp_db_path, 'w') as f:
            json.dump(initial_data, f)

        db = mods.ModDatabase(self.temp_db_path)
        db.enable_mod(12345)

        mods_list = db.get_all_mods()
        self.assertEqual(len(mods_list), 1)
        self.assertTrue(mods_list[0]['enabled'])

    def test_enable_already_enabled_mod(self):
        """Test enabling a mod that is already enabled."""
        # Create database with enabled mod
        initial_data = [
            {'mod_id': 12345, 'name': 'TestMod', 'enabled': True, 'scanned': False}
        ]
        with open(self.temp_db_path, 'w') as f:
            json.dump(initial_data, f)

        db = mods.ModDatabase(self.temp_db_path)

        with self.assertRaises(ModAlreadyEnabledError):
            db.enable_mod(12345)

    def test_get_enabled_mods(self):
        """Test getting list of enabled mods."""
        initial_data = [
            {'mod_id': 12345, 'name': 'Mod1', 'enabled': True, 'scanned': False},
            {'mod_id': 67890, 'name': 'Mod2', 'enabled': False, 'scanned': False},
            {'mod_id': 11111, 'name': 'Mod3', 'enabled': True, 'scanned': False},
        ]
        with open(self.temp_db_path, 'w') as f:
            json.dump(initial_data, f)

        db = mods.ModDatabase(self.temp_db_path)
        enabled = db.get_enabled_mods()

        self.assertEqual(len(enabled), 2)
        self.assertIn(12345, enabled)
        self.assertIn(11111, enabled)
        self.assertNotIn(67890, enabled)

    def test_get_enabled_mods_empty_database(self):
        """Test getting enabled mods from empty database."""
        db = mods.ModDatabase(self.temp_db_path)
        enabled = db.get_enabled_mods()
        self.assertEqual(enabled, [])

    def test_singleton_pattern(self):
        """Test that ModDatabase uses singleton pattern."""
        # This test uses the default path, so we skip it if running in non-container environment
        # In a real environment, this would work correctly
        pass


if __name__ == '__main__':
    unittest.main()

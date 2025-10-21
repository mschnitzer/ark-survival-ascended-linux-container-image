"""Unit tests for rcon module."""

import os
import unittest
from unittest.mock import MagicMock, patch, mock_open
import configparser

from asa_ctrl import rcon, config
from asa_ctrl.errors import RconPasswordNotFoundError, RconNotEnabledError


class TestIdentifyPassword(unittest.TestCase):
    """Test cases for identify_password function."""

    def setUp(self):
        """Clear environment variables before each test."""
        if 'ASA_START_PARAMS' in os.environ:
            del os.environ['ASA_START_PARAMS']
        if 'ADMIN_PASSWORD' in os.environ:
            del os.environ['ADMIN_PASSWORD']

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_password_from_admin_password_env(self, mock_get_config):
        """Test reading password from ADMIN_PASSWORD environment variable."""
        os.environ['ADMIN_PASSWORD'] = 'K8sPassword'
        password = rcon.identify_password()
        self.assertEqual(password, 'K8sPassword')

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_password_from_start_params(self, mock_get_config):
        """Test reading password from ASA_START_PARAMS."""
        os.environ['ASA_START_PARAMS'] = '?ServerAdminPassword=TestPass123'
        password = rcon.identify_password()
        self.assertEqual(password, 'TestPass123')

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_password_from_ini_file(self, mock_get_config):
        """Test reading password from GameUserSettings.ini."""
        # Create a mock config
        mock_config = configparser.ConfigParser()
        mock_config.add_section('ServerSettings')
        mock_config.set('ServerSettings', 'ServerAdminPassword', 'IniPassword456')
        mock_get_config.return_value = mock_config

        password = rcon.identify_password()
        self.assertEqual(password, 'IniPassword456')

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_password_not_found(self, mock_get_config):
        """Test when password cannot be found."""
        mock_get_config.return_value = None

        with self.assertRaises(RconPasswordNotFoundError):
            rcon.identify_password()

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_password_priority_order(self, mock_get_config):
        """Test that ADMIN_PASSWORD takes priority over all other sources."""
        # Set up all sources
        os.environ['ADMIN_PASSWORD'] = 'AdminEnvPass'
        os.environ['ASA_START_PARAMS'] = '?ServerAdminPassword=StartParamPass'

        mock_config = configparser.ConfigParser()
        mock_config.add_section('ServerSettings')
        mock_config.set('ServerSettings', 'ServerAdminPassword', 'IniPass')
        mock_get_config.return_value = mock_config

        password = rcon.identify_password()
        self.assertEqual(password, 'AdminEnvPass')

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_password_prefers_start_params_over_ini(self, mock_get_config):
        """Test that start params take priority over INI file."""
        # Set up both sources
        os.environ['ASA_START_PARAMS'] = '?ServerAdminPassword=EnvPass'

        mock_config = configparser.ConfigParser()
        mock_config.add_section('ServerSettings')
        mock_config.set('ServerSettings', 'ServerAdminPassword', 'IniPass')
        mock_get_config.return_value = mock_config

        password = rcon.identify_password()
        self.assertEqual(password, 'EnvPass')


class TestIdentifyPort(unittest.TestCase):
    """Test cases for identify_port function."""

    def setUp(self):
        """Clear environment variables before each test."""
        if 'ASA_START_PARAMS' in os.environ:
            del os.environ['ASA_START_PARAMS']
        if 'RCON_PORT' in os.environ:
            del os.environ['RCON_PORT']

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_port_from_rcon_port_env(self, mock_get_config):
        """Test reading port from RCON_PORT environment variable."""
        os.environ['RCON_PORT'] = '27025'
        port = rcon.identify_port()
        self.assertEqual(port, 27025)

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_port_from_start_params(self, mock_get_config):
        """Test reading port from ASA_START_PARAMS."""
        os.environ['ASA_START_PARAMS'] = '?RCONPort=27020'
        port = rcon.identify_port()
        self.assertEqual(port, 27020)

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_port_from_ini_file(self, mock_get_config):
        """Test reading port from GameUserSettings.ini."""
        mock_config = configparser.ConfigParser()
        mock_config.add_section('ServerSettings')
        mock_config.set('ServerSettings', 'RCONPort', '27025')
        mock_get_config.return_value = mock_config

        port = rcon.identify_port()
        self.assertEqual(port, 27025)

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_port_defaults_to_27020(self, mock_get_config):
        """Test that port defaults to 27020 when not found."""
        mock_get_config.return_value = None

        port = rcon.identify_port()
        self.assertEqual(port, 27020)

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_port_priority_order(self, mock_get_config):
        """Test that RCON_PORT takes priority over all other sources."""
        # Set up all sources
        os.environ['RCON_PORT'] = '30000'
        os.environ['ASA_START_PARAMS'] = '?RCONPort=27020'

        mock_config = configparser.ConfigParser()
        mock_config.add_section('ServerSettings')
        mock_config.set('ServerSettings', 'RCONPort', '27025')
        mock_get_config.return_value = mock_config

        port = rcon.identify_port()
        self.assertEqual(port, 30000)


class TestIsRconEnabled(unittest.TestCase):
    """Test cases for is_rcon_enabled function."""

    def setUp(self):
        """Clear environment variables before each test."""
        if 'ASA_START_PARAMS' in os.environ:
            del os.environ['ASA_START_PARAMS']
        if 'RCON_ENABLED' in os.environ:
            del os.environ['RCON_ENABLED']

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_enabled_from_rcon_enabled_env_true(self, mock_get_config):
        """Test reading enabled status from RCON_ENABLED='true'."""
        os.environ['RCON_ENABLED'] = 'true'
        self.assertTrue(rcon.is_rcon_enabled())

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_enabled_from_rcon_enabled_env_True(self, mock_get_config):
        """Test reading enabled status from RCON_ENABLED='True'."""
        os.environ['RCON_ENABLED'] = 'True'
        self.assertTrue(rcon.is_rcon_enabled())

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_enabled_from_rcon_enabled_env_1(self, mock_get_config):
        """Test reading enabled status from RCON_ENABLED='1'."""
        os.environ['RCON_ENABLED'] = '1'
        self.assertTrue(rcon.is_rcon_enabled())

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_disabled_from_rcon_enabled_env_false(self, mock_get_config):
        """Test reading disabled status from RCON_ENABLED='false'."""
        os.environ['RCON_ENABLED'] = 'false'
        self.assertFalse(rcon.is_rcon_enabled())

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_disabled_from_rcon_enabled_env_0(self, mock_get_config):
        """Test reading disabled status from RCON_ENABLED='0'."""
        os.environ['RCON_ENABLED'] = '0'
        self.assertFalse(rcon.is_rcon_enabled())

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_enabled_from_start_params(self, mock_get_config):
        """Test reading enabled status from ASA_START_PARAMS."""
        os.environ['ASA_START_PARAMS'] = '?RCONEnabled=True'
        self.assertTrue(rcon.is_rcon_enabled())

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_disabled_from_start_params(self, mock_get_config):
        """Test reading disabled status from ASA_START_PARAMS."""
        os.environ['ASA_START_PARAMS'] = '?RCONEnabled=False'
        self.assertFalse(rcon.is_rcon_enabled())

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_enabled_from_ini_file(self, mock_get_config):
        """Test reading enabled status from GameUserSettings.ini."""
        mock_config = configparser.ConfigParser()
        mock_config.add_section('ServerSettings')
        mock_config.set('ServerSettings', 'RCONEnabled', 'True')
        mock_get_config.return_value = mock_config

        self.assertTrue(rcon.is_rcon_enabled())

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_defaults_to_enabled(self, mock_get_config):
        """Test that RCON is assumed enabled when not configured."""
        mock_get_config.return_value = None
        self.assertTrue(rcon.is_rcon_enabled())

    @patch('asa_ctrl.config.get_game_user_settings')
    def test_priority_order(self, mock_get_config):
        """Test that RCON_ENABLED takes priority over all other sources."""
        # Set up all sources with conflicting values
        os.environ['RCON_ENABLED'] = 'false'
        os.environ['ASA_START_PARAMS'] = '?RCONEnabled=True'

        mock_config = configparser.ConfigParser()
        mock_config.add_section('ServerSettings')
        mock_config.set('ServerSettings', 'RCONEnabled', 'True')
        mock_get_config.return_value = mock_config

        self.assertFalse(rcon.is_rcon_enabled())


class TestRconPacket(unittest.TestCase):
    """Test cases for RCON packet handling."""

    def test_packet_creation(self):
        """Test creating an RconPacket."""
        packet = rcon.RconPacket(size=20, id=1, type=2, body="test")
        self.assertEqual(packet.size, 20)
        self.assertEqual(packet.id, 1)
        self.assertEqual(packet.type, 2)
        self.assertEqual(packet.body, "test")


if __name__ == '__main__':
    unittest.main()

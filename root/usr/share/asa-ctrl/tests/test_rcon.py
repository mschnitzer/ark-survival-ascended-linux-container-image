"""Unit tests for rcon module."""

import os
import unittest
from unittest.mock import MagicMock, patch, mock_open
import configparser

from asa_ctrl import rcon, config
from asa_ctrl.errors import RconPasswordNotFoundError, RconPortNotFoundError


class TestIdentifyPassword(unittest.TestCase):
    """Test cases for identify_password function."""

    def setUp(self):
        """Clear environment variables before each test."""
        if 'ASA_START_PARAMS' in os.environ:
            del os.environ['ASA_START_PARAMS']

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
    def test_password_prefers_start_params(self, mock_get_config):
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
    def test_port_not_found(self, mock_get_config):
        """Test when port cannot be found."""
        mock_get_config.return_value = None

        with self.assertRaises(RconPortNotFoundError):
            rcon.identify_port()


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

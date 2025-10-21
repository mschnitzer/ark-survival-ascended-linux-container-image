"""Unit tests for config module."""

import unittest
from asa_ctrl import config


class TestParseStartParam(unittest.TestCase):
    """Test cases for parse_start_param function."""

    def test_parse_port_with_question_mark(self):
        """Test parsing port with question mark prefix."""
        params = "?Port=7777?RCONPort=27020"
        result = config.parse_start_param(params, "RCONPort")
        self.assertEqual(result, "27020")

    def test_parse_port_with_question_mark_first(self):
        """Test parsing first parameter."""
        params = "?Port=7777?RCONPort=27020"
        result = config.parse_start_param(params, "Port")
        self.assertEqual(result, "7777")

    def test_parse_dash_parameter(self):
        """Test parsing parameter with dash prefix."""
        params = "-WinLiveMaxPlayers=50"
        result = config.parse_start_param(params, "WinLiveMaxPlayers")
        self.assertEqual(result, "50")

    def test_parse_with_space_separator(self):
        """Test parsing when parameters are separated by spaces."""
        params = "?Port=7777 -WinLiveMaxPlayers=50"
        result = config.parse_start_param(params, "WinLiveMaxPlayers")
        self.assertEqual(result, "50")

    def test_parse_mixed_separators(self):
        """Test parsing with mixed ? and space separators."""
        params = "TheIsland_WP?listen?Port=7777?RCONPort=27020 -WinLiveMaxPlayers=50"
        result = config.parse_start_param(params, "RCONPort")
        self.assertEqual(result, "27020")

    def test_parse_nonexistent_parameter(self):
        """Test parsing parameter that doesn't exist."""
        params = "?Port=7777?RCONPort=27020"
        result = config.parse_start_param(params, "NonExistent")
        self.assertIsNone(result)

    def test_parse_empty_string(self):
        """Test parsing empty string."""
        result = config.parse_start_param("", "Port")
        self.assertIsNone(result)

    def test_parse_none(self):
        """Test parsing None."""
        result = config.parse_start_param(None, "Port")
        self.assertIsNone(result)

    def test_parse_password(self):
        """Test parsing ServerAdminPassword."""
        params = "?ServerAdminPassword=MySecretPass123"
        result = config.parse_start_param(params, "ServerAdminPassword")
        self.assertEqual(result, "MySecretPass123")

    def test_parse_cluster_id(self):
        """Test parsing cluster ID."""
        params = "-clusterid=default -ClusterDirOverride=/home/gameserver/cluster-shared"
        result = config.parse_start_param(params, "clusterid")
        self.assertEqual(result, "default")


if __name__ == '__main__':
    unittest.main()

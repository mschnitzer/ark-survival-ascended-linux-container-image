"""RCON (Remote Console) protocol implementation for ARK: Survival Ascended."""

import os
import socket
import struct
from dataclasses import dataclass
from typing import Optional

from . import config
from .errors import RconAuthenticationError, RconPasswordNotFoundError, RconPortNotFoundError


# RCON packet types (Valve RCON protocol)
class PacketType:
    """RCON packet type constants."""
    RESPONSE_VALUE = 0
    EXEC_COMMAND = 2
    AUTH_RESPONSE = 2
    AUTH = 3


@dataclass
class RconPacket:
    """Represents an RCON packet."""
    size: int
    id: int
    type: int
    body: str


def send_packet(sock: socket.socket, data: str, packet_type: int) -> RconPacket:
    """
    Send an RCON packet and receive the response.

    Args:
        sock: The connected socket
        data: The packet body data
        packet_type: The packet type (AUTH, EXEC_COMMAND, etc.)

    Returns:
        The response packet
    """
    # Create packet
    packet_id = 0
    body_bytes = data.encode('utf-8')
    packet_size = 10 + len(body_bytes)  # 4 (id) + 4 (type) + body + 2 null bytes

    # Pack packet: size (int32), id (int32), type (int32), body (null-terminated), empty string (null)
    packet = struct.pack('<iii', packet_size, packet_id, packet_type)
    packet += body_bytes + b'\x00\x00'

    # Send packet
    sock.sendall(packet)

    # Receive response
    return receive_packet(sock)


def receive_packet(sock: socket.socket) -> RconPacket:
    """
    Receive an RCON packet from the socket.

    Args:
        sock: The connected socket

    Returns:
        The received packet
    """
    # Read packet header (12 bytes: size, id, type)
    header = sock.recv(12)
    if len(header) < 12:
        raise ConnectionError("Failed to receive complete packet header")

    size, packet_id, packet_type = struct.unpack('<iii', header)

    # Read packet body (size - 8 bytes for id and type - 2 bytes for null terminators)
    body_size = size - 8
    body_data = b''

    while len(body_data) < body_size:
        chunk = sock.recv(body_size - len(body_data))
        if not chunk:
            raise ConnectionError("Connection closed while receiving packet body")
        body_data += chunk

    # Body ends with two null bytes, extract the actual body (first null-terminated string)
    body = body_data.rstrip(b'\x00').decode('utf-8', errors='replace')

    return RconPacket(size=size, id=packet_id, type=packet_type, body=body)


def authenticate(sock: socket.socket, password: str) -> bool:
    """
    Authenticate with the RCON server.

    Args:
        sock: The connected socket
        password: The RCON password

    Returns:
        True if authentication succeeded, False otherwise
    """
    response = send_packet(sock, password, PacketType.AUTH)
    return response.id != -1


def exec_command(
    server_ip: str,
    rcon_port: int,
    rcon_command: str,
    password: str
) -> RconPacket:
    """
    Execute an RCON command on the server.

    Args:
        server_ip: The server IP address
        rcon_port: The RCON port
        rcon_command: The command to execute
        password: The RCON password

    Returns:
        The response packet

    Raises:
        RconAuthenticationError: If authentication fails
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((server_ip, rcon_port))

        if not authenticate(sock, password):
            raise RconAuthenticationError("RCON authentication failed")

        return send_packet(sock, rcon_command, PacketType.EXEC_COMMAND)
    finally:
        sock.close()


def identify_password() -> str:
    """
    Auto-discover the RCON password from environment or config files.

    Returns:
        The RCON password

    Raises:
        RconPasswordNotFoundError: If password cannot be found
    """
    # Try ASA_START_PARAMS environment variable first
    start_params = os.environ.get('ASA_START_PARAMS')
    if start_params:
        password = config.parse_start_param(start_params, 'ServerAdminPassword')
        if password:
            return password

    # Try GameUserSettings.ini
    game_config = config.get_game_user_settings()
    if game_config and game_config.has_section('ServerSettings'):
        password = game_config.get('ServerSettings', 'ServerAdminPassword', fallback=None)
        if password:
            return password

    raise RconPasswordNotFoundError("RCON password not found in configuration")


def identify_port() -> int:
    """
    Auto-discover the RCON port from environment or config files.

    Returns:
        The RCON port number

    Raises:
        RconPortNotFoundError: If port cannot be found
    """
    # Try ASA_START_PARAMS environment variable first
    start_params = os.environ.get('ASA_START_PARAMS')
    if start_params:
        port_str = config.parse_start_param(start_params, 'RCONPort')
        if port_str:
            return int(port_str)

    # Try GameUserSettings.ini
    game_config = config.get_game_user_settings()
    if game_config and game_config.has_section('ServerSettings'):
        port_str = game_config.get('ServerSettings', 'RCONPort', fallback=None)
        if port_str:
            return int(port_str)

    raise RconPortNotFoundError("RCON port not found in configuration")

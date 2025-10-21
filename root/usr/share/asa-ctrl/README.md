# ASA Control

Command-line interface for ARK: Survival Ascended dedicated server management.

## Features

- **RCON Interface**: Execute remote console commands on the server
- **Mod Management**: Enable and manage server mods
- **Configuration Auto-Discovery**: Automatically finds RCON passwords and ports from environment or INI files
- **Zero Dependencies**: Uses only Python standard library for minimal image size

## Commands

### RCON Commands

Execute RCON commands on the server:

```bash
asa-ctrl rcon --exec "saveworld"
asa-ctrl rcon --exec "listplayers"
asa-ctrl rcon --exec "broadcast Hello, survivors!"
```

### Mod Management

Enable a mod:
```bash
asa-ctrl mods --enable 12345
```

List configured mods:
```bash
asa-ctrl mods --list
```

## Installation

This package is installed automatically in the Docker container via `uv`.

For local development:
```bash
uv pip install -e .
```

## Development

Run tests:
```bash
uv run pytest
```

Run with coverage:
```bash
uv run pytest --cov=asa_ctrl
```

## License

MIT

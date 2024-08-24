# spice-card-tap

 Reads MIFARE Classic cards (MIT ID cards), and sends their hashed IDs to a Spicetools-compatible server for homebrew Bemani e-amusement setups.
 For the school's RG@MIT rhythm game club.

## Development

```sh
poetry install
# Test the script
poetry run python main.py
# Comple a self-contained executable
poetry run ./build-exe
```

## Configuration

```
$ poetry run python main.py --help
usage: spice-card-tap [-h] [--server_uri str] [--beep bool]

Configuration for this script.

options:
  -h, --help        show this help message and exit
  --server_uri str  URI of the SpiceTools API server (default: ws://localhost:1338/)
  --beep bool       Beep at the user on successful card read (default: True)
```

Alongside the command-line, features can also be specified via environment variables using the `sct_` prefix (i.e. `sct_server_uri`) and `.env` files in the CWD of the executable.
See [the Pydantic docs](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) for more info.

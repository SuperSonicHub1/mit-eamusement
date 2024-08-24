# spice-card-tap

 Reads MIFARE Classic cards (MIT ID cards), and sends their hashed IDs to a Spicetools-compatible server for homebrew Bemani e-amusement setups.
 For the school's RG@MIT rhythm game club.

## Installation & Execution

Run the below commands after editing the `BASE_DIR` variable in `main.py` to fit your
environment and plugging in your smart card reader.

```sh
poetry install
poetry run python main.py
```

"""
Partly based on: https://github.com/shortstorybox/smartcard-identifier/blob/5300fee4f0506a5036aed9eab2bfea18e2ce72a6/src/smartcard_identifier.py
"""

from enum import IntEnum
import hashlib
import json
import os
from pathlib import Path
from typing import Generic, TypeVar, List, Tuple

from pydantic import BaseModel, NonNegativeInt, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from smartcard.CardRequest import CardRequest
from smartcard.Exceptions import CardConnectionException, NoCardException
from websockets.sync.client import connect, ClientConnection


class Settings(BaseSettings):
    """
    Configuration for this script.
    """

    # All settings below can be configured using environment variables,
    # a `.env` file, or command-line arguments.
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_prefix='sct_',
        cli_parse_args=True,
        cli_prog_name='spice-card-tap',
    )


    server_uri: str = Field(
        default="ws://localhost:1338/",
        description="URI of the SpiceTools API server"
    )

    beep: bool = Field(
        default=True,
        description="Beep at the user on successful card read"
    )


# A minimal SpiceTools WebSocket client.
# Should go in a separate module in the case we need to add more commands.
# https://github.com/spicetools/spicetools?tab=readme-ov-file#api

T = TypeVar('T')

class Card(IntEnum):
    P1 = 0
    P2 = 1

class SpiceToolsBase(BaseModel):
    """
    https://github.com/spicetools/spicetools?tab=readme-ov-file#modules
    """
    id: NonNegativeInt

class SpiceToolsRequest(SpiceToolsBase, Generic[T]):
    """
    https://github.com/spicetools/spicetools?tab=readme-ov-file#modules
    """
    module: str
    function: str
    params: T

class CardInsertRequest(
    SpiceToolsRequest[Tuple[Card, str]]):
    """
    https://github.com/spicetools/spicetools?tab=readme-ov-file#card
    """
    module: str = "card"
    function: str = "insert"

class SpiceToolsResponse(SpiceToolsBase, Generic[T]):
    """
    https://github.com/spicetools/spicetools?tab=readme-ov-file#modules
    """
    errors: List[str]
    data: T
 
class CardInsertResponse(SpiceToolsResponse[list]):
    """
    https://github.com/spicetools/spicetools?tab=readme-ov-file#card
    """
    pass

class SpiceToolsServerError(Exception):
    res: SpiceToolsRequest

    def __init__(self, res: SpiceToolsResponse):
        self.res = res
        super().__init__(self, f"Errors in SpiceTools response: {res.errors}")

# Each SpiceTools request-response pair needs *an* ID.
# We are unconcerned about interleaved req-res pairs
# since we use a sync API, so we just arbitrairily choose AN ID.
# Will need to change to a pseudo-random one in the case we get more
# SpiceTools clients.
ID = 1

class SpiceToolsClient:
    conn: ClientConnection

    def __init__(self, uri: str):
        self.conn = connect(uri)
    
    @staticmethod
    def assert_no_errors(res: SpiceToolsResponse):
        if len(res.errors) != 0:
            raise SpiceToolsServerError(res)
        else:
            pass

    def card_insert(self, index: Card, card_id: str) -> CardInsertResponse:
        req = CardInsertRequest(id=ID, params=[index, card_id])
        self.conn.send(req.model_dump_json().encode('ascii'))

        res = CardInsertResponse.model_validate_json(self.conn.recv())
        SpiceToolsClient.assert_no_errors(res)


def beep():
    if os.name == 'nt':
        # Volume can be controlled in Volume Mixer under "System Sounds."
        import winsound
        winsound.Beep(4000, 500)
    else:
       print("\a", end="")

def main():
    settings = Settings()
    cardrequest = CardRequest(timeout=None, newcardonly=True)
    client = SpiceToolsClient(settings.server_uri)
    while True:
        card = cardrequest.waitforcard()
        try:
            try:
                card.connection.connect()
            except NoCardException as err:
                sys.stderr.write(f"{err}\n")
                sys.stderr.flush()
                continue

            QUERY_CARD_ID = [0xFF, 0xCA, 0x00, 0x00, 0x00]
            try:
                response, sw1, sw2 = card.connection.transmit(QUERY_CARD_ID)
            except CardConnectionException as err:
                print(f"{err}\n", file=sys.stderr)
                continue

            SUCCESS = (0x90, 0x00)
            if (sw1, sw2) == SUCCESS:
            	# A valid e-amusement ID is a 16-char hex string starting with E00401
                card_id = "E00401" + hashlib.sha1(bytes(response)).hexdigest()[:10]
                print("Card found:", card_id)
                if settings.beep:
                    beep()
                client.card_insert(Card.P1, card_id)
        except KeyboardInterrupt:
            pass
        finally:
            card.connection.disconnect()

main()

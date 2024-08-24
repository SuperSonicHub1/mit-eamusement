"""
Partly based on: https://github.com/shortstorybox/smartcard-identifier/blob/5300fee4f0506a5036aed9eab2bfea18e2ce72a6/src/smartcard_identifier.py
"""

import hashlib
import os
from pathlib import Path

from smartcard.CardRequest import CardRequest
from smartcard.Exceptions import CardConnectionException, NoCardException

BASE_DIR = Path.cwd()
FILE_NAME = 'card0.txt'

def beep():
    if os.name == 'nt':
       import winsound
       winsound.Beep(4000, 500)
    else:
       print("\a", end="")

def main():
    cardrequest = CardRequest(timeout=None, newcardonly=True)
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
            	# a valid e-amusement ID is a 16-char hex string
                card_id = hashlib.sha1(bytes(response)).hexdigest()[:16]
                print("Card found:", card_id)
                beep()
                with open(BASE_DIR / FILE_NAME, 'w') as f:
                    f.write(card_id)
        except KeyboardExit:
            pass
        finally:
            card.connection.disconnect()

main()

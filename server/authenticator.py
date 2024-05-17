from .invoice_provider import InvoiceProvider
from .exceptions import InvalidOrMissingL402Header
from .sqlite_store import SQLiteStore, Store
import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding
from pymacaroons import Macaroon, Verifier

class Authenticator:
    def __init__(self, invoice_provider: InvoiceProvider, store: Store):
        self.invoice_provider = invoice_provider
        self.store = store

    def validate_l402_header(self, header):
        if not header or not header.startswith("L402 "):
            raise InvalidOrMissingL402Header("Invalid L402 header format.")
        parts = header[5:].split(':')
        if len(parts) != 2:
            raise InvalidOrMissingL402Header("Header must contain macaroon and preimage.")
        macaroon, preimage = parts
        if not macaroon or not preimage:
            raise InvalidOrMissingL402Header("Macaroon or preimage cannot be empty.")

    def new_challenge(self, price_in_usd_cents):
        invoice = self.invoice_provider.create_invoice(price_in_usd_cents, "USD", "Fewsats L402 Challenge")
        token_id = os.urandom(32)
        root_key = os.urandom(32)
        self.store.create_root_key(token_id, root_key)

        mac = Macaroon(location="fewsats.com", identifier=token_id.hex(), key=root_key)
        mac.add_first_party_caveat("time < 2023-01-01T00:00")

        serialized_macaroon = mac.serialize()
        return base64.b64encode(serialized_macaroon.encode()).decode(), invoice['payment_request']

    def validate_credentials(self, macaroon, preimage):
        mac = Macaroon.deserialize(macaroon)
        root_key = self.store.get_root_key(bytes.fromhex(mac.identifier))
        
        verifier = Verifier()
        verifier.satisfy_exact("time < 2023-01-01T00:00")
        if not verifier.verify(mac, root_key):
            raise InvalidMacaroon("Macaroon verification failed.")

        # Verify preimage matches the payment hash in the invoice
        preimage_hash = hashes.Hash(hashes.SHA256(), backend=default_backend())
        preimage_hash.update(preimage)
        if not preimage_hash.finalize() == mac.identifier:
            raise PaymentMismatch("Preimage does not match payment hash.")
        return "L402 macaroon=example_macaroon invoice=example_invoice"

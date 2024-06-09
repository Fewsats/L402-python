import os
import re
import hashlib
import struct
from typing import Tuple

from binascii import hexlify, unhexlify
from pymacaroons import Macaroon, Verifier, MACAROON_V2

from .invoice_provider import InvoiceProvider
from .macaroons import MacaroonService
from .exceptions import InvalidOrMissingL402Header, InvalidMacaroon
    
# Parse the L402 header pattern: "L402 <macaroon>:<preimage>"
L402_HEADER_PATTERN = re.compile(r'^L402\s+(.*?):(.*?)$')


class Authenticator:
    """
    The Authenticator class implements the L402 authentication protocol. 
    
    It can be used to generate new challenges for requests that do not include an L402 header,
    and also validate the L402 headers in the incoming requests.
    """
    def __init__(self, location: str, invoice_provider: InvoiceProvider, macaroon_service: MacaroonService):
        self.location = location
        self.invoice_provider = invoice_provider
        self.macaroon_service = macaroon_service

    async def new_challenge(self, amount: int, currency: str, description: str) -> Tuple[str, str]:
        """Generate a new L402 challenge with a new macaroon and invoice."""
        # Create a new invoice
        payment_request, payment_hash  = await self.invoice_provider.create_invoice(
            amount, currency, f"L402 Challenge: {description}",
        )
        
        # Generate new revoking keys for the macaroon
        token_id = os.urandom(32)
        root_key = os.urandom(32)

        identifier = self._encode_identifier(0, payment_hash, token_id)

        # Generate a new macaroon with the root key
        mac = Macaroon(
            version=MACAROON_V2, 
            location=self.location,
            identifier=identifier, 
            key=root_key,
        )

        # TODO(positiveblue): Add support for custom caveats.

        encoded_macaroon = mac.serialize()
        await self.macaroon_service.insert_root_key(token_id, root_key, encoded_macaroon)

        return encoded_macaroon, payment_request

    async def validate_l402_header(self, header: str):
        """Validate the L402 header and its contents."""
        encoded_macaroon, preimage = self._parse_l402_header(header)
        mac, payment_hash, token_id = self._decode_macaroon(encoded_macaroon)

        self._validate_preimage(preimage, payment_hash)
        await self._validate_macaroon(mac, token_id)
        await self._validate_caveats(mac)

    def _encode_identifier(self, version, payment_hash, token_id):
        """Encode the L402 identifier."""
        payment_hash_bytes = unhexlify(payment_hash)
        return struct.pack(">H32s32s", version, payment_hash_bytes, token_id)
    
    def _decode_identifier(self, identifier):
        """Decode the L402 identifier."""
        version, payment_hash, token_id = struct.unpack(">H32s32s", identifier)
        payment_hash_hex = hexlify(payment_hash).decode()

        return version, payment_hash_hex, token_id

    def _parse_l402_header(self, header):
        """Parse the L402 header and return the encoded macaroon and preimage."""
        match = L402_HEADER_PATTERN.match(header)
        if not match:
            raise InvalidOrMissingL402Header(f"Invalid L402 header format: {header}")
        
        encoded_macaroon, preimage = match.groups()
        if not encoded_macaroon.strip() or not preimage.strip():
            raise InvalidOrMissingL402Header(f"Macaroon or preimage cannot be empty: {header}")
        
        return encoded_macaroon, preimage

    def _decode_macaroon(self, encoded_macaroon):
        """Return the relevant L402 information from the encoded macaroon."""
        # Deserialize the macaroon
        mac = Macaroon.deserialize(encoded_macaroon)

        # Check the version in the macaroon identifier
        version, payment_hash, token_id = self._decode_identifier(mac.identifier)
        if version != 0:
            raise ValueError(f"Invalid L402 version: {version}")
        
        return mac, payment_hash, token_id
    
    def _validate_preimage(self, preimage: str, payment_hash: str):
        """Validate the macaoon hash preimage."""
        preimage_bytes = unhexlify(preimage)
        computed_hash = hashlib.sha256(preimage_bytes).digest()

        payment_hash_bytes = bytes.fromhex(payment_hash)

        if payment_hash_bytes != computed_hash:
            raise ValueError("Invalid payment preimage")
    
    async def _validate_macaroon(self, mac, token_id):
        """Verify the macaroon with the linked root key."""
        root_key = await self.macaroon_service.get_root_key(token_id)
        
        verifier = Verifier()
        try:
            verifier.verify(mac, root_key)
        except Exception:
            raise InvalidMacaroon("Macaroon verification failed.")
    
    async def _validate_caveats(self, mac):
        """Validate the macaroon caveats."""
        # TODO(positiveblue): Implement custom caveats validation
        pass
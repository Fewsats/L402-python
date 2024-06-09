from typing import Optional, Union
import re

from httpx import Response as HTTPXResponse
from requests import Response as RequestsResponse

HTTPResponse = Union[RequestsResponse, HTTPXResponse]

MACAROON_REGEX = re.compile(r'macaroon="([^ ]+)"')
INVOICE_REGEX = re.compile(r'invoice="([^ ]+)"')

class L402Credentials:
    """
    A class to represent the credentials required to authenticate a user trying
    to access an L402 protected resource.
    """
    def __init__(self, macaroon: str, preimage: Optional[str], invoice: str):
        self.macaroon = macaroon
        self.preimage = preimage
        self.invoice = invoice

    def authentication_header(self) -> str:
       return f"L402 {self.macaroon}:{self.preimage}"
    
    def set_location(self, location: str):
        # TODO(positiveblue): we need something like "policies". Policies will 
        # allow us to define the conditions under which a credential can be used.
        # By now we will simply set the url.
        self.location = location


def parse_http_402_response(response: HTTPResponse) -> L402Credentials:
    """
    Parse the L402 challenge from a http response with an 402 status code.
    """

    # TODO(positiveblue): check that fastAPI does not change the case of 
    # headers to lowercase.
    challenge = response.headers.get('WWW-Authenticate')
    if not challenge:
        raise ValueError("WWW-Authenticate header missing.")
    
    return _parse_l402_challenge(challenge)


def _parse_l402_challenge(challenge: str) -> L402Credentials:
    """
    Parse an L402 challenge string. Currently the V0 challenge format is:
        `L402 macaroon="{macaroon}", invoice="{invoice}"`
    """
    # TODO(positiveblue): we should check that it has the right format but for 
    # now we will simply patter match the macaroon and invoice.
    macaroon_match = MACAROON_REGEX.search(challenge)
    invoice_match = INVOICE_REGEX.search(challenge)

    if not macaroon_match or not invoice_match:
        raise ValueError(
            f"Challenge parsing failed, macaroon or invoice missing. Challenge: {challenge}",
        )
    
    macaroon = macaroon_match.group(1)
    invoice = invoice_match.group(1)

    # The preimage is currently unkown so we will set it to None.
    preimage = None

    return L402Credentials(macaroon, preimage, invoice)
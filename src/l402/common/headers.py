from abc import ABC, abstractmethod
import copy

from .constants import *
from .exceptions import UnsupportedVersionError, InvalidL402HeaderError


class L402Header(ABC):
    # Abstract base class for L402 headers
    @classmethod
    def version(self):
        # Returns the version of the L402 header
        return self._version


    @classmethod
    def credentials(self):
        # Returns the credentials from the L402 header
        return self._credentials

    @classmethod
    def payment_request(self):
        # Returns the payment request from the L402 header
        return self._payment_request

    @classmethod
    def parameter(self, name):
        # Returns the parameter with the given name from the L402 header
        if self._parameters:
            return self._parameters.get(name)

        return None
        

    @classmethod
    def get_parameters(self):
        # Returns a copy of the parameters from the L402 header
        return copy.deepcopy(self._parameters)

    @classmethod
    def __str__(self):
        # Returns a string representation of the L402 header
        params = " ".join([f"{key}={value}" for key, value in self._parameters.items()])
        return f"{AUTH_SCHEME} version={self.version()} {params}"


class L402HeaderV0(L402Header):
    # L402 header implementation for version 0 based on macaroons and LN invoices
    def __init__(self, macaroon, invoice):
        self._version = L402_VERSION_0
        self._credentials = macaroon
        self._payment_request = invoice

        self._parameters = {
            PARAM_VERSION: self._version, 
            PARAM_MACAROON: self._credentials, 
            PARAM_INVOICE: self._payment_request,
        }


def _gen_l402_v0_header(params: dict) -> L402HeaderV0:
    if PARAM_MACAROON not in params:
        raise InvalidL402HeaderError(f"Invalid L402 header V0 (missing macaroon) {params}")
    
    if PARAM_INVOICE not in params:
        raise InvalidL402HeaderError(f"Invalid L402 header V0 (missing invoice) {params}")
    
    return L402HeaderV0(params[PARAM_MACAROON], params[PARAM_INVOICE])


def parse_l402_challenge_header(header: str) -> L402Header:
    # Parse an L402 challenge header and return an L402Header instance
    if header.startswith(AUTH_SCHEME) is False:
        raise InvalidL402HeaderError(f"Invalid L402 challenge header ({header})")
    
    # Remove the AUTH_SCHEME from the header
    header = header.replace("{AUTH_SCHEME}} ", "", 1)

    # Get all the parameters from the header
    params = {}
    for part in  header.split(" "):
        key, value = part.split("=")

        if key == "" or value == "":
            raise InvalidL402HeaderError(f"invalide key({key})/value({value}) pair ({header})")
        
        params[key] = value
    
    if PARAM_VERSION not in params:
        raise InvalidL402HeaderError(f"Invalid L402 challenge header, no version ({header})")
    
    version = params[PARAM_VERSION]
    if version not in SUPPORTED_VERSIONS:
        raise UnsupportedVersionError(f"Unsupported L402 version({version}) ({header})")

    elif version == L402_VERSION_0:
        return _gen_l402_v0_header(params)
    
    else:
        raise UnsupportedVersionError(f"Unsupported L402 version({version}) ({header})")


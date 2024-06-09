class InvalidOrMissingL402Header(Exception):
    """Exception raised for errors in the L402 header format."""
    pass

class InvalidMacaroon(Exception):
    """Exception raised for errors when validating macaroons."""
    pass
from .credentials import L402Credentials
from .credentias_service import CredentialsService

class MemoryStore(CredentialsService):
    """
    MemoryStore is a simple in-memory store for L402Credentials.

    NOTE: This store is not persistent and will lose all data when the process
    is terminated.
    """
    def __init__(self):
        self.credentials_store = {}

    def insert(self, credentials: L402Credentials):
        """
        Insert a new L402Credentials object into the store.

        NOTE: This will overwrite any existing credentials for the same 
        location.
        """
        location = credentials.location

        self.credentials_store[location] = credentials

    def get(self, location):
        """
        Get the L402Credentials object for the given location.
        """

        # TODO(positiveblue): should we raise an exception if the location is not
        # found?

        # TODOO(positiveblue): when we implement policies, we should check that the
        # credentials are valid for the given location at this time.
        return self.credentials_store.get(location)
    

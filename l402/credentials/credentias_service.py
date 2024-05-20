from abc import ABC, abstractmethod

from .credentials import L402Credentials

class CredentialsService(ABC):
    """
    CredentialsService is an abstract class that defines the interface for 
    storing and retrieving L402 Credentials.
    """
    @abstractmethod
    def insert(self, credentials: L402Credentials):
        """
        Insert a new L402Credentials in the credentials service.
        """
        pass

    @abstractmethod
    def get(self, location):
        """
        Get the L402Credentials object for the given location.
        """
        pass

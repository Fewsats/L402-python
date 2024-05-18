from abc import ABC, abstractmethod

from .credentials import L402Credentials

class Store(ABC):
    """
    Store is an abstract class that defines the interface for storing 
    and retrieving L402 Credentials.

    TODO(positiveblue): probably rename this to CredentialsService so we 
    can use it for external servcices as well.
    """
    @abstractmethod
    def insert(self, credentials: L402Credentials):
        """
        Insert a new L402Credentials object into the store.
        """
        pass

    @abstractmethod
    def get(self, location):
        """
        Get the L402Credentials object for the given location.
        """
        pass

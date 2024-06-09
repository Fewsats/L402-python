from abc import ABC, abstractmethod

from .credentials import L402Credentials

class CredentialsService(ABC):
    """
    Abstract Base Class (ABC) for a Credentials Service.

    A Credentials Service is responsible for storing and retrieving L402 Credentials.
    Any concrete class that inherits from this ABC must implement the `store` and `get` methods.
    """

    @abstractmethod
    async def store(self, credentials: L402Credentials):
        """
        Abstract method to store a new L402Credentials in the credentials service.

        Args:
            credentials (L402Credentials): The credentials to be stored.

        Raises:
            NotImplementedError: This method must be implemented by any concrete class that inherits from this ABC.
        """
        pass

    @abstractmethod
    async def get(self, location: str):
        """
        Abstract method to retrieve the L402Credentials object for a given location.

        Args:
            location (str): The location for which the credentials are to be retrieved.

        Returns:
            L402Credentials: The credentials associated with the given location.

        Raises:
            NotImplementedError: This method must be implemented by any concrete class that inherits from this ABC.
        """
        pass
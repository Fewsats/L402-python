from abc import ABC, abstractmethod

class MacaroonService(ABC):
    """
    MacaroonService is an abstract class that defines the interface for 
    storing and retrieving macaroon related data.
    """
    @abstractmethod
    async def insert_root_key(self, token_id: bytes, root_key: bytes, macaroon: str):
        """
        Insert a new root key in the macaroon service.
        """
        pass

    @abstractmethod
    async def get_root_key(self, token_id: bytes) -> bytes:
        """
        Get the root key for the given token id.
        """
        pass
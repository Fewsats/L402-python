from abc import ABC, abstractmethod

class PreimageProvider(ABC):
    """
    Abstract Base Class (ABC) for a Preimage Provider.

    A Preimage Provider is responsible for retrieving the preimage associated with a given invoice.
    Any concrete class that inherits from this ABC must implement the `get_preimage` method.
    """

    @abstractmethod
    async def get_preimage(self, invoice: str) -> str:
        """
        Abstract method to retrieve the preimage for a given invoice.

        Args:
            invoice (str): The unique identifier of the invoice for which the preimage is to be retrieved.

        Returns:
            str: The preimage associated with the given invoice. The preimage is a string that, when hashed,
                 produces the hash embedded in the invoice.

        Raises:
            NotImplementedError: This method must be implemented by any concrete class that inherits from this ABC.
        """
        pass
from abc import ABC, abstractmethod

class PreimageProvider(ABC):
    """
    The PreimageProvider interface defines the methods that a preimage provider
    must implement.
    """
    @abstractmethod
    def get_preimage(self, invoice):
        """
        Get the preimage for the given invoice using a blocking call.
        """
        pass

    @abstractmethod
    async def get_preimage_async(self, invoice):
        """
        Get the preimage for the given invoice using an async call.
        """
        pass
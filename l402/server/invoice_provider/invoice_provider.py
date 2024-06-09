from typing import Tuple
from abc import ABC, abstractmethod

class InvoiceProvider(ABC):
    """Abstract Base Class (ABC) for an Invoice Provider.

    This abstract base class defines the interface for classes that provide Lightning invoices.
    Any concrete class that inherits from this ABC must implement its abstract methods.
    """

    @abstractmethod
    async def create_invoice(self, amount: int, currency: str, description: str) -> Tuple[str, str]:
        """Abstract method to create a new invoice with a given amount, currency, and description.

        Args:
            amount (int): The amount of the invoice.
            currency (str): The currency of the invoice.
            description (str): A brief description of the purpose of the invoice.

        Returns:
            Tuple[str, str]: A tuple containing the payment_request and payment_hash of the invoice.

        Raises:
            NotImplementedError: This method must be implemented by any concrete class that inherits from this ABC.
        """
        pass

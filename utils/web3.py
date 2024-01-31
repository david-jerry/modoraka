from web3 import Web3

from utils.env_result import INFURA_HTTP_URL
from utils.logger import LOGGER

w3 = Web3(Web3.HTTPProvider(f"{INFURA_HTTP_URL}"))


class Web3Functions:
    def __init__(self, w3, wallet_address):
        self.w3 = w3
        self.wallet_address = wallet_address

    def check_transaction_success(self, tx_hash):
        """
        Checks if a transaction with the given hash was successful.

        Args:
            tx_hash: The transaction hash to check.

        Returns:
            True if the transaction was successful and the receiving wallet matches,
            False otherwise.

        Raises:
            web3.exceptions.TransactionNotFound: If the transaction hash is not found.
        """
        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        except self.w3.exceptions.TransactionNotFound:
            LOGGER.info("Transaction was not found")
            return False

        if receipt["status"] == 1 and receipt["to"].lower() == self.wallet_address.lower():
            return True
        else:
            return False

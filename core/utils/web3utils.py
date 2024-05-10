from web3 import AsyncWeb3, Account
from eth_account.messages import encode_defunct


class Web3Utils:
    def __init__(self, http_provider: str, private_key: str, proxy: str = None) -> None:
        self.private_key = private_key
        self.address = Account.from_key(private_key).address

        self.w3 = AsyncWeb3(AsyncWeb3.AsyncHTTPProvider(endpoint_uri=http_provider, request_kwargs={'proxy': proxy}))
    
    def sign_message(self, message: str) -> str:
        return Account.sign_message(encode_defunct(text=message), self.private_key).signature.hex()

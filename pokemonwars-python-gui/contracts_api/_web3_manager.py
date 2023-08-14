import asyncio
import warnings
from typing import Union, List

import web3
from eth_typing import Address, ChecksumAddress
from web3.contract.async_contract import AsyncContractFunction

from contracts_api._downloader import AbiDownloader
from contracts_api.core import Network


class Web3Manager:
    def __init__(self, infura_api_key: str, network: Network, abi_downloader: AbiDownloader):
        self.infura_api_key = infura_api_key
        self.abi_downloader = abi_downloader
        self._pending_calls: List[asyncio.Task] = []
        self._network = network
        self._w3 = web3.AsyncWeb3(web3.AsyncHTTPProvider(self.get_http_infura_api_url(network)))

    def get_http_infura_api_url(self, network: Network):
        url = None
        if network == Network.MAIN_NET:
            url = "https://mainnet.infura.io/v3/"
        if network == Network.GOERLI:
            url = "https://goerli.infura.io/v3/"
        if network == Network.SEPOLIA:
            url = "https://sepolia.infura.io/v3/"
        if url is not None:
            url += self.infura_api_key
            return url
        raise ValueError(f"infura not supporting '{network}' network")

    @property
    def w3(self) -> web3.AsyncWeb3:
        return self._w3

    @property
    def network(self) -> Network:
        return self._network

    async def get_contract(self, address: Union[Address, ChecksumAddress]):
        if isinstance(address, bytes):
            address = self._w3.to_hex(address)
        abi = await self.abi_downloader.get_abi(address, self._network)
        if abi is None:
            warnings.warn(f"Can't find abi for contract at '{address}'", RuntimeWarning)
        contract = self._w3.eth.contract(address, abi=abi)
        return contract

    @staticmethod
    async def _task_call_function(contract_function: AsyncContractFunction, is_payable: bool):
        if not is_payable:
            await contract_function.call()
        else:
            transaction = await contract_function.build_transaction({
                # 'chainId': self._network.value.chain_id
            })
            await contract_function.transact(transaction)

    async def call_function(self, contract_function: AsyncContractFunction, is_payable: bool):
        task = asyncio.create_task(self._task_call_function(contract_function, is_payable))
        self._pending_calls.append(task)
        return task

    @property
    def pending_calls(self) -> List[asyncio.Task]:
        for i, task in enumerate(self._pending_calls):
            if task.done():
                del self._pending_calls[i]
        return self._pending_calls

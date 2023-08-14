import asyncio
import time
import warnings
from json import JSONDecodeError
from typing import Optional

from aiohttp import ClientSession, ClientError
from async_lru import alru_cache
from eth_typing import HexStr

from contracts_api.core import Network


class AbiDownloader:
    def __init__(self, etherscan_api_key: Optional[str] = None):
        self.etherscan_api_key = etherscan_api_key
        self._time_previous_call = 0

    @staticmethod
    def get_etherscan_api_url(network: Network):
        if network == network.MAIN_NET:
            return "https://api.etherscan.io/api"
        if network == network.GOERLI:
            return "https://api-goerli.etherscan.io/api"
        if network == network.SEPOLIA:
            return "https://api-sepolia.etherscan.io/api"
        raise ValueError(f"etherscan not supporting '{network}' network")

    @alru_cache()
    async def _get_abi_etherscan(self, contract_address: HexStr, network: Network) -> Optional[str]:
        api_url = self.get_etherscan_api_url(network)
        params = {
            "module": "contract",
            "action": "getabi",
            "address": contract_address
        }
        if self.etherscan_api_key:
            params["apikey"] = self.etherscan_api_key
        async with ClientSession() as session:
            tries = 3
            while tries > 0:
                delay_between_calls = time.time()-self._time_previous_call
                if delay_between_calls < 5 and self.etherscan_api_key is None:
                    await asyncio.sleep(5-delay_between_calls)
                try:
                    async with session.get(api_url, params=params) as response:
                        self._time_previous_call = time.time()
                        if not response.ok:
                            warnings.warn(
                                "We received a bad status code from the etherscan server, "
                                f"namely {response.status} {response.reason}", RuntimeWarning
                            )
                        response_json = await response.json()
                    response_status = response_json["status"].lower()
                    if "not verified" in response_status:
                        return None
                    elif int(response_json["status"]) != 1:
                        warnings.warn("We received strange result and can't process it. "
                                      f"Maybe this result '{response_json['result']}' can help you.",
                                      RuntimeWarning)
                    else:
                        return str(response_json['result'])
                except (ClientError, JSONDecodeError, ConnectionError) as error:
                    warnings.warn(
                        "Something went badly wrong :(. "
                        "We couldn't get a response from the etherscan server or couldn't process it as a json."
                        f"Maybe this '{error}' can help you.", RuntimeWarning
                    )
                except KeyError as error:
                    warnings.warn(
                        "Something went badly wrong :(. "
                        "We were able to get a response from the etherscan server but it doesn't have the right fields."
                        f"Maybe this '{error}' '{response_json}' can help you.", RuntimeWarning
                    )
                tries -= 1
        return None

    async def get_abi(self, contract_address: HexStr, network: Network) -> Optional[str]:
        """
        Вернёт двоичный интерфейс смарт контракта.

        :param contract_address: Hex адрес смарт контракта
        :param network: Сеть на которой он расположен
        :return: None, если смарт контракт не верифицирован(или его не смогли получить), в ином случае вернётся abi.
        """
        if not contract_address.startswith("0x"):
            contract_address = "0x" + contract_address
        abi = await self._get_abi_etherscan(contract_address, network)
        return abi


__all__ = ["AbiDownloader"]

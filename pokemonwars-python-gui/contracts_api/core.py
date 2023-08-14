from dataclasses import dataclass
from enum import Enum


@dataclass
class NetworkID:
    chain_id: int
    network_id: int


class Network(Enum):
    MAIN_NET = NetworkID(0, 0)
    GOERLI = NetworkID(5, 5)
    SEPOLIA = NetworkID(11155111, 11155111)

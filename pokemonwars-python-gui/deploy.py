from web3 import Web3, HTTPProvider, eth
from solcx import compile_files
import solcx

solcx.install_solc('0.8.15')
solcx.get_installable_solc_versions()
w3 = Web3(HTTPProvider('http://127.0.0.1:8545/'))
game_file = open("..\\pokemonwars-solidity\\contracts\\Game.sol").read()
erc_file = open("..\\pokemonwars-solidity\\contracts\\ERC1155.sol").read()
pokemon_file = open("..\\pokemonwars-solidity\\contracts\\Pokemon.sol").read()
player_file = open("..\\pokemonwars-solidity\\contracts\\Player.sol").read()

compiled_sol = compile_files([game_file, erc_file, pokemon_file, player_file],
                             output_values=["abi", "bin"], solc_version="0.8.15")
contract_id, contract_interface = compiled_sol.popitem()
TestContract = w3.eth.contract(
    abi=contract_interface["abi"],
    bytecode=contract_interface["bin"]
)

transaction = {
    'from': "0xdD6620a1702362DE85f19934b2603b66cfdFe708",
    'nonce': w3.eth.getTransactionCount("0xdD6620a1702362DE85f19934b2603b66cfdFe708"),
    'chainId': 5
}

game = TestContract.constructor("PokemonWarsToken", "PWT",
                                "gateway.pinata.cloud/ipfs"
                                "/QmU8faiRay5CGENpYUV9TNJ2e8hit75h7RiTxSkbnPLvZf/").buildTransaction(transaction)

closedKey = 'b54f6c59b7037624087800cb616cef9a7cd7ab1e543ede2a2db9249902c63dac'
sign_txt = eth.Account.sign_transaction(game, private_key=closedKey)
transaction_hash = w3.eth.send_raw_transaction(sign_txt.rawTransaction)
transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
print(transaction_receipt)


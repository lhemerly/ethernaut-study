# This one is a bit tricky. Even though you can decode function calls input parameters it is
# a bit harder to get it from constructors. The way I found to decode the deploy bytecode to
# the input was to use the block explorer decompiler.

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

# We proceed to instance the contract
buildFile = open('../contracts/build/contracts/levels/Vault.sol/Vault.json', "r")
build = json.loads(buildFile.read())
targetContract = w3Provider.eth.contract(address='', abi=build['abi']) #TODO: Include deployed contract address

# We use the password obtained by decompiling the contract using the block explorer
password = Web3.toBytes(text='A very strong secret password :)')

transaction = targetContract.functions.unlock(password).transact()
print(w3Provider.eth.wait_for_transaction_receipt(transaction))
lockState = targetContract.functions.locked().call()
print(lockState)


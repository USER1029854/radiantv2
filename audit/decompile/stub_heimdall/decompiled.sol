// SPDX-License-Identifier: MIT
pragma solidity >=0.8.0;

/// @title            Decompiled Contract
/// @author           Jonathan Becker <jonathan@jbecker.dev>
/// @custom:version   heimdall-rs v0.9.2
///
/// @notice           This contract was decompiled using the heimdall-rs decompiler.
///                     It was generated directly by tracing the EVM opcodes from this contract.
///                     As a result, it may not compile or even be valid solidity code.
///                     Despite this, it should be obvious what each function does. Overall
///                     logic should have been preserved throughout decompiling.
///
/// @custom:github    You can find the open-source decompiler here:
///                       https://heimdall.rs

contract DecompiledContract {
    address public benefit;
    
    
    /// @custom:selector    0xc4d66de8
    /// @custom:signature   initialize(address arg0) public pure
    /// @param              arg0 ["address", "uint160", "bytes20", "int160"]
    function initialize(address arg0) public pure {
        require(arg0 == (address(arg0)));
    }
    
    /// @custom:selector    0x93f63e70
    /// @custom:signature   setBenefit(address arg0) public payable
    /// @param              arg0 ["address", "uint160", "bytes20", "int160"]
    function setBenefit(address arg0) public payable {
        require(arg0 == (address(arg0)));
        require(address(msg.sender) == 0x911215cf312a64c128817af3c24b9fdf66b7ac95, "onlyOwner");
        benefit = (address(arg0) * 0x01) | (uint96(benefit));
    }
    
    /// @custom:selector    0xf5121a99
    /// @custom:signature   Unresolved_f5121a99(address arg0, uint256 arg1) public payable
    /// @param              arg0 ["address", "uint160", "bytes20", "int160"]
    /// @param              arg1 ["uint256", "bytes32", "int256"]
    function Unresolved_f5121a99(address arg0, uint256 arg1) public payable {
        require(arg0 == (address(arg0)));
        require(!arg1 > 0xffffffffffffffff);
        require(!(arg1) > 0xffffffffffffffff);
        require(!((var_c + (uint248(((arg1 * 0x20) + 0x20) + 0x1f))) > 0xffffffffffffffff) | ((var_c + (uint248(((arg1 * 0x20) + 0x20) + 0x1f))) < var_c));
        require(!((0x04 + arg1) + 0x20) < (((0x04 + arg1) + 0x20) + (arg1 * 0x20)));
        require((arg1 + 0x20) == (address(arg1 + 0x20)));
        require(address(msg.sender) == 0xc24927bd40bab67ccfb2ca0a90d6cbb8edb21302);
        address var_f = address(var_g);
        (bool success, bytes memory ret0) = address(arg0).Unresolved_70a08231(var_f); // staticcall
        var_c = var_c + (uint248(ret0.length + 0x1f));
        require(!((var_c + ret0.length) - var_c) < 0x20);
        require(var_h == (var_h));
        address var_j = address(var_g);
        (bool success, bytes memory ret0) = address(arg0).Unresolved_dd62ed3e(var_j); // staticcall
        var_c = var_c + (uint248(ret0.length + 0x1f));
        require(!((var_c + ret0.length) - var_c) < 0x20);
        require(var_h == (var_h));
        require(!(var_h) > (var_h));
        require(!(var_h) > 0);
        var_k = address(var_g);
        require(address(arg0).code.length);
        (bool success, bytes memory ret0) = address(arg0).Unresolved_23b872dd(var_k); // call
    }
}
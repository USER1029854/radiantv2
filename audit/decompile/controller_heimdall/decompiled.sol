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
    
    /// @custom:selector    0xfebb4f76
    /// @custom:signature   Unresolved_febb4f76(address arg0) public pure
    /// @param              arg0 ["address", "uint160", "bytes20", "int160"]
    function Unresolved_febb4f76(address arg0) public pure {
        require(arg0 == (address(arg0)));
    }
    
    /// @custom:selector    0x63fb0b96
    /// @custom:signature   multicall(address[] arg0, bytes[] arg1) public pure
    /// @param              arg0 ["uint256", "bytes32", "int256"]
    /// @param              arg1 ["address", "uint160", "bytes20", "int160"]
    function multicall(address[] arg0, bytes[] arg1) public pure {
        require(!arg0 > 0xffffffffffffffff);
        require(!(arg0) > 0xffffffffffffffff);
        require(!((var_c + (uint248(((arg0 * 0x20) + 0x20) + 0x1f))) > 0xffffffffffffffff) | ((var_c + (uint248(((arg0 * 0x20) + 0x20) + 0x1f))) < var_c));
        require(!((0x04 + arg0) + 0x20) < (((0x04 + arg0) + 0x20) + (arg0 * 0x20)));
        require((arg0 + 0x20) == (address(arg0 + 0x20)));
        require(!arg1 > 0xffffffffffffffff);
        require(!(arg1) > 0xffffffffffffffff);
    }
}
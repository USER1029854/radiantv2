pragma solidity 0.8.24;
contract P3 { function sz(address a) external view returns(uint256 s){ assembly{ s:=extcodesize(a) } } }

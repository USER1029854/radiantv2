# Resolved facts (all chain-verified, Arbitrum chainid 42161)
TARGET LendingPool proxy: 0xF4B1486DD74D07706052A33d31d7c0AAFD0659E1 (shell 2023-03-18)
  - EIP-1967 impl slot -> 0x3d4c56cdb97355807157f5c7d4f54957f0e9af44 (stub, created 2024-10-17)
  - EIP-1967 admin slot = 0x0 (immutable-admin); immutable admin (from proxy bytecode PUSH32) = AddressesProvider
  - holds 0 ETH, 0 USDC/WETH/ARB/WBTC
AddressesProvider: 0x091d52cace1edc5527c99cdcfa6937c1635330e4 (standard Aave Ownable; all setters owner-gated)
  - owner() = 0x57ba8957ed2ff2e7ae38f4935451e81ce1eefbf5 (controller)
  - getLendingPool()=0xF4B1..; getPriceOracle()=0xc0ce5d..; getLendingPoolConfigurator()=0xe51dfe..
Controller 0x57ba8957.. (created 2024-10-02, unverified; recovered from creation bytecode)
  - owner = deployer EOA 0x0629b1048298ae9deff0f4100a31967fb3f98962
  - fn 63fb0b96 execute(address[],bytes[]) onlyOwner  -> arbitrary call executor
  - fn febb4f76 deployChild(address,address) onlyOwner -> CREATE child sweeper
Stub 0x3d4c.. (behind pool proxy; heimdall+empirical confirmed)
  - benefit()/2e5113b7 public getter (slot0)
  - setBenefit()/93f63e70 onlyOwner==0x911215cf312a64c128817af3c24b9fdf66b7ac95 (sets slot0 dest)
  - initialize()/c4d66de8 NO-OP
  - f5121a99(token, address[] froms) onlyAdmin==0xc24927bd40bab67ccfb2ca0a90d6cbb8edb21302
      per-from: token.transferFrom(from, benefit, min(balanceOf(from), allowance(from, pool)))
  - NO fallback/receive; unknown selectors revert
  - slot0 benefit = 0x070ca92f568037d351666b3918a0f6ba7ad20ed1 (EOA, dest)
Child sweeper 0xf0c0a1a19886791c2dd6af71307496b1e16aa232 (deployed by controller)
  - immutables: owner=controller, 0x911215cf.., admin=0xc24927bd.. (same operators)
  - 191ba4ed onlyOwner (aToken transferUnderlyingTo sweep); f5121a99 onlyAdmin; empty now
Oracle 0xc0ce5d.. = AaveOracle, LIVE (USDC=$0.9999)
12 reserves; ALL rTokens drained to 0 underlying (WBTC/USDT/USDC.e/DAI/WETH/wstETH/ARB/USDC/weETH..)
Ownership timeline of AP: ...->Safe 0x111ceeee.. (Gnosis Safe = Radiant DAO multisig) ->[2024-10-16 hack day, via 0x0629b1 exec]-> controller 0x57ba8957
Sweeper active: f5121a99 from 0xc24927bd.. hits pool regularly; latest ~2026-08-19; all succeed
Empirical: non-owner 0xc14cd16d.. calls to controller execute/deploy REVERT (guards hold)
Operator 0xc24927bd funded by vanity-sibling 0xd35a27bd..; infra pre-positioned 2024-10-02

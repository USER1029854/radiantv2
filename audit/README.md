# Audit artifacts — Radiant V2 LendingPool (Arbitrum 42161)

Main report: ../AUDIT_REPORT.md

- `bytecode/`   raw runtime/creation bytecode fetched via Etherscan V2 eth_getCode
    - `proxy_F4B1.hex`   LendingPool proxy (immutable-admin proxy; admin=AddressesProvider baked in bytecode)
    - `impl_3d4c.hex`    sweeper stub behind the pool (the "implementation")
    - `ap_091d52.hex`    LendingPoolAddressesProvider (std Aave Ownable)
    - `gov_57ba.hex` / `gov_57ba_creation.hex`  controller runtime / creation (creation embeds clean child template)
    - `child_f0c0.hex`   child sweeper deployed by the controller
- `decompile/`  disassembly (`*.asm`) + heimdall solidity (`*_heimdall/decompiled.sol`)
    - `stub_heimdall/decompiled.sol`  confirms benefit()/setBenefit(onlyOwner)/initialize(no-op)/f5121a99(onlyAdmin sweep)
- `traces/`     decoded events (reserve list) 
- `notes/facts.md`  consolidated chain-verified facts + timeline
- `rpc.py` / `keccak.py` / `disasm.py` / `check_rtokens.py`  tooling used (pure-python keccak; Etherscan V2 proxy calls)

Key confirmations:
- pool getters revert (frozen); all 12 rTokens = 0 underlying; proxy holds 0
- live sweep tx 0x8a97b982…dfbc4: f5121a99(USDC,[0x40280eab…]) → USDC Transfer 0x40280eab→0x070ca92f (=slot0 benefit)
- non-owner 0xc14cd16d… calls to controller execute/deployChild revert (guards hold)
- AP ownership: Radiant Gnosis-Safe 0x111ceeee → EOA controller 0x57ba8957 on hack day 2024-10-16

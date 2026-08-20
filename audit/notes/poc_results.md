# PoC / fork-simulation results (all against LIVE Arbitrum state, no broadcast)
Method: eth_call with state overrides + Multicall3 on https://arbitrum.publicnode.com (+arb1.arbitrum.io)
Compiler: solc 0.8.24 (via solcx). Prober/Mal sources in audit/*.sol

## F-1 gate (nothing else gates the sweep)
- eth_call f5121a99(USDC,[victim]) from ADMIN 0xc24927bd => SUCCESS (returns 0x)
- eth_call same from RANDOM 0x1111... => REVERT "onlyAdmin"
- prober@non-admin calling pool.f5121a99 => REVERT "sweep-call-reverted" (inner onlyAdmin)
=> the ONLY gate is msg.sender==0xc24927bd; no pause/other guard exists.

## F-1 live exact-amount PoC (state-override prober @ admin)
victim 0xfb2a899d... USDC: before 16.872382 -> after 0.000000
benefit 0x070ca92f... USDC: before 524.429224 -> after 541.301606  (+16.872382)
=> admin moves exactly min(balance,allowance) to benefit, on current state.

## F-2 gate + end-to-end (single-EOA upgrade => arbitrary drain)
- controller.63fb0b96([AP],[setLendingPoolImpl(X)]) from OWNER 0x0629b1 => SUCCESS; from RANDOM => REVERT "onlyOwner"
- direct AP.setLendingPoolImpl(X) from CONTROLLER(owner) => SUCCESS; from RANDOM => REVERT "Ownable: caller is not the owner"
- END-TO-END (one simulated tx): EOA 0x0629b1 -> controller -> AP.setLendingPoolImpl(MALICIOUS) -> pool.pwn():
    victim 0xfb2a899d USDC 16.872382 -> 0 ; attacker 0x..bEEF 0 -> 16.872382
  => owner installs arbitrary code and drains victim's FULL balance to ANY address (not just benefit).

## Realized extraction to date (inbound to benefit 0x070ca92f, real reserve tokens)
USDC 115,805.91 | USDT 233,564.40 | USDC.e 42,563.52 | ARB 57,115.07 | DAI 3,887.93 | WBTC 2.6599 | wstETH 1.03 | weETH 0.011
~ $600k-700k already swept, from ~300+ distinct victims.

## Current standing exposure (live approvers to the pool) - snapshot, refills continuously
token | historical approvers | still-OPEN allowance | live balance | AT-RISK NOW (capped bal<=totalSupply)
USDC  | 28548 | 6408 | 2585 | 43,211.19 USDC
USDT  | 13295 | 5087 |  886 |  4,279.47 USDT
USDC.e| 14648 | 4580 |  991 |  5,287.79 USDC.e
ARB   | 17569 | 3706 | 1312 | (recompute w/ cap pending)
WBTC  |  5652 |  751 |  155 |  0.512 WBTC
WETH  |    14 |    7 |    1 | ~0 (WETH went via gateway)

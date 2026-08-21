# Radiant V2 (Arbitrum / BNB Chain) — live approval exposure & how to prevent loss

**What is happening.** After the October 2024 key-compromise hack, the Radiant LendingPool proxies on **Arbitrum** and **BNB Chain** were replaced with an attacker-controlled "sweeper" implementation. A bot holding the attacker's key continuously calls the pool's sweep function, which does `transferFrom(you → attacker, min(yourBalance, yourAllowance))` for any token you still have **approved** to the pool. The pools' own deposits were already drained in 2024; what remains exposed is **standing user approvals**.

**This cannot be fixed on-chain or recovered by Radiant** (the attacker owns the upgrade key). The **only** way to prevent loss is for each affected wallet to **revoke its token approvals** to the pool.

## The only action that prevents loss
Revoke (set allowance to 0) for **every token** you ever approved to these spender addresses:

| Chain | Spender to REVOKE (the LendingPool proxy) | Status |
|---|---|---|
| **Arbitrum** | `0xF4B1486DD74D07706052A33d31d7c0AAFD0659E1` | **actively sweeping today** |
| **BNB Chain** | `0xd50cf00b6e600dd036ba8ef475677d816d6c4281` | attacker backdoor live; bot dormant ~2 months but can resume at any time |

**NOT affected — no action needed for this reason:** Ethereum-mainnet Radiant (`0xA950974f…`, normal code under a 3-day timelock) and Base. Only revoke the two spenders above.

How to revoke: use revoke.cash (connect wallet → select the spender above → revoke), your wallet's token-approval manager, or the block explorer's "Token Approvals" tab. Set the allowance to 0 for each token. Priority tokens on Arbitrum: USDC, USDC.e, USDT, ARB, WBTC, DAI, wstETH, weETH.

## Scale of the live, preventable exposure (Arbitrum, measured on-chain today)
- **~$115,833 is seizable this instant** — the sum of `min(balance, allowance)` across **8,021 wallets that hold a balance right now** in a token they've approved to the pool.
- **26,438 distinct wallets have at least one open approval** to the pool — every one of them loses any *future* balance in the approved token the moment it arrives, until revoked.
- Largest single exposures right now include wallets with ~$16k USDC, ~175k ARB, ~0.2 WBTC each. Full per-address list: `audit/arbitrum_exposure.csv` (address, USD seizable now, token breakdown); complete revoke population: `audit/arbitrum_standing_approvals.txt`.
- **~$595k has already been swept** this way over ~22 months, and the total keeps growing with each sweep (last observed sweep: ~9h before this report).

BNB Chain has the same mechanism but its residuals are largely exhausted (the collection address holds only ~$40 there now); full enumeration is blocked by lack of free BSC archive access, so revoke on BSC as a precaution regardless.

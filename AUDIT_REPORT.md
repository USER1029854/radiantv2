# Security Audit — Radiant Capital V2 "LendingPool" (Arbitrum)

**Target (as handed):**
- LendingPool proxy `0xF4B1486DD74D07706052A33d31d7c0AAFD0659E1` (Arbitrum, chainid 42161)
- LendingPool implementation `0x3d4c56cdb97355807157f5c7d4f54957f0e9af44` (created 2024-10-17, unverified)

**Scope:** find any way an *unprivileged* attacker can take value or seize control they weren't entitled to, plus the standing trust/authority exposure over user funds. All claims below are anchored to on-chain reads, disassembly, a heimdall decompilation, and decoded live transactions (artifacts under `audit/`).

---

## 0. Headline — the premise is wrong, and that is the most important finding

The address handed over is described as a *"LendingPool implementation, Aave-v2 fork."* **It is not.** Chain state at audit time (2026-08-20) shows:

1. **The implementation behind the pool is a 2.2 KB, four-function "sweeper" stub, not a lending pool.** Calling any normal Aave getter on the proxy reverts (`getAddressesProvider()` → `execution reverted`, `paused()` → revert). The only real logic is a token-approval sweeper. Confirmed by disassembly + heimdall (`audit/decompile/stub_heimdall/decompiled.sol`).
2. **The market is drained and frozen.** All 12 reserves' rTokens hold **0** underlying (WBTC, USDT, USDC.e, DAI, WETH, wstETH, ARB, USDC, weETH, …). The proxy itself holds 0 ETH and 0 of every reserve token. There is no pooled TVL left to attack.
3. **This is the aftermath of the October 16 2024 key-compromise exploit.** The AddressesProvider's ownership was moved from the Radiant DAO Gnosis-Safe multisig (`0x111ceeee…`) to an **EOA-controlled controller** on the exact hack day, the pools were drained, and a **fresh 4-function stub was installed behind the pool the next day (2024-10-17)** whose sole purpose is to keep sweeping any residual user approvals.

So the correct object of this audit is **a drained, frozen post-exploit shell plus a live residual-approval harvesting apparatus**, not a lending market. Everything below audits that reality.

**Bottom line on the scoped question:** After enumerating and reading every externally-reachable entry point across the whole resolved graph, **I found no path by which an *unprivileged* attacker can take value or seize control.** Every value-moving function is gated by `msg.sender == <fixed address>` (immutable or hard-coded EOA), empirically confirmed to revert for non-owners. The system's danger is entirely **centralization / key custody** (unverified EOAs with unbounded power over residual user approvals and over the pool implementation) and the **live, ongoing harvesting of user approvals** — reported below with sizing and scope caveats, and explicitly flagged as privileged-party / trust issues rather than unprivileged exploits.

---

## 1. Resolved system (trust graph)

```
                 user token approvals to the pool  ─────────────┐
                                                                 ▼
  AddressesProvider 0x091d52…          LendingPool PROXY 0xF4B1486D…  (immutable-admin proxy, shell 2023-03-18)
  (std Aave, Ownable)  ── immutable admin ─────►  EIP-1967 impl slot
        │  owner()                                        │
        ▼                                                 ▼
  Controller 0x57ba8957…  (created 2024-10-02,     "Sweeper stub" 0x3d4c56cd…  (created 2024-10-17)
   unverified; recovered)                            fns: benefit() / setBenefit(onlyOwner=0x911215cf)
        │  owner = EOA 0x0629b1…                          initialize()[no-op] / f5121a99(onlyAdmin=0xc24927bd)
        │  63fb0b96 execute(address[],bytes[]) onlyOwner   sweeps transferFrom(from, benefit, min(bal,allow))
        │  febb4f76 deployChild(addr,addr)    onlyOwner            │ benefit (slot0) = 0x070ca92f…  (EOA, dest)
        ▼                                                          ▼
  Child sweeper 0xf0c0a1a1…  (same operator EOAs 0x911215cf / 0xc24927bd; empty)

  Registry side-branch (frozen, unused while pool is a stub):
     AaveOracle 0xc0ce5d…  (LIVE, USDC=$0.9999)      Configurator 0xe51dfe…      12 rTokens (all drained → 0)
```

### 1.1 Addresses, roles, and how each was established

| Contract / EOA | What it is | How established |
|---|---|---|
| `0xF4B1486DD74D07706052A33d31d7c0AAFD0659E1` | LendingPool **proxy** (`InitializableImmutableAdminUpgradeabilityProxy`) | proxy bytecode read; EIP-1967 impl slot → stub; admin slot = 0 (immutable admin baked in bytecode) |
| `0x3d4c56cdb97355807157f5c7d4f54957f0e9af44` | **Sweeper stub** impl (4 fns) | `eth_getCode` + disasm + heimdall + live tx decode |
| `0x091d52cace1edc5527c99cdcfa6937c1635330e4` | **LendingPoolAddressesProvider** (proxy's immutable admin) | extracted from proxy bytecode (`PUSH32 …091d52…`); confirmed `getLendingPool()==0xF4B1…` |
| `0x57ba8957ed2ff2e7ae38f4935451e81ce1eefbf5` | **Recovery/attack controller** (owns the AddressesProvider) | `AddressesProvider.owner()`; recovered from creation bytecode |
| `0x0629b1048298ae9deff0f4100a31967fb3f98962` | **EOA — top authority** (owner of the controller) | controller constructor stores `msg.sender`; = contract creator |
| `0x911215cf312a64c128817af3c24b9fdf66b7ac95` | **EOA — "owner"** of the stub (sets sweep destination) | hard-coded constant in stub bytecode; heimdall `setBenefit` guard |
| `0xc24927bd40bab67ccfb2ca0a90d6cbb8edb21302` | **EOA — "admin"** of the stub (triggers sweeps) | hard-coded constant in stub bytecode; live tx sender |
| `0x070ca92f568037d351666b3918a0f6ba7ad20ed1` | **EOA — sweep destination** (`benefit`, slot 0) | proxy storage slot 0; confirmed as `to` in a decoded sweep tx |
| `0xf0c0a1a19886791c2dd6af71307496b1e16aa232` | **Child sweeper** (standalone) | only `CREATE` from the controller; immutables read from its code |
| `0xc0ce5de939aad880b0bddcf9ab5750a53eda454b` | **AaveOracle** (live) | `AddressesProvider.getPriceOracle()`; verified name |
| `0xe51dfe7188d0b9a84141ff47d04ab07aeb82b89d` | LendingPoolConfigurator | `AddressesProvider.getLendingPoolConfigurator()` |

### 1.2 Recovered behavior of the unverified value-path contracts

**Sweeper stub `0x3d4c…`** (heimdall + hand-disasm + a decoded live tx all agree — `audit/decompile/stub_heimdall/decompiled.sol`):
- `benefit()` `0x2e5113b7` — public getter of storage slot 0 (the destination). Harmless.
- `setBenefit(address)` `0x93f63e70` — `require(msg.sender == 0x911215cf…, "onlyOwner")`; writes slot 0. **The sweep destination is mutable by this one EOA.**
- `initialize(address)` `0xc4d66de8` — **no-op** (`require(arg==arg)`); no state write, no re-init hazard.
- `f5121a99(address token, address[] froms)` — `require(msg.sender == 0xc24927bd…)`; for each `from`: `token.transferFrom(from, benefit, min(token.balanceOf(from), token.allowance(from, address(this))))`. Because it runs by `delegatecall` in the proxy, `address(this)` = the pool, i.e. it spends the *pool's* allowance — exactly the approvals users granted when they used Radiant. No `fallback`/`receive`; every other selector reverts.
- **Live confirmation** (tx `0x8a97b982…e328a8a191dfbc4`): input `f5121a99(USDC, [0x40280eab…])`; log = USDC `Transfer(0x40280eab… → 0x070ca92f…, 24.782179)`. `to` == slot-0 `benefit`. This is the authoritative reading; the byte-trace matches it.

**Controller `0x57ba8957…`** (recovered from full creation bytecode, which embeds clean compiler output + the child template; `audit/bytecode/gov_57ba_creation.hex`, `audit/decompile/controller_heimdall/`):
- constructor stores `msg.sender` (deployer `0x0629b1…`) as the immutable owner.
- `execute(address[] targets, bytes[] datas)` `0x63fb0b96` — `require(msg.sender == owner, "onlyOwner")`; loops `targets[i].call(datas[i])`. **An arbitrary-call executor**; since the controller owns the AddressesProvider, its owner can do anything the provider can (e.g. `setLendingPoolImpl`, `setAddress(LENDING_POOL, …)`) → reinstall any implementation behind the pool.
- `deployChild(address,address)` `0xfebb4f76` — `onlyOwner`; `CREATE`s a child sweeper parameterized by two addresses (owner=controller, plus an admin).

**Child sweeper `0xf0c0a1a1…`** — immutables read directly: owner=controller, and the same operator EOAs `0x911215cf…` / `0xc24927bd…`. Functions: `191ba4ed(...)` `onlyOwner` (calls aToken `transferUnderlyingTo` to drain rToken underlyings — only works while the caller is the pool), `initialize` no-op, `f5121a99` `onlyAdmin` (victim-approval sweep to a fixed immutable). Holds 0 tokens now.

**AddressesProvider `0x091d52…`** — byte-behaviour matches the standard Aave-v2 `LendingPoolAddressesProvider`: full selector set enumerated (`audit/` notes), Ownable, **every setter routes through the owner check** (`"Ownable: caller is not the owner"`); the two non-standard selectors (`0x5afaf018`/`0xe216ab44`) are an owner-gated getter/setter for one extra address slot — not a backdoor. Upgrade authority therefore = AP owner = controller = EOA `0x0629b1…`.

---

## 2. Live authority & configuration state (the reality the code can't show)

- **Pool implementation:** slot `0x360894…382bbc` = `0x3d4c56cd…` (the stub). Unchanged at audit time.
- **Proxy admin:** immutable = AddressesProvider `0x091d52…` (EIP-1967 admin slot is 0, as expected for the immutable-admin proxy).
- **AddressesProvider owner:** controller `0x57ba8957…`; **controller owner:** EOA `0x0629b1…`. No timelock, no multisig anywhere in this chain of control.
- **Stub roles (immutable, hard-coded in bytecode):** sweep-trigger admin `0xc24927bd…` (EOA); destination-setter owner `0x911215cf…` (EOA); destination `benefit` = `0x070ca92f…` (EOA).
- **Oracle:** `AaveOracle` live, returns sane prices (USDC $0.9999). Irrelevant while the pool is a stub, relevant only if a real pool were re-installed.
- **Solvency reconciliation:** internal accounting is moot (pool frozen); the physical check is decisive — **every rToken = 0 underlying, proxy = 0**. Nothing is stranded and nothing is claimed-but-absent; the market was fully drained in Oct-2024. The only assets in motion are the **inbound residual approvals** being swept to `0x070ca92f…` (currently ~524 USDC / ~40 USDC.e / ~127 ARB sitting there before forwarding).

### 2.1 Ownership timeline (chain-verified)
- 2023-03-18 — pool proxy shell created (original Radiant V2).
- 2024-10-02 — controller `0x57ba8957…` created; child sweeper + operator EOA already active (pre-positioning).
- **2024-10-16 (hack day)** — AddressesProvider ownership moved **from the Radiant DAO Gnosis-Safe `0x111ceeee…` to the EOA-controlled controller**, executed via `0x0629b1…` → `controller.execute(...)` (tx `0x7856552d…`); pools drained to 0.
- 2024-10-17 — sweeper **stub `0x3d4c…` created and installed** behind the pool.
- 2024→2026 — operator `0xc24927bd…` runs `f5121a99` sweeps on a schedule; **most recent ~2026-08-19**; all succeed.

---

## 3. Entry-point ledger (every externally-reachable entry, and why it isn't an unprivileged exploit)

| Contract | Entry point | Guard | Unprivileged-attacker outcome |
|---|---|---|---|
| Pool proxy `0xF4B1…` | `fallback` → delegatecall stub | n/a | delegates to stub only |
| Pool proxy (admin fns `3659cfe6/4f1ef286/…`) | `msg.sender == admin(=AddressesProvider)` | immutable | revert for anyone else |
| Stub | `benefit()` | none (view) | leaks the destination address; no value |
| Stub | `setBenefit(address)` | `== 0x911215cf…` | **revert** |
| Stub | `initialize(address)` | none | no-op, no state change |
| Stub | `f5121a99(token,froms)` | `== 0xc24927bd…` | **revert** |
| Stub | any other selector | dispatch default | **revert** (no fallback/receive) |
| Controller | `execute(address[],bytes[])` | `== owner 0x0629b1…` | **revert** (empirically: `0xc14cd16d…` tried → failed) |
| Controller | `deployChild(address,address)` | `== owner` | **revert** (empirically confirmed) |
| Child | `191ba4ed` / `f5121a99` | `onlyOwner` / `onlyAdmin` | **revert** |
| AddressesProvider | all `set*` (impl, address, oracle, admins, marketId, ownership) | `onlyOwner` | **revert** |
| AddressesProvider | all `get*` | none (view) | read-only |
| AaveOracle | `getAssetPrice`, etc. | view / owner setters | read-only or owner-gated |

No signatures, hash-preimages, merkle proofs, or stored secrets are used as guards anywhere — so the "secret sitting in bytecode" class does not arise; every guard is a plain identity check against a fixed address.

---

## 4. Dependency / composition analysis

- **Sweep magnitude is bounded by the victim's own exposure.** `f5121a99` moves `min(balanceOf(from), allowance(from, pool))`. It can never take more than what a user already approved to the pool and still holds — no way to inflate it, and no cross-user leakage (each `transferFrom` is bounded by that user's own allowance). So even the *privileged* operator cannot exceed the sum of live residual approvals.
- **`setBenefit` → `f5121a99` composition** is the only stateful pairing (writer = destination, reader = sweep). Both writer and reader are gated by (different) fixed EOAs; an unprivileged actor can reach neither, so the composition adds no unprivileged path.
- **No-op `initialize` + upgrade** — could an attacker front-run initialization to seize the stub? No: `initialize` writes nothing and the proxy is already initialized; there is no uninitialized owner slot to grab.
- **Storage-collision / re-init** — the stub uses only slot 0 (`benefit`); the immutable-admin proxy keeps its admin in bytecode, not storage, so there is no attacker-writable slot that collides with control state.
- **rToken `transferUnderlyingTo`** is `onlyLendingPool` = only `0xF4B1…`; the current stub never calls it, and the rTokens are empty regardless. No unprivileged drain of rToken underlyings.

---

## 5. Findings

> None of these is an *unprivileged* exploit (the scoped attack question is answered "no path found"). They are the standing **trust / centralization / user-exposure** facts that the audit is nonetheless obligated to report, size, and scope, because each concerns what the code allows a privileged or external actor to do, and where the limits are absent.

### F-1 (HIGH, user-actionable, ongoing) — Residual user approvals to the pool are being actively harvested by a single EOA, to a mutable EOA destination, indefinitely
- **What:** Any address that ever approved the Radiant LendingPool `0xF4B1…` for USDC / USDC.e / ARB / USDT / etc. and still holds a balance can be swept for `min(balance, allowance)` at will by EOA `0xc24927bd…`, to destination `0x070ca92f…` — and that destination is changeable in one tx by EOA `0x911215cf…`. This is **live**: sweeps run on a schedule and the most recent observed is ~2026-08-19.
- **Code basis:** stub `f5121a99` (heimdall + tx `0x8a97b982…`).
- **Bound / sizing:** capped per user at their own remaining approval × current balance in the swept token; unbounded in *time* (runs forever until the user revokes) and in *set of victims* (any historical approver). No cap, rate-limit, allow-list, or expiry in the code. Current on-chain evidence shows individual sweeps of tens–hundreds of USDC and the long tail is what remains at risk.
- **Why it's not an unprivileged bug:** the trigger is identity-gated to a fixed EOA; an outside attacker cannot invoke it. It is reported because the *code imposes no limit* on what that privileged input can take from users, and because the exposure is real and current.
- **Mitigation (operational, on the user side):** affected users must **revoke** their ERC-20 approvals to `0xF4B1486DD74D07706052A33d31d7c0AAFD0659E1`. There is no on-chain fix available from within these contracts.
- **Falsified if:** a user holds no approval to `0xF4B1…`, or holds zero balance in every swept token → nothing to take.

### F-2 (HIGH, centralization) — The pool implementation and all registry addresses are controlled by a single unverified EOA with no timelock
- **What:** AddressesProvider owner = controller `0x57ba8957…`, whose owner is EOA `0x0629b1…`, which via `execute(...)` can call `setLendingPoolImpl` / `setAddress` and reinstall **any** implementation behind `0xF4B1…`. A malicious impl could re-open `transferFrom`-style draining of any *new* approvals or funds routed to the pool.
- **Bound / sizing:** immediate pooled value at risk is **0** (rTokens drained, proxy empty). The at-risk surface is *future* approvals/funds and anyone who still trusts `0xF4B1…` as a live money-market. Same single-key structure that was catastrophically exploited on 2024-10-16.
- **Why it's not an unprivileged bug:** upgrade authority is owner-gated (empirically: non-owner `0xc14cd16d…` calls revert). Reported as an unbounded-privileged-input / key-custody finding.
- **Falsified if:** ownership were held by a timelocked multisig — it is not (it is an EOA; `0x0629b1…` has code length 0).

### F-3 (INFORMATIONAL → CRITICAL-context) — Premise correction & attribution
- The target is **not** a functioning lending pool; it is a drained post-exploit shell with a live approval-harvester (Section 0). Any downstream contract, dashboard, integrator, or user treating `0xF4B1…` as a live Aave-v2 market is operating on a false premise; deposits revert and approvals are harvested.
- **Attribution (evidence-based, not proven):** the control-transfer pattern is **strongly consistent with the Oct-2024 attacker retaining control**, not a whitehat recovery: (a) AddressesProvider ownership moved from the Radiant DAO **Gnosis-Safe** to an **EOA-controlled** arbitrary-call executor on the exact hack day; (b) sweeper infra was **pre-positioned two weeks earlier** (2024-10-02); (c) proceeds consolidate to an **unlabeled EOA** (`0x070ca92f…`) rather than a published recovery multisig, with no user returns observed; (d) the operator EOA `0xc24927bd…` was funded by a **vanity-sibling** `0xd35a27bd…4322413`. I cannot cryptographically tie these to published attacker addresses from chain state alone, so I state this as inference. **Either way (attacker-retained or centralized whitehat), the user-actionable conclusion is identical: revoke approvals to `0xF4B1…`.**

### F-4 (DORMANT / "if re-enabled") — the Jan-2024 rounding class would need re-audit before any relaunch on this registry
- If governance ever re-installed a real Aave-v2 pool implementation behind this proxy + AddressesProvider, the empty-market first-depositor / share-rounding class (the root of Radiant's **January 2024** incident) must be re-audited on the new impl before any market with zero liquidity is opened; the oracle is live and would feed it. This is **not** a live switch here — relaunching requires a full redeployment, not a flag flip — so it is context for a future action, not a current exploit.

---

## 6. Rebuttal register (candidates considered and killed, with citations)

| Candidate unprivileged attack | Why it dies |
|---|---|
| Call `f5121a99` to sweep users yourself | `require(msg.sender == 0xc24927bd…)` in stub bytecode; reverts for anyone else (heimdall + disasm) |
| Point `benefit` at your own address then sweep | `setBenefit` gated `== 0x911215cf…`; reverts |
| Front-run / abuse `initialize` to seize the stub | `initialize` is a verified no-op; writes nothing; proxy already initialized |
| Hijack the controller's `execute` to own the registry | `onlyOwner==0x0629b1…`; empirically observed non-owner `0xc14cd16d…` calls revert (isError=1) |
| Take over the AddressesProvider via an unguarded setter | full selector enumeration shows every setter is `onlyOwner`; the 2 non-standard selectors are an owner-gated address slot, not a backdoor |
| Drain rToken underlyings via `transferUnderlyingTo` | `onlyLendingPool`; the stub never calls it; rTokens hold 0 anyway |
| Exploit a hard-coded secret/signature guard | none exists — all guards are plain `msg.sender ==` identity checks |
| Extract pooled TVL | none exists — every reserve rToken and the proxy hold 0 |
| Storage-collision through the no-op `initialize`/`benefit` slot | attacker cannot write slot 0 (setter is gated); immutable-admin proxy keeps admin off-storage |
| Child sweeper `0xf0c0a1a1…` mis-guard or held funds | `onlyOwner`/`onlyAdmin`; empty; not wired into the pool's approval path |

None survived. No pair of killed candidates composes into a live unprivileged chain (F-1/F-2 are privileged-input findings, and their triggers are the very guards the killed candidates could not pass).

---

## 7. What I could not fully establish, and how it cuts

- **Attribution (attacker vs. whitehat).** Chain state cannot definitively label `0x0629b1…` / `0xc24927bd…` / `0x070ca92f…`. If **attacker**, F-1 is a live theft in progress (severity as stated, user must revoke *now*). If **whitehat recovery**, F-1/F-2 are centralization risks over user funds held by single keys (still HIGH, still revoke). The technical findings and the user action do not change either way.
- **Off-chain components.** The sweeper is driven by an **off-chain bot** (the scheduled `0xc24927bd…` transactions) that decides *which* approvers to target and *when*; whoever holds that key, and the key `0x911215cf…` that can repoint `benefit`, and the key `0x0629b1…` that can reinstall any implementation, are the entire trust basis. There is no on-chain constraint on any of them (no cap, rate-limit, allow-list, timelock, or multisig). If any key is honest the residual approvals are (at worst) protected; if any is malicious they are taken. No oracle/bridge/validator sits in the current value path (the pool is frozen), so those classes are N/A until a real pool is re-installed.
- **Decompilation confidence.** The stub was cross-checked three ways (hand-disasm, heimdall, a decoded live sweep tx) and they agree; the controller and child were recovered from **clean creation bytecode** (compiler output with intact `"onlyOwner"/"onlyAdmin"` strings), which is source-equivalent for the guard logic. The AddressesProvider is byte-behaviour-identical to standard Aave-v2 Ownable. I am confident in the reconstructed logic.

## 8. Verdict

**No unprivileged-attacker vulnerability was found in the current deployment.** The scoped target is a **drained, frozen post-exploit shell** whose only live behaviour is a **privileged, EOA-gated harvester of residual ERC-20 approvals** to the old Radiant LendingPool. Every value-moving entry point across the resolved graph is identity-gated and empirically reverts for non-owners; there is no pooled value left to steal and no open door for an outside attacker.

The real and current exposure is **F-1**: anyone who still has a live approval to `0xF4B1486DD74D07706052A33d31d7c0AAFD0659E1` is exposed to an unbounded, indefinite sweep by a single key and **should revoke immediately**. The system also carries **F-2** single-EOA upgrade control with no timelock — the exact structural weakness behind the 2024 loss.

**This verdict is a snapshot that rests on mutable state** (the impl pointer and the three controlling EOA keys). It ends the moment a real implementation is re-installed behind the proxy — at which point the market must be re-audited from scratch (including the F-4 rounding class).

---

# Part II — PoC / fork verification (added after review)

All simulations run against **live Arbitrum state** via `eth_call` with state overrides + Multicall3 (RPCs `arbitrum.publicnode.com`, `arb1.arbitrum.io`); nothing broadcast. Compiler solc 0.8.24. Sources/scripts: `audit/Prober.sol`, `audit/Mal.sol`, `audit/Prober2.sol`, `audit/*exposure*.py`, `audit/realized.py`. Verdict: **F-1 and F-2 are confirmed and, if anything, were under-stated. F-3's premise facts are all confirmed on-chain.**

## F-1 — approval sweeper: CONFIRMED, nothing else gates it
- **Gate (differential):** `f5121a99(USDC,[victim])` from admin `0xc24927bd…` → **executes** (returns `0x`); from a random address → **revert `onlyAdmin`**; a prober contract at a non-admin address calling the pool → **revert** (inner `onlyAdmin`). The sole gate is `msg.sender == 0xc24927bd…` — no pause, no second check.
- **Live exact-amount PoC** (prober deployed at the admin via `code` override, current state): victim `0xfb2a899d…` USDC **16.872382 → 0**, destination `benefit 0x070ca92f…` **524.429224 → 541.301606** (**+16.872382**). Moves exactly `min(balance, allowance)`.
- **Realized damage to date** (real reserve-token inflows to `benefit`, priced at the live on-chain oracle, which cross-checks to CoinGecko within 0.1%): **≈ $595,000** already taken from **~300+ distinct victims** — USDT $233k, **WBTC 2.66 ($194k)**, USDC $116k, USDC.e $43k, ARB, DAI.
- **Current standing exposure** (enumerated every historical approver per token, live `allowance`+`balance` via Multicall3):

  | token | historical approvers | still-OPEN allowance | live balance now | seizable now |
  |---|--:|--:|--:|--:|
  | USDC | 28,531 | 6,393 | 2,580 | 43,092 USDC |
  | USDT | 13,295 | 5,087 | 886 | 4,279 USDT |
  | USDC.e | 14,648 | 4,580 | 991 | 5,288 USDC.e |
  | ARB | 17,569 | 3,649 | 1,274 | 216,282 ARB |
  | WBTC | 5,652 | 751 | 155 | 0.512 WBTC |
  | WETH | 14 | 7 | 1 | ~0 (WETH used a gateway) |

  **≈ 20,000+ still-open allowances**; **≈ $110,000 seizable at this instant** (USDC $43k + WBTC $37k + ARB $20k + USDC.e $5k + USDT $4k), and it **refills** every time any of those ~20k addresses receives one of these tokens. So F-1 is a live, unbounded-in-time drain — not exaggerated.

## F-2 — single-EOA upgrade control: CONFIRMED end-to-end
- **Gate:** `setLendingPoolImpl(X)` succeeds from the AP owner (the controller) and via `controller.63fb0b96` from EOA `0x0629b1…`; **reverts `onlyOwner` / `Ownable: caller is not the owner`** for any other caller.
- **End-to-end drain PoC (one simulated tx, current state):** `EOA 0x0629b1… → controller.63fb0b96 → AP.setLendingPoolImpl(MALICIOUS) → pool.pwn()` drained victim `0xfb2a899d…`'s **entire** balance **16.872382 USDC → attacker `0x…bEEF`** (an arbitrary address, **not** the sweeper's `benefit`). Proves the owner key can install arbitrary logic and take the **full** balance of **any** of the ~20k open-allowance approvers, to **anywhere**, in a single transaction.

## Correction to Part-I sizing (F-2)
Part I said F-2's "immediate pooled value at risk is 0." That is right for *pooled TVL* (rTokens are empty) but **understates the live exposure**: F-2 reaches the **same live user approvals as F-1** — **~$110k seizable now, ~20k standing allowances, plus all future balances of those addresses** — and, unlike the sweeper, sends them to an arbitrary destination. F-1 and F-2 hit the **same at-risk pool** (not additive); F-1 is the drip currently realizing it (~$595k so far), F-2 is the one-tx total-drain-and-redirect upgrade path.

## F-3 — premise facts confirmed (attribution is not a fork question)
Confirmed on-chain: pool getters revert (frozen), all 12 rTokens hold 0, proxy holds 0, and control sits with EOAs. The AaveOracle is **live and accurate** (ARB $0.0909, WBTC $73,025 — both match CoinGecko), so the "if re-enabled" oracle concern (F-4) is about *staleness risk on a dead feed being reused*, not a current misprice. Whether the operator EOAs are the Oct-2024 attacker or a whitehat cannot be settled by a fork; the ~$595k consolidation to an unlabeled EOA remains the evidence, and the user action (revoke) is identical either way.

---

# Part III — Cost to execute, liveness, and cross-chain scope (added after review)

## 1. Cost to execute: ~zero capital — this is a *key-gated* drain, not a capital/flash-loan attack
These findings are **not** economic exploits with a capital hurdle (no $Xm flash loan, no price manipulation, no stake). The cost is **gas only**, and the barrier is **possession of a specific private key**:
- **F-1 sweep:** one `f5121a99` call — measured **65,022–130,846 gas ≈ $0.002–0.007** on Arbitrum (from real on-chain sweeps). No capital.
- **F-2 upgrade+drain:** `execute → setLendingPoolImpl → drain` — gas only, no capital.
- For **anyone without the key** the cost is effectively infinite: the call **reverts** (`onlyAdmin` / `onlyOwner`), proven live. For the **keyholder** it is nearly free and the "profit" is 100% of what it moves.

**Reframing that matters:** because the gate is identity (a held key), not capital, the usual "profit > cost" economic test doesn't apply — the profit-to-cost ratio is essentially infinite for the keyholder. The correct question is *who holds the key*, and the on-chain evidence says the **October-2024 attacker** does (see Part I §F-3 + the cross-chain pre-positioning below). So this is best read as **"the 2024 attacker retains a live, free-to-use backdoor over residual user approvals,"** not "anyone can drain it."

## 2. Is it at risk *today*, or just leftover from the 2024 exploit? — Live today, and still growing
It is **not** a frozen relic of the hack; it is the hack's **persistent, still-running harvester**:
- **Last Arbitrum sweep: 2026-08-20 15:22 UTC — ~9 hours before this analysis**, with multiple sweeps over the preceding days (all succeed).
- The **~$595k Arbitrum realized figure is cumulative over ~22 months and still increasing** — every time one of the ~20k open-allowance addresses receives USDC/USDT/ARB/etc., the next sweep takes it.
- The live PoC in Part II used a victim who had a balance **right now**; the ~20k open allowances and ~$110k instantaneous snapshot are **current reads**.
- Distinction worth stating plainly: the **large 2024 principal drain (~$50M+) is finished** (all rTokens are empty). What is **live now** is the **ongoing residual-approval harvesting** — smaller per event, continuous, unbounded in time.

## 3. Are the other Radiant deployments ("mainnet" pools) at risk now?
Radiant deployed on four chains. State verified independently on each (weakest-deployment-governs):

| Chain | LendingPool | Current impl | Governance / control | State now | At risk? |
|---|---|---|---|---|---|
| **Arbitrum** | `0xF4B1486D…` | sweeper stub `0x3d4c…` | attacker EOAs (owner `0x0629b1…`, sweep admin `0xc24927bd…`) | **actively swept, last run ~9h ago** | **YES — live** |
| **BNB Chain** | `0xd50cf00b…` | sweeper stub `0x3c09ae85…` (byte-identical design, 2,294 B) | **same** owner EOA `0x911215cf…`; **same** destination `0x070ca92f…`; BSC admin `0x579145d6…` (6,812 txs) | stub **live** (gate confirmed on current state), but **no sweeps to the destination in ~69 days** — bot dormant, residuals largely exhausted | **YES (capability live), but harvesting wound down** |
| **Ethereum mainnet** | `0xA950974f…` | **verified `LendingPool`** `0x3f6b71c1…` (normal Aave-v2) | **3-day `TimelockController`** `0x27fc8f3b…`; attacker holds **no** `PROPOSER_ROLE` | normal code, not paused, wound down to dust (~$15–20k stables + ~62 wstETH) | **NO — legitimately governed; the timelock delay is why it survived the hack** |
| **Base** | (Radiant Base market) | — | — | sweeper operator EOA `0x911215cf…` has **nonce 0 on Base** (never transacted) | **NO — operator never present** |

**Direct answer to "are the mainnet pools at risk now?":** **Ethereum-mainnet Radiant is *not* at risk** from this — it runs verified normal code under a 3-day timelock the attacker does not control, and holds only dust. **Base is unaffected.** The attacker-controlled pools are **Arbitrum (actively draining today)** and **BNB Chain (backdoor live but dormant)** — and on both, the exposure is residual *user approvals*, since the pools' own principal was already drained in 2024. The cross-chain reuse (same owner key `0x911215cf…`, same collection address `0x070ca92f…`, sweeper infra pre-positioned on Arbitrum, BSC, and mainnet-laundering rails **before** the Oct-16 hack) is itself strong corroboration that one actor — the 2024 attacker — runs all of it.

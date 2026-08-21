import mc, rpc, json, sys
POOL="0xf4b1486dd74d07706052a33d31d7c0aafd0659e1"
ORACLE="0xc0ce5de939aad880b0bddcf9ab5750a53eda454b"
# token -> (address, decimals, approver-file)
TOKENS={
"USDC":("0xaf88d065e77c8cc2239327c5edb3a432268e5831",6,"approvers_USDC.txt"),
"USDT":("0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",6,"approvers_USDT.txt"),
"USDC.e":("0xff970a61a04b1ca14834a43f5de4533ebddb5cc8",6,"approvers_USDCe.txt"),
"ARB":("0x912ce59144191c1204e64559fe8253a0e49e6548",18,"approvers_ARB.txt"),
"WBTC":("0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f",8,"approvers_WBTC.txt"),
"DAI":("0xda10009cbd5d07dd0cecc66161fc93d7c9000da1",18,"approvers_DAI.txt"),
"wstETH":("0x5979d7b546e38e414f7e9822514be443a4800529",18,"approvers_wstETH.txt"),
"weETH":("0x35751007a407ca6feffe80b3cb397736d2cf4dbe",18,"approvers_weETH.txt"),
}
def price(a):
    r=rpc.eth_call(ORACLE,"0xb3596f07"+"0"*24+a[2:]); return int(r,16)/1e8 if r and r!="0x" else 0
def ts(a):
    r=rpc.eth_call(a,"0x18160ddd"); return int(r,16) if r and r!="0x" else 10**40
per_addr={}   # addr -> {"usd":x, "toks":{sym:amt}}
summary={}
for sym,(tok,dec,fn) in TOKENS.items():
    try: owners=[l.strip() for l in open(fn) if l.strip()]
    except FileNotFoundError: print(f"  [skip {sym}: no file]"); continue
    px=price(tok); TS=ts(tok)
    al=mc.batched([(tok,"0xdd62ed3e"+mc.enc(o)+mc.enc(POOL)) for o in owners], size=500)
    open_idx=[i for i,(s,v) in enumerate(al) if s and v>0]
    ba=mc.batched([(tok,"0x70a08231"+mc.enc(owners[i])) for i in open_idx], size=500)
    n_live=0; val=0
    for k,i in enumerate(open_idx):
        b=ba[k][1] if k<len(ba) and ba[k][0] else 0
        if b>TS: b=0
        m=min(al[i][1], b)
        if m>0:
            amt=m/10**dec; usd=amt*px
            a=owners[i]
            e=per_addr.setdefault(a,{"usd":0,"toks":{}})
            e["usd"]+=usd; e["toks"][sym]=e["toks"].get(sym,0)+amt
            n_live+=1; val+=usd
    summary[sym]=(len(owners),len(open_idx),n_live,val,px)
    print(f"  {sym}: approvers={len(owners)} open={len(open_idx)} live={n_live} at_risk=${val:,.0f} (px ${px:,.4f})")
# write CSV sorted by usd
rows=sorted(per_addr.items(), key=lambda kv:-kv[1]["usd"])
with open("arbitrum_exposure.csv","w") as f:
    f.write("address,usd_seizable_now,tokens\n")
    for a,e in rows:
        toks=";".join(f"{s}:{v:.4f}" for s,v in e["toks"].items())
        f.write(f"{a},{e['usd']:.2f},{toks}\n")
tot=sum(e["usd"] for _,e in rows)
print(f"\n=== ARBITRUM consolidated: {len(rows)} addresses exposed now, ${tot:,.0f} seizable this instant ===")
print("Top 15 exposed addresses:")
for a,e in rows[:15]:
    print(f"  {a}  ${e['usd']:>10,.2f}  {';'.join(f'{s}:{v:.2f}' for s,v in e['toks'].items())}")
print("\nStanding allowances (any future balance at risk until revoked):")
open_total=sum(s[1] for s in summary.values())
print(f"  ~{open_total} open allowance positions across tokens (dedup addresses fewer)")

import mc, sys
POOL="0xf4b1486dd74d07706052a33d31d7c0aafd0659e1"
token=sys.argv[1]; dec=int(sys.argv[2]); name=sys.argv[3]; fn=sys.argv[4]
owners=[l.strip() for l in open(fn) if l.strip()]
# pass 1: allowances
al=mc.batched([(token,"0xdd62ed3e"+mc.enc(o)+mc.enc(POOL)) for o in owners], size=500)
open_idx=[i for i,(s,v) in enumerate(al) if s and v>0]
# pass 2: balances for open ones
ba=mc.batched([(token,"0x70a08231"+mc.enc(owners[i])) for i in open_idx], size=500)
at_risk=0; live=0
for k,i in enumerate(open_idx):
    allowv=al[i][1]; b=ba[k][1] if k<len(ba) and ba[k][0] else 0
    m=min(allowv,b)
    if m>0: at_risk+=m; live+=1
print(f"{name}: approvers={len(owners)} open_allowance={len(open_idx)} live_balance={live} AT_RISK_NOW={at_risk/10**dec:,.4f} {name}")

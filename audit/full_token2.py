import mc, rpc, sys
POOL="0xf4b1486dd74d07706052a33d31d7c0aafd0659e1"
APPROVAL="0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"
token=sys.argv[1]; dec=int(sys.argv[2]); name=sys.argv[3]
ts=rpc.eth_call(token,"0x18160ddd"); TS=int(ts,16) if ts and ts!="0x" else 10**40  # totalSupply cap
owners=set(); start=0
for _ in range(60):
    r=rpc._get({"module":"logs","action":"getLogs","address":token,"topic0":APPROVAL,"topic2":"0x"+"0"*24+POOL[2:],"fromBlock":start,"toBlock":"latest","page":1,"offset":1000})
    res=r.get("result")
    if not res or not isinstance(res,list) or len(res)==0: break
    for lg in res: owners.add("0x"+lg["topics"][1][-40:])
    if len(res)<1000: break
    start=int(res[-1]["blockNumber"],16)+1
owners=sorted(owners)
al=mc.batched([(token,"0xdd62ed3e"+mc.enc(o)+mc.enc(POOL)) for o in owners], size=500)
open_idx=[i for i,(s,v) in enumerate(al) if s and v>0]
ba=mc.batched([(token,"0x70a08231"+mc.enc(owners[i])) for i in open_idx], size=500)
rows=[]
for k,i in enumerate(open_idx):
    b=ba[k][1] if k<len(ba) and ba[k][0] else 0
    if b>TS: b=0   # sanity: ignore bogus balances above total supply
    m=min(al[i][1], b)
    if m>0: rows.append((m, owners[i]))
rows.sort(reverse=True)
at_risk=sum(m for m,_ in rows)
print(f"{name}|approvers={len(owners)}|open_allow={len(open_idx)}|live={len(rows)}|AT_RISK_NOW={at_risk/10**dec:,.4f}")
print("  top:", [(f'{m/10**dec:,.2f}',a[:10]) for m,a in rows[:4]])

import mc, rpc, sys
POOL="0xf4b1486dd74d07706052a33d31d7c0aafd0659e1"
APPROVAL="0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"
token=sys.argv[1]; dec=int(sys.argv[2]); name=sys.argv[3]
# collect approvers via etherscan getLogs
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
at_risk=0; live=0
for k,i in enumerate(open_idx):
    m=min(al[i][1], ba[k][1] if k<len(ba) and ba[k][0] else 0)
    if m>0: at_risk+=m; live+=1
print(f"{name}|{len(owners)}|{len(open_idx)}|{live}|{at_risk/10**dec:.4f}")

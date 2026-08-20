import rpc, json, sys
POOL="0xf4b1486dd74d07706052a33d31d7c0aafd0659e1"
APPROVAL="0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"
def getlogs(token):
    owners=set(); start=0
    for _ in range(80):
        r=rpc._get({"module":"logs","action":"getLogs","address":token,"topic0":APPROVAL,"topic2":"0x"+"0"*24+POOL[2:],"fromBlock":start,"toBlock":"latest","page":1,"offset":1000})
        res=r.get("result")
        if not res or not isinstance(res,list) or len(res)==0: break
        for lg in res: owners.add("0x"+lg["topics"][1][-40:])
        if len(res)<1000: break
        start=int(res[-1]["blockNumber"],16)+1
    return owners
tok=sys.argv[1]; name=sys.argv[2]
o=getlogs(tok)
open(f"approvers_{name}.txt","w").write("\n".join(sorted(o)))
print(f"{name}: {len(o)} distinct approvers")

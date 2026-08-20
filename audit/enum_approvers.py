import json, urllib.request, time, sys
RPC="https://arbitrum.publicnode.com"
POOL="0xf4b1486dd74d07706052a33d31d7c0aafd0659e1"
APPROVAL="0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"
def rpc(method,params):
    req=urllib.request.Request(RPC,data=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode(),headers={"content-type":"application/json"})
    for _ in range(4):
        try:
            return json.loads(urllib.request.urlopen(req,timeout=40).read())
        except Exception as e:
            time.sleep(1.5)
    return {}
def getlogs_chunked(token, start, end, step=800000):
    owners=set(); b=start
    while b<=end:
        e=min(b+step,end)
        r=rpc("eth_getLogs",[{"address":token,"topics":[APPROVAL,None,"0x"+"0"*24+POOL[2:]],"fromBlock":hex(b),"toBlock":hex(e)}])
        if "error" in r:
            # shrink
            if step>50000:
                return getlogs_chunked(token,start,end,step//2)
            b=e+1; continue
        for lg in r.get("result",[]):
            owners.add("0x"+lg["topics"][1][-40:])
        b=e+1
    return owners
if __name__=="__main__":
    token=sys.argv[1]; start=int(sys.argv[2]); end=int(sys.argv[3])
    owners=getlogs_chunked(token,start,end)
    print("\n".join(sorted(owners)))

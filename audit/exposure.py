import rpc, json, sys
POOL="0xf4b1486dd74d07706052a33d31d7c0aafd0659e1"
APPROVAL="0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925"
TOKENS={"USDC":("0xaf88d065e77c8cc2239327c5edb3a432268e5831",6),"USDT":("0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",6),
"USDC.e":("0xff970a61a04b1ca14834a43f5de4533ebddb5cc8",6),"ARB":("0x912ce59144191c1204e64559fe8253a0e49e6548",18),
"WETH":("0x82af49447d8a07e3bd95bd0d56f35241523fbab1",18),"WBTC":("0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f",8)}
def getlogs(token):
    owners=set(); start=0
    for _ in range(60):
        r=rpc._get({"module":"logs","action":"getLogs","address":token,"topic0":APPROVAL,"topic2":"0x"+"0"*24+POOL[2:],"topic0_2_opr":"and","fromBlock":start,"toBlock":"latest","page":1,"offset":1000})
        res=r.get("result")
        if not res or not isinstance(res,list) or len(res)==0: break
        for lg in res: owners.add("0x"+lg["topics"][1][-40:])
        if len(res)<1000: break
        start=int(res[-1]["blockNumber"],16)+1
    return owners
def bal(t,a):
    r=rpc.eth_call(t,"0x70a08231"+"0"*24+a[2:]); return int(r,16) if r and r!="0x" else 0
def allow(t,a):
    r=rpc.eth_call(t,"0xdd62ed3e"+"0"*24+a[2:]+"0"*24+POOL[2:]); return int(r,16) if r and r!="0x" else 0
sym=sys.argv[1]; tok,dec=TOKENS[sym]
owners=getlogs(tok)
at_risk=0; live=0; open_allow=0
for a in owners:
    al=allow(tok,a)
    if al>0: open_allow+=1
    if al>0:
        b=bal(tok,a); m=min(b,al)
        if m>0: at_risk+=m; live+=1
print(f"{sym}: {len(owners)} historical approvers | {open_allow} still have OPEN allowance | {live} have live balance | AT-RISK NOW = {at_risk/10**dec:,.4f} {sym}")

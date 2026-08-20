import json, subprocess, keccak, sys
POOL="0xf4b1486dd74d07706052a33d31d7c0aafd0659e1"
MC3="0xcA11bde05977b3631167028862bE2a173976CA11"
def rpc(method,params):
    req={"jsonrpc":"2.0","id":1,"method":method,"params":params}
    open("/tmp/mc.json","w").write(json.dumps(req))
    out=subprocess.run(["curl","-s","--max-time","60","--noproxy","*","-X","POST","https://arbitrum.publicnode.com","-H","content-type: application/json","--data","@/tmp/mc.json"],capture_output=True,text=True).stdout
    return json.loads(out)
def enc_addr(a): return a[2:].lower().rjust(64,"0")
def w(n): return hex(n)[2:].rjust(64,"0")
# aggregate3((address,bool,bytes)[])
AGG=keccak.sel("aggregate3((address,bool,bytes)[])")
def build_agg(calls):  # calls=[(target,calldata_hex)]
    n=len(calls)
    head=w(0x20)+w(n)
    # tuple array: offsets then tuples
    offs=""; body=""; base=n*32
    parts=[]
    for target,cd in calls:
        cdb=bytes.fromhex(cd[2:]); L=len(cdb); pad=(32-(L%32))%32
        tup=enc_addr(target)+w(1)+w(0x60)+w(L)+cd[2:]+"00"*pad
        parts.append(tup)
    offs=""; cur=base
    for p in parts: offs+=w(cur); cur+=len(bytes.fromhex(p))
    return "0x"+AGG+head+offs+"".join(parts)
def call_allow(owner): return "0xdd62ed3e"+enc_addr(owner)+enc_addr(POOL)
def call_bal(owner): return "0x70a08231"+enc_addr(owner)
def decode_agg(res):
    x=res[2:]; # returns (Result[] {bool,bytes})
    # offset
    off=int(x[0:64],16)*2; n=int(x[off:off+64],16); p=off+64
    outs=[]
    elem_offs=[int(x[p+i*64:p+(i+1)*64],16)*2 for i in range(n)]
    for eo in elem_offs:
        st=p+eo
        succ=int(x[st:st+64],16); rlen=int(x[st+64:st+128],16)*2
        ret=x[st+128:st+128+rlen]
        outs.append((succ, int(ret[:64],16) if rlen>=64 and succ else 0))
    return outs
owners=[l.strip() for l in open(sys.argv[1]) if l.strip()]
dec=int(sys.argv[2]); name=sys.argv[3]
BATCH=600
at_risk=0; open_allow=0; live=0
for i in range(0,len(owners),BATCH):
    chunk=owners[i:i+BATCH]
    calls=[]
    for o in chunk: calls.append((sys.argv[4],call_allow(o)))
    r=rpc("eth_call",[{"to":MC3,"data":build_agg(calls)},"latest"])
    if "result" not in r: continue
    allows=decode_agg(r["result"])
    # balances for those with allowance>0
    idx=[j for j,(s,v) in enumerate(allows) if s and v>0]
    open_allow+=len(idx)
    if idx:
        calls2=[(sys.argv[4],call_bal(chunk[j])) for j in idx]
        r2=rpc("eth_call",[{"to":MC3,"data":build_agg(calls2)},"latest"])
        bals=decode_agg(r2["result"]) if "result" in r2 else []
        for k,j in enumerate(idx):
            al=allows[j][1]; b=bals[k][1] if k<len(bals) and bals[k][0] else 0
            m=min(al,b)
            if m>0: at_risk+=m; live+=1
print(f"{name}: approvers={len(owners)} open_allowance={open_allow} live_balance={live} AT_RISK_NOW={at_risk/10**dec:,.4f}")

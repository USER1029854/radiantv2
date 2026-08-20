import json, subprocess, keccak
MC3="0xcA11bde05977b3631167028862bE2a173976CA11"
enc=lambda a:a[2:].lower().rjust(64,"0"); w=lambda n:hex(n)[2:].rjust(64,"0")
AGG=keccak.sel("aggregate3((address,bool,bytes)[])")[2:]
def rpc(data):
    req={"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":MC3,"data":data},"latest"]}
    open("/tmp/mc.json","w").write(json.dumps(req))
    return json.loads(subprocess.run(["curl","-s","--max-time","60","--noproxy","*","-X","POST","https://arbitrum.publicnode.com","-H","content-type: application/json","--data","@/tmp/mc.json"],capture_output=True,text=True).stdout)
def build(calls):
    n=len(calls); parts=[]
    for target,cd in calls:
        cdb=bytes.fromhex(cd[2:]); L=len(cdb); pad=(32-(L%32))%32
        parts.append(enc(target)+w(1)+w(0x60)+w(L)+cd[2:]+"00"*pad)
    cur=n*32; offs=""
    for p in parts: offs+=w(cur); cur+=len(bytes.fromhex(p))
    return "0x"+AGG+w(0x20)+w(n)+offs+"".join(parts)
def decode(res):
    x=res[2:]; off=int(x[0:64],16)*2; n=int(x[off:off+64],16); p=off+64
    eos=[int(x[p+i*64:p+(i+1)*64],16)*2 for i in range(n)]; outs=[]
    for eo in eos:
        st=p+eo; succ=int(x[st:st+64],16); boff=int(x[st+64:st+128],16)*2
        bpos=st+boff; blen=int(x[bpos:bpos+64],16)*2; data=x[bpos+64:bpos+64+blen]
        outs.append((succ, int(data[:64],16) if blen>=64 and succ else 0))
    return outs
def batched(calls, size=500):
    out=[]
    for i in range(0,len(calls),size):
        r=rpc(build(calls[i:i+size]))
        if "result" in r: out+=decode(r["result"])
        else: out+=[(0,0)]*len(calls[i:i+size])
    return out

import rpc, json
POOL="0xf4b1486dd74d07706052a33d31d7c0aafd0659e1"
TOKENS={"USDC":("0xaf88d065e77c8cc2239327c5edb3a432268e5831",6),"USDT":("0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",6),
"USDC.e":("0xff970a61a04b1ca14834a43f5de4533ebddb5cc8",6),"ARB":("0x912ce59144191c1204e64559fe8253a0e49e6548",18)}
# gather victims from recent sweep tx inputs
r=rpc._get({"module":"account","action":"txlist","address":POOL,"startblock":0,"endblock":99999999,"page":1,"offset":60,"sort":"desc"}).get("result",[])
victims=set()
for t in r:
    inp=t.get("input","")
    if inp.startswith("0xf5121a99"):
        # f5121a99(token, address[]): parse array
        body=inp[10:]
        # word0=token, word1=offset(0x40), word2=len, word3..=elems
        try:
            n=int(body[128:192],16)
            for i in range(n):
                victims.add("0x"+body[192+i*64:192+(i+1)*64][-40:])
        except: pass
def bal(tok,a): 
    r=rpc.eth_call(tok,"0x70a08231"+"0"*24+a[2:]); return int(r,16) if r and r!="0x" else 0
def allow(tok,a):
    r=rpc.eth_call(tok,"0xdd62ed3e"+"0"*24+a[2:]+"0"*24+POOL[2:]); return int(r,16) if r and r!="0x" else 0
print(f"checking {len(victims)} recent victims for live balance*allowance ...")
for v in victims:
    for sym,(tok,dec) in TOKENS.items():
        b=bal(tok,v); al=allow(tok,v)
        m=min(b,al)
        if m>0:
            print(f"LIVE: {v} {sym} bal={b/10**dec:.4f} allow={al/10**dec if al<10**30 else 'inf'} min={m/10**dec:.4f}")

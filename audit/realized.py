import rpc, json
BENEFIT="0x070ca92f568037d351666b3918a0f6ba7ad20ed1"
# real reserve tokens (ignore homoglyph scam tokens)
REAL={
"0xaf88d065e77c8cc2239327c5edb3a432268e5831":("USDC",6),
"0xff970a61a04b1ca14834a43f5de4533ebddb5cc8":("USDC.e",6),
"0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9":("USDT",6),
"0x912ce59144191c1204e64559fe8253a0e49e6548":("ARB",18),
"0x82af49447d8a07e3bd95bd0d56f35241523fbab1":("WETH",18),
"0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f":("WBTC",8),
"0xda10009cbd5d07dd0cecc66161fc93d7c9000da1":("DAI",18),
"0x5979d7b546e38e414f7e9822514be443a4800529":("wstETH",18),
"0x35751007a407ca6feffe80b3cb397736d2cf4dbe":("weETH",18),
}
totals={}; senders={}
page=1
while True:
    r=rpc._get({"module":"account","action":"tokentx","address":BENEFIT,"startblock":0,"endblock":99999999,"page":page,"offset":10000,"sort":"asc"}).get("result")
    if not r or not isinstance(r,list) or len(r)==0: break
    for t in r:
        ca=t["contractAddress"].lower()
        if ca in REAL and t["to"].lower()==BENEFIT:
            sym,dec=REAL[ca]
            totals[sym]=totals.get(sym,0)+int(t["value"])
            senders.setdefault(sym,set()).add(t["from"].lower())
    if len(r)<10000: break
    page+=1
    if page>20: break
print("=== REALIZED inbound to sweep destination 0x070ca92f (real reserve tokens) ===")
for sym in totals:
    dec=[d for c,(s,d) in REAL.items() if s==sym][0]
    print(f"{sym:8s} {totals[sym]/10**dec:>18,.4f}   from {len(senders[sym])} distinct victims")

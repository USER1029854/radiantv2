import json,urllib.request,time,sys
K="R6PYYNEX4CNFAXX4YX3K8W4NXSBGGG4QGJ"
_last=[0.0]
def call(chain,to,data):
    dt=time.time()-_last[0]
    if dt<0.45: time.sleep(0.45-dt)
    _last[0]=time.time()
    u=f"https://api.etherscan.io/v2/api?chainid={chain}&module=proxy&action=eth_call&to={to}&data={data}&tag=latest&apikey={K}"
    for _ in range(5):
        try:
            r=json.loads(urllib.request.urlopen(u,timeout=30).read()).get("result")
            if r and "rate limit" not in str(r).lower(): return r
        except: pass
        time.sleep(1.0)
    return None

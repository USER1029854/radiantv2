#!/usr/bin/env python3
import json, sys, time, urllib.request, urllib.parse, os
EK="R6PYYNEX4CNFAXX4YX3K8W4NXSBGGG4QGJ"; CHAIN=42161
BASE="https://api.etherscan.io/v2/api"
_LAST=[0.0]
def _throttle():
    dt=time.time()-_LAST[0]
    if dt<0.4: time.sleep(0.4-dt)
    _LAST[0]=time.time()
def _get(params, retries=6):
    params=dict(params); params["chainid"]=CHAIN; params["apikey"]=EK
    url=BASE+"?"+urllib.parse.urlencode(params)
    last=None
    for i in range(retries):
        _throttle()
        try:
            with urllib.request.urlopen(url, timeout=45) as r:
                d=json.loads(r.read().decode())
            s=json.dumps(d)
            if "rate limit" in s.lower() or "Max calls per sec" in s:
                time.sleep(1.2); continue
            return d
        except Exception as e:
            last=e; time.sleep(1.5*(i+1))
    if last: raise last
    return {}
def eth_call(to,data,tag="latest"):
    return _get({"module":"proxy","action":"eth_call","to":to,"data":data,"tag":tag}).get("result")
def get_code(addr,tag="latest"):
    return _get({"module":"proxy","action":"eth_getCode","address":addr,"tag":tag}).get("result")
def get_storage(addr,slot,tag="latest"):
    return _get({"module":"proxy","action":"eth_getStorageAt","address":addr,"position":slot,"tag":tag}).get("result")
def get_source(addr):
    return _get({"module":"contract","action":"getsourcecode","address":addr}).get("result")
def balance(addr,tag="latest"):
    return _get({"module":"proxy","action":"eth_getBalance","address":addr,"tag":tag}).get("result")
def txlist(addr,startblock=0,page=1,offset=20,sort="asc"):
    return _get({"module":"account","action":"txlist","address":addr,"startblock":startblock,"endblock":99999999,"page":page,"offset":offset,"sort":sort}).get("result")
def eth_call_from(frm,to,data,tag="latest"):
    return _get({"module":"proxy","action":"eth_call","from":frm,"to":to,"data":data,"tag":tag}).get("result")
if __name__=="__main__":
    cmd=sys.argv[1]
    if cmd=="code": print(get_code(sys.argv[2]))
    elif cmd=="storage": print(get_storage(sys.argv[2],sys.argv[3]))
    elif cmd=="call": print(eth_call(sys.argv[2],sys.argv[3]))
    elif cmd=="callfrom": print(eth_call_from(sys.argv[2],sys.argv[3],sys.argv[4]))
    elif cmd=="source": r=get_source(sys.argv[2]); print(json.dumps(r,indent=2)[:4000] if r else "None")
    elif cmd=="balance": print(balance(sys.argv[2]))
    elif cmd=="txlist": print(json.dumps(txlist(sys.argv[2],offset=int(sys.argv[3]) if len(sys.argv)>3 else 20),indent=2)[:6000])

import json, keccak, subprocess, os
ADMIN="0xc24927bd40bab67ccfb2ca0a90d6cbb8edb21302"
POOL="0xf4b1486dd74d07706052a33d31d7c0aafd0659e1"
USDC="0xaf88d065e77c8cc2239327c5edb3a432268e5831"
VICTIM="0xfb2a899dd5655ecdd999796f4c6d6855f49b0f09"
BENEFIT="0x070ca92f568037d351666b3918a0f6ba7ad20ed1"
AP="0x091d52cace1edc5527c99cdcfa6937c1635330e4"
CTRL="0x57ba8957ed2ff2e7ae38f4935451e81ce1eefbf5"
CTRL_OWNER="0x0629b1048298ae9deff0f4100a31967fb3f98962"
STUB="0x3d4c56cdb97355807157f5c7d4f54957f0e9af44"
enc=lambda a:a[2:].lower().rjust(64,"0")
w=lambda n:hex(n)[2:].rjust(64,"0")
def rpc(params):
    req={"jsonrpc":"2.0","id":1,"method":"eth_call","params":params}
    open("/tmp/rq.json","w").write(json.dumps(req))
    out=subprocess.run(["curl","-s","--max-time","40","--noproxy","*","-X","POST","https://arbitrum.publicnode.com","-H","content-type: application/json","--data","@/tmp/rq.json"],capture_output=True,text=True).stdout
    return json.loads(out)
def show(tag,r):
    if "error" in r: print(f"{tag}: REVERT -> {r['error'].get('message','')}")
    else: print(f"{tag}: SUCCESS (result {r['result'][:20]}...)")

# ---- F-1 negative: prober at a NON-admin addr calls pool.f5121a99 -> must revert ----
runtime=open("prober_runtime.hex").read().strip()
sel=keccak.sel("probe(address,address,address,address)")
data=sel+enc(POOL)+enc(USDC)+enc(VICTIM)+enc(BENEFIT)
NONADMIN="0x000000000000000000000000000000000000c0de"
r=rpc([{"from":"0x0000000000000000000000000000000000001234","to":NONADMIN,"data":data},"latest",{NONADMIN:{"code":runtime}}])
show("F-1 sweep from NON-admin (prober@0x..c0de)", r)

# ---- F-2: controller.execute([AP],[AP.setLendingPoolImpl(STUB)]) ----
inner="0x5aef021f"+enc(STUB)                       # setLendingPoolImpl(address)
# execute(address[] targets, bytes[] datas)
sel_exec="0x63fb0b96"
# ABI: head: off_targets(0x40), off_datas; targets:[len,AP]; datas:[len, off0(0x20), (len,inner_padded)]
targets_blob = w(1)+enc(AP)
inner_bytes = bytes.fromhex(inner[2:]); inner_len=len(inner_bytes)
inner_padded = inner[2:] + "0"*((32-(inner_len%32))%32)
datas_blob = w(1)+w(0x20)+w(inner_len)+inner_padded
off_targets=0x40
off_datas=0x40+len(bytes.fromhex(targets_blob))
calldata=sel_exec+w(off_targets)+w(off_datas)+targets_blob+datas_blob
# positive: from controller owner
r=rpc([{"from":CTRL_OWNER,"to":CTRL,"data":calldata},"latest"])
show("F-2 execute(setLendingPoolImpl) from OWNER 0x0629b1", r)
# negative: from random
r=rpc([{"from":"0x0000000000000000000000000000000000009999","to":CTRL,"data":calldata},"latest"])
show("F-2 execute(setLendingPoolImpl) from RANDOM", r)
# also direct AP.setLendingPoolImpl from controller (owner of AP) vs random
r=rpc([{"from":CTRL,"to":AP,"data":inner},"latest"]); show("F-2 direct AP.setLendingPoolImpl from CONTROLLER(owner)", r)
r=rpc([{"from":"0x0000000000000000000000000000000000009999","to":AP,"data":inner},"latest"]); show("F-2 direct AP.setLendingPoolImpl from RANDOM", r)

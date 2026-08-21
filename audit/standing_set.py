import mc
POOL="0xf4b1486dd74d07706052a33d31d7c0aafd0659e1"
TOKENS={"USDC":"0xaf88d065e77c8cc2239327c5edb3a432268e5831","USDT":"0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9",
"USDC.e":"0xff970a61a04b1ca14834a43f5de4533ebddb5cc8","ARB":"0x912ce59144191c1204e64559fe8253a0e49e6548",
"WBTC":"0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f","DAI":"0xda10009cbd5d07dd0cecc66161fc93d7c9000da1",
"wstETH":"0x5979d7b546e38e414f7e9822514be443a4800529","weETH":"0x35751007a407ca6feffe80b3cb397736d2cf4dbe"}
files={"USDC":"approvers_USDC.txt","USDT":"approvers_USDT.txt","USDC.e":"approvers_USDCe.txt","ARB":"approvers_ARB.txt",
"WBTC":"approvers_WBTC.txt","DAI":"approvers_DAI.txt","wstETH":"approvers_wstETH.txt","weETH":"approvers_weETH.txt"}
standing=set()
for sym,tok in TOKENS.items():
    owners=[l.strip() for l in open(files[sym]) if l.strip()]
    al=mc.batched([(tok,"0xdd62ed3e"+mc.enc(o)+mc.enc(POOL)) for o in owners], size=500)
    for i,(s,v) in enumerate(al):
        if s and v>0: standing.add(owners[i])
open("arbitrum_standing_approvals.txt","w").write("\n".join(sorted(standing)))
print(f"distinct addresses with >=1 open allowance to the Arbitrum pool: {len(standing)}")

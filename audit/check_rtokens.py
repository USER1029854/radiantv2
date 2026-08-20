import rpc
# (asset, rToken, symbol, decimals)
reserves=[
("0x2f2a2543b76a4166549f7aab2e75bef0aefc5b0f","0x727354712bdfcd8596a3852fd2065b3c34f4f770","WBTC",8),
("0xfd086bc7cd5c481dcc9c85ebe478a1c0b69fcbb9","0xd69d402d1bdb9a2b8c3d88d98b9ceaf9e4cd72d9","USDT",6),
("0xff970a61a04b1ca14834a43f5de4533ebddb5cc8","0x48a29e756cc1c097388f3b2f3b570ed270423b3d","USDC.e",6),
("0xda10009cbd5d07dd0cecc66161fc93d7c9000da1","0x0d914606f3424804fa1bbbe56ccc3416733acec6","DAI",18),
("0x82af49447d8a07e3bd95bd0d56f35241523fbab1","0x0df5dfd95966753f01cb80e76dc20ea958238c46","WETH",18),
("0x5979d7b546e38e414f7e9822514be443a4800529","0x42c248d137512907048021b30d9da17f48b5b7b2","wstETH",18),
("0x912ce59144191c1204e64559fe8253a0e49e6548","0x2dade5b7df9da3a7e1c9748d169cd6dff77e3d01","ARB",18),
("0xaf88d065e77c8cc2239327c5edb3a432268e5831","0x3a2d44e354f2d88ef6da7a5a4646fd70182a7f55","USDC",6),
("0x35751007a407ca6feffe80b3cb397736d2cf4dbe","0xb11a56da177c5532d5e29cc8363d145bd0822c81","weETH",18),
]
def bal(token, holder):
    d="0x70a08231"+"0"*24+holder[2:].lower()
    r=rpc.eth_call(token,d)
    return int(r,16) if r and r!="0x" else 0
for asset,rtok,sym,dec in reserves:
    b=bal(asset,rtok)
    print(f"{sym:8s} rToken underlying balance = {b/10**dec:,.4f}")

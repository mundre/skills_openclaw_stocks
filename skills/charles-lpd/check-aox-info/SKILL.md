---
name: check-aox-info
description: 查看 AOX 基本信息，1. AO链提现到原生链，当天可提现的金额。 原生链支持的 Token, 包含 chainType，decimals，symbol，locker，tokenId， 以及 跨到 ao 链上的 wrappedTokenId 。AO链支持的 Token, 包含 name，ticker，denomination， 以及跨到原生链上的 wrappedTokenId 。不同的链，充值提现都有单独的暂时关闭，例如 closeArweaveBurn: true ，关闭提现到Arweave 链，closeEthBurn: true ,关闭提现到 ethereum 链。
command: node script/index.js
---

# 获取 AOX 基本信息

## Trigger

当用户问到 AOX 跨链的基本信息时。

- 都有哪些交易对？
- 某一个链当前是否可以充值或提现？
- 某 Token 最大提现额度是多少？


## Output
### 示例返回
```js
{
    "bridgePid": "MysFttDUI1YJKcFwYIyqVWGfFGnetcCp_5TGjdhVgS4",
    "arLocker": "AKQcAkNtnNXmEWBMMxfJ08oeoHP3RLs2jshRGnje1ow",
    "chainTokens": [
        {
            "chainType": "arweave",
            "chainId": 0,
            "symbol": "AR",
            "decimals": 12,
            "stableRange": 10,
            "locker": "AKQcAkNtnNXmEWBMMxfJ08oeoHP3RLs2jshRGnje1ow",
            "tokenId": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
            "wrappedTokenId": "xU9zFkq3X2ZQ6olwNVvr1vUWIjc3kXTWr7xKQD6dh10"
        },
        {
            "chainType": "ethereum",
            "chainId": 1,
            "symbol": "USDC",
            "decimals": 6,
            "stableRange": 20,
            "locker": "0xB3F2f559Fe40c1F1eA1e941E982d9467208e17ae",
            "tokenId": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
            "wrappedTokenId": "7zH9dlMNoxprab9loshv3Y7WG45DOny_Vrq9KrXObdQ"
        },
        {
            "chainType": "ethereum",
            "chainId": 1,
            "symbol": "4EVER",
            "decimals": 18,
            "stableRange": 20,
            "locker": "0xB3F2f559Fe40c1F1eA1e941E982d9467208e17ae",
            "tokenId": "0xe355De6a6043b0580Ff5A26b46051A4809B12793",
            "wrappedTokenId": "y9NnhY2RtCz0JP7LMJM8lIG2yGpZDAg0FUMYwDK_0Pg"
        },
        {
            "chainType": "ethereum",
            "chainId": 1,
            "symbol": "ANS",
            "decimals": 18,
            "stableRange": 20,
            "locker": "0xB3F2f559Fe40c1F1eA1e941E982d9467208e17ae",
            "tokenId": "0x937EFa4a5Ff9d65785691b70a1136aAf8aDA7e62",
            "wrappedTokenId": "kCHI8LYxZf1NsmRoHCKHsf6PD4sMAvfPsMSkLta54Rw"
        },
        {
            "chainType": "ethereum",
            "chainId": 1,
            "symbol": "ANYONE",
            "decimals": 18,
            "stableRange": 20,
            "locker": "0xB3F2f559Fe40c1F1eA1e941E982d9467208e17ae",
            "tokenId": "0xFeAc2Eae96899709a43E252B6B92971D32F9C0F9",
            "wrappedTokenId": "H41CVAmengY3BuSz1aLjFJf26RKFbj0ENGTI7aG8j-U"
        },
        {
            "chainType": "ethereum",
            "chainId": 1,
            "symbol": "ETH",
            "decimals": 18,
            "stableRange": 20,
            "locker": "0xB3F2f559Fe40c1F1eA1e941E982d9467208e17ae",
            "tokenId": "0x0000000000000000000000000000000000000000",
            "wrappedTokenId": "cBgS-V_yGhOe9P1wCIuNSgDA_JS8l4sE5iFcPTr0TD0"
        },
        {
            "chainType": "bsc",
            "chainId": 56,
            "symbol": "USDT",
            "decimals": 18,
            "stableRange": 20,
            "locker": "0x694f7D125557b0d43080932D61ad5EAEC203CDb9",
            "tokenId": "0x55d398326f99059fF775485246999027B3197955",
            "wrappedTokenId": "7j3jUyFpTuepg_uu_sJnwLE6KiTVuA9cLrkfOp2MFlo"
        }
    ],
    "wrappedTokens": [
        {
            "wrappedTokenId": "kCHI8LYxZf1NsmRoHCKHsf6PD4sMAvfPsMSkLta54Rw",
            "name": "Ethereum-Wrapped ANS",
            "ticker": "wANS",
            "denomination": "18",
            "totalSupply": "",
            "minBurnAmt": "",
            "burnFee": "",
            "feeRecipient": "",
            "mintFee": "",
            "holderNum": "",
            "bridgeProcessId": "MysFttDUI1YJKcFwYIyqVWGfFGnetcCp_5TGjdhVgS4"
        },
        {
            "wrappedTokenId": "H41CVAmengY3BuSz1aLjFJf26RKFbj0ENGTI7aG8j-U",
            "name": "Ethereum-Wrapped ANYONE",
            "ticker": "wANYONE",
            "denomination": "18",
            "totalSupply": "",
            "minBurnAmt": "",
            "burnFee": "",
            "feeRecipient": "",
            "mintFee": "",
            "holderNum": "",
            "bridgeProcessId": "MysFttDUI1YJKcFwYIyqVWGfFGnetcCp_5TGjdhVgS4"
        },
        {
            "wrappedTokenId": "cBgS-V_yGhOe9P1wCIuNSgDA_JS8l4sE5iFcPTr0TD0",
            "name": "Ethereum-Wrapped ETH",
            "ticker": "wETH",
            "denomination": "18",
            "totalSupply": "1803818424274527748",
            "minBurnAmt": "130000000000000",
            "burnFee": "130000000000000",
            "feeRecipient": "4S58xCqS6uKcrvqb2JlrCWllC2VIBs7qxU15QbWa3ZI",
            "mintFee": "0",
            "holderNum": "46",
            "bridgeProcessId": "MysFttDUI1YJKcFwYIyqVWGfFGnetcCp_5TGjdhVgS4"
        },
        {
            "wrappedTokenId": "7j3jUyFpTuepg_uu_sJnwLE6KiTVuA9cLrkfOp2MFlo",
            "name": "BSC-Wrapped USDT",
            "ticker": "wUSDT",
            "denomination": "18",
            "totalSupply": "3750901227756733227206",
            "minBurnAmt": "1000000000000000000",
            "burnFee": "500000000000000000",
            "feeRecipient": "4S58xCqS6uKcrvqb2JlrCWllC2VIBs7qxU15QbWa3ZI",
            "mintFee": "0",
            "holderNum": "107",
            "bridgeProcessId": "MysFttDUI1YJKcFwYIyqVWGfFGnetcCp_5TGjdhVgS4"
        },
        {
            "wrappedTokenId": "xU9zFkq3X2ZQ6olwNVvr1vUWIjc3kXTWr7xKQD6dh10",
            "name": "Wrapped AR",
            "ticker": "wAR",
            "denomination": "12",
            "totalSupply": "129769196913862835",
            "minBurnAmt": "500000000000",
            "burnFee": "300000000000",
            "feeRecipient": "4S58xCqS6uKcrvqb2JlrCWllC2VIBs7qxU15QbWa3ZI",
            "mintFee": "0",
            "holderNum": "43018",
            "bridgeProcessId": "MysFttDUI1YJKcFwYIyqVWGfFGnetcCp_5TGjdhVgS4"
        },
        {
            "wrappedTokenId": "7zH9dlMNoxprab9loshv3Y7WG45DOny_Vrq9KrXObdQ",
            "name": "Ethereum-Wrapped USDC",
            "ticker": "wUSDC",
            "denomination": "6",
            "totalSupply": "488791608436",
            "minBurnAmt": "271524",
            "burnFee": "271524",
            "feeRecipient": "4S58xCqS6uKcrvqb2JlrCWllC2VIBs7qxU15QbWa3ZI",
            "mintFee": "0",
            "holderNum": "1480",
            "bridgeProcessId": "MysFttDUI1YJKcFwYIyqVWGfFGnetcCp_5TGjdhVgS4"
        },
        {
            "wrappedTokenId": "y9NnhY2RtCz0JP7LMJM8lIG2yGpZDAg0FUMYwDK_0Pg",
            "name": "Ethereum-Wrapped 4EVER",
            "ticker": "w4EVER",
            "denomination": "18",
            "totalSupply": "2256952763705823141862600",
            "minBurnAmt": "5000000000000000000000",
            "burnFee": "2000000000000000000000",
            "feeRecipient": "4S58xCqS6uKcrvqb2JlrCWllC2VIBs7qxU15QbWa3ZI",
            "mintFee": "0",
            "holderNum": "32",
            "bridgeProcessId": "MysFttDUI1YJKcFwYIyqVWGfFGnetcCp_5TGjdhVgS4"
        }
    ],
    "burnLimits": {
        "4EVER": {
            "dailyDate": "2026-03-13",
            "dailyLimit": "1000000.00",
            "dailyBurned": "0.00",
            "perLimit": "100000.00"
        },
        "ANS": {
            "dailyDate": "2026-03-13",
            "dailyLimit": "5000.00",
            "dailyBurned": "0.00",
            "perLimit": "500.00"
        },
        "ANYONE": {
            "dailyDate": "2026-03-13",
            "dailyLimit": "1000000.00",
            "dailyBurned": "0.00",
            "perLimit": "100000.00"
        },
        "AR": {
            "dailyDate": "2026-03-17",
            "dailyLimit": "20000.00",
            "dailyBurned": "1.76",
            "perLimit": "5000.00"
        },
        "ETH": {
            "dailyDate": "2026-03-13",
            "dailyLimit": "200.00",
            "dailyBurned": "0.00",
            "perLimit": "10.00"
        },
        "USDC": {
            "dailyDate": "2026-03-17",
            "dailyLimit": "150000.00",
            "dailyBurned": "0.00",
            "perLimit": "50000.00"
        },
        "USDT": {
            "dailyDate": "2026-03-13",
            "dailyLimit": "50000.00",
            "dailyBurned": "0.00",
            "perLimit": "10000.00"
        }
    },
    "mintLimits": {
        "4EVER": 100000,
        "ANS": 500,
        "ANYONE": 100000,
        "AR": 2000,
        "ETH": 10,
        "USDC": 50000,
        "USDT": 50000
    },
    "HmBridgeTokenPairs": {
        "": {
            "tokenId": "",
            "name": "",
            "ticker": ""
        }
    },
    "closeServer": {
        "closeBaseMint": true,
        "closeEthMint": false,
        "closeBscMint": false,
        "closeArweaveMint": false,
        "closeEthBurn": true,
        "closeBscBurn": true,
        "closeArweaveBurn": true,
        "closeTransfer": true
    }
}
```
``
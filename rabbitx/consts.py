ETHEREUM_MAINNET = "ethereum"
ETHEREUM_TESTNET = "ethereum-sepolia"
BLAST_MAINNET = "blast"
BLAST_TESTNET = "blast-sepolia"
ARBITRUM = "arbitrum"
BASE = "base"
SONIC = "sonic"

CHAIN_ID = {
    ETHEREUM_MAINNET: 1,
    ETHEREUM_TESTNET: 11155111,
    BLAST_MAINNET: 59144,
    BLAST_TESTNET: 168587773,
    ARBITRUM: 42161,
    BASE: 8453,
    SONIC: 146,
}

# EIDs
EID = {
    ETHEREUM_MAINNET: "rbx",
    ETHEREUM_TESTNET: "rbx",
    BLAST_MAINNET: "bfx",
    BLAST_TESTNET: "bfx",
    ARBITRUM: "rbx_arbitrum",
    BASE: "rbx_base",
    SONIC: "rbx_sonic",
}

API_URL = {
    ETHEREUM_MAINNET: "https://api.rabbitx.com",
    ETHEREUM_TESTNET: "https://api.testnet.rabbitx.io",
    BLAST_MAINNET: "https://api.blastfutures.com",
    BLAST_TESTNET: "https://api.testnet.blastfutures.com",
}

API_URL[ARBITRUM] = API_URL[ETHEREUM_MAINNET]
API_URL[BASE] = API_URL[ETHEREUM_MAINNET]
API_URL[SONIC] = API_URL[ETHEREUM_MAINNET]

WS_URL = {
    ETHEREUM_MAINNET: "wss://api.rabbitx.com/ws",
    ETHEREUM_TESTNET: "wss://api.testnet.rabbitx.io/ws",
    BLAST_MAINNET: "wss://api.bfx.trade/ws",
    BLAST_TESTNET: "wss://api.testnet.blastfutures.com/ws",
}

WS_URL[ARBITRUM] = WS_URL[ETHEREUM_MAINNET]
WS_URL[BASE] = WS_URL[ETHEREUM_MAINNET]
WS_URL[SONIC] = WS_URL[ETHEREUM_MAINNET]

EIP712_DOMAIN = {
    ETHEREUM_MAINNET: "RabbitXId",
    ETHEREUM_TESTNET: "RabbitXId",
    BLAST_MAINNET: "BfxId",
    BLAST_TESTNET: "BfxId",
}

EIP712_DOMAIN[ARBITRUM] = EIP712_DOMAIN[ETHEREUM_MAINNET]
EIP712_DOMAIN[BASE] = EIP712_DOMAIN[ETHEREUM_MAINNET]
EIP712_DOMAIN[SONIC] = EIP712_DOMAIN[ETHEREUM_MAINNET]

EIP712_MESSAGE = {
    ETHEREUM_MAINNET: "Welcome to RabbitX!\n\nClick to sign in and on-board your wallet for trading perpetuals.\n\nThis request will not trigger a blockchain transaction or cost any gas fees. This signature only proves you are the true owner of this wallet.\n\nBy signing this message you agree to the terms and conditions of the exchange.",
    ETHEREUM_TESTNET: "Welcome to RabbitX!\n\nClick to sign in and on-board your wallet for trading perpetuals.\n\nThis request will not trigger a blockchain transaction or cost any gas fees. This signature only proves you are the true owner of this wallet.\n\nBy signing this message you agree to the terms and conditions of the exchange.",
    BLAST_MAINNET: "Welcome to Bfx!\n\nClick to sign in and on-board your wallet for trading perpetuals.\n\nThis request will not trigger a blockchain transaction or cost any gas fees. This signature only proves you are the true owner of this wallet.\n\nBy signing this message you agree to the terms and conditions of the exchange.",
    BLAST_TESTNET: "Welcome to Bfx!\n\nClick to sign in and on-board your wallet for trading perpetuals.\n\nThis request will not trigger a blockchain transaction or cost any gas fees. This signature only proves you are the true owner of this wallet.\n\nBy signing this message you agree to the terms and conditions of the exchange.",
}

EIP712_MESSAGE[ARBITRUM] = EIP712_MESSAGE[ETHEREUM_MAINNET]
EIP712_MESSAGE[BASE] = EIP712_MESSAGE[ETHEREUM_MAINNET]
EIP712_MESSAGE[SONIC] = EIP712_MESSAGE[ETHEREUM_MAINNET]

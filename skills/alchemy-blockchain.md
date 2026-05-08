# 🔗 Alchemy Blockchain Master Skill

## Purpose
This skill enables AI agents and developers to intelligently route any blockchain task
to the correct Alchemy product (Node / Data / Wallets / Rollups) across EVM and non-EVM chains.
EVM-first (Ethereum + Base), with Solana awareness.

---

## 🗺️ Chain Map

### EVM Chains (JSON-RPC compatible)
| Category              | Chains                                                       |
|-----------------------|--------------------------------------------------------------|
| Ethereum L1           | Ethereum Mainnet, Sepolia testnet                            |
| Optimistic L2s        | Base (OP Stack ✅ recommended L2), Arbitrum, OP Mainnet      |
| ZK L2s                | Polygon zkEVM, zkSync Era, Scroll, Linea, Starknet           |
| Other EVM L2s         | Polygon PoS, Blast, Mode, Zora, Mantle, Unichain, World Chain|
| Other EVM L1s         | BNB Chain, Avalanche, Gnosis, Rootstock                      |

### Non-EVM Chains (different RPC style)
| Category              | Chains                                                       |
|-----------------------|--------------------------------------------------------------|
| High-perf alt L1      | Solana (Solana API + Yellowstone gRPC + DAS for NFTs)        |
| Other alt L1s         | Aptos, Sui, Bitcoin, Flow, Berachain, Monad, Sei, Celo       |

> 💡 Default pick: **Base** for low-fee EVM L2. **Ethereum** for max DeFi composability.

---

## 🧠 Core Mental Model

```
Request comes in
       │
       ▼
Is it about raw chain state / tx submission / events?
       │ YES → Node / Chain API
       │ NO
       ▼
Is it about enriched data (portfolio, NFTs, prices, transfers)?
       │ YES → Data API
       │ NO
       ▼
Is it about smart UX (gasless, batching, retries, session keys)?
       │ YES → Wallet API
       │ NO
       ▼
Does the app need its own dedicated chain?
          YES → Rollups
```

---

## ⚡ Node / Chain API

**Use for:** raw EVM reads, writes, events. Low-level. Chain-agnostic JSON-RPC.

### Endpoint pattern
```
https://{chain-slug}.g.alchemy.com/v2/{API_KEY}
```

### Key methods (EVM)
| Task                          | Method                        |
|-------------------------------|-------------------------------|
| Read native balance           | `eth_getBalance`              |
| Call contract view function   | `eth_call`                    |
| Get block info                | `eth_getBlockByNumber`        |
| Get transaction               | `eth_getTransactionByHash`    |
| Filter/read contract events   | `eth_getLogs`                 |
| Submit signed tx              | `eth_sendRawTransaction`      |
| Estimate gas                  | `eth_estimateGas`             |
| Get fee data                  | `eth_maxPriorityFeePerGas`    |

### Write flow
```
Build tx → Sign offline (ethers/viem) → eth_sendRawTransaction → poll eth_getTransactionReceipt
```

### Real-time (WebSockets)
```
wss://{chain-slug}.g.alchemy.com/v2/{API_KEY}

Subscriptions:
- newHeads            → new blocks
- logs (filter)       → contract events
- newPendingTxs       → mempool txs
```

### Advanced
- **Trace API** – deep internal tx traces and replay
- **Debug API** – non-standard inspection + debug methods
- **Yellowstone gRPC** – high-perf real-time Solana streams

---

## 📊 Data API

**Use for:** pre-indexed, enriched data. Portfolios, NFTs, prices, transfers, webhooks, simulations.

### Hero modules
| Module           | Use case                                           | Key method                          |
|------------------|----------------------------------------------------|-------------------------------------|
| Portfolio API    | Full wallet view (tokens + NFTs)                   | `getPortfolio`                      |
| Token API        | Token balances + metadata                          | `alchemy_getTokenBalances`          |
| Transfers API    | Historical asset movement for an address           | `alchemy_getAssetTransfers`         |
| Prices API       | Token price (current + historical)                 | `getTokenPrices`                    |
| NFT API          | NFT discovery, ownership, metadata (EVM)           | `getNftsForOwner`, `getNftMetadata` |
| Solana NFT / DAS | Solana NFT discovery + metadata                    | DAS `getAssetsByOwner`              |
| Webhooks         | Push events: transfers, balance changes, contract  | Address Activity, Custom Webhook    |
| Simulation API   | Simulate tx before sending, see state changes      | `simulateAssetChanges`              |
| Utility API      | Helpers (block by timestamp, receipts, etc.)       | `getBlockByTimestamp`               |

### Common intent → Data API mapping
| What you want                          | Use this                              |
|----------------------------------------|---------------------------------------|
| Show wallet dashboard (tokens + NFTs)  | Portfolio API + Token API + NFT API   |
| Activity feed / transfer history       | Transfers API + Webhooks              |
| Token price for display                | Prices API                            |
| User's NFT collection                  | NFT API (`getNftsForOwner`)           |
| NFT metadata (name, image, traits)     | NFT API (`getNftMetadata`)            |
| Notify on wallet deposit/withdrawal    | Webhooks (Address Activity)           |
| Preview tx effects before sending      | Simulation API                        |
| Historical portfolio value             | Prices API + Token API combined       |

---

## 💳 Wallet API

**Use for:** Smart wallet UX. When you want to abstract gas, batch txs, or build session-based flows.

> Layer this ON TOP of Node/Data. If a tx flow needs any of the below, use Wallets not raw Node.

### When to use Wallet API instead of raw Node
| Requirement                              | Wallet feature           |
|------------------------------------------|--------------------------|
| User shouldn't need gas / ETH            | Gas Sponsorship          |
| User pays gas in ERC-20 (USDC etc.)      | ERC-20 Gas Payments      |
| Combine multiple actions atomically      | Batch Calls              |
| Stuck tx needs auto-retry/reprice        | Automatic Retries        |
| Autonomous bot / game loop signing       | Session Keys             |
| Multiple txs without nonce collisions    | Parallel Transactions    |
| In-app token swap (same or cross-chain)  | Swaps API                |
| EOA upgraded to smart wallet behavior    | EIP-7702                 |

### TypeScript SDK pattern
```typescript
import { createAlchemySmartAccountClient } from "@alchemy/aa-alchemy";

// Send one or more calls
const result = await client.sendCalls({
  calls: [
    { to: CONTRACT_ADDRESS, data: encodedCallData },
    { to: TOKEN_ADDRESS, data: encodedApproveData }
  ]
});

// Wait for confirmation
await client.waitForCallsStatus({ id: result.id });
```

### Wallet infra (low level, if needed)
- **Gas Manager API** – configure gas sponsorship rules + limits
- **Bundler API** – ERC-4337 UserOperation bundling (raw AA infra)
- **Privy** – recommended embedded wallet provider (social login, OTP, passkeys)

---

## 🔁 Rollups

**Use for:** When you need your OWN dedicated chain (game ecosystems, custom economies, full control).

### Types
| Type        | How it works                                      | Finality         |
|-------------|---------------------------------------------------|------------------|
| Optimistic  | Assume valid, fraud proofs for challenge period   | Slower (days)    |
| ZK          | Cryptographic proof per batch                     | Fast (minutes)   |

### Supported stacks (Alchemy Rollups)
- **OP Stack** – powers Base, OP Mainnet (Optimistic)
- **Arbitrum Stack** – Arbitrum Orbit chains (Optimistic)
- **zkSync Stack** – ZK rollup family

### When to consider your own rollup
- You want full blockspace control (no congestion for your users)
- You want custom gas token (e.g. BROski$)
- You want custom precompiles or chain-level identity hooks
- You want to capture tx fees + MEV for your ecosystem
- You're building a game world, NFT platform, or DeFi protocol at scale

> 💡 For HyperFocus/BROski world: your own L3 rollup on Base using OP Stack is a legit endgame.

---

## 🌐 Multi-chain Routing

| Use case                              | Chain recommendation               |
|---------------------------------------|------------------------------------|
| Low-fee EVM app + Coinbase alignment  | **Base** (OP Stack L2)             |
| Max DeFi composability                | **Ethereum Mainnet**               |
| High-performance + Solana ecosystem   | **Solana** (Solana API + DAS)      |
| Cheap EVM testnet                     | **Sepolia** (Ethereum testnet)     |
| ZK rollup use case                    | **zkSync Era** or **Polygon zkEVM**|

---

## 🚀 Quick-Reference Decision Table

| Task                                | Chain      | Product         | Method / API                      |
|-------------------------------------|------------|-----------------|-----------------------------------|
| Read contract view function         | EVM        | Node            | `eth_call`                        |
| Get native balance                  | EVM        | Node            | `eth_getBalance`                  |
| Submit a transaction                | EVM        | Node (or Wallet)| `eth_sendRawTransaction`          |
| Watch contract events live          | EVM        | Node (WS)       | `eth_subscribe` logs              |
| Show wallet token balances          | EVM        | Data            | `alchemy_getTokenBalances`        |
| Show wallet NFTs                    | EVM        | Data            | `getNftsForOwner`                 |
| Transfer history for address        | EVM        | Data            | `alchemy_getAssetTransfers`       |
| Get token price                     | EVM        | Data            | `getTokenPrices`                  |
| Simulate tx before sending          | EVM        | Data            | `simulateAssetChanges`            |
| Push webhook on wallet activity     | EVM        | Data            | Address Activity Webhook          |
| Gasless tx for user                 | EVM        | Wallets         | `sendCalls` + Gas Sponsorship     |
| Batch approve + mint                | EVM        | Wallets         | `sendCalls` batch                 |
| Auto-retry stuck tx                 | EVM        | Wallets         | Automatic Retries                 |
| Solana wallet NFTs                  | Solana     | Data (DAS)      | `getAssetsByOwner`                |
| Solana real-time tx stream          | Solana     | Node            | Yellowstone gRPC                  |
| Own chain for game economy          | Any        | Rollups         | Alchemy Rollups (OP/ARB/ZK stack) |

---

## 🔑 Auth & Setup

```bash
# All Alchemy APIs use API key in URL or header
Base URL (EVM): https://{chain}.g.alchemy.com/v2/{API_KEY}
WebSocket (EVM): wss://{chain}.g.alchemy.com/v2/{API_KEY}

# Chain slugs examples:
eth-mainnet
base-mainnet
arb-mainnet
opt-mainnet
polygon-mainnet
solana-mainnet
```

---

## 📚 Solana Track (extend later)
- Solana API: JSON-RPC compatible Solana node endpoint
- Yellowstone gRPC: real-time high-performance Solana streams
- DAS API: Solana NFT discovery + metadata (replaces Metaplex)
- Solana Wallet APIs: separate flows from EVM smart wallets

---

*Skill version: 1.0 | EVM-first | Solana-aware | Built for HyperFocus Zone ecosystem*

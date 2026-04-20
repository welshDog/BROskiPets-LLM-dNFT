# ⛓️ EEPVengers Smart Contracts

Solidity contracts for the BROskiPets dNFT system.

## Quick Start

```bash
# Install Foundry (if not already)
curl -L https://foundry.paradigm.xyz | bash
foundryup

# From this directory:
forge install OpenZeppelin/openzeppelin-contracts
forge test -v

# Fuzz test (10k runs):
forge test --fuzz-runs 10000

# Static analysis:
slither . --config-file slither.config.json
```

## Contracts

### `EEPVengers.sol`
Core dNFT contract. ERC-721 with dynamic per-token metadata.

| Function | Role Required | Description |
|----------|--------------|-------------|
| `mint(to, petId, cid)` | `MINTER_ROLE` | Mint a new EEP |
| `evolve(tokenId, newCID, newStage)` | `AGENT_ROLE` | Update metadata on evolution |
| `pause()` / `unpause()` | `DEFAULT_ADMIN_ROLE` | Emergency freeze |
| `totalMinted()` | Public | How many EEPs minted so far |

### Key Design Decisions
- **MAX_SUPPLY = 78** — hardcoded, matches EEPVengers squad exactly
- **EVOLVE_COOLDOWN = 1 hour** — rate-limits agent backend, protects against compromised keys
- **AGENT_ROLE ≠ MINTER_ROLE** — separation of duties; agent can only evolve, not mint
- **evolutionStage mapping** — on-chain source of truth (1=Baby → 6=Quantum)
- **petId mapping** — links tokenId → off-chain `pet_id` (recommended canonical IDs like `001`; API also supports aliases like `spider_001`)

## Deployment (Sepolia Testnet)

```bash
forge script script/Deploy.s.sol \
  --rpc-url $SEPOLIA_RPC \
  --private-key $DEPLOYER_KEY \
  --broadcast
```

## Security
- `ReentrancyGuard` on all state-changing functions
- `Pausable` for emergency freeze
- Role-based access control (no `onlyOwner` single point of failure)
- Evolve cooldown prevents agent key compromise from corrupting all pets at once
- Run Slither before any mainnet deployment

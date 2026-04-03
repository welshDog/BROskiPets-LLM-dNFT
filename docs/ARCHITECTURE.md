# 🏗️ BROskiPets Architecture

## 4-Layer Stack

### Layer 1 — On-Chain (Polygon)
- `EEPVengers.sol` — Main dNFT contract
- `BROskiToken.sol` — ERC-20 Polygon wrapper
- `BROskiTreasury.sol` — Treasury vault
- `EEPStaking.sol` — Passive earning
- `RoyaltyVault.sol` — EIP-2981 7.8% royalty

### Layer 2 — dNFT Metadata Engine
- `agent.py` (Ollama LLM) — Per-EEP personality
- `metadata.py` — Trait updater
- Redis — Live state cache
- IPFS/Pinata — Art + metadata storage

### Layer 3 — Game Logic
- Battle Engine
- Quest System
- Squad Mechanics
- Evolution System
- Breeding (Phase 2)

### Layer 4 — Frontend + Community
- Game Dashboard
- Discord Bot
- Leaderboard
- Mobile View (dyslexic-friendly)

## Battle Formula
```
Attack Power = base_power × rarity_multiplier × (energy/100) × squad_buff
```

### Rarity Multipliers
| Rarity | Multiplier |
|---|---|
| ☁️ Common | 1.0x |
| 🟢 Uncommon | 1.5x |
| 🔵 Rare | 2.5x |
| 🟡 Legendary | 5.0x |
| ⚛️ Quantum | 10.0x |

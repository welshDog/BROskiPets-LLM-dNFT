# 🧬 BROskiPets — LLM-Powered dNFT Pet Agents
### Hyper Index // Visual Control Center // Evolution Command Deck

> **78 unique AI-native pets.** Each one has a real LLM brain, evolves on-chain, and now has a full visual upgrade system — backgrounds, auras, frames, badges, and a shop.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests: 108 passing](https://img.shields.io/badge/tests-108%20passing-brightgreen.svg)](docs/testing.md)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://python.org)
[![Solidity 0.8.24+](https://img.shields.io/badge/solidity-0.8.24%2B-purple.svg)](contracts/src/EEPVengers.sol)
[![Docker Ready](https://img.shields.io/badge/docker-ready-blue.svg)](docker-compose.yml)
[![Visual System](https://img.shields.io/badge/visual%20system-ACTIVE-brightgreen.svg)](#-visual-layer-system)
[![Shop](https://img.shields.io/badge/shop-27%20items-orange.svg)](#-shop-index)

---

## ⚡ What Is This?

BROskiPets is an open-source framework for **LLM-powered virtual pet agents** that live as **dynamic NFTs (dNFTs)** on-chain. Each pet has its own personality, memory, and needs — and now **evolves visually and on-chain** as you interact with it.

**Core properties:**

- 🧠 **LLM brain** — each pet runs on Qwen2.5:7b via Ollama, with a unique personality and Redis-backed memory
- 🔗 **Dynamic NFT** — ERC-721 contract with updatable IPFS metadata; the token URI changes on evolution
- 🐾 **78 EEPs** — the EEPVengers squad, ranging from Common to Quantum rarity
- 🎨 **Visual upgrade system** — swappable backgrounds, frames, auras, badges, all IPFS-pinned
- 🛒 **BROski$ shop** — 27 items to customise and power up your pet
- 🔒 **Security-first** — prompt injection guards, Docker isolation, role-based contract access

---

## 🗺️ System Map

> ![STATUS: ACTIVE](https://img.shields.io/badge/status-ACTIVE-brightgreen)

| Zone | What it holds | Status |
|---|---|---|
| `broski_pets/` | Core pet art folders by species | 🟢 Active |
| `backgrounds/` | Card background layers by rarity | 🟢 Active |
| `frames/` | Border / frame overlays | 🟢 Active |
| `auras/` | Glow / VFX overlays | 🟢 Active |
| `badges/` | Corner badge overlays | 🟢 Active |
| `metadata/` | Generated JSON per token | 🟢 Active |
| `contracts/` | ERC-721 smart contracts | 🟢 Active |
| `eeps/` | Full squad list and powers | 🟢 Active |
| `shop/` | Upgrade item catalogue | 🟢 Active |

---

## 🐾 Pet Index

> ![STATUS: READY](https://img.shields.io/badge/visual%20art-READY-brightgreen)

| Species | Vibe | Folder | Stage Art |
|---|---|---|---|
| Apex Dragon | Apex mythic power beast | `broski_pets/apex_dragon/` | evo1–evo5 |
| Blizzard Lizard | Ice / cold / frost tech | `broski_pets/blizzard_lizard/` | evo1–evo5 |
| Chaos Cat | Glitch / chaotic energy | `broski_pets/chaos_cat/` | evo1–evo5 |
| Cyber Fox | Fast / stealth / neon tech | `broski_pets/cyber_fox/` | evo1–evo5 |
| Eeps | Legacy prototype line | `broski_pets/eeps/` | evo1–evo5 |
| Gigabyte Guinea Pig | Cute / digital / chunky power | `broski_pets/gigabyte_guinea_pig/` | evo1–evo5 |
| Hyper Beam Bunny | Light / beam / speed | `broski_pets/hyper_beam_bunny/` | evo1–evo5 |
| Hyper Hamster | Speed / focus / tiny tank | `broski_pets/hyper_hamster/` | evo1–evo5 |
| Hyperfocus Horse | Endurance / focus / noble | `broski_pets/hyperfocus_horse/` | evo1–evo5 |
| Power Pup | Loyal / heroic / attack mode | `broski_pets/power_pup/` | evo1–evo5 |
| Sonic Spider | Precision / web / signal control | `broski_pets/sonic_spider/` | evo1–evo5 |
| Storm Hawk | Sky / strike / storm energy | `broski_pets/storm_hawk/` | evo1–evo5 |
| Super Snake | Smooth / venom / power flow | `broski_pets/super_snake/` | evo1–evo5 |
| Terra Mole | Earth / tunnel / build mode | `broski_pets/terra_mole/` | evo1–evo5 |
| Ultra Goldfish | Rare / elegant / bright power | `broski_pets/ultra_goldfish/` | evo1–evo5 |
| Welshdog | Founder / mascot / hero | `broski_pets/welshdog/` | evo1–evo5 |
| Wire Wolf | Cyber / metal / pack leader | `broski_pets/wire_wolf/` | evo1–evo5 |

---

## 🧪 Evolution Index

> ![STATUS: ACTIVE](https://img.shields.io/badge/status-ACTIVE-brightgreen)

Each pet evolves across 5 visual stages and 6 named levels.

### Stage art ladder

| File | Level | Name | XP Required | Visual energy |
|---|---|---|---|---|
| `evo1.png` | 1 | Baby | 0 | Cute, simple, clean |
| `evo2.png` | 2 | Young | 100 | Sharper edge, small tech |
| `evo3.png` | 3 | Trained | 500 | Battle-ready, stronger aura |
| `evo4.png` | 4 | Elite | 2,000 | Advanced gear, big energy |
| `evo5.png` | 5 | Legendary | 10,000 | Ornate, cinematic power |
| *(special)* | 6 | Quantum | 50,000 | Reality-bending, god-tier |

---

## 💎 Rarity Index

> ![STATUS: LIVE](https://img.shields.io/badge/status-LIVE-blue)

| Rarity | Drop chance | Count | Visual rule |
|---|---|---|---|
| Common | 50% | ~39 | Clean, readable, minimal glow |
| Uncommon | 30% | ~23 | Better highlights, more atmosphere |
| Rare | 15% | ~12 | Strong aura, bright particles |
| Legendary | 4% | 3 | Heavy glow, ornate, dramatic |
| Quantum | 1% | 2 | Space fracture, glitch light, max flex |

> Full squad: [`eeps/squad.json`](eeps/squad.json) | [`docs/EEPS-POWERS.md`](docs/EEPS-POWERS.md)

---

## 🎨 Visual Layer System

> ![STATUS: ACTIVE](https://img.shields.io/badge/status-ACTIVE-brightgreen) ![IPFS](https://img.shields.io/badge/storage-IPFS-blue)

Each card is a **stack of 5 layers**. Every layer is a separate IPFS-pinned asset. Any layer can be upgraded via the shop without reminting.

```
┌──────────────────────────┐
│  5. UI Layer             │  HUD glyphs, stat rings, XP label
│  4. Badge Layer          │  Corner emblems, founder stamps
│  3. Frame Layer          │  Card border and foil effects
│  2. Aura Layer           │  Glow, VFX, energy rings
│  1. Pet Art Layer        │  Core species image (evo1–5)
│  0. Background Layer     │  Card world behind the pet
└──────────────────────────┘
```

**Layer rules:**
- Pet art stays the hero at all times
- Background must be darker than the pet so the pet pops
- Overlays must never hide the species silhouette
- Keep all overlays readable at thumbnail size
- Quantum visuals may break symmetry — that is intentional

---

## 🌌 Background Index

> ![STATUS: PINNED](https://img.shields.io/badge/status-PINNED%20%2F%20READY-yellow)

| Asset ID | Label | Rarity | Cost (BRO$) | CID |
|---|---|---|---|---|
| `bg_common` | Lab Dark | Any | Free | TBD |
| `bg_uncommon` | Nebula Drift | Any | 400 | TBD |
| `bg_rare` | Deep Circuit | Any | 800 | TBD |
| `bg_legendary` | Cosmic Vortex | Legendary+ | 2,500 | TBD |
| `bg_quantum` | Reality Fracture | Quantum only | 5,000 | TBD |

---

## 🖼️ Frame Index

> ![STATUS: PINNED](https://img.shields.io/badge/status-PINNED%20%2F%20READY-yellow)

| Asset ID | Label | Rarity gate | Cost (BRO$) | CID |
|---|---|---|---|---|
| `frame_basic` | Basic Neon | Any | Free | TBD |
| `frame_glitch` | Glitch RGB | Any | 500 | TBD |
| `frame_holographic` | Holographic Foil | Any | 2,000 | TBD |
| `frame_quantum` | Quantum Crack | Quantum only | Free | TBD |
| `frame_welshdog` | WelshDog Celtic | Any | 9,999 | TBD |

---

## ✨ Aura Index

> ![STATUS: PINNED](https://img.shields.io/badge/status-PINNED%20%2F%20READY-yellow)

| Asset ID | Label | Cost (BRO$) | CID |
|---|---|---|---|
| `aura_none` | No Aura | Free | — |
| `aura_flame` | Flame Aura | 300 | TBD |
| `aura_electric` | Electric Crackle | 600 | TBD |
| `aura_matrix` | Matrix Code Rain | 1,000 | TBD |
| `aura_cosmic` | Cosmic Swirl | 1,500 | TBD |
| `aura_hyperfocus` | HyperFocus Pulse Rings | 2,500 | TBD |

---

## 🏅 Badge Index

> ![STATUS: LIVE](https://img.shields.io/badge/status-LIVE-blue)

| Asset ID | Label | How to get | CID |
|---|---|---|---|
| `badge_none` | No Badge | Default | — |
| `badge_broski` | BROski♾️ Holographic | OG holder (free) | TBD |
| `badge_founder` | Founder Stamp | First 100 mints | TBD |
| `badge_hyperfocus` | HyperFocus Zone Crest | Complete the course | TBD |
| `badge_welsh` | 🏴󠁧󠁢󠁷󠁬󠁳󠁠 Welsh Dragon | Special drop | TBD |
| `badge_dev_legend` | Dev Legend | 3,000 BRO$ | TBD |

---

## 🛒 Shop Index

> ![STATUS: LIVE](https://img.shields.io/badge/status-LIVE-blue) — 27 items

### Visual upgrades

| Item | Type | BRO$ cost |
|---|---|---|
| Nebula Background | background | 400 |
| Deep Circuit Background | background | 800 |
| Cosmic Vortex Background | background | 2,500 |
| Reality Fracture Background | background | 5,000 |
| Glitch RGB Frame | frame | 500 |
| Holographic Foil Frame | frame | 2,000 |
| WelshDog Celtic Frame | frame | 9,999 |
| Flame Aura | aura | 300 |
| Electric Crackle Aura | aura | 600 |
| Matrix Code Rain Aura | aura | 1,000 |
| Cosmic Swirl Aura | aura | 1,500 |
| HyperFocus Pulse Rings | aura | 2,500 |
| Dev Legend Badge | badge | 3,000 |

### Stat boosts

| Item | Effect | BRO$ cost |
|---|---|---|
| Hyper Kibble | Full hunger refill | 100 |
| Happiness Max | Max happiness instantly | 150 |
| XP Booster x2 | Double XP for 24h | 200 |
| Evolution Potion | Instant stage-up (if XP met) | 800 |
| Quantum Shard | Early Quantum unlock | 10,000 |

---

## 🔥 Prompt Forge

> ![STATUS: ACTIVE](https://img.shields.io/badge/status-ACTIVE-brightgreen)

Use this template when generating or upgrading any pet art.

```text
Ultra-detailed BROskiPets dNFT artwork of {PET_NAME},
a {RARITY} {SPECIES} in its {STAGE} stage.
Heroic 3/4 view, full body in frame, slight low angle,
futuristic HyperFocus chamber platform.
Style: cyberpunk OS + arcade card + sci-fi HUD.
Glowing rings, neon particles, volumetric fog, cinematic lighting.
Dark background with cyan, magenta and lime rim lights.
Background vibe: {BACKGROUND_STYLE}.
Frame vibe: {FRAME_STYLE}.
Aura vibe: {AURA_STYLE}.
The pet must remain instantly readable as {SPECIES}.
Ultra high resolution, crisp focus, no text blocks, no logos.
```

**Stage visual dials:**

| Stage | Keyword |
|---|---|
| Baby | cute, rounded, simple sparks |
| Young | slight tech, light aura |
| Trained | gear, strong aura |
| Elite | layered armour, conduits |
| Legendary | ornate, lightning everywhere |
| Quantum | reality fracture, glitch geometry |

---

## 🚀 Quick Start

### Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| Docker + Docker Compose | 24+ | Run the full stack |
| Python | 3.10+ | Backend dev |
| Node.js | 18+ | Contract tooling |
| Foundry | Latest | Solidity tests |

```bash
git clone https://github.com/welshDog/BROskiPets-LLM-dNFT.git
cd BROskiPets-LLM-dNFT
cp .env.example .env
docker compose up
```

Visit `http://localhost:8080` when all containers are healthy.

---

## 🧠 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROskiPets Core                          │
│  ┌─────────────────┐    ┌──────────────────┐                   │
│  │   agent.py       │    │   metadata.py     │                   │
│  │  BROskiPet class │    │  EEPMetadata      │                   │
│  │  LLM chat loop   │    │  Visual attributes│                   │
│  │  Injection guard │    │  IPFS uploader    │                   │
│  └────────┬────────┘    └────────┬─────────┘                   │
│           │                      │                              │
│  ┌────────▼──────────────────────▼─────────┐                   │
│  │              Redis (pet state)           │                   │
│  │  hunger · energy · happiness · xp        │                   │
│  │  equipped_frame · equipped_aura          │                   │
│  └─────────────────────────────────────────┘                   │
│  ┌─────────────────┐    ┌──────────────────┐                   │
│  │  Ollama (LLM)   │    │   IPFS / Pinata  │                   │
│  │  Qwen2.5:7b     │    │  Art + metadata  │                   │
│  └─────────────────┘    └──────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │  EEPVengers.sol     │
                    │  ERC-721 dNFT      │
                    │  Ethereum / Polygon │
                    └────────────────────┘
```

| Layer | Lives here | Updates |
|---|---|---|
| On-chain | Token ownership, evolution stage, IPFS CID | Per evolution |
| Redis | Hunger, energy, happiness, XP, equipped items | Per interaction |
| IPFS | Metadata JSON, art layers | Per evolution |

---

## 🧊 Asset Status Levels

| Badge | Meaning |
|---|---|
| ![DRAFT](https://img.shields.io/badge/status-DRAFT-lightgrey) | Being designed |
| ![REVIEW](https://img.shields.io/badge/status-REVIEW-yellow) | Awaiting approval |
| ![LIVE](https://img.shields.io/badge/status-LIVE-blue) | In use in metadata |
| ![PINNED](https://img.shields.io/badge/status-PINNED-orange) | Pinned to IPFS |
| ![FROZEN](https://img.shields.io/badge/status-FROZEN-red) | Locked — do not change |
| ![LEGACY](https://img.shields.io/badge/status-LEGACY-grey) | Archived old version |

---

## 🧯 Safety Rules

- Use `ipfs://` for canonical references — never HTTP-only links
- Use gateway URLs for preview and display only
- Never overwrite a frozen asset — bump the version instead
- Never change a CID without updating the registry above
- Never let a frame or aura hide the pet silhouette
- Pet art stays readable at 64×64 thumbnail size

---

## 🔐 Testing

```bash
# Python tests — no external services required
python -m pytest tests/ -v

# Solidity tests + 10k fuzz runs
cd contracts && forge test -v

# Full suite
python -m pytest tests/ -v && cd contracts && forge test
```

| Suite | Tests | Status |
|---|---|---|
| Python pytest | 108 | ✅ Passing |
| Solidity Foundry | 16 | ✅ Passing |
| Fuzz runs | 10,001 | ✅ Passing |

---

## 🗓️ Roadmap

| Year | Milestone |
|---|---|
| 2026 Q2–Q4 | Testnet launch, 78 EEPs minted, BROski$ token, visual upgrade shop live |
| 2027 | Cross-chain, EEP battling, mobile app, 1k holders |
| 2028 | Multimodal EEPs, DAO governance, 10k holders |
| 2030 | AR companion app, robot body integration |
| 2036 | Quantum-secured EEPs, brain-computer interface, 1M holders |

Full roadmap: [roadmaps/2036-vision.md](roadmaps/2036-vision.md)

---

## 🐶 Built By

**Lyndon Williams** (welshDog) — AI Agent Architect, dyslexic tinkerer, carpenter who codes. Based in South Wales 🏴󠁧󠁢󠁷󠁬󠁳󠁠

> *Hyperfocus Zone — Building tools for neurodivergent minds*

[![GitHub](https://img.shields.io/badge/GitHub-welshDog-black.svg)](https://github.com/welshDog)

---

## 📄 License

MIT — see [LICENSE](LICENSE)

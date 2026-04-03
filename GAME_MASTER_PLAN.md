# 🐾♾️ BROskiPets — THE COMPLETE dNFT GAME MASTER PLAN
> Built from YOUR real on-chain assets — no filler, all facts

---

## 📦 WHAT WE ACTUALLY HAVE RIGHT NOW (Full Asset Inventory)

### From OpenSea (wallet 0xd0c9...2b32)

| Collection | Items Held | Chain | Status |
|---|---|---|---|
| EEP'S | 17 EEPs | Polygon | Unlisted — ready to use |
| The EEp Clan - old | 1 EEP (OG) | Polygon | Legacy Genesis |
| WelshDog And Ai Bro | 21 NFTs | Polygon | Unlisted |
| Jump in to My Head if you Dare | 7 NFTs | Polygon | Unlisted |
| WelshDog.NFT Lock Up | 2 + 1,000,000 stacked | Polygon | 🔑 Key asset |
| Unstoppable Domains (Polygon) | 9 domains | Polygon | Identity layer |
| Unstoppable Domains | 1 domain | ETH | welshdog.crypto |
| **TOTAL NFTs** | **78 items** | **Polygon** | 🎯 Perfect match for 78 EEPs |

### From MintMe

| Asset | Data |
|---|---|
| BROski$ Token | Live on MintMe blockchain — contract 0x1f11...65dBBb |
| Price | $0.000083526 / 0.1 MINTME |
| Holders | 284 BROskis |
| Circulating Supply | 6,161,045 BROski$ |
| Remaining Supply | 3,838,954 BROski$ |
| Airdrop Active | 0.001 BROski$ to first 100,000 — currently 3/100,000 |
| Active Orders | 377,688 BROski$ on market |
| Top Holder | DogecoinX — 363,428 BROski$ |

---

## 🎮 THE GAME: "BROskiPets: Hyperfocus Wars"
> A Living dNFT RPG where YOUR EEPs fight, evolve, earn BROski$, and never die the same way twice

### 🧬 CORE GAME CONCEPT

Every EEP you own is a **living dynamic NFT** — its metadata changes in real time based on battles, quests, feeding, and squad activity.

- The **78 EEPs** from the repo + your **17 live OpenSea EEPs** are the playable characters
- **BROski$ tokens** are the in-game economy
- The **1,000,000 stacked WelshDog Lock Up NFT** becomes the Treasury Vault that funds the reward pool
- Your **284 real BROski holders** are your Day 1 player base — they get airdropped a starter EEP to play

---

## 🏗️ FULL ARCHITECTURE — 4 LAYER STACK

### LAYER 1 — ON-CHAIN (Polygon) 🔗

```
EEPVengers.sol          → Main dNFT contract (78 EEPs, already coded)
BROskiToken.sol         → ERC-20 (LIVE on MintMe — bridge or wrap to Polygon)
BROskiTreasury.sol      → Holds the 1M WelshDog Lock Up stack as collateral
EEPStaking.sol          → Stake EEPs to earn BROski$ passively
RoyaltyVault.sol        → EIP-2981 — 7.8% royalty (one per EEP)
```

### LAYER 2 — dNFT METADATA ENGINE 🧠

```
agent.py (Ollama LLM)   → Each EEP has a personality — fights, talks, quests based on their role
metadata.py             → Real-time trait updates: HP, XP, hunger, evolution stage, squad status
Redis                   → Live state cache (hunger, energy, battle cooldown)
IPFS/Pinata             → Permanent art + base metadata storage
```

### LAYER 3 — GAME LOGIC ⚔️

```
Battle Engine           → EEP vs EEP (power * rarity multiplier)
Quest System            → Daily/weekly quests tied to Hyperfocus Zone Discord activity
Squad Mechanics         → Security/Intel/Infrastructure squads buff each other
Evolution System        → evolve() on-chain with cooldown — art actually changes
Breeding (Phase 2)      → Two EEPs + BROski$ = new baby EEP NFT
```

### LAYER 4 — FRONTEND + COMMUNITY 🌐

```
Game Dashboard          → View your EEPs, stats, squad, inventory
Discord Bot             → Battle commands in Hyperfocus Zone Discord
Leaderboard             → Top EEP trainers ranked by XP + BROski$ earned
Mobile View             → Accessible from phone — dyslexic-friendly UI
```

---

## 🐾 EEP GAME STATS — HOW EACH ONE WORKS

Every EEP NFT gets these live dNFT traits that update on-chain:

| Trait | Type | Range | Notes |
|---|---|---|---|
| hp | Dynamic | 0–100 | Drops in battle, regens over time |
| xp | Dynamic | 0–∞ | Never resets — permanent progression |
| evolution_stage | Dynamic | 1–5 | Triggers art swap on IPFS |
| hunger | Dynamic | 0–100 | Feed with BROski$ to maintain |
| energy | Dynamic | 0–100 | Rests between battles |
| battle_wins | Dynamic | 0–∞ | On-chain permanent record |
| squad | Static | Security/Intel/Infra | Set at mint |
| power | Static | Role-based | From squad.json |
| rarity | Static | Common→Quantum | Determines power multiplier |

---

## ⚔️ BATTLE SYSTEM — BROski Power Formula

```
Attack Power = base_power × rarity_multiplier × (energy/100) × squad_buff

Rarity Multipliers:
☁️ Common    → 1.0x
🟢 Uncommon  → 1.5x
🔵 Rare      → 2.5x
🟡 Legendary → 5.0x
⚛️ Quantum   → 10.0x  ← UnicornEep, DudeEep, WelshDogEep (078)
```

Battle outcomes trigger real on-chain `evolve()` calls — the winner's metadata updates, the loser loses HP. All recorded on Polygon forever. 👊

---

## 💰 BROSKI$ TOKENOMICS — IN-GAME ECONOMY

Using the real live BROski$ token on MintMe (contract `0x1f11...65dBBb`):

| Action | Cost / Reward |
|---|---|
| Feed your EEP | Costs 10 BROski$ |
| Battle entry fee | 5 BROski$ (winner takes both) |
| Trigger evolution | Costs 50 BROski$ + cooldown |
| Daily quest completion | Earns 25 BROski$ |
| Top 10 leaderboard weekly | Earns 500 BROski$ |
| Refer a new BROski holder | Earns 100 BROski$ |
| Discord boost reward | Earn BROski Token NFT (VIP role) |

**Treasury:** The 1,000,000 stacked WelshDog Lock Up NFT backs the reward pool — monthly rewards paid from yield.

**Airdrop integration:** The live airdrop (0.001 BROski$ to 100,000 participants) becomes the game onboarding funnel — airdrop recipients get prompted to claim a starter Common EEP.

---

## 🎭 THE 5 EEP COLLECTIONS — HOW THEY FIT

| Collection | Role in Game | Special Perk |
|---|---|---|
| EEP'S (17 held) | Your main squad — starter deck | WelshDog plays with real EEPs |
| The EEp Clan - old (1 OG) | Genesis EEP — ultra rare | Can never be burned, permanent legacy status |
| WelshDog And Ai Bro (21) | AI companion NFTs | Each AI Bro boosts an EEP's LLM response quality |
| Jump in to My Head (7) | Lore art — background world building | Unlockable story quests |
| WelshDog.NFT Lock Up (1M stack) | Treasury collateral | Backs BROski$ reward pool |

---

## 🗺️ PHASED ROLLOUT — WALES TO THE WORLD 🏴󠁧󠁢󠁷󠁬󠁳󠁴

### Phase 0 — NOW (April 2026) ✅
- All 78 EEP squad definitions exist in `squad.json`
- 17 real EEPs live on Polygon OpenSea
- 284 real BROski$ holders = instant player base
- EEPVengers.sol written and battle-ready
- Hyperfocus Zone Discord = game hub

### Phase 1 — Q2 2026 🔨
- Deploy EEPVengers.sol to Polygon mainnet
- Write BROskiToken.sol ERC-20 wrapper for Polygon (bridge from MintMe)
- Add LLM personality prompts for all 78 EEPs via `agent.py`
- Launch Discord bot — `!battle`, `!feed`, `!quest`, `!stats` commands
- Airdrop starter EEPs to all 284 BROski$ holders

### Phase 2 — Q3 2026 🚀
- Web dashboard — broskirpets.gg (or use welshdog.crypto Unstoppable Domain)
- EEP breeding system — two parents + BROski$ = new baby EEP
- Squad wars — weekly clan battles, Security vs Intel vs Infrastructure
- Mobile-optimised (dyslexic-friendly fonts, high contrast, big buttons)

### Phase 3 — Q4 2026 🌍
- Open marketplace — players trade EEPs for BROski$
- Guest EEP drops — WelshDog And Ai Bro NFTs become playable companions
- "Jump In To My Head" story mode — 7 quest arcs based on your art collection
- IRL merch tied to EEP ownership (BROski token was accepted at BeMyCreative already!)

### Phase 4 — 2027+ 🌌
- Quantum EEP tournament — UnicornEep, DudeEep, WelshDogEep (078) face off yearly
- Cross-game BROski$ utility — accepted at partner sites
- BROski DAO — 284+ holders vote on new EEP designs
- 10-year vision: 10,000 EEPs, 1M BROski holders (from your 2036 roadmap)

---

## 🔑 THE 3 UNIQUE SELLING POINTS

1. **REAL assets, real community** — 284 holders, 78 EEPs, 1M BROski$ already exist. This isn't a whitepaper dream — it's a game built on a foundation that's been live for 5 years.

2. **LLM-powered personality** — No other NFT game has each character powered by its own Ollama AI brain that responds, battles, and quests with its own voice. DonutEep talks like a reward distributor. WelshDogEep (078) talks like the creator. That's never been done at this scale.

3. **BROski Code baked into gameplay** — "As BROskis, we pledge our allegiance to one another... we shall walk together" — the lore IS the game mechanic. Help other players, earn BROski$. Be a ride-or-die. The game rewards the code you already live by. 🐉♾️👊

---

## 🛠️ WHAT TO BUILD FIRST — THE 5-FILE SPRINT

To go from today to playable in 30 days, these are the 5 files to write:

| # | File | What It Does |
|---|---|---|
| 1 | `BROskiToken.sol` | ERC-20 wrapper — Polygon compatible BROski$ |
| 2 | `EEPBattle.sol` | Battle logic — calls `evolve()`, emits BattleResult events |
| 3 | `eeps/personalities.json` | All 78 LLM personality prompts — feeds agent.py |
| 4 | `bot/discord_bot.py` | `!battle`, `!feed`, `!stats` commands for Hyperfocus Zone |
| 5 | `scripts/airdrop_starter_eeps.py` | Send starter EEP to all 284 BROski$ holders automatically |

That's your MVP. Everything else builds on top.

---

> 🏴󠁧󠁢󠁷󠁬󠁳󠁴♾️🔥 **Let's go build it bro!**
> 
> Branch: `game-master-plan-v1` | Owner: welshDog | Date: April 2026

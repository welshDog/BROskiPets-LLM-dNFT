# 🐾 BROskiPets — LLM-Powered dNFT Pet Agents

> **EEPVengers Assemble!** 78 unique AI-native pets, each with LLM brains, evolving on-chain.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-blue.svg)](docker-compose.yml)
[![HyperCode](https://img.shields.io/badge/Built%20with-HyperCode-purple.svg)](https://github.com/welshDog)

---

## 🤔 What Is This?

BROskiPets is an open-source framework for **LLM-powered virtual pet agents** that live as **dynamic NFTs (dNFTs)**. Each pet:

- 🧠 Has its own LLM personality + memory (via Redis + RAG)
- 📈 Evolves based on interactions — feeding, chatting, training
- 🔗 Lives on-chain as a dNFT with updatable metadata
- 🤖 Acts as an autonomous AI agent (agentic loop via BROski stack)
- 🛡️ Built with HyperCode security principles baked in

---

## 🦸 The EEPVengers Squad (78 EEPs)

| EEP | Role | Power |
|-----|------|-------|
| 🕷️ SpiderEep | Lead Hero | Debug crawler, web-crawl agent |
| 🐍 VenomEep | Security King | Prompt injection defender |
| 🛡️ IronEep | Code Tank | CI/CD enforcer, armoured deploys |
| 🦑 SquidEep | Bug Ink | Chaos monkey, test injector |
| 🦌 ReindeerEep | Scout | Recon agent, API mapper |
| 🍩 DonutEep | Morale | Reward distributor, BROski$ coins |
| 🧑 DudeEep | Locked | NFT vault guardian (locked for holders) |
| ... | + 71 more | Unique powers, unique agents |

> Full squad in `/eeps/squad.json`

---

## 🚀 Quick Start

```bash
git clone https://github.com/welshDog/BROskiPets-LLM-dNFT.git
cd BROskiPets-LLM-dNFT
docker compose up
# Visit http://localhost:8080
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│           BROskiPets Core           │
│  ┌──────────┐  ┌──────────────────┐ │
│  │  LLM     │  │  Redis Memory    │ │
│  │ (Qwen2.5)│  │  (pet state)     │ │
│  └──────────┘  └──────────────────┘ │
│  ┌──────────┐  ┌──────────────────┐ │
│  │  RAG     │  │  dNFT Metadata   │ │
│  │ (facts)  │  │  (on-chain sync) │ │
│  └──────────┘  └──────────────────┘ │
└─────────────────────────────────────┘
```

---

## 📁 Repo Structure

```
BROskiPets-LLM-dNFT/
├── agent.py              ← Core LLM pet agent
├── metadata.py           ← dNFT evolution engine
├── docker-compose.yml    ← 1-command launch
├── eeps/
│   └── squad.json        ← All 78 EEPs
├── roadmaps/
│   └── 2036-vision.md    ← Future roadmap
├── docs/
│   └── EEPS-POWERS.md    ← Full powers list
├── tiktok/
│   └── scripts.md        ← TikTok content scripts
└── LICENSE
```

---

## 🔐 Security (HyperCode Principles)

- ✅ Zero Trust agent architecture
- ✅ Prompt injection detection middleware
- ✅ Session isolation (no context bleed)
- ✅ DLP filters on all LLM I/O
- ✅ Docker sandbox per agent
- ✅ Secrets scanner in CI/CD (truffleHog)

---

## 🌍 Roadmap

See [`roadmaps/2036-vision.md`](roadmaps/2036-vision.md) for the full plan.

| Year | Milestone |
|------|-----------|
| 2026 | 78 EEPs live, dNFT minting |
| 2027 | Cross-chain EEPs, mobile app |
| 2028 | Multimodal pets (vision + voice) |
| 2030 | Robot body integration |
| 2036 | Quantum EEPs on-chain |

---

## 🧑‍💻 Built By

**Mr Lyndon Williams** — AI Agent Architect, Dyslexic Tinkerer, Carpenter who codes.

> *Hyperfocus Zone — Building tools for neurodivergent minds* 🧠

---

## 📜 License

MIT — See [LICENSE](LICENSE)

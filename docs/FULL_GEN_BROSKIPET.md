# 🐾 Full Gen BROskiPet — HuggingFace Playbook

> Run this every time you want to generate, style, animate and prep a new BROskiPet NFT asset.
> All steps use HuggingFace Spaces via MCP tools or direct browser links.

---

## ⚡ Quick Reference — Seeds to Recreate

| Asset | Seed |
|-------|------|
| Original Cyber Wolf BROskiPet | `157069` |
| Anime Neon Edit | `1423238280` |
| Multi-Angle Side Profile | `1272794535` |

---

## 🗺️ Full Step-by-Step Pipeline

### ✅ Step 1 — Generate Base BROskiPet
**Tool:** `mcp-tools/z-image-turbo` (or FLUX.1 Krea for higher quality)

**Prompt used:**
```
A futuristic cyber wolf mascot, HyperCode themed, glowing neon blue and purple
circuit board fur patterns, holographic rainbow mane, golden crown with circuit
traces, glowing cyan eyes, floating digital code particles around it, dark
background with deep space and neon grid lines, ultra detailed, vibrant,
NFT art style, hyper stylized, professional digital art
```

**Settings:**
- Resolution: `1024x1024 (1:1)`
- Steps: `8`
- Random seed: `true`

**Direct HF Link:** https://huggingface.co/spaces/mcp-tools/FLUX.1-Krea-dev

---

### ✅ Step 2 — Remove Background
**Tool:** `not-lain/background-removal`

**How:**
- Pass the image URL from Step 1
- Returns transparent PNG — perfect for NFT layering

**If Space is down → use:** https://remove.bg (free, instant)

**Direct HF Link:** https://huggingface.co/spaces/not-lain/background-removal

---

### ✅ Step 3 — Anime / Neon Style Edit
**Tool:** `prithivMLmods/Qwen-Image-Edit-2509-LoRAs-Fast`

**Settings:**
- `lora_adapter`: `Photo-to-Anime`
- `steps`: `4`
- `randomize_seed`: `true`

**Prompt used:**
```
Convert to vibrant anime style with neon glowing outlines, electric blue and
purple neon lighting, hyper detailed anime fur, glowing cyber eyes, neon circuit
patterns, dark atmospheric background
```

**Other LoRA options to try:**
| LoRA | Effect |
|------|--------|
| `Photo-to-Anime` | Full anime conversion |
| `Relight` | Dramatic lighting changes |
| `Dotted-Illustration` | Pop art / comic style |
| `Upscale2K` | High resolution upscale |
| `Next-Scene` | Background scene change |

**Direct HF Link:** https://huggingface.co/spaces/prithivMLmods/Qwen-Image-Edit-2509-LoRAs-Fast

---

### ✅ Step 4 — BROski Voice / TTS
**Tool:** `ResembleAI/Chatterbox`

**BROski Script:**
```
Yo! What is UP BROski! Welcome to HyperCode — the world's first
neurodivergent-first AI infrastructure platform! We built the future
that people keep saying they want. And we actually did it. Let's GO!
```

**Settings:**
- `exaggeration`: `0.8` (hype energy 🔥)
- `temperature`: `0.9` (natural variety)
- `cfgw`: `0.5`
- Optional: upload a reference audio to clone a voice style

**Direct HF Link:** https://huggingface.co/spaces/ResembleAI/Chatterbox

---

### ✅ Step 5 — Multi-Angle Views
**Tool:** `prithivMLmods/Qwen-Image-Edit-2509-LoRAs-Fast`

**Settings:**
- `lora_adapter`: `Multiple-Angles`
- `steps`: `4`
- `randomize_seed`: `true`

**Prompt used:**
```
Show the HyperCode cyber wolf BROskiPet from a side profile angle,
keeping all neon circuit fur, glowing cyan eyes, golden crown and
holographic mane exactly the same
```

**Angle ideas to try:**
- Side profile
- Top-down bird's eye
- Low angle hero shot
- Front face close-up

---

### ✅ Step 6 — Pet Animation Clip
**Tool:** `zerogpu-aoti/wan2-2-fp8da-aoti-faster`

> ⚠️ Requires ZeroGPU quota. Free quota = limited per day.
> Subscribe to HF PRO for 25 min/day: https://huggingface.co/subscribe/pro

**Settings:**
- `duration_seconds`: `3.5`
- `steps`: `6`
- `randomize_seed`: `true`

**Prompt used:**
```
The cyber wolf comes alive, glowing neon circuit fur pulses with electric
blue and purple energy, holographic mane flows like aurora borealis,
golden crown shimmers, glowing cyan eyes blink and scan the horizon,
digital code particles swirl around the wolf, cinematic slow motion,
dramatic lighting, epic NFT animation
```

**Direct HF Link:** https://huggingface.co/spaces/zerogpu-aoti/wan2-2-fp8da-aoti-faster

---

### ✅ Step 7 — OCR Test / Document Extraction
**Tool:** `mcp-tools/DeepSeek-OCR-experimental`

**Settings:**
- `model_size`: `Gundam (Recommended)`
- `task_type`: choose based on use case:

| Task Type | When to Use |
|-----------|-------------|
| `Free OCR` | Extract text from error screenshots |
| `Convert to Markdown` | Turn docs/diagrams into Markdown for agents |
| `Parse Figure` | Analyse Grafana/architecture screenshots |
| `Locate Object by Reference` | Find specific elements in complex screenshots |

**HyperCode Power Moves:**
- Screenshot a Prometheus alert → OCR → feed into HyperAgent
- Scan a PDF doc → Convert to Markdown → load into RAG pipeline
- Screenshot a terminal error → Free OCR → auto-debug with agents

**Direct HF Link:** https://huggingface.co/spaces/mcp-tools/DeepSeek-OCR-experimental

---

## 🔥 Full Pipeline Summary

```
Generate → Remove BG → Style Edit → TTS Voice → Multi-Angle → Animate → OCR
   1            2            3            4             5           6       7
```

## 📋 All HuggingFace Spaces Used

| Space | Category | Link |
|-------|----------|------|
| FLUX.1 Krea Dev | Image Gen | https://huggingface.co/spaces/mcp-tools/FLUX.1-Krea-dev |
| Background Removal | BG Remove | https://huggingface.co/spaces/not-lain/background-removal |
| Qwen-Image-Edit LoRAs | Image Edit | https://huggingface.co/spaces/prithivMLmods/Qwen-Image-Edit-2509-LoRAs-Fast |
| Chatterbox TTS | Voice | https://huggingface.co/spaces/ResembleAI/Chatterbox |
| Wan2.2 Video | Animation | https://huggingface.co/spaces/zerogpu-aoti/wan2-2-fp8da-aoti-faster |
| DeepSeek OCR | Text Extract | https://huggingface.co/spaces/mcp-tools/DeepSeek-OCR-experimental |

---

*Generated during HyperCode build session — May 6, 2026* 🚀
*BROski♾ — Built by welshDog @ Hyperfocus Zone, S.Wales*

# 📡 BROskiPets — Full Pinata IPFS Audit Report
> Master IPFS infrastructure report for BROski Brain.
> All 5 Pinata groups. Every asset category. Every risk and next move.
> Last audited: May 2026 — HyperFocus Zone ♾️

---

## 🗂️ Group Overview

| Group Name | Group ID | Created | Asset Type | Status |
|---|---|---|---|---|
| `BROski_pets_dNFTs` | `2aedcf70-d4bb-4e13-94c9-ef6098d49aca` | 5/7/2026 | Pet mint metadata + baby art | ✅ LIVE — mixed bucket |
| `BROski_OG_EEPs_dNFTs` | `b4e17293-b3ef-4739-9a7a-cf6b71fb5724` | 5/10/2026 | Original EEP animated GIFs + JPGs | ✅ LIVE — 10 assets |
| `BROski_Dark_EEPs_dNFTs` | `cec7d61c-6d9b-410a-8db9-17489b40bd41` | 5/10/2026 | Horror villain animated GIFs | ✅ LIVE — 7 assets |
| `BROski_EEPVENGERS_dNFTs` | `e829dd09-64ff-4e60-a3b6-83825a89525e` | 5/10/2026 | Superhero animated GIFs | ✅ LIVE — 10 assets |
| `BROski_Token_dNFT` | `57d6e6bb-8587-4d67-b567-5ce5c9c9752b` | 5/10/2026 | BROski$ token art | ⚠️ Not yet audited |

**IPFS Gateway:** `aqua-few-dolphin-310.mypinata.cloud`

---

## 🐉 Group 1: BROski_pets_dNFTs

**Group ID:** `2aedcf70-d4bb-4e13-94c9-ef6098d49aca`
**Role:** Primary production bucket — mint metadata + seed baby art

### What's inside

**Numbered mint metadata (production):**
- `002_mint.json` through `078_mint.json` — sequential batch
- Created: 5/9/2026
- Size: ~1.03–1.06 KB each
- These are live minted token metadata files

**Named baby species metadata + images (seed wave):**

| Species | Metadata | Image |
|---|---|---|
| Apex Dragon | `Apex Dragon — Baby metadata` | `Apex Dragon — Baby image` |
| Blizzard Lizard | `Blizzard Lizard — Baby metadata` | `Blizzard Lizard — Baby image` |
| Chaos Cat | `Chaos Cat — Baby metadata` | `Chaos Cat — Baby image` |
| Cyber Fox | `Cyber Fox — Baby metadata` | `Cyber Fox — Baby image` |
| Gigabyte Guinea Pig | `Gigabyte Guinea Pig — Baby metadata` | `Gigabyte Guinea Pig — Baby image` |
| Hyper Beam Bunny | `Hyper Beam Bunny — Baby metadata` | `Hyper Beam Bunny — Baby image` |
| Hyper Hamster | `Hyper Hamster — Baby metadata` | `Hyper Hamster — Baby image` |
| Hyperfocus Horse | `Hyperfocus Horse — Baby metadata` | `Hyperfocus Horse — Baby image` |
| Power Pup | `Power Pup — Baby metadata` | `Power Pup — Baby image` |
| Sonic Spider | `Sonic Spider — Baby metadata` | `Sonic Spider — Baby image` |

**Alias/duplicate files present:**
- `cyber_fox_baby.json`
- `cyber_fox_evo1.png`

**Test artifact present:**
- `jwt-scope-probe` (1 B — can be deleted)

### ⚠️ Risks
- Mixed-use bucket: mint metadata + media + test files all together
- Alias naming (`cyber_fox_baby.json` vs `Cyber Fox — Baby metadata`) creates ambiguity
- Test artifact should not be in production

### ✅ Next moves
1. Export all filenames + CIDs to master inventory
2. Map each numbered mint JSON to its species/token ID
3. Delete `jwt-scope-probe`
4. Standardise naming convention going forward
5. Upload remaining 6 species baby images (Terra Mole, Ultra Goldfish, WelshDog, Wire Wolf, Storm Hawk, Super Snake)
6. Upload evo2–evo6 art as generated

---

## 🐾 Group 2: BROski_OG_EEPs_dNFTs

**Group ID:** `b4e17293-b3ef-4739-9a7a-cf6b71fb5724`
**Role:** Original canonical EEP character collection

### Full asset roster

| # | Filename | Size | Format | Character |
|---|---|---|---|---|
| 1 | `TomEEP.gif` | 8.90 MB | 🎬 Animated | Tom (Tom & Jerry) |
| 2 | `SlaughterEEp.gif` | 7.39 MB | 🎬 Animated | Slaughter EEP |
| 3 | `RudolphEEp.gif` | 7.45 MB | 🎬 Animated | Rudolph EEP |
| 4 | `Rov3rEEP.jpg` | 68 KB | 🖼️ Static | Rover EEP |
| 5 | `MuskEEp.gif` | 10.70 MB | 🎬 Animated | Elon Musk EEP |
| 6 | `LuckyEEP.gif` | 3.60 MB | 🎬 Animated | Lucky EEP |
| 7 | `LollyEEP.jpg` | 70 KB | 🖼️ Static | Lolly EEP |
| 8 | `Laszer_EyeEEp.gif` | 8.39 MB | 🎬 Animated | Laser Eye EEP |
| 9 | `INVISIBLEEP.gif` | 2.81 MB | 🎬 Animated | Invisible EEP |
| 10 | `HoudiniEEp.gif` | 4.75 MB | 🎬 Animated | Houdini EEP |

**Total: 10 assets | 8 animated GIF | 2 static JPG**

### ⚠️ Notes
- 2 static JPGs (`Rov3rEEP.jpg`, `LollyEEP.jpg`) are significantly smaller than the GIFs — confirm if these are final art or placeholders
- `MuskEEp.gif` at 10.70 MB is the largest in this group

### ✅ Next moves
1. Grab CIDs for all 10 via Pinata API script
2. Wire CIDs into Supabase `eep_assets` table
3. Confirm if static JPGs need upgrading to animated GIFs
4. Add metadata JSON for each OG EEP

---

## 🌑 Group 3: BROski_Dark_EEPs_dNFTs

**Group ID:** `cec7d61c-6d9b-410a-8db9-17489b40bd41`
**Role:** Horror villain EEP corruption forms — Dark EEP collection

### Full asset roster

| # | Filename | Size | Format | Horror Villain |
|---|---|---|---|---|
| 1 | `VoorhEEp.gif` | 29 MB | 🎬 Animated | Jason Voorhees |
| 2 | `Squid_Games.gif` | 5.78 MB | 🎬 Animated | Squid Game Guard |
| 3 | `Slendeep.gif` | 6.15 MB | 🎬 Animated | Slender Man |
| 4 | `PennyEEPwise.gif` | 22 MB | 🎬 Animated | Pennywise |
| 5 | `Jokeep.gif` | 5.96 MB | 🎬 Animated | The Joker |
| 6 | `fredEEP_krueger.gif` | 18.72 MB | 🎬 Animated | Freddy Krueger |
| 7 | `Eeple_juice.gif` | 14.67 MB | 🎬 Animated | Beetlejuice |

**Total: 7 assets | All animated GIF**

### ⚠️ Notes
- `VoorhEEp.gif` at 29 MB is the largest single asset in the entire ecosystem — consider compression or optimisation for web delivery
- `PennyEEPwise.gif` at 22 MB and `fredEEP_krueger.gif` at 18.72 MB are also large — same consideration
- These are currently horror/villain themed rather than the abstract burnout variants described in COMPENDIUM.md — lore update needed

### ✅ Next moves
1. Compress GIFs over 15 MB for faster IPFS loading
2. Update COMPENDIUM.md to reflect real villain Dark EEP roster
3. Add metadata JSON for each Dark EEP
4. Define redemption path mechanics per villain form

---

## ⚡ Group 4: BROski_EEPVENGERS_dNFTs

**Group ID:** `e829dd09-64ff-4e60-a3b6-83825a89525e`
**Role:** Superhero EEP forms — the EEPVengers squad collection

### Full asset roster

| # | Filename | Size | Format | Superhero |
|---|---|---|---|---|
| 1 | `WOLVEREEP.gif` | 5.65 MB | 🎬 Animated | Wolverine |
| 2 | `VemonEEp.gif` | 12.30 MB | 🎬 Animated | Venom |
| 3 | `THOREEP.gif` | 4.60 MB | 🎬 Animated | Thor |
| 4 | `SuperEEP.gif` | 3.61 MB | 🎬 Animated | Superman |
| 5 | `SpiderEEP.gif` | 5.87 MB | 🎬 Animated | Spider-Man |
| 6 | `MystquEEP.gif` | 10.57 MB | 🎬 Animated | Mystique |
| 7 | `IRONEEP.gif` | 5.64 MB | 🎬 Animated | Iron Man |
| 8 | `HULKEEP.gif` | 3.19 MB | 🎬 Animated | Hulk |
| 9 | `FlashEEP.gif` | 4.10 MB | 🎬 Animated | The Flash |
| 10 | `DEAD_EEP_PooL.gif` | 4.04 MB | 🎬 Animated | Deadpool |

**Total: 10 assets | All animated GIF**

### ⚠️ Notes
- This is a **separate collection** from the BROskiPets species — EEPVengers are their own superhero EEP line
- `VemonEEp.gif` at 12.30 MB and `MystquEEP.gif` at 10.57 MB are the largest here
- The abstract EEPVengers squad described in COMPENDIUM.md (APEX, PACKMASTER etc) refers to the BROskiPets species squads — these are a separate superhero-themed EEP drop

### ✅ Next moves
1. Add metadata JSON for each EEPVenger
2. Wire into Supabase with `collection_type: eepvengers`
3. Update COMPENDIUM.md to clarify EEPVengers (superhero EEP collection) vs EEPVengers squad (pet species team)
4. Consider: are Dark EEPs and EEPVengers the villain/hero counterparts of the same characters?

---

## 💰 Group 5: BROski_Token_dNFT

**Group ID:** `57d6e6bb-8587-4d67-b567-5ce5c9c9752b`
**Role:** BROski$ token art and currency visuals
**Status:** ⚠️ Not yet fully audited — open this group to see contents

### ✅ Next moves
1. Open group in Pinata and audit contents
2. Confirm what token art exists (coin, badge, currency icon)
3. Wire CIDs to Supabase `broski_tokens` table

---

## 📊 Full Ecosystem Asset Count

| Collection | Assets | Formats | Status |
|---|---|---|---|
| BROski Pets (baby seed wave) | 10 species × metadata + image | JSON + images | ✅ Baby stage live |
| BROski Pets (mint series) | ~76 numbered JSONs (002–078) | JSON | ✅ Metadata minted |
| OG EEPs | 10 | 8 GIF + 2 JPG | ✅ Live |
| Dark EEPs | 7 | All GIF | ✅ Live |
| EEPVengers | 10 | All GIF | ✅ Live |
| Token dNFT | Unknown | TBC | ⚠️ Audit needed |
| **TOTAL CONFIRMED** | **27 EEP GIFs + ~76 mint JSONs + 10 baby art pairs** | Mixed | **LIVE** |

---

## 🛠️ Master Action List

### 🔴 Urgent (do first)
- [ ] Open `BROski_Token_dNFT` group and audit contents
- [ ] Click into any numbered mint JSON (e.g. `069_mint.json`) and share contents so we know what image URL it points to
- [ ] Delete `jwt-scope-probe` from `BROski_pets_dNFTs`

### 🟡 Important (do next)
- [ ] Run Pinata API script to export all CIDs for all 5 groups into `pinata_cid_inventory.json`
- [ ] Wire all 27 EEP GIF CIDs into Supabase
- [ ] Compress GIFs over 15 MB (VoorhEEp, PennyEEPwise, fredEEP_krueger)
- [ ] Update COMPENDIUM.md Dark EEPs and EEPVengers sections with real rosters

### 🟢 Next (art pipeline)
- [ ] Generate evo1–evo6 images for remaining 6 species (Terra Mole, Ultra Goldfish, WelshDog, Wire Wolf, Storm Hawk, Super Snake)
- [ ] Upload to `BROski_pets_dNFTs` and update numbered mint JSONs with real CIDs
- [ ] Add metadata JSON for all OG EEPs and EEPVengers

---

## 🔧 Pinata API Script

Run this to auto-export all CIDs from all 5 groups:

```python
# pinata_cid_export.py
# Auto-grabs all file CIDs from all 5 BROskiPets Pinata groups
# Outputs: pinata_cid_inventory.json

import requests
import json
import os

PINATA_JWT = os.environ.get("PINATA_JWT")  # Set in your .env

GROUPS = {
    "BROski_pets_dNFTs":      "2aedcf70-d4bb-4e13-94c9-ef6098d49aca",
    "BROski_OG_EEPs_dNFTs":   "b4e17293-b3ef-4739-9a7a-cf6b71fb5724",
    "BROski_Dark_EEPs_dNFTs": "cec7d61c-6d9b-410a-8db9-17489b40bd41",
    "BROski_EEPVENGERS_dNFTs":"e829dd09-64ff-4e60-a3b6-83825a89525e",
    "BROski_Token_dNFT":      "57d6e6bb-8587-4d67-b567-5ce5c9c9752b",
}

GATEWAY = "https://aqua-few-dolphin-310.mypinata.cloud/ipfs"
HEADERS = {"Authorization": f"Bearer {PINATA_JWT}"}

inventory = {}

for group_name, group_id in GROUPS.items():
    print(f"\n📡 Fetching: {group_name}")
    url = f"https://api.pinata.cloud/data/pinList?groupId={group_id}&status=pinned&pageLimit=1000"
    res = requests.get(url, headers=HEADERS)
    data = res.json()
    files = data.get("rows", [])
    inventory[group_name] = []
    for f in files:
        cid = f["ipfs_pin_hash"]
        name = f["metadata"]["name"]
        size = f["size"]
        entry = {
            "name": name,
            "cid": cid,
            "size_bytes": size,
            "ipfs_url": f"{GATEWAY}/{cid}",
            "pinata_url": f"https://gateway.pinata.cloud/ipfs/{cid}"
        }
        inventory[group_name].append(entry)
        print(f"  ✅ {name} → {cid}")

with open("pinata_cid_inventory.json", "w") as out:
    json.dump(inventory, out, indent=2)

print("\n🎉 Done! Saved to pinata_cid_inventory.json")
print(f"Total groups: {len(inventory)}")
print(f"Total files: {sum(len(v) for v in inventory.values())}")
```

**Run with:**
```bash
export PINATA_JWT=your_jwt_here
python pinata_cid_export.py
```

Then hand the `pinata_cid_inventory.json` to the Supabase wiring script.

---

## 🗃️ Gateway URLs Format

All IPFS assets use this format:
```
https://aqua-few-dolphin-310.mypinata.cloud/ipfs/{CID}
```

Or via public Pinata gateway:
```
https://gateway.pinata.cloud/ipfs/{CID}
```

---
*BROskiPets Pinata IPFS Audit — May 2026*
*Maintained by BROski Brain | HyperFocus Zone ♾️ 🏴󠁧󠁢󠁷󠁬󠁳󠁠*

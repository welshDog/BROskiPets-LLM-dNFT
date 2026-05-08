---
name: pinata-ipfs-pin
description: Pinata IPFS pinning for BROskiPets — folder pins for EEP images (EEPVengers/{pet_id}/{stage}.png), metadata JSON pins, JWT auth, IMAGES_ROOT_CID. Use when the user says "pin to IPFS", "Pinata 403", "upload images", "IMAGES_ROOT_CID", "metadata 404", "tokenURI not resolving", or before calling evolve().
---

# pinata-ipfs-pin

IPFS via Pinata. Two pin types: the **image folder** (one-time, then `IMAGES_ROOT_CID` is fixed) and **metadata JSON** (per-evolution).

## The Folder Structure (image pin — done once)

```
EEPVengers/
├── 001/
│   ├── baby.png
│   ├── young.png
│   ├── trained.png
│   ├── elite.png
│   ├── legendary.png
│   └── quantum.png
├── 002/
│   └── ...
...
└── 078/
    └── quantum.png
```

**Stages must be lowercase** — `baby young trained elite legendary quantum`. The contract reads stage names case-sensitively.

After pinning the folder, set:

```env
IMAGES_ROOT_CID=Qm...    # the CID returned by Pinata
```

Image URIs then resolve as:

```
ipfs://{IMAGES_ROOT_CID}/EEPVengers/{pet_id}/{stage}.png
```

## Pin via Pinata Web UI (one-shot, easiest for the folder)

1. Go to `https://app.pinata.cloud/pinmanager`
2. Click **Upload → Folder**
3. Select `EEPVengers/`
4. Wait for upload (78 pets × 6 stages = 468 files; 5–15 mins depending on speed)
5. Copy the resulting CID
6. Update `.env IMAGES_ROOT_CID=<that CID>`
7. Restart the API container so it re-reads `.env`:
   ```powershell
   docker compose restart api
   ```

## Pin via API (programmatic — for metadata JSON, per-evolve)

```python
import os, requests, json

PINATA_JWT = os.environ['PINATA_JWT']
PINATA_API = 'https://api.pinata.cloud/pinning/pinJSONToIPFS'

def pin_metadata(metadata: dict) -> str:
    """Pin a metadata JSON to Pinata. Returns the CID."""
    response = requests.post(
        PINATA_API,
        headers={
            'Authorization': f'Bearer {PINATA_JWT}',
            'Content-Type':  'application/json',
        },
        json={
            'pinataContent':  metadata,
            'pinataMetadata': {'name': f'EEP_{metadata.get("name","unknown")}'},
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()['IpfsHash']
```

Returned CID → use as `tokenURI`:

```python
new_uri = f"ipfs://{cid}"
contract.functions.evolve(token_id, new_uri).transact(...)
```

## Required Env

```env
PINATA_JWT=eyJhbGciOiJIUzI1...   # full JWT from Pinata dashboard
IMAGES_ROOT_CID=Qm...             # set after one-time folder pin
```

## Common Failures

| Symptom | Cause | Fix |
|---|---|---|
| `403 Forbidden` from Pinata | `PINATA_JWT` missing in container | Confirm `env_file: .env` in compose, restart container |
| `403 Forbidden` even with JWT | JWT revoked or expired | Generate a new JWT in Pinata dashboard, update `.env` |
| Pin succeeds but `ipfs://` URL 404s | Public IPFS gateways take a few mins to propagate | Wait 1–2 mins, or use Pinata's dedicated gateway |
| Image not showing in wallet | `IMAGES_ROOT_CID` not set, or wrong path | Check `.env`, confirm path is `EEPVengers/{id}/{stage}.png` |
| `429 Too Many Requests` | Free tier rate limit | Add backoff, or upgrade Pinata plan |
| `pinata-api: invalid request body` | JSON not serializable, or missing `pinataContent` | Check the request body shape (above pattern) |
| Folder upload fails partway | Network drop, large folder | Retry — Pinata dedupes by content hash, so existing files won't re-upload |
| Wrong CID in `.env` after re-pin | New folder upload created a new CID (content changed) | This is correct — every change → new CID; only update `IMAGES_ROOT_CID` if content is the canonical |

## Verify a Pin Resolves

```powershell
# Public gateway (slow first hit, then cached)
curl https://ipfs.io/ipfs/<CID>

# Pinata's dedicated gateway (faster, requires gateway URL from dashboard)
curl https://<your-gateway>.mypinata.cloud/ipfs/<CID>

# Metadata for a token
$tokenURI = cast call $env:CONTRACT_ADDRESS "tokenURI(uint256)(string)" 1 --rpc-url $env:SEPOLIA_RPC
# Returns ipfs://Qm... — fetch via gateway
```

## When To Re-Pin

- **Folder pin (images):** only when art changes. New CID → update `IMAGES_ROOT_CID`.
- **Metadata pin:** every evolution. Pin new JSON → set new `tokenURI`.

The contract emits a `MetadataUpdate(tokenId)` event on `evolve()` so wallets refresh — but the IPFS CID must be valid and resolvable when wallets check.

## Cost / Quotas (Pinata free tier)

- 1 GB storage free
- 100k API requests/month
- 78 pets × 6 stages × ~200KB each = ~94 MB images
- Metadata JSON ~2 KB each — negligible

If approaching the limit, upgrade or switch to a different pinning service (Web3.Storage, Filebase).

## Companion Skills

- `dnft-evolve-flow` — the per-evolution metadata pin happens here
- `sepolia-ops` — `tokenURI` is read via `cast`
- `eep-mint-batch` — initial mint sets `tokenURI` to the `baby` stage URI

## Hard Rules

- **Stages are lowercase** — `baby young trained elite legendary quantum`
- **Pin metadata BEFORE calling `evolve()`** — never set `tokenURI` to a CID that doesn't resolve yet
- **NEVER expose `PINATA_JWT`** to the browser — server-side only
- **`IMAGES_ROOT_CID` is sticky** — once set, only change it if you re-pin the entire folder
- **Folder uploads dedupe** — Pinata content-hashes; identical files won't re-upload

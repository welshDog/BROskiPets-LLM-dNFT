---
name: sepolia-ops
description: Ethereum Sepolia testnet operations for the EEPVengers dNFT contract — Foundry deploy/verify, RPC config, Etherscan verification, cast inspection, gas estimation. Use when the user says "deploy to Sepolia", "verify on Etherscan", "cast call", "RPC issue", "Foundry not found", "PATH for forge", "redeploy contract", or any Sepolia interaction.
---

# sepolia-ops

The deployed-and-verified canon for EEPVengers on Sepolia. **Never use mainnet ETH for testing.**

## Live Contract (canonical)

```
Network:    Ethereum Sepolia (chainId 11155111)
Address:    0x3691470c6c56D9bb3cBe8052A2cEAcDdeeEe2F09
Verified:   ✅ on Sepolia Etherscan
RPC:        https://ethereum-sepolia-rpc.publicnode.com
Deployer:   0xb58B8e2E80451cc4ba8064cf8a0ad67aaa88FD41
Wallet:     Trust Wallet Extension (Sepolia account)
Constraints: MAX_SUPPLY=78, EVOLVE_COOLDOWN=3600s
```

If you need to redeploy: bump version, expect to re-mint, update `.env CONTRACT_ADDRESS`, re-pin metadata.

## Foundry on Windows — PATH Setup

Foundry binaries live at `$env:USERPROFILE\.foundry\bin`. PowerShell doesn't add this automatically — append per-session:

```powershell
$env:PATH += ";$env:USERPROFILE\.foundry\bin"
forge --version    # confirms forge is on PATH
cast --version     # confirms cast is on PATH
```

Or make it permanent:

```powershell
[Environment]::SetEnvironmentVariable("PATH", $env:PATH + ";$env:USERPROFILE\.foundry\bin", "User")
# restart shell
```

If `forge --version` fails with "command not found":
1. Confirm `~/.foundry/bin/forge.exe` exists
2. If not, run `foundryup` (PowerShell): `.\foundryup.ps1`

## Required `.env` Keys (NEVER commit)

```env
SEPOLIA_RPC=https://ethereum-sepolia-rpc.publicnode.com
DEPLOYER_KEY=0x<64 hex chars from Trust Wallet>
CONTRACT_ADDRESS=0x3691470c6c56D9bb3cBe8052A2cEAcDdeeEe2F09
ETHERSCAN_API_KEY=<your sepolia Etherscan API key>
ADMIN_ADDRESS=0xb58B8e2E80451cc4ba8064cf8a0ad67aaa88FD41
```

Load `.env` into a PowerShell session (when not running through Docker):

```powershell
cd H:\dNFTpet\BROskiPets-LLM-dNFT
Get-Content .env | ForEach-Object {
  $line = $_.Trim()
  if (-not $line -or $line.StartsWith('#') -or $line -notmatch '=') { return }
  $k,$v = $line.Split('=',2)
  $k=$k.Trim()
  $v=$v.Trim().Trim('"').Trim("'")
  if ($k) { [Environment]::SetEnvironmentVariable($k, $v, 'Process') }
}
```

## Deploy + Verify (full flow)

```powershell
cd H:\dNFTpet\BROskiPets-LLM-dNFT
$env:PATH += ";$env:USERPROFILE\.foundry\bin"
cd contracts

forge script script/Deploy.s.sol `
  --rpc-url $env:SEPOLIA_RPC `
  --private-key $env:DEPLOYER_KEY `
  --broadcast `
  --verify `
  --etherscan-api-key $env:ETHERSCAN_API_KEY `
  -vvv
```

After deploy:
1. Copy the printed contract address into `.env` as `CONTRACT_ADDRESS=0x...`
2. Open Sepolia Etherscan + confirm "Contract Source Code Verified ✅"
3. Confirm `AGENT_ROLE` granted to the address that will call `evolve()`

## Cast — Inspect On-Chain State

```powershell
$env:PATH += ";$env:USERPROFILE\.foundry\bin"

# Read tokenURI for token #1
cast call $env:CONTRACT_ADDRESS "tokenURI(uint256)(string)" 1 --rpc-url $env:SEPOLIA_RPC

# Read evolution stage (uint8: 0=baby, 1=young, 2=trained, 3=elite, 4=legendary, 5=quantum)
cast call $env:CONTRACT_ADDRESS "evolutionStage(uint256)(uint8)" 1 --rpc-url $env:SEPOLIA_RPC

# Read remaining cooldown (in seconds)
cast call $env:CONTRACT_ADDRESS "evolveCooldownRemaining(uint256)(uint256)" 1 --rpc-url $env:SEPOLIA_RPC

# Read totalSupply
cast call $env:CONTRACT_ADDRESS "totalSupply()(uint256)" --rpc-url $env:SEPOLIA_RPC

# Read MAX_SUPPLY (constant)
cast call $env:CONTRACT_ADDRESS "MAX_SUPPLY()(uint256)" --rpc-url $env:SEPOLIA_RPC
```

## Forge Build + Test

```powershell
cd H:\dNFTpet\BROskiPets-LLM-dNFT\contracts
forge build
forge test -vvv

# Run a specific test
forge test --match-test testEvolveAfterCooldown -vvv

# Coverage
forge coverage
```

108 tests should pass (per April 22 baseline). Drop = regression.

## Common Failures

| Symptom | Cause | Fix |
|---|---|---|
| `forge: command not found` | Foundry not on PATH | Append `~/.foundry/bin` to PATH (see top) |
| `Error: Failed to detect network` | `SEPOLIA_RPC` missing or wrong | Check `.env`, reload into shell |
| `Error: insufficient funds for gas * price + value` | Sepolia ETH balance too low | Get Sepolia ETH from faucet (sepoliafaucet.com) |
| Verification fails: "Already Verified" | Contract was already verified | Skip — that's a success state |
| Verification fails: "no Etherscan API key" | `ETHERSCAN_API_KEY` not loaded | Load `.env` into session |
| `gasPrice` related errors on Sepolia | Sepolia is post-EIP-1559 — `gasPrice` is rejected | Use `eip1559-gas` skill |
| `replacement transaction underpriced` | Stuck pending tx, new tx too cheap | Speed up via Trust Wallet UI, or use higher `maxPriorityFeePerGas` |
| `nonce too low` | Account state out of sync | `cast nonce $env:DEPLOYER_ADDRESS --rpc-url $env:SEPOLIA_RPC` to confirm |

## Companion Skills

- `eip1559-gas` — EIP-1559 transaction patterns (Sepolia rejects `gasPrice`)
- `dnft-evolve-flow` — the API → IPFS → on-chain flow that uses these contracts
- `pinata-ipfs-pin` — pin metadata + images before referencing in `tokenURI`
- `eep-mint-batch` — minting all 78 EEPs

## Hard Rules

- **NEVER use mainnet ETH** for development — Sepolia only (chainId 11155111)
- **NEVER commit `.env`** — `DEPLOYER_KEY` is a real private key
- **EIP-1559 only on Sepolia** — `gasPrice` will fail
- **Always verify on Etherscan** — `--verify --etherscan-api-key $env:ETHERSCAN_API_KEY` on every deploy
- **Confirm AGENT_ROLE granted** before testing `evolve()` — without it, the call reverts

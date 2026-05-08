---
name: eip1559-gas
description: EIP-1559 transaction gas pattern for Sepolia (replaces legacy gasPrice). Use when seeing `gasPrice` errors on Sepolia, fixing scripts/sepolia_mint_first_eep.py, building a new web3.py transaction, or when the user says "gas error", "1559", "maxFeePerGas", "transaction underpriced".
---

# eip1559-gas

Sepolia is post-EIP-1559. **Legacy `gasPrice` is rejected** — you must use `maxFeePerGas` + `maxPriorityFeePerGas`.

## The Bug We Hit (real story)

`scripts/sepolia_mint_first_eep.py` originally used:

```python
tx['gasPrice'] = w3.eth.gas_price   # ❌ rejected by Sepolia
```

The fix:

```python
base_fee     = w3.eth.get_block('latest')['baseFeePerGas']
priority_fee = w3.to_wei(1, 'gwei')

tx['maxPriorityFeePerGas'] = priority_fee
tx['maxFeePerGas']         = base_fee * 2 + priority_fee
tx['chainId']              = 11155111   # Sepolia
# REMOVE: tx['gasPrice']
```

## Canonical Transaction Builder (web3.py)

```python
from web3 import Web3

def build_eip1559_tx(w3, contract_fn, sender_address, **fn_args):
    base_fee     = w3.eth.get_block('latest')['baseFeePerGas']
    priority_fee = w3.to_wei(1, 'gwei')          # 1 gwei tip — cheap on Sepolia
    nonce        = w3.eth.get_transaction_count(sender_address)
    chain_id     = 11155111                       # Sepolia

    tx = contract_fn(**fn_args).build_transaction({
        'from':                  sender_address,
        'nonce':                 nonce,
        'chainId':               chain_id,
        'maxPriorityFeePerGas':  priority_fee,
        'maxFeePerGas':          base_fee * 2 + priority_fee,   # 2x base fee headroom
        # NEVER set 'gasPrice' on Sepolia
    })
    return tx
```

Then sign + send:

```python
signed = w3.eth.account.sign_transaction(tx, private_key=os.environ['DEPLOYER_KEY'])
tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
```

## Why `base_fee * 2 + priority_fee`?

- `base_fee` is set by the network and burned. Each block can vary by ±12.5%.
- `2x` gives 8 blocks of headroom before your tx becomes uncompetitive.
- `priority_fee` is the tip to the validator. 1 gwei is plenty on Sepolia.
- `maxFeePerGas` is the **cap** — you only pay `min(maxFeePerGas, base_fee + priority_fee)`. Setting it high doesn't cost more.

## Common Failures

| Symptom | Cause | Fix |
|---|---|---|
| `eth_estimateGas: gas required exceeds allowance` | The call would revert (logic error, not gas) | Fix the underlying call, not the gas |
| `transaction underpriced` | `maxFeePerGas` too low for current base fee | Refresh `base_fee = w3.eth.get_block('latest')['baseFeePerGas']` and rebuild |
| `replacement transaction underpriced` | Resending same nonce with similar fees | Use `2x maxFeePerGas` of the original tx, OR cancel + retry |
| `nonce too low` | Account already used this nonce | Refresh nonce: `w3.eth.get_transaction_count(addr, 'pending')` |
| `intrinsic gas too low` | `gas` (limit) is too low — separate from gas price | Set `'gas': 200000` (or estimate from contract) |
| `invalid sender` | Not signing with the right key | Confirm `signed.from == sender_address` |
| `Method not found: eth_gasPrice` | Some RPCs deprecated `eth_gasPrice` | Don't use it on Sepolia anyway — use `eth_feeHistory` or just `base_fee` from latest block |

## Cancel a Stuck Transaction

If a tx is pending forever, send a 0-value tx to yourself with the **same nonce** but **higher gas**:

```python
cancel_tx = {
    'from':                 sender_address,
    'to':                   sender_address,
    'value':                0,
    'nonce':                stuck_nonce,
    'chainId':              11155111,
    'gas':                  21000,
    'maxPriorityFeePerGas': w3.to_wei(2, 'gwei'),                  # 2x the stuck tx
    'maxFeePerGas':         w3.eth.get_block('latest')['baseFeePerGas'] * 3 + w3.to_wei(2, 'gwei'),
}
```

Sign, send, mined → original tx is dropped.

## Foundry Equivalent (cast)

`cast send` automatically uses EIP-1559 on Sepolia. No special flag needed:

```powershell
cast send $env:CONTRACT_ADDRESS "evolve(uint256,string)" 1 "ipfs://Qm..." `
  --rpc-url $env:SEPOLIA_RPC `
  --private-key $env:AGENT_KEY
```

If you need to override fees:

```powershell
cast send ... `
  --priority-gas-price 1gwei `
  --gas-price 50gwei
```

(`--gas-price` for `cast` maps to `maxFeePerGas`.)

## Companion Skills

- `sepolia-ops` — broader Sepolia + Foundry context
- `dnft-evolve-flow` — uses these patterns for the on-chain `evolve()` call
- `eep-mint-batch` — `mint_all_eeps.py` must use this pattern

## Hard Rules

- **NEVER set `gasPrice` on Sepolia** — the tx will be rejected
- **ALWAYS include `chainId`** — `11155111` for Sepolia
- **ALWAYS refresh nonce** before sending (especially in batch scripts)
- **`maxFeePerGas` is a cap, not the price** — set it generous, you don't overpay
- **For batch scripts** (e.g. `mint_all_eeps.py`): increment nonce manually, don't fetch per-tx (RPC will lag)

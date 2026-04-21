// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/EEPVengers.sol";

/**
 * @title Deploy
 * @notice Foundry deployment script for the EEPVengers dNFT contract.
 *
 * Usage — Sepolia testnet:
 *   forge script script/Deploy.s.sol \
 *     --rpc-url $SEPOLIA_RPC \
 *     --private-key $DEPLOYER_KEY \
 *     --broadcast \
 *     --verify \
 *     --etherscan-api-key $ETHERSCAN_API_KEY
 *
 * Usage — local Anvil:
 *   anvil  (in another terminal)
 *   forge script script/Deploy.s.sol \
 *     --rpc-url http://localhost:8545 \
 *     --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 \
 *     --broadcast
 *
 * Required env vars:
 *   ADMIN_ADDRESS   — wallet that will hold DEFAULT_ADMIN_ROLE (use a Gnosis Safe on mainnet)
 *   MINTER_ADDRESS  — wallet for MINTER_ROLE (mint service)
 *   AGENT_ADDRESS   — wallet for AGENT_ROLE (Python backend)
 *
 * Optional env vars:
 *   ETHERSCAN_API_KEY  — for source verification (--verify flag)
 */
contract Deploy is Script {

    // ─── Entry point ─────────────────────────────────────────────────────────

    function run() external {
        // Load required addresses from environment
        address admin  = vm.envAddress("ADMIN_ADDRESS");
        address minter = vm.envOr("MINTER_ADDRESS", admin); // default to admin for testnet
        address agent  = vm.envOr("AGENT_ADDRESS",  admin); // default to admin for testnet

        _validateAddresses(admin, minter, agent);

        console.log("=== EEPVengers Deployment ===");
        console.log("Admin:  ", admin);
        console.log("Minter: ", minter);
        console.log("Agent:  ", agent);
        console.log("Chain:  ", block.chainid);
        console.log("---");

        vm.startBroadcast();

        // Deploy contract — admin gets DEFAULT_ADMIN_ROLE + MINTER_ROLE initially
        EEPVengers nft = new EEPVengers(admin);

        // Grant MINTER_ROLE to dedicated minter wallet (if different from admin)
        if (minter != admin) {
            nft.grantRole(nft.MINTER_ROLE(), minter);
            console.log("MINTER_ROLE granted to:", minter);
        }

        // Grant AGENT_ROLE to Python backend wallet
        nft.grantRole(nft.AGENT_ROLE(), agent);
        console.log("AGENT_ROLE granted to:", agent);

        vm.stopBroadcast();

        // ── Post-deploy summary ───────────────────────────────────────────────
        console.log("---");
        console.log("EEPVengers deployed at:", address(nft));
        console.log("MAX_SUPPLY:            ", nft.MAX_SUPPLY());
        console.log("EVOLVE_COOLDOWN (s):   ", nft.EVOLVE_COOLDOWN());
        console.log("Total minted:          ", nft.totalMinted());
        console.log("---");
        console.log("Next steps:");
        console.log("  1. Set CONTRACT_ADDRESS in .env");
        console.log("  2. Upload images to IPFS for each EEP");
        console.log("  3. Run: python scripts/mint_all_eeps.py");

        _warnIfMainnet();
    }

    // ─── Internal helpers ─────────────────────────────────────────────────────

    function _validateAddresses(address admin, address minter, address agent) internal pure {
        require(admin  != address(0), "Deploy: ADMIN_ADDRESS is zero");
        require(minter != address(0), "Deploy: MINTER_ADDRESS is zero");
        require(agent  != address(0), "Deploy: AGENT_ADDRESS is zero");
    }

    function _warnIfMainnet() internal view {
        if (block.chainid == 1) {
            console.log("WARNING: Mainnet deployment detected.");
            console.log("  - Verify admin is a Gnosis Safe multisig");
            console.log("  - Revoke admin from deployer after Gnosis setup");
            console.log("  - Run Slither before this point: slither . --exclude-dependencies");
        }
    }
}

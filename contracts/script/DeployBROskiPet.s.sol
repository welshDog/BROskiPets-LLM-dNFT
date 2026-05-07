// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "forge-std/console.sol";
import "../src/BROskiPet.sol";

/**
 * @title DeployBROskiPet
 * @notice Foundry deploy script for the open-supply BROskiPet dNFT.
 *
 * Required env vars:
 *   ADMIN_ADDRESS           — DEFAULT_ADMIN_ROLE holder (Gnosis Safe on mainnet)
 *   BACKEND_SIGNER_ADDRESS  — wallet that signs EIP-712 mint authorizations (after Supabase BROski$ deduction)
 *   AGENT_ADDRESS           — LLM/agent backend wallet (evolves pets)
 *
 * Optional:
 *   MAX_PER_WALLET          — override default 5 (uint256)
 *   MAX_SUPPLY              — override default 100_000 (uint256, 0 = unlimited)
 *   ETHERSCAN_API_KEY       — for --verify
 *
 * Usage — Base Sepolia testnet:
 *   forge script script/DeployBROskiPet.s.sol \
 *     --rpc-url $BASE_SEPOLIA_RPC \
 *     --private-key $DEPLOYER_KEY \
 *     --broadcast --verify \
 *     --etherscan-api-key $ETHERSCAN_API_KEY
 *
 * Usage — local Anvil:
 *   anvil
 *   forge script script/DeployBROskiPet.s.sol \
 *     --rpc-url http://localhost:8545 \
 *     --private-key 0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80 \
 *     --broadcast
 */
contract DeployBROskiPet is Script {
    function run() external {
        address admin         = vm.envAddress("ADMIN_ADDRESS");
        address backendSigner = vm.envAddress("BACKEND_SIGNER_ADDRESS");
        address agent         = vm.envAddress("AGENT_ADDRESS");

        require(admin         != address(0), "Deploy: ADMIN_ADDRESS is zero");
        require(backendSigner != address(0), "Deploy: BACKEND_SIGNER_ADDRESS is zero");
        require(agent         != address(0), "Deploy: AGENT_ADDRESS is zero");

        uint256 maxPerWallet = vm.envOr("MAX_PER_WALLET", uint256(0));
        uint256 maxSupply    = vm.envOr("MAX_SUPPLY",     uint256(0));

        console.log("=== BROskiPet Deployment ===");
        console.log("Admin:         ", admin);
        console.log("BackendSigner: ", backendSigner);
        console.log("Agent:         ", agent);
        console.log("Chain:         ", block.chainid);
        console.log("---");

        vm.startBroadcast();

        BROskiPet nft = new BROskiPet(admin);
        nft.grantRole(nft.BACKEND_SIGNER_ROLE(), backendSigner);
        nft.grantRole(nft.AGENT_ROLE(),          agent);

        if (maxPerWallet != 0) nft.setMaxPerWallet(maxPerWallet);
        if (maxSupply    != 0) nft.setMaxSupply(maxSupply);

        vm.stopBroadcast();

        console.log("---");
        console.log("BROskiPet at:        ", address(nft));
        console.log("Domain separator:    ");
        console.logBytes32(nft.domainSeparator());
        console.log("maxPerWallet:        ", nft.maxPerWallet());
        console.log("maxSupply:           ", nft.maxSupply());
        console.log("EVOLVE_COOLDOWN (s): ", nft.EVOLVE_COOLDOWN());
        console.log("---");
        console.log("Next steps:");
        console.log("  1. Save contract address + domain separator to backend env");
        console.log("  2. Wire EIP-712 signer in Supabase Edge Function (mint-auth)");
        console.log("  3. Frontend: integrate wagmi + RainbowKit; call mintWithAuth(auth, sig)");

        if (block.chainid == 1) {
            console.log("WARNING: Mainnet detected. Ensure admin is a Gnosis Safe; run Slither first.");
        }
    }
}

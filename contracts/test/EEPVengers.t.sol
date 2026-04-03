// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../EEPVengers.sol";

/**
 * @title EEPVengersTest
 * @notice Foundry test suite for the EEPVengers dNFT contract.
 * @dev Run with: forge test -v  (from the /contracts directory)
 *      Fuzz: forge test --fuzz-runs 10000
 */
contract EEPVengersTest is Test {
    EEPVengers public nft;

    address admin    = makeAddr("admin");
    address minter   = makeAddr("minter");
    address agent    = makeAddr("agent");   // Python backend wallet
    address user1    = makeAddr("user1");
    address attacker = makeAddr("attacker");

    string constant BASE_CID    = "QmBaseMetadataCIDForBabyStage";
    string constant EVOLVED_CID = "QmEvolvedMetadataCIDForYoungStage";
    string constant PET_ID      = "spider_001";

    // ─── Setup ────────────────────────────────────────────────────────────────
    function setUp() public {
        vm.startPrank(admin);
        nft = new EEPVengers(admin);
        nft.grantRole(nft.MINTER_ROLE(), minter);
        nft.grantRole(nft.AGENT_ROLE(),  agent);
        vm.stopPrank();
    }

    // ─── Minting ──────────────────────────────────────────────────────────────
    function test_MintSucceeds() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, BASE_CID);

        assertEq(nft.ownerOf(1), user1);
        assertEq(nft.evolutionStage(1), 1);
        assertEq(nft.petId(1), PET_ID);
        assertEq(nft.tokenURI(1), string(abi.encodePacked("ipfs://", BASE_CID)));
        assertEq(nft.totalMinted(), 1);
    }

    function test_MintEmitsEvent() public {
        vm.expectEmit(true, true, false, true);
        emit EEPVengers.PetMinted(1, user1, PET_ID, BASE_CID);

        vm.prank(minter);
        nft.mint(user1, PET_ID, BASE_CID);
    }

    function test_MintRevertsIfNotMinter() public {
        vm.prank(attacker);
        vm.expectRevert();
        nft.mint(attacker, PET_ID, BASE_CID);
    }

    function test_MintRevertsAfterMaxSupply() public {
        vm.startPrank(minter);
        // Mint all 78
        for (uint256 i = 0; i < 78; i++) {
            nft.mint(user1, string(abi.encodePacked("eep_", vm.toString(i))), BASE_CID);
        }
        // 79th should revert
        vm.expectRevert("EEPVengers: All 78 EEPs minted");
        nft.mint(user1, "eep_79", BASE_CID);
        vm.stopPrank();
    }

    // ─── Evolution ────────────────────────────────────────────────────────────
    function test_EvolveSucceeds() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, BASE_CID);

        vm.prank(agent);
        nft.evolve(1, EVOLVED_CID, 2);

        assertEq(nft.evolutionStage(1), 2);
        assertEq(nft.tokenURI(1), string(abi.encodePacked("ipfs://", EVOLVED_CID)));
    }

    function test_EvolveEmitsEvent() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, BASE_CID);

        vm.expectEmit(true, false, false, true);
        emit EEPVengers.PetEvolved(1, 2, EVOLVED_CID, block.timestamp);

        vm.prank(agent);
        nft.evolve(1, EVOLVED_CID, 2);
    }

    function test_EvolveRevertsIfNotAgent() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, BASE_CID);

        vm.prank(attacker);
        vm.expectRevert();
        nft.evolve(1, EVOLVED_CID, 2);
    }

    function test_EvolveRevertsOnCooldown() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, BASE_CID);

        vm.startPrank(agent);
        nft.evolve(1, EVOLVED_CID, 2);

        // Try again immediately — should revert
        vm.expectRevert("EEPVengers: Evolution on cooldown");
        nft.evolve(1, "QmSomeOtherCID", 3);
        vm.stopPrank();
    }

    function test_EvolveSucceedsAfterCooldown() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, BASE_CID);

        vm.startPrank(agent);
        nft.evolve(1, EVOLVED_CID, 2);

        // Warp 1 hour forward
        vm.warp(block.timestamp + 1 hours + 1);
        nft.evolve(1, "QmTrainedCID", 3);
        vm.stopPrank();

        assertEq(nft.evolutionStage(1), 3);
    }

    function test_EvolveRevertsDeEvolution() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, BASE_CID);

        vm.startPrank(agent);
        nft.evolve(1, EVOLVED_CID, 2);
        vm.warp(block.timestamp + 2 hours);

        vm.expectRevert("EEPVengers: Cannot de-evolve");
        nft.evolve(1, BASE_CID, 1); // Try to go backwards
        vm.stopPrank();
    }

    function test_EvolveRevertsAboveMaxStage() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, BASE_CID);

        vm.prank(agent);
        vm.expectRevert("EEPVengers: Max stage is 6 (Quantum)");
        nft.evolve(1, EVOLVED_CID, 7);
    }

    // ─── Cooldown view ────────────────────────────────────────────────────────
    function test_CooldownRemainingIsZeroBeforeFirstEvolve() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, BASE_CID);
        assertEq(nft.evolveCooldownRemaining(1), 0);
    }

    function test_CooldownRemainingAfterEvolve() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, BASE_CID);

        vm.prank(agent);
        nft.evolve(1, EVOLVED_CID, 2);

        uint256 remaining = nft.evolveCooldownRemaining(1);
        assertGt(remaining, 0);
        assertLe(remaining, 1 hours);
    }

    // ─── Pause ────────────────────────────────────────────────────────────────
    function test_PauseBlocksMint() public {
        vm.prank(admin);
        nft.pause();

        vm.prank(minter);
        vm.expectRevert();
        nft.mint(user1, PET_ID, BASE_CID);
    }

    function test_UnpauseRestoresMint() public {
        vm.startPrank(admin);
        nft.pause();
        nft.unpause();
        vm.stopPrank();

        vm.prank(minter);
        nft.mint(user1, PET_ID, BASE_CID); // Should succeed
        assertEq(nft.ownerOf(1), user1);
    }

    // ─── Fuzz ─────────────────────────────────────────────────────────────────
    function testFuzz_EvolveStageRange(uint8 stage) public {
        vm.assume(stage >= 1 && stage <= 6);

        vm.prank(minter);
        nft.mint(user1, PET_ID, BASE_CID);

        vm.prank(agent);
        // Stage 1 is current, so stages 1-6 should all succeed (same stage = allowed)
        nft.evolve(1, EVOLVED_CID, stage);
        assertEq(nft.evolutionStage(1), stage);
    }
}

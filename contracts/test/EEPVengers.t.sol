// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../EEPVengers.sol";

contract EEPVengersTest is Test {
    EEPVengers public nft;

    address admin  = makeAddr("admin");
    address minter = makeAddr("minter");
    address agent  = makeAddr("agent");
    address user1  = makeAddr("user1");
    address user2  = makeAddr("user2");

    string constant PET_ID  = "spider_001";
    string constant CID_V1  = "QmBabySpiderCID";
    string constant CID_V2  = "QmYoungSpiderCID";

    function setUp() public {
        nft = new EEPVengers(admin, minter, agent);
    }

    // ── Minting ──────────────────────────────────────────────────────────────

    function test_MintSucceeds() public {
        vm.prank(minter);
        uint256 tokenId = nft.mint(user1, PET_ID, CID_V1);

        assertEq(tokenId, 1);
        assertEq(nft.ownerOf(1), user1);
        assertEq(nft.tokenURI(1), string(abi.encodePacked("ipfs://", CID_V1)));
        assertEq(nft.evolutionStage(1), 1);
        assertEq(nft.petId(1), PET_ID);
        assertEq(nft.totalSupply(), 1);
    }

    function test_MintRevertsIfNotMinter() public {
        vm.prank(user1);
        vm.expectRevert();
        nft.mint(user1, PET_ID, CID_V1);
    }

    function test_MintRevertsAfterMaxSupply() public {
        vm.startPrank(minter);
        for (uint256 i = 0; i < 78; i++) {
            nft.mint(user1, string(abi.encodePacked("pet_", vm.toString(i))), CID_V1);
        }
        vm.expectRevert(EEPVengers.MaxSupplyReached.selector);
        nft.mint(user1, "extra", CID_V1);
        vm.stopPrank();
    }

    // ── Evolution ────────────────────────────────────────────────────────────

    function test_EvolveSucceeds() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, CID_V1);

        vm.prank(agent);
        nft.evolve(1, 2, CID_V2);

        assertEq(nft.evolutionStage(1), 2);
        assertEq(nft.tokenURI(1), string(abi.encodePacked("ipfs://", CID_V2)));
    }

    function test_EvolveRevertsIfNotAgent() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, CID_V1);

        vm.prank(user1);
        vm.expectRevert();
        nft.evolve(1, 2, CID_V2);
    }

    function test_EvolveRevertsOnCooldown() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, CID_V1);

        vm.prank(agent);
        nft.evolve(1, 2, CID_V2);

        // Immediately try again — should revert
        vm.prank(agent);
        vm.expectRevert();
        nft.evolve(1, 3, "QmTrainedSpider");
    }

    function test_EvolveSucceedsAfterCooldown() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, CID_V1);

        vm.prank(agent);
        nft.evolve(1, 2, CID_V2);

        vm.warp(block.timestamp + 1 hours + 1);

        vm.prank(agent);
        nft.evolve(1, 3, "QmTrainedSpider");

        assertEq(nft.evolutionStage(1), 3);
    }

    function test_EvolveRevertsAtMaxStage() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, CID_V1);

        vm.startPrank(agent);
        for (uint8 stage = 2; stage <= 6; stage++) {
            vm.warp(block.timestamp + 1 hours + 1);
            nft.evolve(1, stage, CID_V2);
        }
        vm.warp(block.timestamp + 1 hours + 1);
        vm.expectRevert(EEPVengers.AlreadyMaxEvolution.selector);
        nft.evolve(1, 6, CID_V2);
        vm.stopPrank();
    }

    // ── Cooldown view ────────────────────────────────────────────────────────

    function test_CooldownRemainingIsZeroBeforeFirstEvolve() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, CID_V1);
        assertEq(nft.evolveCooldownRemaining(1), 0);
    }

    function test_CooldownRemainingAfterEvolve() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, CID_V1);

        vm.prank(agent);
        nft.evolve(1, 2, CID_V2);

        uint256 remaining = nft.evolveCooldownRemaining(1);
        assertGt(remaining, 0);
        assertLe(remaining, 1 hours);
    }

    // ── Pause ────────────────────────────────────────────────────────────────

    function test_PauseBlocksMint() public {
        vm.prank(admin);
        nft.pause();

        vm.prank(minter);
        vm.expectRevert();
        nft.mint(user1, PET_ID, CID_V1);
    }

    function test_UnpauseRestoresMint() public {
        vm.prank(admin);
        nft.pause();

        vm.prank(admin);
        nft.unpause();

        vm.prank(minter);
        uint256 tokenId = nft.mint(user1, PET_ID, CID_V1);
        assertEq(tokenId, 1);
    }

    // ── Events ───────────────────────────────────────────────────────────────

    function test_MintEmitsPetMintedEvent() public {
        vm.expectEmit(true, true, false, true);
        emit EEPVengers.PetMinted(1, user1, PET_ID, CID_V1);

        vm.prank(minter);
        nft.mint(user1, PET_ID, CID_V1);
    }

    function test_EvolveEmitsPetEvolvedEvent() public {
        vm.prank(minter);
        nft.mint(user1, PET_ID, CID_V1);

        vm.expectEmit(true, false, false, true);
        emit EEPVengers.PetEvolved(1, 2, CID_V2);

        vm.prank(agent);
        nft.evolve(1, 2, CID_V2);
    }
}

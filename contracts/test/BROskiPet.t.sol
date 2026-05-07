// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/BROskiPet.sol";

/**
 * @title BROskiPetTest
 * @notice Foundry suite for BROskiPet — covers signature mint, evolution,
 *         admin, edge cases, and EIP-712 domain.
 *
 * Run:
 *   forge test --match-contract BROskiPetTest -v
 *   forge test --match-contract BROskiPetTest --fuzz-runs 10000
 */
contract BROskiPetTest is Test {
    BROskiPet public nft;

    // EIP-712 type constants (must mirror the contract)
    bytes32 private constant MINT_AUTH_TYPEHASH = keccak256(
        "MintAuth(address to,string petId,string ipfsCID,uint256 nonce,uint256 expiry)"
    );

    address admin    = makeAddr("admin");
    address agent    = makeAddr("agent");
    address user1    = makeAddr("user1");
    address user2    = makeAddr("user2");
    address attacker = makeAddr("attacker");

    // Backend signer with a known private key so we can sign in tests
    uint256 backendSignerPk = 0xA11CE;
    address backendSigner;

    string constant BASE_CID    = "QmBaseCID";
    string constant EVOLVED_CID = "QmEvolvedCID";
    string constant PET_ID      = "broski_user1_001";

    function setUp() public {
        backendSigner = vm.addr(backendSignerPk);

        vm.startPrank(admin);
        nft = new BROskiPet(admin);
        nft.grantRole(nft.BACKEND_SIGNER_ROLE(), backendSigner);
        nft.grantRole(nft.AGENT_ROLE(), agent);
        vm.stopPrank();
    }

    // ─── Helpers ──────────────────────────────────────────────────────────────
    function _buildAuth(
        address to,
        string memory _petId,
        string memory cid,
        uint256 nonce,
        uint256 expiry
    ) internal pure returns (BROskiPet.MintAuth memory) {
        return BROskiPet.MintAuth({
            to: to,
            petId: _petId,
            ipfsCID: cid,
            nonce: nonce,
            expiry: expiry
        });
    }

    function _signAuth(BROskiPet.MintAuth memory auth, uint256 signerPk)
        internal
        view
        returns (bytes memory)
    {
        bytes32 structHash = keccak256(
            abi.encode(
                MINT_AUTH_TYPEHASH,
                auth.to,
                keccak256(bytes(auth.petId)),
                keccak256(bytes(auth.ipfsCID)),
                auth.nonce,
                auth.expiry
            )
        );
        bytes32 digest = keccak256(
            abi.encodePacked("\x19\x01", nft.domainSeparator(), structHash)
        );
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(signerPk, digest);
        return abi.encodePacked(r, s, v);
    }

    function _mintTo(address to, uint256 nonce) internal returns (uint256) {
        BROskiPet.MintAuth memory auth = _buildAuth(
            to, PET_ID, BASE_CID, nonce, block.timestamp + 1 hours
        );
        bytes memory sig = _signAuth(auth, backendSignerPk);
        vm.prank(to);
        nft.mintWithAuth(auth, sig);
        return nft.totalMinted();
    }

    // ─── Mint ─────────────────────────────────────────────────────────────────
    function test_MintWithValidAuthSucceeds() public {
        uint256 tokenId = _mintTo(user1, 1);

        assertEq(nft.ownerOf(tokenId), user1);
        assertEq(nft.evolutionStage(tokenId), 1);
        assertEq(nft.petId(tokenId), PET_ID);
        assertEq(nft.tokenURI(tokenId), string(abi.encodePacked("ipfs://", BASE_CID)));
        assertEq(nft.totalMinted(), 1);
        assertEq(nft.mintedBy(user1), 1);
        assertTrue(nft.mintNonceUsed(1));
    }

    function test_MintEmitsEvent() public {
        BROskiPet.MintAuth memory auth = _buildAuth(
            user1, PET_ID, BASE_CID, 42, block.timestamp + 1 hours
        );
        bytes memory sig = _signAuth(auth, backendSignerPk);

        vm.expectEmit(true, true, false, true);
        emit BROskiPet.PetMinted(1, user1, PET_ID, BASE_CID, 42);

        vm.prank(user1);
        nft.mintWithAuth(auth, sig);
    }

    function test_MintRevertsIfSignerLacksRole() public {
        BROskiPet.MintAuth memory auth = _buildAuth(
            user1, PET_ID, BASE_CID, 1, block.timestamp + 1 hours
        );
        // Signed by attacker (not BACKEND_SIGNER_ROLE)
        uint256 attackerPk = 0xBAD;
        bytes memory sig = _signAuth(auth, attackerPk);

        vm.prank(user1);
        vm.expectRevert(BROskiPet.AuthSignerInvalid.selector);
        nft.mintWithAuth(auth, sig);
    }

    function test_MintRevertsIfRecipientMismatch() public {
        BROskiPet.MintAuth memory auth = _buildAuth(
            user1, PET_ID, BASE_CID, 1, block.timestamp + 1 hours
        );
        bytes memory sig = _signAuth(auth, backendSignerPk);

        // user2 tries to redeem an auth meant for user1
        vm.prank(user2);
        vm.expectRevert(BROskiPet.AuthRecipientMismatch.selector);
        nft.mintWithAuth(auth, sig);
    }

    function test_MintRevertsIfExpired() public {
        BROskiPet.MintAuth memory auth = _buildAuth(
            user1, PET_ID, BASE_CID, 1, block.timestamp + 100
        );
        bytes memory sig = _signAuth(auth, backendSignerPk);

        vm.warp(block.timestamp + 200);
        vm.prank(user1);
        vm.expectRevert(BROskiPet.AuthExpired.selector);
        nft.mintWithAuth(auth, sig);
    }

    function test_MintRevertsOnReplay() public {
        _mintTo(user1, 7);

        // Same auth — same nonce — replay attempt
        BROskiPet.MintAuth memory auth = _buildAuth(
            user1, PET_ID, BASE_CID, 7, block.timestamp + 1 hours
        );
        bytes memory sig = _signAuth(auth, backendSignerPk);

        vm.prank(user1);
        vm.expectRevert(BROskiPet.AuthNonceUsed.selector);
        nft.mintWithAuth(auth, sig);
    }

    function test_MintRevertsIfTamperedAfterSign() public {
        BROskiPet.MintAuth memory auth = _buildAuth(
            user1, PET_ID, BASE_CID, 1, block.timestamp + 1 hours
        );
        bytes memory sig = _signAuth(auth, backendSignerPk);

        // Tamper with CID after signature
        auth.ipfsCID = "QmEvilTamperedCID";

        vm.prank(user1);
        vm.expectRevert(BROskiPet.AuthSignerInvalid.selector);
        nft.mintWithAuth(auth, sig);
    }

    function test_MintRevertsAtPerWalletCap() public {
        for (uint256 i = 1; i <= 5; i++) {
            _mintTo(user1, i);
        }
        // 6th — should hit cap
        BROskiPet.MintAuth memory auth = _buildAuth(
            user1, PET_ID, BASE_CID, 6, block.timestamp + 1 hours
        );
        bytes memory sig = _signAuth(auth, backendSignerPk);

        vm.prank(user1);
        vm.expectRevert(BROskiPet.MintCapReached.selector);
        nft.mintWithAuth(auth, sig);
    }

    function test_AdminCanRaiseMaxPerWallet() public {
        for (uint256 i = 1; i <= 5; i++) {
            _mintTo(user1, i);
        }

        vm.prank(admin);
        nft.setMaxPerWallet(10);

        // 6th now succeeds
        _mintTo(user1, 6);
        assertEq(nft.mintedBy(user1), 6);
    }

    function test_MintRevertsAtSupplyCap() public {
        vm.prank(admin);
        nft.setMaxSupply(2);

        _mintTo(user1, 1);
        _mintTo(user2, 2);

        BROskiPet.MintAuth memory auth = _buildAuth(
            user1, PET_ID, BASE_CID, 3, block.timestamp + 1 hours
        );
        bytes memory sig = _signAuth(auth, backendSignerPk);

        vm.prank(user1);
        vm.expectRevert(BROskiPet.SupplyCapReached.selector);
        nft.mintWithAuth(auth, sig);
    }

    function test_SupplyCapZeroDisablesCheck() public {
        vm.prank(admin);
        nft.setMaxSupply(0);

        // Mint several — no cap should fire
        _mintTo(user1, 1);
        _mintTo(user2, 2);
        assertEq(nft.totalMinted(), 2);
    }

    // ─── Evolution ────────────────────────────────────────────────────────────
    function test_EvolveSucceeds() public {
        _mintTo(user1, 1);

        vm.prank(agent);
        nft.evolve(1, EVOLVED_CID, 2);

        assertEq(nft.evolutionStage(1), 2);
        assertEq(nft.tokenURI(1), string(abi.encodePacked("ipfs://", EVOLVED_CID)));
    }

    function test_EvolveRevertsIfNotAgent() public {
        _mintTo(user1, 1);

        vm.prank(attacker);
        vm.expectRevert();
        nft.evolve(1, EVOLVED_CID, 2);
    }

    function test_EvolveRevertsOnCooldown() public {
        _mintTo(user1, 1);

        vm.startPrank(agent);
        nft.evolve(1, EVOLVED_CID, 2);

        vm.expectRevert(BROskiPet.EvolveOnCooldown.selector);
        nft.evolve(1, "QmAnother", 3);
        vm.stopPrank();
    }

    function test_EvolveSucceedsAfterCooldown() public {
        _mintTo(user1, 1);

        vm.startPrank(agent);
        nft.evolve(1, EVOLVED_CID, 2);
        vm.warp(block.timestamp + 1 hours + 1);
        nft.evolve(1, "QmTrained", 3);
        vm.stopPrank();

        assertEq(nft.evolutionStage(1), 3);
    }

    function test_EvolveRevertsDeEvolution() public {
        _mintTo(user1, 1);

        vm.startPrank(agent);
        nft.evolve(1, EVOLVED_CID, 3);
        vm.warp(block.timestamp + 2 hours);
        vm.expectRevert(BROskiPet.CannotDeEvolve.selector);
        nft.evolve(1, BASE_CID, 2);
        vm.stopPrank();
    }

    function test_EvolveRevertsAboveMaxStage() public {
        _mintTo(user1, 1);

        vm.prank(agent);
        vm.expectRevert(BROskiPet.StageOutOfRange.selector);
        nft.evolve(1, EVOLVED_CID, 7);
    }

    function test_EvolveRevertsForNonexistentToken() public {
        vm.prank(agent);
        vm.expectRevert(BROskiPet.TokenDoesNotExist.selector);
        nft.evolve(999, EVOLVED_CID, 2);
    }

    // ─── Pause ────────────────────────────────────────────────────────────────
    function test_PauseBlocksMint() public {
        vm.prank(admin);
        nft.pause();

        BROskiPet.MintAuth memory auth = _buildAuth(
            user1, PET_ID, BASE_CID, 1, block.timestamp + 1 hours
        );
        bytes memory sig = _signAuth(auth, backendSignerPk);

        vm.prank(user1);
        vm.expectRevert();
        nft.mintWithAuth(auth, sig);
    }

    function test_UnpauseRestoresMint() public {
        vm.startPrank(admin);
        nft.pause();
        nft.unpause();
        vm.stopPrank();

        _mintTo(user1, 1);
        assertEq(nft.ownerOf(1), user1);
    }

    // ─── Fuzz ─────────────────────────────────────────────────────────────────
    function testFuzz_NonceUniqueness(uint256 nonce) public {
        BROskiPet.MintAuth memory auth = _buildAuth(
            user1, PET_ID, BASE_CID, nonce, block.timestamp + 1 hours
        );
        bytes memory sig = _signAuth(auth, backendSignerPk);

        vm.prank(user1);
        nft.mintWithAuth(auth, sig);
        assertTrue(nft.mintNonceUsed(nonce));

        // Replay should always revert
        vm.prank(user1);
        vm.expectRevert(BROskiPet.AuthNonceUsed.selector);
        nft.mintWithAuth(auth, sig);
    }

    function testFuzz_EvolveStageRange(uint8 stage) public {
        vm.assume(stage >= 1 && stage <= 6);

        _mintTo(user1, 1);

        vm.prank(agent);
        nft.evolve(1, EVOLVED_CID, stage);
        assertEq(nft.evolutionStage(1), stage);
    }
}

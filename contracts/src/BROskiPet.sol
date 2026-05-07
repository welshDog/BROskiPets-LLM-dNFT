// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// OpenZeppelin v5
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";
import "@openzeppelin/contracts/utils/cryptography/EIP712.sol";

/**
 * @title BROskiPet
 * @notice Open-supply dynamic NFT (dNFT) for student-owned BROski Pets.
 * @dev Sister contract to EEPVengers (78-limited elite collection). BROskiPets
 *      are the regular pet line — every Hyper Vibe Course student can mint and
 *      evolve their own. Mint is gated by an EIP-712 signature from a backend
 *      signer that has verified the user spent BROski$ in Supabase.
 *
 * Architecture:
 *   - BROski$ balance: offchain (Supabase users.broski_tokens column)
 *   - Mint authorization: EIP-712 signature from BACKEND_SIGNER role
 *   - Pet metadata: IPFS CID per token, mutable by AGENT_ROLE on evolution
 *   - Evolution: AGENT_ROLE (LLM backend), rate-limited cooldown
 *
 * Mint flow:
 *   1. User requests pet mint in app (POST /api/pets/mint)
 *   2. Backend deducts BROski$ in Supabase (atomic), constructs MintAuth
 *   3. Backend signs MintAuth with BACKEND_SIGNER private key (EIP-712)
 *   4. Backend returns sig + nonce + expiry to client
 *   5. User submits tx: mintWithAuth(auth, sig)
 *   6. Contract verifies sig, marks nonce used, mints
 *
 * Author: welshDog (Lyndon Williams) — Hyperfocus Zone
 */
contract BROskiPet is ERC721URIStorage, AccessControl, Pausable, ReentrancyGuard, EIP712 {
    using ECDSA for bytes32;

    // ─── Roles ────────────────────────────────────────────────────────────────
    /// @notice Backend wallet that signs EIP-712 mint authorizations after Supabase deduction.
    bytes32 public constant BACKEND_SIGNER_ROLE = keccak256("BACKEND_SIGNER_ROLE");
    /// @notice LLM/agent backend that updates metadata on pet evolution.
    bytes32 public constant AGENT_ROLE          = keccak256("AGENT_ROLE");

    // ─── Config ───────────────────────────────────────────────────────────────
    /// @notice Maximum pets a single wallet can mint. Prevents runaway minting from one account.
    uint256 public maxPerWallet = 5;

    /// @notice Optional global supply cap. Set to 0 to disable. Admin can raise.
    uint256 public maxSupply = 100_000;

    /// @notice Seconds between consecutive evolve() calls per token.
    uint256 public constant EVOLVE_COOLDOWN = 1 hours;

    /// @notice Maximum evolution stage (1=Baby, 2=Young, 3=Trained, 4=Elite, 5=Legendary, 6=Quantum).
    uint8 public constant MAX_STAGE = 6;

    // ─── EIP-712 typed data ──────────────────────────────────────────────────
    bytes32 private constant MINT_AUTH_TYPEHASH = keccak256(
        "MintAuth(address to,string petId,string ipfsCID,uint256 nonce,uint256 expiry)"
    );

    /// @notice Typed-data struct signed by BACKEND_SIGNER_ROLE off-chain.
    struct MintAuth {
        address to;        // recipient
        string  petId;     // off-chain pet id (e.g. "broski_user42_001")
        string  ipfsCID;   // initial Baby-stage metadata CID
        uint256 nonce;     // single-use, server-issued
        uint256 expiry;    // unix timestamp; must be > block.timestamp
    }

    // ─── State ────────────────────────────────────────────────────────────────
    uint256 private _nextTokenId = 1;

    /// @dev tokenId => evolution stage
    mapping(uint256 => uint8)   public evolutionStage;
    /// @dev tokenId => offchain pet id
    mapping(uint256 => string)  public petId;
    /// @dev tokenId => last evolve timestamp (cooldown)
    mapping(uint256 => uint256) public lastEvolved;
    /// @dev wallet => count of pets minted
    mapping(address => uint256) public mintedBy;
    /// @dev nonce => used? (single-use mint authorizations)
    mapping(uint256 => bool)    public mintNonceUsed;

    // ─── Events ───────────────────────────────────────────────────────────────
    event PetMinted(uint256 indexed tokenId, address indexed owner, string petId, string ipfsCID, uint256 nonce);
    event PetEvolved(uint256 indexed tokenId, uint8 newStage, string newCID, uint256 timestamp);
    event ConfigUpdated(uint256 maxPerWallet, uint256 maxSupply);

    // ─── Errors ───────────────────────────────────────────────────────────────
    error AuthExpired();
    error AuthNonceUsed();
    error AuthRecipientMismatch();
    error AuthSignerInvalid();
    error MintCapReached();
    error SupplyCapReached();
    error TokenDoesNotExist();
    error CannotDeEvolve();
    error StageOutOfRange();
    error EvolveOnCooldown();

    // ─── Constructor ──────────────────────────────────────────────────────────
    /**
     * @param adminMultisig  Holds DEFAULT_ADMIN_ROLE (use Gnosis Safe on mainnet).
     */
    constructor(address adminMultisig)
        ERC721("BROskiPet", "BROPET")
        EIP712("BROskiPet", "1")
    {
        _grantRole(DEFAULT_ADMIN_ROLE, adminMultisig);
    }

    // ─── Mint (signature-gated) ──────────────────────────────────────────────
    /**
     * @notice Mint a pet using a backend-issued EIP-712 authorization.
     * @dev Signature must come from an address holding BACKEND_SIGNER_ROLE.
     *      The backend issues the signature only after deducting BROski$ from
     *      the user's Supabase balance. Each `auth.nonce` can be used once.
     */
    function mintWithAuth(MintAuth calldata auth, bytes calldata signature)
        external
        whenNotPaused
        nonReentrant
    {
        if (block.timestamp > auth.expiry)             revert AuthExpired();
        if (mintNonceUsed[auth.nonce])                 revert AuthNonceUsed();
        if (msg.sender != auth.to)                     revert AuthRecipientMismatch();
        if (mintedBy[auth.to] >= maxPerWallet)         revert MintCapReached();
        if (maxSupply != 0 && _nextTokenId > maxSupply) revert SupplyCapReached();

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
        address signer = _hashTypedDataV4(structHash).recover(signature);
        if (!hasRole(BACKEND_SIGNER_ROLE, signer))     revert AuthSignerInvalid();

        mintNonceUsed[auth.nonce] = true;
        mintedBy[auth.to] += 1;

        uint256 tokenId = _nextTokenId++;
        _safeMint(auth.to, tokenId);
        _setTokenURI(tokenId, string(abi.encodePacked("ipfs://", auth.ipfsCID)));
        evolutionStage[tokenId] = 1;
        petId[tokenId]          = auth.petId;

        emit PetMinted(tokenId, auth.to, auth.petId, auth.ipfsCID, auth.nonce);
    }

    // ─── Evolution ────────────────────────────────────────────────────────────
    /**
     * @notice Update a pet's metadata CID + stage on evolution.
     * @dev Only AGENT_ROLE. Cooldown-protected.
     */
    function evolve(uint256 tokenId, string calldata newCID, uint8 newStage)
        external
        onlyRole(AGENT_ROLE)
        whenNotPaused
        nonReentrant
    {
        if (_ownerOf(tokenId) == address(0))                revert TokenDoesNotExist();
        if (newStage < evolutionStage[tokenId])             revert CannotDeEvolve();
        if (newStage > MAX_STAGE)                           revert StageOutOfRange();
        if (
            lastEvolved[tokenId] != 0 &&
            block.timestamp < lastEvolved[tokenId] + EVOLVE_COOLDOWN
        )                                                   revert EvolveOnCooldown();

        _setTokenURI(tokenId, string(abi.encodePacked("ipfs://", newCID)));
        evolutionStage[tokenId] = newStage;
        lastEvolved[tokenId]    = block.timestamp;

        emit PetEvolved(tokenId, newStage, newCID, block.timestamp);
    }

    // ─── Views ────────────────────────────────────────────────────────────────
    function totalMinted() external view returns (uint256) { return _nextTokenId - 1; }

    function evolveCooldownRemaining(uint256 tokenId) external view returns (uint256) {
        if (lastEvolved[tokenId] == 0) return 0;
        uint256 ready = lastEvolved[tokenId] + EVOLVE_COOLDOWN;
        if (block.timestamp >= ready) return 0;
        return ready - block.timestamp;
    }

    /// @notice Domain separator for off-chain signers (ethers / viem).
    function domainSeparator() external view returns (bytes32) {
        return _domainSeparatorV4();
    }

    // ─── Admin ────────────────────────────────────────────────────────────────
    function setMaxPerWallet(uint256 newCap) external onlyRole(DEFAULT_ADMIN_ROLE) {
        maxPerWallet = newCap;
        emit ConfigUpdated(maxPerWallet, maxSupply);
    }

    function setMaxSupply(uint256 newSupply) external onlyRole(DEFAULT_ADMIN_ROLE) {
        maxSupply = newSupply;
        emit ConfigUpdated(maxPerWallet, maxSupply);
    }

    function pause()   external onlyRole(DEFAULT_ADMIN_ROLE) { _pause(); }
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) { _unpause(); }

    // ─── Overrides ────────────────────────────────────────────────────────────
    function supportsInterface(bytes4 interfaceId)
        public view override(ERC721URIStorage, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}

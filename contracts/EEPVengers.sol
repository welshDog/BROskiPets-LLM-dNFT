// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

// OpenZeppelin v5 — install via: npm install @openzeppelin/contracts
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

/**
 * @title EEPVengers
 * @notice Dynamic NFT (dNFT) contract for the BROskiPets EEPVengers squad.
 *         Each EEP is an ERC-721 token whose metadata URI updates on-chain
 *         whenever the pet evolves (driven by the off-chain Python agent).
 *
 * Architecture:
 *   - MINTER_ROLE   : backend wallet that mints new EEPs
 *   - AGENT_ROLE    : backend wallet that triggers evolution (metadata updates)
 *   - DEFAULT_ADMIN : multisig (Gnosis Safe) — controls roles, pause, withdraw
 *
 * Metadata lives on IPFS. tokenURI() returns the current IPFS CID for the pet.
 * Evolution is rate-limited: one update per EVOLVE_COOLDOWN seconds per token.
 */
contract EEPVengers is ERC721URIStorage, AccessControl, Pausable, ReentrancyGuard {

    // ── Roles ────────────────────────────────────────────────────────────────
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant AGENT_ROLE  = keccak256("AGENT_ROLE");

    // ── Config ───────────────────────────────────────────────────────────────
    uint256 public constant MAX_SUPPLY      = 78;        // exactly 78 EEPs
    uint256 public constant EVOLVE_COOLDOWN = 1 hours;   // rate-limit per token

    // ── State ────────────────────────────────────────────────────────────────
    uint256 private _nextTokenId;
    mapping(uint256 => uint256) public lastEvolved;      // tokenId → timestamp
    mapping(uint256 => uint8)   public evolutionStage;   // tokenId → stage (1–6)
    mapping(uint256 => string)  public petId;            // tokenId → off-chain pet_id

    // ── Events ───────────────────────────────────────────────────────────────
    event PetMinted(uint256 indexed tokenId, address indexed to, string petId, string ipfsCID);
    event PetEvolved(uint256 indexed tokenId, uint8 newStage, string newIPFSCID);
    event PetURIUpdated(uint256 indexed tokenId, string newURI);

    // ── Errors ───────────────────────────────────────────────────────────────
    error MaxSupplyReached();
    error EvolveCooldownActive(uint256 availableAt);
    error AlreadyMaxEvolution();
    error TokenDoesNotExist(uint256 tokenId);

    // ── Constructor ──────────────────────────────────────────────────────────
    constructor(address admin, address minter, address agent)
        ERC721("EEPVengers", "EEP")
    {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(MINTER_ROLE, minter);
        _grantRole(AGENT_ROLE, agent);
        _nextTokenId = 1; // token IDs start at 1
    }

    // ── Minting ──────────────────────────────────────────────────────────────

    /**
     * @notice Mint a new EEP to `to`. Only callable by MINTER_ROLE.
     * @param to        Recipient wallet address.
     * @param _petId    Off-chain pet ID (e.g. "spider_001") for cross-system linking.
     * @param ipfsCID   IPFS CID of the initial (Baby stage) metadata JSON.
     */
    function mint(address to, string calldata _petId, string calldata ipfsCID)
        external
        onlyRole(MINTER_ROLE)
        whenNotPaused
        nonReentrant
        returns (uint256 tokenId)
    {
        if (_nextTokenId > MAX_SUPPLY) revert MaxSupplyReached();

        tokenId = _nextTokenId++;
        petId[tokenId] = _petId;
        evolutionStage[tokenId] = 1; // Baby

        _safeMint(to, tokenId);
        _setTokenURI(tokenId, _buildURI(ipfsCID));

        emit PetMinted(tokenId, to, _petId, ipfsCID);
    }

    // ── Evolution ────────────────────────────────────────────────────────────

    /**
     * @notice Update a pet's metadata URI when it evolves. Only AGENT_ROLE.
     * @param tokenId   The EEP token to evolve.
     * @param newStage  New evolution stage (1=Baby … 6=Quantum).
     * @param ipfsCID   IPFS CID of the new metadata JSON for this stage.
     */
    function evolve(uint256 tokenId, uint8 newStage, string calldata ipfsCID)
        external
        onlyRole(AGENT_ROLE)
        whenNotPaused
        nonReentrant
    {
        if (!_exists(tokenId)) revert TokenDoesNotExist(tokenId);
        if (evolutionStage[tokenId] >= 6) revert AlreadyMaxEvolution();

        uint256 available = lastEvolved[tokenId] + EVOLVE_COOLDOWN;
        if (block.timestamp < available) revert EvolveCooldownActive(available);

        evolutionStage[tokenId] = newStage;
        lastEvolved[tokenId] = block.timestamp;
        _setTokenURI(tokenId, _buildURI(ipfsCID));

        emit PetEvolved(tokenId, newStage, ipfsCID);
    }

    // ── Views ────────────────────────────────────────────────────────────────

    /**
     * @notice Returns seconds remaining until this token can evolve again.
     *         Returns 0 if cooldown has passed.
     */
    function evolveCooldownRemaining(uint256 tokenId) external view returns (uint256) {
        uint256 available = lastEvolved[tokenId] + EVOLVE_COOLDOWN;
        if (block.timestamp >= available) return 0;
        return available - block.timestamp;
    }

    /**
     * @notice Total EEPs minted so far.
     */
    function totalSupply() external view returns (uint256) {
        return _nextTokenId - 1;
    }

    // ── Admin ────────────────────────────────────────────────────────────────

    function pause()   external onlyRole(DEFAULT_ADMIN_ROLE) { _pause(); }
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) { _unpause(); }

    // ── Internal ─────────────────────────────────────────────────────────────

    function _buildURI(string calldata cid) internal pure returns (string memory) {
        return string(abi.encodePacked("ipfs://", cid));
    }

    function _exists(uint256 tokenId) internal view returns (bool) {
        return _ownerOf(tokenId) != address(0);
    }

    // Required override — ERC721URIStorage + AccessControl both implement supportsInterface
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(ERC721URIStorage, AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
}

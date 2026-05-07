/**
 * Pets.tsx — /pets route
 * 3-step mint flow: pick species → name pet → mint on Base.
 * Replaces mock data (Vibe Pup, CodeKitsu, BROski, Glitchling).
 *
 * TODO after Pinata upload:
 *   - Replace /pets/{species} image paths with Pinata gateway URLs from pinata_cids.json
 *   - Replace mock collection with on-chain event query or Supabase mirror
 */

import { useState } from "react";
import { SpeciesPicker, type SpeciesId } from "@/components/pets/SpeciesPicker";
import { MintPetButton } from "@/components/pets/MintPetButton";

interface MintedPet {
  petId: string;
  petName: string;
  species: SpeciesId;
  txHash: string;
}

type MintStep = "pick" | "name" | "mint";

export default function PetsPage() {
  const [selectedSpecies, setSelectedSpecies] = useState<SpeciesId | null>(null);
  const [petName, setPetName]     = useState("");
  const [minted, setMinted]       = useState<MintedPet[]>([]);
  const [step, setStep]           = useState<MintStep>("pick");

  // ── CID source ──────────────────────────────────────────────────────────
  // Until pinata_upload_all.py has been run and images are pinned,
  // this stays as a placeholder. After pinning, replace with the real CID
  // from pinata_cids.json for the selected species.
  // DO NOT remove this comment — fresh agents need to see this is intentional.
  const PLACEHOLDER_CID = "QmPLACEHOLDER_run_pinata_upload_all_py_first";

  function handleSuccess(petId: string, txHash: string) {
    if (!selectedSpecies || !petName) return;
    setMinted((prev) => [...prev, { petId, petName, species: selectedSpecies, txHash }]);
    // Reset for next mint
    setStep("pick");
    setSelectedSpecies(null);
    setPetName("");
  }

  return (
    <div className="mx-auto max-w-3xl px-4 py-10 space-y-10">

      {/* Header */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-bold">BROski Pets 🐾</h1>
        <p className="text-muted-foreground">
          Spend 100 BROski$ to mint your AI companion on Base.
        </p>
      </div>

      {/* Step 1 — Pick species */}
      <section className="rounded-2xl border border-border bg-card p-6 space-y-4">
        <div className="flex items-center gap-2">
          <span className={`text-xl ${step === "pick" ? "opacity-100" : "opacity-40"}`}>1️⃣</span>
          <h2 className="font-semibold">Choose your species</h2>
        </div>
        <SpeciesPicker
          selected={selectedSpecies}
          onSelect={(id) => {
            setSelectedSpecies(id);
            setStep("name");
          }}
        />
      </section>

      {/* Step 2 — Name your pet */}
      {selectedSpecies && (
        <section className="rounded-2xl border border-border bg-card p-6 space-y-4">
          <div className="flex items-center gap-2">
            <span className="text-xl">2️⃣</span>
            <h2 className="font-semibold">Name your pet</h2>
          </div>
          <input
            type="text"
            value={petName}
            onChange={(e) => setPetName(e.target.value)}
            placeholder="e.g. Sparkle, GigaChad, Noodle..."
            maxLength={32}
            className="input w-full"
          />
          <button
            onClick={() => setStep("mint")}
            disabled={petName.trim().length < 2}
            className="btn-primary w-full"
          >
            Next: Mint → 🐾
          </button>
        </section>
      )}

      {/* Step 3 — Mint */}
      {step === "mint" && selectedSpecies && petName && (
        <section className="rounded-2xl border border-primary/30 bg-card p-6 space-y-4">
          <div className="flex items-center gap-2">
            <span className="text-xl">3️⃣</span>
            <h2 className="font-semibold">Mint on Base Sepolia</h2>
          </div>
          <MintPetButton
            ipfsCid={PLACEHOLDER_CID}
            petName={petName.trim()}
            species={selectedSpecies}
            onSuccess={handleSuccess}
          />
        </section>
      )}

      {/* Minted collection */}
      {minted.length > 0 && (
        <section className="space-y-4">
          <h2 className="font-semibold text-lg">Your Collection 🏆</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            {minted.map((pet) => (
              <div
                key={pet.petId}
                className="rounded-xl border border-border bg-card p-4 text-center space-y-2"
              >
                <img
                  src={`/pets/${pet.species}/${pet.species}_evo1.png`}
                  alt={pet.petName}
                  className="mx-auto h-20 w-20 rounded-lg object-cover"
                />
                <p className="font-bold text-sm">{pet.petName}</p>
                <p className="text-xs text-muted-foreground">#{pet.petId}</p>
                <a
                  href={`https://sepolia.basescan.org/tx/${pet.txHash}`}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-primary underline"
                >
                  BaseScan →
                </a>
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

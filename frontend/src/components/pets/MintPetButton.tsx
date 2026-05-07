/**
 * MintPetButton.tsx
 * Drives the existing useMintPet() hook — DO NOT swap the hook.
 * State machine: idle → authorizing → awaiting-signature → mining → success | error
 * Balance gate: hides button if BROski$ < 100.
 * Success state: shows pet image + BaseScan link.
 */

import { useEffect } from "react";
import { useAccount } from "wagmi";
import { ConnectButton } from "@rainbow-me/rainbowkit";
import { useMintPet } from "@/hooks/useMintPet";
import type { SpeciesId } from "./SpeciesPicker";

const MINT_COST = 100;

const STEP_LABELS: Record<string, string> = {
  idle:                 "Mint My Pet 🐾",
  authorizing:          "Spending BROski$...",
  "awaiting-signature": "Approve in wallet...",
  mining:               "Waiting for block...",
  success:              "Minted! 🎉",
  error:                "Try again",
};

const STEP_TRAIL = [
  { key: "authorizing",         icon: "💸", label: "Spend"  },
  { key: "awaiting-signature",  icon: "✍️",  label: "Sign"   },
  { key: "mining",              icon: "⛓️",  label: "Mine"   },
];

interface MintPetButtonProps {
  ipfsCid: string;
  petName: string;
  species: SpeciesId;
  onSuccess?: (petId: string, txHash: string) => void;
}

export function MintPetButton({ ipfsCid, petName, species, onSuccess }: MintPetButtonProps) {
  const { isConnected } = useAccount();
  // useMintPet is the canonical hook — string petId + string ipfsCID, matches contract typehash
  const { mint, step, error, txHash, petId, balance, isLoading } = useMintPet();

  const canAfford = (balance ?? 0) >= MINT_COST;
  const isWorking = isLoading;
  const isDone    = step === "success";
  const isErr     = step === "error";

  useEffect(() => {
    if (isDone && petId && txHash) onSuccess?.(petId, txHash);
  }, [isDone, petId, txHash, onSuccess]);

  if (!isConnected) {
    return (
      <div className="flex flex-col items-center gap-3 w-full">
        <ConnectButton label="Connect Wallet to Mint 🔗" />
        <p className="text-xs text-muted-foreground">
          MetaMask · Coinbase · Rainbow · WalletConnect
        </p>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 w-full">

      {/* BROski$ balance bar */}
      <div className="flex items-center justify-between rounded-xl bg-muted/50 px-4 py-2 text-sm">
        <span className="text-muted-foreground">BROski$ balance</span>
        <span className={`font-bold ${canAfford ? "text-green-400" : "text-red-400"}`}>
          {balance === null ? "..." : balance}
          <span className="font-normal text-muted-foreground"> / {MINT_COST} needed</span>
        </span>
      </div>

      {/* Mint button */}
      <button
        onClick={() => mint(ipfsCid, petName, species)}
        disabled={isWorking || isDone || !canAfford || !ipfsCid}
        className={`
          btn-primary w-full py-3 text-base font-bold transition-all duration-200
          ${isWorking ? "animate-pulse opacity-80 cursor-wait" : ""}
          ${!canAfford && !isWorking ? "opacity-40 cursor-not-allowed" : ""}
        `}
      >
        {STEP_LABELS[step] ?? STEP_LABELS.idle}
      </button>

      {/* Earn more hint */}
      {!canAfford && !isWorking && (
        <p className="text-center text-xs text-amber-400">
          💰 Earn more BROski$ by completing courses!
        </p>
      )}

      {/* Step progress trail */}
      {isWorking && (
        <div className="flex justify-center gap-4 text-xs">
          {STEP_TRAIL.map(({ key, icon, label }) => (
            <span
              key={key}
              className={`flex items-center gap-1 transition-all ${
                step === key
                  ? "text-primary font-bold scale-110"
                  : "text-muted-foreground opacity-40"
              }`}
            >
              {icon} {label}
            </span>
          ))}
        </div>
      )}

      {/* Success */}
      {isDone && txHash && (
        <div className="rounded-xl border border-green-500/30 bg-green-500/10 p-4 text-center space-y-2">
          <p className="font-bold text-green-400 text-base">
            🎉 {petName} (#{petId}) is alive!
          </p>
          <img
            src={`/pets/${species}/${species}_evo1.png`}
            alt={petName}
            className="mx-auto h-24 w-24 rounded-xl object-cover"
          />
          <a
            href={`https://sepolia.basescan.org/tx/${txHash}`}
            target="_blank"
            rel="noreferrer"
            className="text-xs text-muted-foreground underline block"
          >
            View on BaseScan →
          </a>
        </div>
      )}

      {/* Error */}
      {isErr && error && (
        <p className="text-sm text-red-400 text-center">⚠️ {error}</p>
      )}
    </div>
  );
}

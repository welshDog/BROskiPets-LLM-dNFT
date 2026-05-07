/**
 * SpeciesPicker.tsx
 * Grid of 10 BROski Pet species — click to select.
 * Images served from /pets/{species}/{species}_evo1.png (Option B: Vercel public/)
 * Switch to Pinata gateway URLs after running pinata_upload_all.py (Option A).
 */

const SPECIES = [
  { id: "apex_dragon",         label: "Apex Dragon",         emoji: "🐉" },
  { id: "blizzard_lizard",     label: "Blizzard Lizard",     emoji: "🦎" },
  { id: "chaos_cat",           label: "Chaos Cat",           emoji: "🐱" },
  { id: "cyber_fox",           label: "Cyber Fox",           emoji: "🦊" },
  { id: "gigabyte_guinea_pig", label: "Gigabyte Guinea Pig", emoji: "🐹" },
  { id: "hyper_beam_bunny",    label: "Hyper Beam Bunny",    emoji: "🐰" },
  { id: "hyper_hamster",       label: "Hyper Hamster",       emoji: "🐭" },
  { id: "hyperfocus_horse",    label: "Hyperfocus Horse",    emoji: "🐴" },
  { id: "power_pup",           label: "Power Pup",           emoji: "🐶" },
  { id: "sonic_spider",        label: "Sonic Spider",        emoji: "🕷️" },
] as const;

export type SpeciesId = typeof SPECIES[number]["id"];

interface SpeciesPickerProps {
  selected: SpeciesId | null;
  onSelect: (id: SpeciesId) => void;
}

export function SpeciesPicker({ selected, onSelect }: SpeciesPickerProps) {
  return (
    <div className="w-full">
      <p className="mb-3 text-sm font-semibold text-muted-foreground uppercase tracking-wide">
        Choose your species
      </p>
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {SPECIES.map((s) => {
          const isSelected = selected === s.id;
          return (
            <button
              key={s.id}
              onClick={() => onSelect(s.id)}
              className={`
                flex flex-col items-center gap-2 rounded-xl border p-3
                transition-all duration-150 hover:scale-105
                ${
                  isSelected
                    ? "border-primary bg-primary/10 ring-2 ring-primary"
                    : "border-border bg-muted/30 hover:border-primary/50"
                }
              `}
            >
              <img
                src={`/pets/${s.id}/${s.id}_evo1.png`}
                alt={s.label}
                className="h-16 w-16 rounded-lg object-cover"
                onError={(e) => {
                  // Emoji fallback if image not yet copied to public/pets/
                  (e.currentTarget as HTMLImageElement).style.display = "none";
                }}
              />
              <span className="text-2xl">{s.emoji}</span>
              <span className="text-center text-xs font-medium leading-tight">
                {s.label}
              </span>
              {isSelected && (
                <span className="text-xs text-primary font-bold">Selected ✓</span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
}

import numpy as np
from ase.build import bulk

# --- settings ---
N_REP = 4                              # 4x4x4 conventional cells -> 256 atoms
A0_GUESS = 3.59                        # Å, rough austenitic guess, will be relaxed
ORDER = ["Fe", "Cr", "Ni"]             # MUST match the element order you use in pair_coeff
X = {"Fe": 0.545, "Cr": 0.266, "Ni": 0.189}   # your wt% -> at% result from Step 1
SEEDS = [11, 22, 33]

def counts(N):
    raw = {k: X[k] * N for k in ORDER}
    n = {k: int(np.floor(raw[k])) for k in ORDER}
    left = N - sum(n.values())
    for k in sorted(raw, key=lambda k: raw[k] - n[k], reverse=True)[:left]:
        n[k] += 1
    return n

atoms0 = bulk("Ni", "fcc", a=A0_GUESS, cubic=True).repeat((N_REP,) * 3)
N = len(atoms0)
n = counts(N)
print("N =", N, "counts =", n)

for s in SEEDS:
    rng = np.random.default_rng(s)
    species = np.concatenate([[k] * n[k] for k in ORDER])
    rng.shuffle(species)
    a = atoms0.copy()
    a.set_chemical_symbols(list(species))

    L = a.cell.lengths()
    pos = a.get_positions()
    types = [ORDER.index(sym) + 1 for sym in a.get_chemical_symbols()]
    with open(f"data/bulk_N{N}_seed{s}.data", "w") as f:
        f.write(f"Random Fe-Cr-Ni seed {s}\n\n{N} atoms\n3 atom types\n\n")
        f.write(f"0.0 {L[0]:.8f} xlo xhi\n0.0 {L[1]:.8f} ylo yhi\n0.0 {L[2]:.8f} zlo zhi\n\n")
        f.write("Masses\n\n1 55.845\n2 51.996\n3 58.693\n\nAtoms # atomic\n\n")
        for i, (t, p) in enumerate(zip(types, pos), 1):
            f.write(f"{i} {t} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}\n")
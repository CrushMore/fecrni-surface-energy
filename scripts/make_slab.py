import sys
import numpy as np
from ase.build import fcc111, fcc100, fcc110

# usage: python scripts/make_slab.py SURF NX NY NLAYERS GAP SEED [A]
surf   = sys.argv[1]            # 111, 100 or 110
nx, ny = int(sys.argv[2]), int(sys.argv[3])
nl     = int(sys.argv[4])       # number of atomic layers
gap    = float(sys.argv[5])     # vacuum gap between periodic images (Å)
seed   = int(sys.argv[6])
a      = float(sys.argv[7]) if len(sys.argv) > 7 else 3.55

ORDER = ["Fe", "Cr", "Ni"]
X = {"Fe": 0.545, "Cr": 0.266, "Ni": 0.189}   # same as Step 2
MASS = [55.845, 51.996, 58.693]

build = {"111": fcc111, "100": fcc100, "110": fcc110}[surf]
slab = build("Ni", size=(nx, ny, nl), a=a, vacuum=0.0, orthogonal=True)
N = len(slab)

# integer counts (largest remainder), then random shuffle
raw = {k: X[k] * N for k in ORDER}
n = {k: int(np.floor(raw[k])) for k in ORDER}
for k in sorted(raw, key=lambda k: raw[k] - n[k], reverse=True)[: N - sum(n.values())]:
    n[k] += 1
species = np.concatenate([[k] * n[k] for k in ORDER])
np.random.default_rng(seed).shuffle(species)

pos = slab.get_positions()
zmin, zmax = pos[:, 2].min(), pos[:, 2].max()
Lx, Ly = slab.cell[0][0], slab.cell[1][1]
Lz = (zmax - zmin) + gap                 # gap = distance between periodic slab images
pos[:, 2] += gap / 2 - zmin

name = f"slab_{surf}_{nx}x{ny}x{nl}_g{gap:g}_s{seed}"
with open(f"data/{name}.data", "w") as f:
    f.write(f"{name}\n\n{N} atoms\n3 atom types\n\n")
    f.write(f"0 {Lx:.8f} xlo xhi\n0 {Ly:.8f} ylo yhi\n0 {Lz:.8f} zlo zhi\n\n")
    f.write("Masses\n\n" + "\n".join(f"{i+1} {m}" for i, m in enumerate(MASS)))
    f.write("\n\nAtoms # atomic\n\n")
    for i, (s, p) in enumerate(zip(species, pos), 1):
        f.write(f"{i} {ORDER.index(s)+1} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}\n")

print(name, "N =", N, "counts =", n, "Lx,Ly,Lz =", round(Lx,3), round(Ly,3), round(Lz,3))

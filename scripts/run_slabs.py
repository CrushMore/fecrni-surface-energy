import subprocess, shutil, os, re
import numpy as np
from concurrent.futures import ThreadPoolExecutor

LMP = "lmp"
GAP = 20
SEEDS = [11, 22, 33]
TEMPS = [300, 500, 700]
A_T  = {300: 3.5745, 500: 3.5932, 700: 3.6142}          # from NPT bulk
EB_T = {300: -4.07956, 500: -4.04909, 700: -4.01573}    # eV/atom
# surface: (NX, NY, layers)  -- CHECK the printed N, Lx, Ly on the first run
SURF = {"111": (8, 8, 8), "100": (8, 8, 9), "110": (8, 6, 12)}

jobs = []
for surf, (nx, ny, nl) in SURF.items():
    for T in TEMPS:
        for s in SEEDS:
            base = f"slab_{surf}_{nx}x{ny}x{nl}_g{GAP}_s{s}"
            name = f"{base}_T{T}"
            if not os.path.exists(f"data/{name}.data"):
                subprocess.run(["python", "scripts/make_slab.py", surf, str(nx), str(ny),
                                str(nl), str(GAP), str(s), str(A_T[T])], check=True)
                shutil.move(f"data/{base}.data", f"data/{name}.data")
            jobs.append((surf, T, s, name))

def run(j):
    surf, T, s, name = j
    log = f"data/log_{name}.txt"
    if not os.path.exists(log) or "RESULT_SLAB_T" not in open(log).read():
        subprocess.run([LMP, "-in", "slab_NVT.in", "-var", "name", name, "-var", "T", str(T),
                        "-var", "seed", str(s), "-log", f"../{log}", "-screen", "none"],
                       cwd="lammps", check=True)
    return j

with ThreadPoolExecutor(max_workers=8) as ex:
    list(ex.map(run, jobs))

rows = []
for surf, T, s, name in jobs:
    for line in open(f"data/log_{name}.txt"):
        if line.startswith("RESULT_SLAB_T"):
            p = line.split()
            N, E, Lx, Ly = int(p[5]), float(p[7]), float(p[9]), float(p[11])
            g = (E - N * EB_T[T]) / (2 * Lx * Ly) * 16.0217663
            rows.append((surf, T, s, N, E, g))

import csv
with open("data/gamma_production.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["surface", "T_K", "seed", "N", "E_eV", "gamma_J_m2"]); w.writerows(rows)

print("\n===== gamma (J/m2), mean +- std over seeds 11, 22, 33 =====")
for surf in SURF:
    for T in TEMPS:
        g = np.array([r[5] for r in rows if r[0] == surf and r[1] == T])
        print(f"({surf}) {T} K: {g.mean():.3f} +- {g.std(ddof=1):.3f}   N={rows[[r[0]==surf for r in rows].index(True)][3]}")
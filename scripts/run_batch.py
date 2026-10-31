import subprocess, csv, os
EBULK = -4.1201          # provisional; we will recompute with the 12-seed mean
LMP = "lmp"
SURF, NX, NY, GAP = "111", 4, 4, 20
LAYERS = [6, 8, 10, 12]
SEEDS = [11, 22, 33, 44, 55]

rows = []
for nl in LAYERS:
    for s in SEEDS:
        name = f"slab_{SURF}_{NX}x{NY}x{nl}_g{GAP}_s{s}"
        log = f"data/log_{name}.txt"
        if not os.path.exists(log):
            subprocess.run(["python", "scripts/make_slab.py", SURF, str(NX), str(NY), str(nl), str(GAP), str(s)], check=True)
            subprocess.run([LMP, "-in", "slab_0K.in", "-var", "name", name, "-var", "Ebulk", str(EBULK),
                            "-log", f"../{log}"], cwd="lammps", check=True)
        for line in open(log):
            if line.startswith("RESULT_SLAB"):
                p = line.split()
                rows.append([name, nl, s, int(p[3]), float(p[5]), float(p[7])])
with open("data/conv_thickness_111.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["name", "layers", "seed", "N", "E_eV", "gamma_J_m2"]); w.writerows(rows)

import numpy as np
for nl in LAYERS:
    g = np.array([r[5] for r in rows if r[1] == nl])
    print(nl, "layers: mean", round(g.mean(), 3), "std", round(g.std(ddof=1), 3),
          "SE", round(g.std(ddof=1) / np.sqrt(len(g)), 3))
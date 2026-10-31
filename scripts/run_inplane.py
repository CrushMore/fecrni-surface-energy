import subprocess, csv, os
import numpy as np

EBULK = -4.1201          # provisional, recomputed later with the final bulk average
LMP = "lmp"              # change if your LAMMPS command has a different name
SURF, NL, GAP = "111", 8, 20
SIZES = [(4, 4), (6, 6), (8, 8)]    # (NX, NY); NY must be even for (111)
SEEDS = [11, 22, 33, 44, 55]

rows = []
for nx, ny in SIZES:
    for s in SEEDS:
        name = f"slab_{SURF}_{nx}x{ny}x{NL}_g{GAP}_s{s}"
        log = f"data/log_{name}.txt"
        if not os.path.exists(log):
            subprocess.run(["python", "scripts/make_slab.py", SURF, str(nx), str(ny),
                            str(NL), str(GAP), str(s)], check=True, stdout=subprocess.DEVNULL)
            subprocess.run([LMP, "-in", "slab_0K.in", "-var", "name", name,
                            "-var", "Ebulk", str(EBULK), "-log", f"../{log}",
                            "-screen", "none"], cwd="lammps", check=True)
        for line in open(log):
            if line.startswith("RESULT_SLAB"):
                p = line.split()
                rows.append([name, f"{nx}x{ny}", s, int(p[3]), float(p[5]), float(p[7])])

with open("data/conv_inplane_111.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["name", "size", "seed", "N", "E_eV", "gamma_J_m2"])
    w.writerows(rows)

print("\n===== IN-PLANE SIZE TEST SUMMARY (111, 8 layers, gap 20) =====")
for nx, ny in SIZES:
    g = np.array([r[5] for r in rows if r[1] == f"{nx}x{ny}"])
    print(f"{nx}x{ny}: N {[r[3] for r in rows if r[1] == f'{nx}x{ny}'][0]}  mean {g.mean():.3f}  std {g.std(ddof=1):.3f}  SE {g.std(ddof=1)/np.sqrt(len(g)):.3f}")
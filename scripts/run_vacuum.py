import subprocess, csv, os
import numpy as np

EBULK = -4.1201          # provisional, we will recompute with the final bulk average
LMP = "lmp"              # change if your LAMMPS command has a different name
SURF, NX, NY, NL = "111", 4, 4, 8
GAPS = [10, 15, 20, 25, 30]
SEEDS = [11, 22, 33, 44, 55]

rows = []
for gap in GAPS:
    for s in SEEDS:
        name = f"slab_{SURF}_{NX}x{NY}x{NL}_g{gap}_s{s}"
        log = f"data/log_{name}.txt"
        if not os.path.exists(log):
            subprocess.run(["python", "scripts/make_slab.py", SURF, str(NX), str(NY),
                            str(NL), str(gap), str(s)], check=True, stdout=subprocess.DEVNULL)
            subprocess.run([LMP, "-in", "slab_0K.in", "-var", "name", name,
                            "-var", "Ebulk", str(EBULK), "-log", f"../{log}",
                            "-screen", "none"], cwd="lammps", check=True)
        for line in open(log):
            if line.startswith("RESULT_SLAB"):
                p = line.split()
                rows.append([name, gap, s, int(p[3]), float(p[5]), float(p[7])])

with open("data/conv_vacuum_111.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["name", "gap_A", "seed", "N", "E_eV", "gamma_J_m2"])
    w.writerows(rows)

print("\n===== VACUUM TEST SUMMARY (111, 8 layers, 4x4) =====")
for gap in GAPS:
    g = np.array([r[5] for r in rows if r[1] == gap])
    print(f"gap {gap} A: mean {g.mean():.3f}  std {g.std(ddof=1):.3f}  SE {g.std(ddof=1)/np.sqrt(len(g)):.3f}")
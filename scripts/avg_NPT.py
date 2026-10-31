import numpy as np, glob
for T in (300, 500, 700):
    for s in (11, 22, 33):
        d = np.loadtxt(f"data/npt_bulk_T{T}_s{s}.txt", comments="#")
        print(f"T {T} seed {s}: E_per_atom {d[:,1].mean():.5f}  a {d[:,2].mean():.4f}  (n={len(d)})")

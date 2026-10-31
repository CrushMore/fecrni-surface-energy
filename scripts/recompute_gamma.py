import pandas as pd, numpy as np, re, glob

# E_bulk = mean of the three 500-atom cells (fill in from your RESULT lines)
EB_SEEDS = {11: -4.11926318447617, 22: -4.12141186578537, 33: -4.11956385106335}
EB = float(np.mean(list(EB_SEEDS.values())))
EB_STD = float(np.std(list(EB_SEEDS.values()), ddof=1))
print(f"E_bulk = {EB:.5f} eV/atom, std across 3 cells = {EB_STD:.5f}")

def area(name):
    t = open(f"data/{name}.data").read()
    lx = float(re.search(r"0(?:\.0+)? ([\d.]+) xlo xhi", t).group(1))
    ly = float(re.search(r"0(?:\.0+)? ([\d.]+) ylo yhi", t).group(1))
    return lx * ly

for f in ["conv_thickness_111", "conv_vacuum_111", "conv_inplane_111"]:
    d = pd.read_csv(f"data/{f}.csv")
    d = d[d.seed.isin([11, 22, 33])].copy()
    d["gamma_new"] = [(r.E_eV - r.N * EB) / (2 * area(r["name"])) * 16.0217663
                      for _, r in d.iterrows()]
    d.to_csv(f"data/{f}_final.csv", index=False)
    key = d.columns[1]
    print("\n", f)
    for k, g in d.groupby(key):
        x = g.gamma_new.values
        print(f"{key} {k}: mean {x.mean():.3f} std {x.std(ddof=1):.3f}")
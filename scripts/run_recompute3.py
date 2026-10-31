import pandas as pd, numpy as np
for f, col in [("conv_thickness_111", "layers"), ("conv_vacuum_111", "gap_A"), ("conv_inplane_111", "size")]:
    d = pd.read_csv(f"data/{f}.csv")
    d = d[d.seed.isin([11, 22, 33])]
    print("\n", f)
    for k, g in d.groupby(col):
        x = g.gamma_J_m2.values
        print(f"{col} {k}: n={len(x)} mean {x.mean():.3f} std {x.std(ddof=1):.3f} SE {x.std(ddof=1)/np.sqrt(len(x)):.3f}")
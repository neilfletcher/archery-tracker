# Regenerates agb-data.js from archeryutils (pip install archeryutils). Run: python3 tools/gen-agb-data.py
import json, numpy as np
from archeryutils import load_rounds as L
import archeryutils.handicaps as hc
import archeryutils.classifications as c
from archeryutils.classifications.AGB_data import AGB_bowstyles as B, AGB_genders as G, AGB_ages as A
from archeryutils.classifications.agb_outdoor_classifications import agb_outdoor_classifications as OD
from archeryutils.classifications.agb_indoor_classifications import agb_indoor_classifications as ID
scheme = hc.handicap_scheme("AGB")
H = np.arange(0, 151)
bows = {"Recurve": B.RECURVE, "Barebow": B.BAREBOW, "Compound": B.COMPOUND, "Longbow": B.LONGBOW}
genders = {"Open": G.OPEN, "Female": G.FEMALE}
ages = {"Adult": A.ADULT, "50+": A.OVER_50, "U21": A.UNDER_21, "U18": A.UNDER_18, "U16": A.UNDER_16, "U15": A.UNDER_15, "U14": A.UNDER_14, "U12": A.UNDER_12}
out = {"rounds": {}, "classHC": {"outdoor": {}, "indoor": {}}}
sets = [("outdoor", L.AGB_outdoor_imperial), ("outdoor", L.AGB_outdoor_metric), ("outdoor", L.WA_outdoor),
        ("indoor", L.AGB_indoor), ("indoor", L.WA_indoor), ("misc", L.misc)]
for loc, rs in sets:
    for code, r in rs.items():
        pass  # all miscellaneous rounds (252s, Frostbite, 2 and 3 dozen practice rounds, Lancaster)
        scores = scheme.score_for_round(H, r, rounded_score=True).astype(int).tolist()
        # store as descending deltas to keep it compact
        entry = {"n": r.name, "a": int(sum(p.n_arrows for p in r.passes)), "loc": "indoor" if (loc == "indoor" or code.startswith("lancaster")) else "outdoor", "max": int(r.max_score()),
                 "s": scores, "cls": {}}
        for bn, b in bows.items():
          for gn, g in genders.items():
            for an, a in ages.items():
                try:
                    if loc == "outdoor":
                        v = c.agb_outdoor_classification_scores(code, b, g, a)
                    elif loc == "indoor":
                        v = c.agb_indoor_classification_scores(code, b, g, a)
                    else:
                        continue
                except Exception as e:
                    continue
                entry["cls"].setdefault(bn, {}).setdefault(gn, {})[an] = [int(x) if x > 0 else None for x in v]
        out["rounds"][code] = entry
for bn in bows:
  for gn in ["Open", "Female"]:
    for an, key in [("Adult","ADULT"),("50+","OVER_50"),("U21","UNDER_21"),("U18","UNDER_18"),("U16","UNDER_16"),("U15","UNDER_15"),("U14","UNDER_14"),("U12","UNDER_12")]:
        g = f"{key}_{gn.upper()}_{bn.upper()}"
        out["classHC"]["outdoor"].setdefault(bn, {}).setdefault(gn, {})[an] = [float(x) for x in OD[g]["class_HC"]]
        out["classHC"]["indoor"].setdefault(bn, {}).setdefault(gn, {})[an] = [float(x) for x in ID[g]["class_HC"]]
print(len(out["rounds"]))
print(out["classHC"]["outdoor"]["Barebow"], out["classHC"]["indoor"]["Barebow"])
print(out["rounds"]["misc_252_20"]["n"], out["rounds"]["misc_252_20"]["s"][40:60])
# compact encode scores: first value + deltas
for r in out["rounds"].values():
    s = r["s"]; r["s"] = [s[0]] + [s[i-1]-s[i] for i in range(1, len(s))]
js = "/* Generated from archeryutils " + "3.0.0" + " (AGB 2023 handicap and classification scheme, open and female categories, all age groups). Do not edit by hand. */\nwindow.AGB_DATA = " + json.dumps(out, separators=(",", ":")) + ";\n"
open(__import__("os").path.join(__import__("os").path.dirname(__file__), "..", "agb-data.js"), "w").write(js)
print(len(js))
